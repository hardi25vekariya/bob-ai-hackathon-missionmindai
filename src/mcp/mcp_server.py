"""
========================================================================================
IBM BOB / MCP LAYER: MILITARY ASSET MISSION READINESS & PREDICTIVE MAINTENANCE
========================================================================================

Architecture Role:
This module represents "Stage 5: IBM Bob / MCP Layer" in docs/architecture.md.
It wraps the Python analytical engines in src/pipeline/ (readiness_classifier, failure_predictor,
and maintenance_planner) as standard Model Context Protocol (MCP) tools.

Why MCP Grounding Matters for Defense & Aerospace:
When commanders or flight engineers ask mission-critical questions ("Why is Tail-108
grounded?", "Which assets should we repair with 2 crews?"), an ungrounded LLM may hallucinate
plausible-sounding reasons. By routing queries through these MCP tools, IBM Bob inspects
live sensor telemetry (vibration, temps, oil quality) and verified maintenance logs to deliver
100% deterministic, auditable, and fact-grounded responses.

----------------------------------------------------------------------------------------
HOW TO REGISTER THIS MCP SERVER WITH IBM BOB (per bob.ibm.com/docs):
----------------------------------------------------------------------------------------
1. Open your IBM Bob configuration file (e.g. mcp_config.json or Bob Assistant Settings).
2. Add this server under the 'mcpServers' section:

   {
     "mcpServers": {
       "military-readiness-copilot": {
         "command": "python",
         "args": ["src/mcp/mcp_server.py", "--stdio"],
         "env": {}
       }
     }
   }

3. Restart or reload IBM Bob. Bob will automatically discover the 3 registered tools:
   - get_fleet_readiness
   - get_asset_risk
   - get_maintenance_plan
========================================================================================
"""

import sys
import json
import os

# Add src/pipeline directory to sys.path so pipeline imports resolve cleanly
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PIPELINE_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "pipeline"))
_DATA_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "data"))

if _PIPELINE_DIR not in sys.path:
    sys.path.insert(0, _PIPELINE_DIR)

# Import existing core pipeline functions without reimplementing logic
from readiness_classifier import classify_readiness
from failure_predictor import predict_failures
from maintenance_planner import generate_maintenance_plan, DEFAULT_AVAILABLE_CREWS, DEFAULT_PARTS_INVENTORY

# Default data file paths
DEFAULT_SENSOR_PATH = os.path.join(_DATA_DIR, "sensor_data.csv")
DEFAULT_SERVICE_PATH = os.path.join(_DATA_DIR, "service_history.csv")


# =====================================================================
# MCP TOOL DEFINITIONS & SCHEMAS
# =====================================================================

TOOLS = [
    {
        "name": "get_fleet_readiness",
        "description": (
            "Retrieve the overall mission readiness status (READY vs NON-READY) for all "
            "aircraft in the fleet, including specific threshold breach explanations and "
            "recent maintenance history notes. Use this tool when the user asks fleet-level "
            "readiness questions like: 'Which assets are ready?', 'What is the fleet readiness "
            "status?', or 'Show all grounded aircraft.'"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "sensor_file": {
                    "type": "string",
                    "description": "Optional custom path to sensor CSV (defaults to 'src/data/sensor_data.csv')."
                },
                "service_file": {
                    "type": "string",
                    "description": "Optional custom path to service history CSV (defaults to 'src/data/service_history.csv')."
                }
            },
            "required": []
        }
    },
    {
        "name": "get_asset_risk",
        "description": (
            "Get the failure risk assessment, predicted at-risk subsystem component (engine, "
            "hydraulics, fuel_system, landing_gear, avionics), calculated risk score (0-100), "
            "and plain-language diagnostic rationale for a specific asset or the entire fleet. "
            "Use this tool when the user asks specific asset diagnostic questions like: 'Why is "
            "Tail-108 flagged?', 'What component is failing on Tail-112?', or 'Which aircraft have "
            "the highest failure risk?'"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "asset_id": {
                    "type": "string",
                    "description": "Optional asset identifier (e.g. 'Tail-101', 'Tail-108'). If omitted, returns all assets ranked by risk score."
                },
                "sensor_file": {
                    "type": "string",
                    "description": "Optional custom path to sensor CSV."
                },
                "service_file": {
                    "type": "string",
                    "description": "Optional custom path to service history CSV."
                }
            },
            "required": []
        }
    },
    {
        "name": "get_maintenance_plan",
        "description": (
            "Generate a prioritized maintenance triage schedule for non-ready assets under "
            "crew capacity and spare parts inventory constraints. Use this tool when the user "
            "asks maintenance planning or resource allocation questions like: 'What should we fix "
            "first?', 'Generate a work order plan with 2 crews and 1 engine spare', or 'Which jets "
            "are queued for repairs?'"
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "available_crews": {
                    "type": "integer",
                    "description": "Number of maintenance technician teams available (default: 3)."
                },
                "available_parts_per_component": {
                    "type": "object",
                    "description": "Dictionary of spare parts in stock per component, e.g. {'engine': 2, 'landing_gear': 1, 'avionics': 3, 'hydraulics': 2, 'fuel_system': 2}."
                },
                "sensor_file": {
                    "type": "string",
                    "description": "Optional custom path to sensor CSV."
                },
                "service_file": {
                    "type": "string",
                    "description": "Optional custom path to service history CSV."
                }
            },
            "required": []
        }
    }
]


# =====================================================================
# TOOL 1 HANDLER: get_fleet_readiness
# =====================================================================
def handle_get_fleet_readiness(sensor_file=None, service_file=None):
    """
    Executes classify_readiness() and returns structured JSON with summary metrics.
    """
    try:
        df = classify_readiness(sensor_file, service_file)
        
        total = len(df)
        ready_count = int(df["is_ready"].sum())
        non_ready_count = total - ready_count
        readiness_pct = round((ready_count / total) * 100, 1)

        records = df.to_dict(orient="records")

        return {
            "status": "success",
            "fleet_metrics": {
                "total_assets": total,
                "mission_ready_count": ready_count,
                "non_ready_count": non_ready_count,
                "readiness_rate_pct": readiness_pct
            },
            "assets": records
        }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "error_type": "FileNotFoundError",
            "message": f"Underlying dataset file missing: {str(e)}. Please check file paths."
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Error evaluating fleet readiness: {str(e)}"
        }


# =====================================================================
# TOOL 2 HANDLER: get_asset_risk
# =====================================================================
def handle_get_asset_risk(asset_id=None, sensor_file=None, service_file=None):
    """
    Executes predict_failures() and returns risk scores and diagnostic reasons.
    If asset_id is provided, returns data for that single asset; otherwise returns all.
    """
    try:
        df = predict_failures(sensor_file, service_file)

        if asset_id:
            clean_id = asset_id.strip()
            match = df[df["asset_id"].str.lower() == clean_id.lower()]

            if match.empty:
                valid_ids = df["asset_id"].tolist()
                return {
                    "status": "error",
                    "error_type": "AssetNotFound",
                    "message": f"Asset '{asset_id}' not found in fleet database.",
                    "available_assets": valid_ids
                }

            asset_record = match.iloc[0].to_dict()
            return {
                "status": "success",
                "asset_id": asset_record["asset_id"],
                "is_ready": bool(asset_record["is_ready"]),
                "predicted_component_at_risk": asset_record["predicted_component_at_risk"],
                "risk_score": float(asset_record["risk_score"]),
                "reason": asset_record["reason"],
                "diagnostic_reason": asset_record["reason"],
                "readiness_details": asset_record["readiness_explanation"],
                "cancellation_probability": float(asset_record.get("cancellation_probability", 0.0)),
                "subsystem_risks": asset_record.get("subsystem_risks", {})
            }

        else:
            records = df.to_dict(orient="records")
            return {
                "status": "success",
                "total_evaluated": len(records),
                "ranked_risk_list": records
            }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "error_type": "FileNotFoundError",
            "message": f"Dataset file missing: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Error calculating failure risks: {str(e)}"
        }


# =====================================================================
# TOOL 3 HANDLER: get_maintenance_plan
# =====================================================================
def handle_get_maintenance_plan(
    available_crews=DEFAULT_AVAILABLE_CREWS,
    available_parts_per_component=None,
    sensor_file=None,
    service_file=None
):
    """
    Executes generate_maintenance_plan() with resource constraints and returns
    the executive summary and prioritized work order schedule as JSON.
    """
    try:
        if available_crews is None or available_crews < 0:
            available_crews = DEFAULT_AVAILABLE_CREWS
        else:
            available_crews = int(available_crews)

        if available_parts_per_component is None or not isinstance(available_parts_per_component, dict):
            parts_input = DEFAULT_PARTS_INVENTORY
        else:
            parts_input = available_parts_per_component

        summary, plan_df = generate_maintenance_plan(
            available_crews=available_crews,
            available_parts=parts_input,
            sensor_file=sensor_file,
            service_file=service_file
        )

        plan_records = plan_df.to_dict(orient="records")
        scheduled_count = sum(1 for r in plan_records if r["status"] == "scheduled")
        queued_count = sum(1 for r in plan_records if r["status"] == "queued")

        return {
            "status": "success",
            "executive_summary": summary,
            "constraints_applied": {
                "available_crews": available_crews,
                "available_parts": parts_input
            },
            "metrics": {
                "total_requiring_maintenance": len(plan_records),
                "scheduled_count": scheduled_count,
                "queued_count": queued_count
            },
            "maintenance_schedule": plan_records
        }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "error_type": "FileNotFoundError",
            "message": f"Dataset file missing: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Error generating maintenance plan: {str(e)}"
        }


# =====================================================================
# MCP PROTOCOL DISPATCHER (JSON-RPC 2.0 / Stdio Support)
# =====================================================================
def dispatch_tool_call(tool_name, arguments):
    """
    Routes an incoming tool call to the appropriate handler.
    """
    if not isinstance(arguments, dict):
        arguments = {}

    if tool_name == "get_fleet_readiness":
        return handle_get_fleet_readiness(
            sensor_file=arguments.get("sensor_file"),
            service_file=arguments.get("service_file")
        )

    elif tool_name == "get_asset_risk":
        return handle_get_asset_risk(
            asset_id=arguments.get("asset_id"),
            sensor_file=arguments.get("sensor_file"),
            service_file=arguments.get("service_file")
        )

    elif tool_name == "get_maintenance_plan":
        return handle_get_maintenance_plan(
            available_crews=arguments.get("available_crews", DEFAULT_AVAILABLE_CREWS),
            available_parts_per_component=arguments.get("available_parts_per_component"),
            sensor_file=arguments.get("sensor_file"),
            service_file=arguments.get("service_file")
        )

    else:
        return {
            "status": "error",
            "error_type": "UnknownTool",
            "message": f"Tool '{tool_name}' is not recognized. Available tools: {[t['name'] for t in TOOLS]}"
        }


def run_mcp_stdio_server():
    """
    Standard MCP JSON-RPC 2.0 stdio server loop for integration with IBM Bob,
    Claude Desktop, Cursor, and any MCP-compliant client.
    """
    sys.stderr.write("[MCP Server] Military Asset Readiness Copilot MCP Server starting...\n")
    sys.stderr.flush()

    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            req_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})

            # MCP initialization handshake
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "military-readiness-copilot",
                            "version": "1.0.0"
                        }
                    }
                }
            # List available tools
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "tools": TOOLS
                    }
                }
            # Execute tool call
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                result_data = dispatch_tool_call(tool_name, tool_args)

                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_data, indent=2)
                            }
                        ]
                    }
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            err_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal JSON-RPC error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(err_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
        run_mcp_stdio_server()
    else:
        print("=" * 80)
        print("MCP SERVER STANDALONE TEST MODE")
        print("=" * 80)
        
        print(">>> TOOL 1: get_fleet_readiness")
        print(handle_get_fleet_readiness()["fleet_metrics"])

        print("\n>>> TOOL 2: get_asset_risk (Target: Tail-108)")
        print(json.dumps(handle_get_asset_risk("Tail-108"), indent=2))

        print("\n>>> TOOL 3: get_maintenance_plan (Crews: 2, Engine parts: 1)")
        plan_res = handle_get_maintenance_plan(available_crews=2, available_parts_per_component={"engine": 1, "landing_gear": 1, "avionics": 2, "hydraulics": 1, "fuel_system": 1})
        print("Summary:", plan_res["executive_summary"])
        print("Metrics:", plan_res["metrics"])
