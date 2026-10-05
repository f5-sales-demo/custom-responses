# ruff: noqa: PT009 -- standard-library unittest keeps tests runnable without extra packages
"""Check shared-host metadata against an independent untransformed control."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "verify_live_test", ROOT / "scripts/verify_live.py"
)
assert spec is not None
assert spec.loader is not None
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)
check_metadata = verify.check_metadata


class MetadataControlTests(unittest.TestCase):
    """Require an untransformed host when checking shared metadata."""

    def test_transformation_requires_distinct_untransformed_control(self):
        """Reject transformed fields on the independent control host."""
        positive = {
            "headers": (
                "Content-Type: text/html\n"
                "X-Showcase: custom-responses\n"
                "Set-Cookie: showcase=custom-responses; Path=/\n"
            )
        }
        control = {
            "headers": (
                "Content-Type: text/html\n"
                "X-Origin-Remove: synthetic\n"
                "Set-Cookie: origin-remove=synthetic; Path=/\n"
            )
        }
        self.assertEqual(check_metadata(positive, control), [])
        control["headers"] += "X-Showcase: custom-responses\n"
        self.assertIn(
            "untransformed host control failed", check_metadata(positive, control)
        )
        positive["headers"] += "X-Origin-Remove: synthetic\n"
        self.assertIn(
            "removed header/cookie retained", check_metadata(positive, control)
        )


if __name__ == "__main__":
    unittest.main()
