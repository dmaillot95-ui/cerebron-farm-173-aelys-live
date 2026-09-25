#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

class PluginClientError(RuntimeError):
    pass

CAPABILITY_PROVIDER={
  "rdx.search":"F152_RDX",
  "rdx.fetch":"F152_RDX",
  "memory.canonical_lookup":"F114",
  "memory.semantic_recall":"F115",
  "memory.lineage_check":"F116",
  "evidence.fetch":"F119",
  "governor.check":"F120",
  "presenter.compose":"AELYS",
  "avatar.speak":"ELYRA",
  "audit.review":"AFAH"
}

def route(capability: str) -> str:
    if capability not in CAPABILITY_PROVIDER:
        raise PluginClientError("UNKNOWN_CAPABILITY_DENY")
    return CAPABILITY_PROVIDER[capability]

def make_request(request_id: str, capability: str, payload: dict) -> dict:
    provider=route(capability)
    body={
      "schema":"F173_PLUGIN_REQUEST_V1",
      "request_id":request_id,
      "capability":capability,
      "provider":provider,
      "payload":payload,
      "training_eligible":False
    }
    raw=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    body["sha256"]=hashlib.sha256(raw).hexdigest()
    return body
