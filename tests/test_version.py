from __future__ import annotations

from pathlib import Path
import re
import unittest

from claude_chat_exporter import __version__


VERSION_INFO = Path(__file__).resolve().parents[1] / "assets" / "version_info.txt"


class VersionTests(unittest.TestCase):
    # The release workflow only compares the tag with ProductVersion, so the
    # other version fields must be kept equal to it here.
    def test_exe_version_info_matches_package_version(self) -> None:
        text = VERSION_INFO.read_text(encoding="utf-8")
        numbers = tuple(int(part) for part in __version__.split(".")) + (0,)
        for field in ("filevers", "prodvers"):
            with self.subTest(field=field):
                match = re.search(rf"{field}=\(([\d, ]+)\)", text)
                self.assertIsNotNone(match)
                self.assertEqual(tuple(int(part) for part in match.group(1).split(",")), numbers)
        for name in ("FileVersion", "ProductVersion"):
            with self.subTest(name=name):
                self.assertIn(f"StringStruct('{name}', '{__version__}')", text)


if __name__ == "__main__":
    unittest.main()
