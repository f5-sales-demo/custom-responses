# ruff: noqa: PT009 -- standard-library unittest keeps tests runnable without extra packages
"""Check shared-host metadata against an independent untransformed control."""

import unittest

from scripts.verify_live import check_metadata


class MetadataControlTests(unittest.TestCase):
    def test_transformation_requires_distinct_untransformed_control(self):
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
