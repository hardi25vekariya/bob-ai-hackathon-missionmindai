import subprocess
import json
import os
import sys

print("=" * 80)
print("VERIFYING MCP PROTOCOL JSON-RPC OVER STDIO (src/mcp/mcp_server.py)")
print("=" * 80)

# Resolve path to mcp_server.py
server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")

# Spawn MCP stdio process
p = subprocess.Popen(
    [sys.executable, server_path, "--stdio"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

def rpc(method, params=None, req_id=1):
    req = {"jsonrpc": "2.0", "id": req_id, "method": method}
    if params is not None:
        req["params"] = params
    p.stdin.write(json.dumps(req) + "\n")
    p.stdin.flush()
    res = p.stdout.readline()
    return json.loads(res)

# 1. Test initialize
init_res = rpc("initialize", req_id=1)
print("\n[Step 1: Initialize Handshake]")
print(json.dumps(init_res, indent=2))

# 2. Test tools/list
tools_res = rpc("tools/list", req_id=2)
print("\n[Step 2: Tool Discovery (tools/list)]")
tools_list = tools_res["result"]["tools"]
print(f"Found {len(tools_list)} tools:")
for t in tools_list:
    desc_snippet = t["description"][:65]
    print(f"  - {t['name']}: {desc_snippet}...")

# 3. Test tools/call: get_fleet_readiness
call1_res = rpc("tools/call", {"name": "get_fleet_readiness", "arguments": {}}, req_id=3)
data1 = json.loads(call1_res["result"]["content"][0]["text"])
print("\n[Step 3: Call get_fleet_readiness]")
print(f"Status: {data1['status']}, Fleet Metrics: {data1['fleet_metrics']}")

# 4. Test tools/call: get_asset_risk for Tail-108
call2_res = rpc("tools/call", {"name": "get_asset_risk", "arguments": {"asset_id": "Tail-108"}}, req_id=4)
data2 = json.loads(call2_res["result"]["content"][0]["text"])
print("\n[Step 4: Call get_asset_risk for Tail-108]")
print(f"Asset: {data2['asset_id']}, Subsystem: {data2['predicted_component_at_risk']}, Score: {data2['risk_score']}")
print(f"Reason: {data2['reason']}")

# 5. Test tools/call: get_maintenance_plan with constraints
call3_res = rpc("tools/call", {"name": "get_maintenance_plan", "arguments": {"available_crews": 3, "available_parts_per_component": {"engine": 2, "landing_gear": 1, "avionics": 3, "hydraulics": 2, "fuel_system": 2}}}, req_id=5)
data3 = json.loads(call3_res["result"]["content"][0]["text"])
print("\n[Step 5: Call get_maintenance_plan]")
print(f"Executive Summary: {data3['executive_summary']}")
print(f"Scheduled: {data3['metrics']['scheduled_count']}, Queued: {data3['metrics']['queued_count']}")

p.kill()
print("\n" + "=" * 80)
print("VERIFICATION COMPLETE: MCP SERVER OPERATIONAL WITH ZERO ERRORS!")
print("=" * 80)
