from canary.local_http_loopback_canary import run_canary

def test_http_loopback_canary():
    r=run_canary()
    assert r["http_status"]==200
    assert r["transport"]=="HTTP_LOOPBACK"
    assert r["bind"]=="127.0.0.1"
    assert r["response"]["event_id"]=="F173-HTTP-CANARY-001"
    assert r["response"]["user_ref_hash_present"] is True
    assert r["response"]["raw_user_ref_persisted"] is False
    assert r["response"]["presentation_status"]=="HOLD"
    assert r["response"]["external_calls_executed"] is False
    assert r["external_endpoint_used"] is False
    assert r["paid_provider_used"] is False
    assert r["production_live_claimed"] is False
    assert r["training_executed"] is False
    assert len(r["result_sha256"])==64
