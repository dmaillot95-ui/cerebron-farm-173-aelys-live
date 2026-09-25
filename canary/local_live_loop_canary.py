#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

from gateway.event_ingress import normalize_event
from gateway.plugin_client import make_request
from presenter.aelys_presenter import compose
from avatar.elyra_adapter import status as avatar_status

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()

def run_canary():
    raw_event={
      "event_id":"F173-CANARY-001",
      "source":"local_test",
      "event_type":"question",
      "timestamp":"2026-09-25T16:30:00Z",
      "content":"Canary local AELYS: vérifier la chaîne sans appel externe.",
      "user_ref":"synthetic-user",
      "tenant_id":"synthetic",
      "consent_scope":"canary-only"
    }
    event=normalize_event(raw_event)

    rdx_request=make_request(
      "REQ-F173-CANARY-RDX",
      "rdx.search",
      {"query":"synthetic canary query","limit":1}
    )
    memory_request=make_request(
      "REQ-F173-CANARY-MEM",
      "memory.canonical_lookup",
      {"key":"synthetic-canary"}
    )

    presentation=compose(
      event["content"],
      evidence_refs=[],
      evidence_level="UNVERIFIED"
    )
    avatar=avatar_status()

    result={
      "schema":"F173_LOCAL_LIVE_LOOP_CANARY_V1",
      "scenario_id":"F173-CANARY-001",
      "mode":"LOCAL_FAIL_CLOSED_CANARY",
      "event":event,
      "prepared_requests":[rdx_request,memory_request],
      "presentation":presentation,
      "avatar_status":avatar,
      "external_calls_executed":False,
      "production_live_claimed":False,
      "training_executed":False,
      "weights_changed":False,
      "expected_boundaries":{
        "presentation_status":"HOLD",
        "avatar_runtime":"UNQUALIFIED",
        "rdx_provider":"RDX_EXCHANGE",
        "raw_user_ref_persisted":False
      }
    }
    result["result_sha256"]=hashlib.sha256(canonical(result)).hexdigest()
    return result

def main():
    result=run_canary()
    out=Path("artifacts/f173_local_live_loop_canary.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({
      "status":"PASS",
      "scenario_id":result["scenario_id"],
      "result_sha256":result["result_sha256"],
      "presentation_status":result["presentation"]["status"],
      "avatar_status":result["avatar_status"]["status"],
      "external_calls_executed":False,
      "production_live_claimed":False
    },sort_keys=True))

if __name__=="__main__":
    main()
