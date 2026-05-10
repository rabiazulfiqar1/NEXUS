"""
Unit tests for app.core.rate_limiter — configuration validation and identifier extraction.
"""
import pytest
from unittest.mock import MagicMock
from app.core.rate_limiter import RATE_LIMITS, rate_limit, _get_identifier


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RATE_LIMITS configuration
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestRateLimitsConfig:
    def test_all_expected_routes_present(self):
        expected_keys = {"resume_enhance", "cv_generate", "ats_score", "jobs_list", "career_analyze"}
        assert expected_keys == set(RATE_LIMITS.keys())

    def test_each_limit_is_tuple_of_two_ints(self):
        for key, value in RATE_LIMITS.items():
            assert isinstance(value, tuple), f"{key} is not a tuple"
            assert len(value) == 2, f"{key} tuple length is not 2"
            max_requests, window = value
            assert isinstance(max_requests, int)
            assert isinstance(window, int)
            assert max_requests > 0
            assert window > 0

    def test_window_is_one_hour(self):
        for key, (_, window) in RATE_LIMITS.items():
            assert window == 3600, f"{key} window is not 3600"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  rate_limit factory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestRateLimitFactory:
    def test_returns_callable(self):
        dep = rate_limit("resume_enhance")
        assert callable(dep)

    def test_raises_on_unknown_route(self):
        with pytest.raises(KeyError):
            rate_limit("nonexistent_route")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  _get_identifier
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TestGetIdentifier:
    def test_authenticated_user_returns_user_id(self):
        mock_request = MagicMock()
        mock_user = MagicMock()
        mock_user.id = "user-uuid-123"
        mock_request.state.user = mock_user

        result = _get_identifier(mock_request)
        assert result == "user-uuid-123"

    def test_no_user_falls_back_to_ip(self):
        mock_request = MagicMock()
        mock_request.state.user = None
        mock_request.client.host = "192.168.1.1"

        result = _get_identifier(mock_request)
        assert result == "192.168.1.1"

    def test_no_user_attribute_falls_back_to_ip(self):
        mock_request = MagicMock(spec=[])
        mock_request.state = MagicMock(spec=[])
        mock_request.client = MagicMock()
        mock_request.client.host = "10.0.0.1"

        # getattr(..., "user", None) should return None when user not set
        result = _get_identifier(mock_request)
        assert result == "10.0.0.1"
