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
    assert out["provider"]=="RDX_EXCHANGE"
    assert out["training_eligible"] is False
    assert len(out["sha256"])==64

def test_avatar_fails_closed_until_runtime_canary():
    assert status()["status"]=="UNQUALIFIED"
    with pytest.raises(AvatarAdapterError):
        speak("hello")


def test_f152_never_routes_rdx():
    routing=json.loads((Path(__file__).resolve().parents[1] / "config/live-routing.json").read_text())
    assert "F152_RDX" not in routing["knowledge_route"]
    assert "RDX_EXCHANGE" in routing["knowledge_route"]
    assert routing["routing_invariants"]["f152_identity"]=="BETA"
    assert routing["routing_invariants"]["f152_must_not_route_rdx"] is True


def test_runtime_qualification_stays_evidence_safe():
    q=json.loads((Path(__file__).resolve().parents[1] / "config/runtime-qualification.json").read_text())
    assert q["overall_status"]=="LOCAL_LIVE_LOOP_CANARY_PASS_EXTERNAL_RUNTIME_UNQUALIFIED"
    assert q["invariants"]["production_live"] is False
    assert q["invariants"]["training_executed"] is False
    assert q["invariants"]["weights_changed"] is False
    assert q["invariants"]["automatic_external_calls"] is False
    assert q["invariants"]["f152_routes_rdx"] is False
    assert q["invariants"]["rdx_provider"]=="RDX_EXCHANGE"
    assert "tts.external_runtime" in q["unqualified_external"]
    assert "avatar_runtime" in q["unqualified_external"]


def test_local_live_loop_canary_evidence_is_fail_closed():
    q=json.loads((Path(__file__).resolve().parents[1] / "config/runtime-qualification.json").read_text())
    c=q["local_live_loop_canary"]
    assert c["status"]=="PASS"
    assert c["run_id"]==36162553038
    assert c["result_sha256"]=="a860b0f9becd088496c6580b6febd608af0964e73c10b6ac04452048326fb3a4"
    assert c["external_calls_executed"] is False
    assert c["production_live_claimed"] is False
    assert c["avatar_runtime"]=="UNQUALIFIED"
    assert c["presentation_status"]=="HOLD"


def test_local_tts_canary_evidence_is_bounded():
    q=json.loads((Path(__file__).resolve().parents[1] / "config/runtime-qualification.json").read_text())
    t=q["local_tts_canary"]
    assert t["status"]=="PASS"
    assert t["run_id"]==36163338754
    assert t["engine"]=="espeak-ng"
    assert t["wav_bytes"]==166854
    assert t["wav_sha256"]=="71eea3f77b68a77b5ca773950c961f63d38b4f33ed06cffcab57c325e56a2e9e"
    assert t["external_service_used"] is False
    assert t["paid_provider_used"] is False
    assert t["production_live_claimed"] is False
    assert t["voice_identity_claimed"] is False
    assert "tts.external_runtime" in q["unqualified_external"]


def test_local_session_replay_canary_evidence_is_bounded():
    q=json.loads((Path(__file__).resolve().parents[1] / "config/runtime-qualification.json").read_text())
    r=q["local_session_replay_canary"]
    assert r["status"]=="PASS"
    assert r["run_id"]==36163483531
    assert r["events"]==3
    assert r["final_trace_hash"]=="abcc5451ebbcb0965a9f220d8b445b2504ff97471e8dba1cbc1426ce9dc783b8"
    assert r["result_sha256"]=="785eef06fa1357f513dbbee3f5dd87e9f36949a4e63588df67c4fffe6c404510"
    assert r["external_calls_executed"] is False
    assert r["production_live_claimed"] is False
    assert r["avatar_runtime"]=="UNQUALIFIED"
    assert r["presentation_status"]=="HOLD"
