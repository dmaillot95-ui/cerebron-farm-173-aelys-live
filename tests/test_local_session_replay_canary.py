from canary.local_session_replay_canary import run_session

def test_session_replay_deterministic_and_ordered():
    a=run_session()
    b=run_session()
    assert a==b
    assert len(a["trace"])==3
    assert [x["seq"] for x in a["trace"]]==[1,2,3]
    assert a["trace"][0]["previous_hash"]=="GENESIS"
    assert a["trace"][1]["previous_hash"]==a["trace"][0]["trace_hash"]
    assert a["trace"][2]["previous_hash"]==a["trace"][1]["trace_hash"]
    assert a["final_trace_hash"]==a["trace"][2]["trace_hash"]

def test_session_replay_stays_fail_closed():
    r=run_session()
    assert all(x["prepared_request"]["provider"]=="RDX_EXCHANGE" for x in r["trace"])
    assert all(x["presentation_status"]=="HOLD" for x in r["trace"])
    assert all("user_ref" not in x["event"] for x in r["trace"])
    assert r["avatar_status"]["status"]=="UNQUALIFIED"
    assert r["external_calls_executed"] is False
    assert r["production_live_claimed"] is False
    assert r["training_executed"] is False
