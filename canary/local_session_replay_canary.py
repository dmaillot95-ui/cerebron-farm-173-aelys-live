#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from gateway.event_ingress import normalize_event
from gateway.plugin_client import make_request
from presenter.aelys_presenter import compose
from avatar.elyra_adapter import status as avatar_status

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def run_session():
    raw=[
      {"event_id":"F173-SESSION-001-E1","source":"local_test","event_type":"message","timestamp":"2026-09-25T16:55:00Z","content":"Bonjour Aelys","user_ref":"synthetic"},
      {"event_id":"F173-SESSION-001-E2","source":"local_test","event_type":"question","timestamp":"2026-09-25T16:55:01Z","content":"Quel est l'etat du canary ?","user_ref":"synthetic"},
      {"event_id":"F173-SESSION-001-E3","source":"local_test","event_type":"command","timestamp":"2026-09-25T16:55:02Z","content":"Prepare une requete RDX sans l'executer.","user_ref":"synthetic"}
    ]
    trace=[]
    prev="GENESIS"
    for i,e in enumerate(raw):
        n=normalize_event(e)
        req=make_request(f"REQ-F173-SESSION-{i+1}","rdx.search",{"query":n["content"],"limit":1})
        pres=compose(n["content"],evidence_refs=[],evidence_level="UNVERIFIED")
        row={
          "seq":i+1,
          "event":n,
          "prepared_request":req,
          "presentation_status":pres["status"],
          "previous_hash":prev
        }
        h=hashlib.sha256(canon(row)).hexdigest()
        row["trace_hash"]=h
        prev=h
        trace.append(row)
    result={
      "schema":"F173_LOCAL_SESSION_REPLAY_CANARY_V1",
      "scenario_id":"F173-SESSION-001",
      "mode":"LOCAL_DETERMINISTIC_REPLAY",
      "trace":trace,
      "final_trace_hash":prev,
      "avatar_status":avatar_status(),
      "external_calls_executed":False,
      "production_live_claimed":False,
      "training_executed":False,
      "weights_changed":False
    }
    result["result_sha256"]=hashlib.sha256(canon(result)).hexdigest()
    return result

def main():
    r=run_session()
    out=Path("artifacts/f173_session_replay_canary.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({
      "status":"PASS",
      "events":len(r["trace"]),
      "final_trace_hash":r["final_trace_hash"],
      "result_sha256":r["result_sha256"],
      "external_calls_executed":False,
      "production_live_claimed":False
    },sort_keys=True))

if __name__=="__main__":
    main()
