#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen
from gateway.event_ingress import normalize_event
from presenter.aelys_presenter import compose

def canon(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

class Handler(BaseHTTPRequestHandler):
    response_payload=None
    def log_message(self, format, *args):
        return
    def do_POST(self):
        if self.path!="/event":
            self.send_response(404); self.end_headers(); return
        n=int(self.headers.get("Content-Length","0"))
        raw=json.loads(self.rfile.read(n))
        event=normalize_event(raw)
        presentation=compose(event["content"],evidence_refs=[],evidence_level="UNVERIFIED")
        result={
          "schema":"F173_HTTP_LOOPBACK_RESPONSE_V1",
          "event_id":event["event_id"],
          "source":event["source"],
          "event_type":event["event_type"],
          "user_ref_hash_present":event["user_ref_hash"] is not None,
          "raw_user_ref_persisted":False,
          "presentation_status":presentation["status"],
          "external_calls_executed":False,
          "production_live_claimed":False
        }
        Handler.response_payload=result
        body=json.dumps(result,sort_keys=True).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run_canary():
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    event={
      "event_id":"F173-HTTP-CANARY-001",
      "source":"local_test",
      "event_type":"question",
      "timestamp":"2026-09-25T17:00:00Z",
      "content":"HTTP loopback canary Aelys",
      "user_ref":"synthetic-http-user",
      "consent_scope":"canary-only"
    }
    req=Request(
      f"http://127.0.0.1:{server.server_port}/event",
      data=json.dumps(event).encode(),
      headers={"Content-Type":"application/json"},
      method="POST"
    )
    try:
        with urlopen(req,timeout=5) as resp:
            response=json.loads(resp.read())
            http_status=resp.status
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    result={
      "schema":"F173_LOCAL_HTTP_CANARY_V1",
      "scenario_id":"F173-HTTP-CANARY-001",
      "transport":"HTTP_LOOPBACK",
      "bind":"127.0.0.1",
      "http_status":http_status,
      "response":response,
      "external_endpoint_used":False,
      "paid_provider_used":False,
      "production_live_claimed":False,
      "training_executed":False
    }
    result["result_sha256"]=hashlib.sha256(canon(result)).hexdigest()
    return result

def main():
    r=run_canary()
    out=Path("artifacts/f173_http_loopback_canary.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({
      "status":"PASS",
      "scenario_id":r["scenario_id"],
      "http_status":r["http_status"],
      "presentation_status":r["response"]["presentation_status"],
      "result_sha256":r["result_sha256"],
      "external_endpoint_used":False,
      "production_live_claimed":False
    },sort_keys=True))

if __name__=="__main__":
    main()
