from canary.local_live_loop_canary import run_canary

def test_local_live_loop_canary_is_deterministic():
    a=run_canary()
    b=run_canary()
    assert a==b
    assert len(a["result_sha256"])==64

def test_local_live_loop_canary_fails_closed():
    r=run_canary()
    assert r["event"]["source"]=="local_test"
    assert r["event"]["training_eligible"] is False
    assert "user_ref" not in r["event"]
    assert r["prepared_requests"][0]["provider"]=="RDX_EXCHANGE"
    assert r["presentation"]["status"]=="HOLD"
    assert r["avatar_status"]["status"]=="UNQUALIFIED"
    assert r["external_calls_executed"] is False
    assert r["production_live_claimed"] is False
    assert r["training_executed"] is False
    assert r["weights_changed"] is False
