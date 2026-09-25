#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from dataclasses import dataclass

ALLOWED_SOURCES={"private_client_web","tiktok_live","local_test"}
ALLOWED_TYPES={"question","message","command"}

class IngressError(RuntimeError):
    pass

def normalize_event(event: dict) -> dict:
    required=("event_id","source","event_type","timestamp","content")
    missing=[k for k in required if not event.get(k)]
    if missing:
        raise IngressError("MISSING_FIELDS:"+",".join(missing))
    if event["source"] not in ALLOWED_SOURCES:
        raise IngressError("UNKNOWN_SOURCE")
    if event["event_type"] not in ALLOWED_TYPES:
        raise IngressError("UNKNOWN_EVENT_TYPE")
    content=str(event["content"]).strip()
    if not content or len(content)>4000:
        raise IngressError("CONTENT_LENGTH_INVALID")
    # Public control-plane events never persist raw identity by default.
    user_ref=event.get("user_ref")
    user_ref_hash=hashlib.sha256(str(user_ref).encode()).hexdigest() if user_ref else None
    out={
      "event_id":str(event["event_id"]),
      "source":event["source"],
      "event_type":event["event_type"],
      "timestamp":str(event["timestamp"]),
      "content":content,
      "user_ref_hash":user_ref_hash,
      "tenant_id":event.get("tenant_id"),
      "consent_scope":event.get("consent_scope"),
      "training_eligible":False
    }
    return out

if __name__=="__main__":
    import sys
    evt=json.loads(sys.stdin.read())
    print(json.dumps(normalize_event(evt),ensure_ascii=False,sort_keys=True))
