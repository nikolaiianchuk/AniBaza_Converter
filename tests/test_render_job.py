"""Tests for models/job.py."""

from pathlib import Path

from models.encoding import EncodingParams
from models.enums import BuildState, LogoState, NvencState
from models.job import RenderJob, VideoPresets, VideoSettings
from models.render_paths import RenderPaths


class TestVideoSettings:
    """Test VideoSettings dataclass."""

    def test_video_settings_default(self):
        """Default VideoSettings has expected values."""
        settings = VideoSettings()

        assert settings.video_tune == "animation"
        assert settings.video_profile == "high10"
        assert settings.profile_level == "4.1"
        assert settings.pixel_format == "yuv420p10le"

    def test_video_settings_immutable(self):
        """VideoSettings is frozen (immutable)."""
        settings = VideoSettings()

        try:
            settings.video_profile = "main"
            assert False, "Should not allow mutation"
        except Exception:
            pass  # Expected


class TestVideoPresets:
    """Test VideoPresets constants."""

    def test_softsub_preset(self):
        """SOFTSUB preset has high10 profile."""
        assert VideoPresets.SOFTSUB.video_profile == "high10"
        assert VideoPresets.SOFTSUB.pixel_format == "yuv420p10le"
        assert VideoPresets.SOFTSUB.video_tune == "animation"

    def test_hardsub_preset(self):
        """HARDSUB preset has main10 profile."""
        assert VideoPresets.HARDSUB.video_profile == "main10"
        assert VideoPresets.HARDSUB.pixel_format == "yuv420p10le"
        assert VideoPresets.HARDSUB.video_tune == "animation"

    def test_potato_preset(self):
        """POTATO preset forces yuv420p and main profile."""
        assert VideoPresets.POTATO.video_profile == "main"
        assert VideoPresets.POTATO.pixel_format == "yuv420p"
        assert VideoPresets.POTATO.video_tune == ""  # No tune


class TestRenderJob:
    """Test RenderJob dataclass."""

    def test_render_job_construction(self):
        """RenderJob can be constructed with RenderPaths."""
        params = EncodingParams(
            avg_bitrate="6M",
            max_bitrate="9M",
            buffer_size="18M",
            crf=18,
            cq=19,
            qmin=17,
            qmax=23,
        )

        paths = RenderPaths(
            raw=Path("/input/raw.mkv"),
            audio=Path("/input/audio.wav"),
            sub=Path("/input/sub.ass"),
            softsub=Path("/output/soft.mkv"),
            hardsub=Path("/output/hard.mp4"),
        )

        job = RenderJob(
            paths=paths,
            episode_name="Episode_01",
            build_state=BuildState.SOFT_AND_HARD,
            nvenc_state=NvencState.NVENC_BOTH,
            logo_state=LogoState.LOGO_BOTH,
            encoding_params=params,
            video_settings=VideoPresets.SOFTSUB,
            potato_mode=False,
        )

        assert job.paths.raw == Path("/input/raw.mkv")
        assert job.episode_name == "Episode_01"
        assert job.build_state == BuildState.SOFT_AND_HARD
        assert job.encoding_params.crf == 18

    def test_render_job_optional_fields(self):
        """RenderJob allows None for optional paths."""
        params = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        paths = RenderPaths(
            raw=Path("/input/raw.mkv"),
            audio=None,  # No audio
            sub=None,  # No subtitles
            softsub=Path("/output/soft.mkv"),
            hardsub=Path("/output/hard.mp4"),
        )

        job = RenderJob(
            paths=paths,
            episode_name="Episode_01",
            build_state=BuildState.HARD_ONLY,
            nvenc_state=NvencState.NVENC_HARD_ONLY,
            logo_state=LogoState.LOGO_HARD_ONLY,
            encoding_params=params,
            video_settings=VideoPresets.HARDSUB,
        )

        assert job.paths.audio is None
        assert job.paths.sub is None
        assert job.paths.hardsub == Path("/output/hard.mp4")

    def test_render_job_runtime_state(self):
        """RenderJob has mutable runtime state fields."""
        params = EncodingParams("6M", "9M", "18M", 18, 19, 17, 23)

        paths = RenderPaths(
            raw=Path("/input/raw.mkv"),
            audio=None,
            sub=None,
            softsub=Path("/output/soft.mkv"),
            hardsub=Path("/output/hard.mp4"),
        )

        job = RenderJob(
            paths=paths,
            episode_name="Episode_01",
            build_state=BuildState.HARD_ONLY,
            nvenc_state=NvencState.NVENC_HARD_ONLY,
            logo_state=LogoState.LOGO_HARD_ONLY,
            encoding_params=params,
            video_settings=VideoPresets.HARDSUB,
        )

        # Runtime state can be modified
        job.total_duration_sec = 1442.05
        job.total_frames = 34560.0
        job.video_res = "1080p"

        assert job.total_duration_sec == 1442.05
        assert job.total_frames == 34560.0
        assert job.video_res == "1080p"
