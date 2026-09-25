#!/usr/bin/env python3
from __future__ import annotations

class AvatarAdapterError(RuntimeError):
    pass

def status() -> dict:
    return {
      "schema":"F173_ELYRA_ADAPTER_STATUS_V1",
      "status":"UNQUALIFIED",
      "tts":"UNQUALIFIED",
      "lip_sync":"UNQUALIFIED",
      "face_animation":"UNQUALIFIED",
      "stream_output":"UNQUALIFIED",
      "reason":"NO_EXECUTABLE_RUNTIME_CANARY_YET"
    }

def speak(text: str) -> dict:
    raise AvatarAdapterError("ELYRA_RUNTIME_UNQUALIFIED")
