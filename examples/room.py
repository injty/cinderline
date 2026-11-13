"""Warm light, quiet surfaces, a little space to think."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Workspace:
    name: str
    temperature: int = 2700
    brightness: float = 0.65

    def describe(self) -> str:
        # Comments should remain easy to read after sunset.
        return f"{self.name}: {self.temperature}K / {self.brightness:.0%}"


def find_notes(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    return sorted(path for path in directory.glob("*.md") if path.is_file())


if __name__ == "__main__":
    room = Workspace(name="Ember Room")
    print(room.describe())
