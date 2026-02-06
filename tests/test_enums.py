"""Tests for models/enums.py."""

from models.enums import BuildState, LogoState, NvencState


class TestEnums:
    """Test enum values match current magic numbers."""

    def test_build_state_values(self):
        """BuildState values match current config dict."""
        assert BuildState.SOFT_AND_HARD == 0
        assert BuildState.SOFT_ONLY == 1
        assert BuildState.HARD_ONLY == 2
        assert BuildState.FOR_HARDSUBBERS == 3
        assert BuildState.RAW_REPAIR == 4

    def test_nvenc_state_values(self):
        """NvencState values match current usage."""
        assert NvencState.NVENC_BOTH == 0
        assert NvencState.NVENC_SOFT_ONLY == 1
        assert NvencState.NVENC_HARD_ONLY == 2
        assert NvencState.NVENC_NONE == 3

    def test_logo_state_values(self):
        """LogoState values match current usage."""
        assert LogoState.LOGO_BOTH == 0
        assert LogoState.LOGO_SOFT_ONLY == 1
        assert LogoState.LOGO_HARD_ONLY == 2

    def test_enum_membership_checks(self):
        """Enums work with 'in' checks (backward compat)."""
        # Current code uses: if state in [0, 1]
        assert BuildState.SOFT_AND_HARD in [0, 1]
        assert BuildState.SOFT_ONLY in [0, 1]
        assert BuildState.HARD_ONLY not in [0, 1]

    def test_enum_comparison(self):
        """Enums compare correctly with ints."""
        assert BuildState.SOFT_AND_HARD == 0
        assert BuildState.SOFT_ONLY > BuildState.SOFT_AND_HARD
        assert BuildState.RAW_REPAIR > BuildState.FOR_HARDSUBBERS
