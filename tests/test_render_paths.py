"""Tests for models/render_paths.py."""

from pathlib import Path

import pytest

from models.render_paths import RenderPaths


class TestRenderPaths:
    """Test RenderPaths dataclass."""

    def test_render_paths_construction(self):
        """RenderPaths constructs with all required fields."""
        paths = RenderPaths(
            raw=Path("/path/to/raw.mkv"),
            audio=Path("/path/to/audio.mka"),
            sub=Path("/path/to/sub.ass"),
            softsub=Path("/output/ep01.mkv"),
            hardsub=Path("/output/ep01.mp4"),
        )

        assert paths.raw == Path("/path/to/raw.mkv")
        assert paths.audio == Path("/path/to/audio.mka")
        assert paths.sub == Path("/path/to/sub.ass")
        assert paths.softsub == Path("/output/ep01.mkv")
        assert paths.hardsub == Path("/output/ep01.mp4")

    def test_render_paths_from_ui_state(self, tmp_path):
        """Factory method creates RenderPaths from UI inputs."""
        softsub_dir = tmp_path / "soft"
        hardsub_dir = tmp_path / "hard"
        softsub_dir.mkdir()
        hardsub_dir.mkdir()

        paths = RenderPaths.from_ui_state(
            raw_path="/raw.mkv",
            audio_path="/audio.mka",
            sub_path="/sub.ass",
            episode_name="Episode 01",
            softsub_dir=softsub_dir,
            hardsub_dir=hardsub_dir,
        )

        assert paths.raw == Path("/raw.mkv")
        assert paths.audio == Path("/audio.mka")
        assert paths.sub == Path("/sub.ass")
        assert paths.softsub == softsub_dir / "Episode 01.mkv"
        assert paths.hardsub == hardsub_dir / "Episode 01.mp4"

    def test_render_paths_from_ui_state_empty_audio(self, tmp_path):
        """Factory method handles empty audio path."""
        softsub_dir = tmp_path / "soft"
        hardsub_dir = tmp_path / "hard"
        softsub_dir.mkdir()
        hardsub_dir.mkdir()

        paths = RenderPaths.from_ui_state(
            raw_path="/raw.mkv",
            audio_path="",  # Empty string
            sub_path="/sub.ass",
            episode_name="Episode 01",
            softsub_dir=softsub_dir,
            hardsub_dir=hardsub_dir,
        )

        assert paths.audio is None

    def test_render_paths_from_ui_state_empty_sub(self, tmp_path):
        """Factory method handles empty subtitle path."""
        softsub_dir = tmp_path / "soft"
        hardsub_dir = tmp_path / "hard"
        softsub_dir.mkdir()
        hardsub_dir.mkdir()

        paths = RenderPaths.from_ui_state(
            raw_path="/raw.mkv",
            audio_path="/audio.mka",
            sub_path="",  # Empty string
            episode_name="Episode 01",
            softsub_dir=softsub_dir,
            hardsub_dir=hardsub_dir,
        )

        assert paths.sub is None

    def test_render_paths_optional_audio_sub(self):
        """Audio and sub paths can be None."""
        paths = RenderPaths(
            raw=Path("/raw.mkv"),
            audio=None,
            sub=None,
            softsub=Path("/soft.mkv"),
            hardsub=Path("/hard.mp4"),
        )

        assert paths.audio is None
        assert paths.sub is None

    def test_render_paths_validation_missing_raw(self, tmp_path):
        """Validation detects missing raw file."""
        paths = RenderPaths(
            raw=tmp_path / "missing.mkv",
            audio=None,
            sub=None,
            softsub=tmp_path / "soft.mkv",
            hardsub=tmp_path / "hard.mp4",
        )

        errors = paths.validate()

        assert len(errors) == 1
        assert "Raw video not found" in errors[0]
        assert "missing.mkv" in errors[0]

    def test_render_paths_validation_missing_audio(self, tmp_path):
        """Validation detects missing audio file when specified."""
        raw = tmp_path / "raw.mkv"
        raw.touch()

        paths = RenderPaths(
            raw=raw,
            audio=tmp_path / "missing_audio.mka",
            sub=None,
            softsub=tmp_path / "soft.mkv",
            hardsub=tmp_path / "hard.mp4",
        )

        errors = paths.validate()

        assert len(errors) == 1
        assert "Audio file not found" in errors[0]
        assert "missing_audio.mka" in errors[0]

    def test_render_paths_validation_missing_sub(self, tmp_path):
        """Validation detects missing subtitle file when specified."""
        raw = tmp_path / "raw.mkv"
        raw.touch()

        paths = RenderPaths(
            raw=raw,
            audio=None,
            sub=tmp_path / "missing_sub.ass",
            softsub=tmp_path / "soft.mkv",
            hardsub=tmp_path / "hard.mp4",
        )

        errors = paths.validate()

        assert len(errors) == 1
        assert "Subtitle file not found" in errors[0]
        assert "missing_sub.ass" in errors[0]

    def test_render_paths_validation_all_exist(self, tmp_path):
        """Validation passes when all required files exist."""
        raw = tmp_path / "raw.mkv"
        audio = tmp_path / "audio.mka"
        sub = tmp_path / "sub.ass"
        raw.touch()
        audio.touch()
        sub.touch()

        paths = RenderPaths(
            raw=raw,
            audio=audio,
            sub=sub,
            softsub=tmp_path / "soft.mkv",
            hardsub=tmp_path / "hard.mp4",
        )

        errors = paths.validate()

        assert len(errors) == 0

    def test_render_paths_validation_optional_not_checked(self, tmp_path):
        """Validation skips None optional paths."""
        raw = tmp_path / "raw.mkv"
        raw.touch()

        paths = RenderPaths(
            raw=raw,
            audio=None,  # Not checked
            sub=None,  # Not checked
            softsub=tmp_path / "soft.mkv",
            hardsub=tmp_path / "hard.mp4",
        )

        errors = paths.validate()

        assert len(errors) == 0

    def test_render_paths_validation_multiple_errors(self, tmp_path):
        """Validation returns all errors at once."""
        paths = RenderPaths(
            raw=tmp_path / "missing_raw.mkv",
            audio=tmp_path / "missing_audio.mka",
            sub=tmp_path / "missing_sub.ass",
            softsub=tmp_path / "soft.mkv",
            hardsub=tmp_path / "hard.mp4",
        )

        errors = paths.validate()

        assert len(errors) == 3
        assert any("Raw video not found" in e for e in errors)
        assert any("Audio file not found" in e for e in errors)
        assert any("Subtitle file not found" in e for e in errors)

    def test_render_paths_immutable(self, tmp_path):
        """RenderPaths is immutable (frozen dataclass)."""
        paths = RenderPaths(
            raw=tmp_path / "raw.mkv",
            audio=None,
            sub=None,
            softsub=tmp_path / "soft.mkv",
            hardsub=tmp_path / "hard.mp4",
        )

        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            paths.raw = tmp_path / "different.mkv"
