"""Render paths dataclass for type-safe path management."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class RenderPaths:
    """Immutable paths for a single render job."""
    # Input paths (from user)
    raw: Path
    audio: Optional[Path]
    sub: Optional[Path]

    # Output paths (computed)
    softsub: Path
    hardsub: Path

    @classmethod
    def from_ui_state(
        cls,
        raw_path: str,
        audio_path: str,
        sub_path: str,
        episode_name: str,
        softsub_dir: Path,
        hardsub_dir: Path
    ) -> 'RenderPaths':
        """Factory method: construct from MainWindow UI state.

        Args:
            raw_path: Path to raw video file
            audio_path: Path to audio file (empty string if not used)
            sub_path: Path to subtitle file (empty string if not used)
            episode_name: Episode name for output files
            softsub_dir: Directory for softsub output (Path or str)
            hardsub_dir: Directory for hardsub output (Path or str)

        Returns:
            RenderPaths instance with validated paths
        """
        # Ensure directory paths are Path objects (defensive)
        softsub_dir = Path(softsub_dir) if not isinstance(softsub_dir, Path) else softsub_dir
        hardsub_dir = Path(hardsub_dir) if not isinstance(hardsub_dir, Path) else hardsub_dir

        return cls(
            raw=Path(raw_path),
            audio=Path(audio_path) if audio_path else None,
            sub=Path(sub_path) if sub_path else None,
            softsub=softsub_dir / f"{episode_name}.mkv",
            hardsub=hardsub_dir / f"{episode_name}.mp4",
        )

    def validate(self) -> list[str]:
        """Validate that required input paths exist.

        Returns:
            List of error messages. Empty list means validation passed.
        """
        errors = []

        if not self.raw.exists():
            errors.append(f"Raw video not found: {self.raw}")

        if self.audio and not self.audio.exists():
            errors.append(f"Audio file not found: {self.audio}")

        if self.sub and not self.sub.exists():
            errors.append(f"Subtitle file not found: {self.sub}")

        return errors
