import re
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts import check_python_runtime


def read_required_python(path: Path) -> str:
    match = re.search(
        r'^requires-python\s*=\s*"([^"]+)"',
        path.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise AssertionError(f"requires-python not found in {path}")
    return match.group(1)


def normalize_spec(spec: str) -> str:
    return spec.replace(" ", "")


def parse_version_pair(version: str) -> tuple[int, int]:
    return check_python_runtime.parse_version_pair(version)


def lower_bound_from_spec(spec: str) -> str:
    match = re.search(r">=\s*(\d+\.\d+)", spec)
    if not match:
        raise AssertionError(f"lower Python bound not found in {spec}")
    return match.group(1)


def is_version_supported(version: tuple[int, int], spec: str) -> bool:
    return check_python_runtime.is_version_supported(version, spec)


class TestPythonRuntimeVersion(unittest.TestCase):
    def test_python_version_declarations_are_aligned(self):
        pyproject_spec = read_required_python(ROOT_DIR / "pyproject.toml")
        lock_spec = read_required_python(ROOT_DIR / "uv.lock")
        pinned_version = (ROOT_DIR / ".python-version").read_text(encoding="utf-8").strip()

        self.assertEqual(normalize_spec(lock_spec), normalize_spec(pyproject_spec))
        self.assertEqual(pinned_version, lower_bound_from_spec(pyproject_spec))
        self.assertTrue(
            is_version_supported(parse_version_pair(pinned_version), pyproject_spec)
        )

    def test_current_python_satisfies_project_declaration(self):
        pyproject_spec = read_required_python(ROOT_DIR / "pyproject.toml")
        current_version = sys.version_info[:2]

        self.assertTrue(is_version_supported(current_version, pyproject_spec))

    def test_runtime_check_script_accepts_current_python(self):
        self.assertEqual(check_python_runtime.main(), 0)


if __name__ == "__main__":
    unittest.main()
