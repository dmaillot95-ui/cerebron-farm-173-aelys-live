import json
from pathlib import Path
import pytest

from gateway.event_ingress import IngressError, normalize_event
from gateway.plugin_client import PluginClientError, make_request, route
from avatar.elyra_adapter import AvatarAdapterError, speak, status

def test_unknown_capability_denied():
    with pytest.raises(PluginClientError):
        route("training.auto")

def test_live_event_never_training_eligible():
    out=normalize_event({
      "event_id":"E1","source":"local_test","event_type":"question",
      "timestamp":"TEST","content":"What is RDX?","user_ref":"tester"
    })
    assert out["training_eligible"] is False
    assert "user_ref" not in out
    assert len(out["user_ref_hash"])==64

def test_plugin_request_never_training_eligible():
    out=make_request("R1","rdx.search",{"query":"test"})
    assert out["provider"]=="F152_RDX"
    assert out["training_eligible"] is False
    assert len(out["sha256"])==64

def test_avatar_fails_closed_until_runtime_canary():
    assert status()["status"]=="UNQUALIFIED"
    with pytest.raises(AvatarAdapterError):
        speak("hello")
