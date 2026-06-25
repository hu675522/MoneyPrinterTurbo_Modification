import re
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def read_required_python(path: Path = ROOT_DIR / "pyproject.toml") -> str:
    match = re.search(
        r'^requires-python\s*=\s*"([^"]+)"',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise RuntimeError(f"requires-python not found in {path}")
    return match.group(1)


def parse_version_pair(version: str) -> tuple[int, int]:
    major, minor, *_rest = version.strip().split(".")
    return int(major), int(minor)


def is_version_supported(version: tuple[int, int], spec: str) -> bool:
    for clause in spec.split(","):
        clause = clause.strip()
        if clause.startswith(">="):
            if version < parse_version_pair(clause[2:]):
                return False
        elif clause.startswith("<"):
            if version >= parse_version_pair(clause[1:]):
                return False
        else:
            raise RuntimeError(f"unsupported Python version clause: {clause}")
    return True


def main() -> int:
    spec = read_required_python()
    version = sys.version_info[:2]
    version_text = f"{version[0]}.{version[1]}"
    if is_version_supported(version, spec):
        print(f"***** Python runtime: {version_text}, required: {spec} *****")
        return 0

    print(
        f"***** Unsupported Python runtime: {version_text}, required: {spec} *****",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
