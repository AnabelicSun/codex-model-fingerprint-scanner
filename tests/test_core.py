from codex_fingerprint.classify import classify_sample, summarize
from codex_fingerprint.limiter import GlobalStartLimiter, ProxySlots
from codex_fingerprint.model_preflight import classify_404, mapping_supports, with_identity_mapping


def test_behavior_beats_response_model():
    assert classify_sample(
        requested_model="gpt-6.2-astra",
        behavior_prediction="gpt-5.6-luna",
        response_model="gpt-6.2-astra",
    ) == "candidate_model_mismatch"


def test_platform_404_is_separate():
    assert classify_sample(
        requested_model="gpt-6.2-astra",
        response_model=None,
        http_status=404,
        error='Model "gpt-6.2-astra" is not supported by any configured account in this group',
    ) == "model_unavailable"


def test_429_is_separate():
    assert classify_sample(requested_model="gpt-6.2-astra", http_status=429) == "rate_limited"


def test_summary():
    assert summarize([{"classification": "rate_limited"}, {"classification": "rate_limited"}]) == {"rate_limited": 2}


def test_mapping_preflight_is_copy_and_supports_wildcards():
    original = {"gpt-6-astra": "gpt-6-astra", "gpt-5.*": "gpt-5.6"}
    extended = with_identity_mapping(original, "gpt-6.2-astra")
    assert "gpt-6.2-astra" not in original
    assert mapping_supports(extended, "gpt-6.2-astra")
    assert mapping_supports(original, "gpt-5.6-luna")
    assert classify_404('Model "x" is not available for this group') == "platform_group_allowlist"
    assert classify_404('Model "x" is not supported by any configured account in this group') == "platform_account_mapping"


def test_constructor_validation():
    try:
        GlobalStartLimiter(-1)
        assert False
    except ValueError:
        pass
    try:
        ProxySlots(0)
        assert False
    except ValueError:
        pass
