from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from theme_manager.cli import SUPPORTED_FILES, ThemeManager


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class ThemeManagerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.tempdir.name) / "repo"
        self.home = Path(self.tempdir.name) / "home"
        self.repo_root.mkdir(parents=True)
        self.home.mkdir(parents=True)
        write_text(self.repo_root / ".local" / "bin" / "themectl", "#!/usr/bin/env python3\n")
        for relative_path in SUPPORTED_FILES:
            content = f"# {relative_path}\n"
            if relative_path == "hypr/hyprlock.conf":
                content = "path = {{theme.lockscreen_wallpaper}}\n"
            if relative_path == "hypr/hyprpaper.conf":
                content = "path = {{theme.wallpaper_dir}}\n"
            write_text(self.repo_root / "themes" / "_base" / "files" / relative_path, content)
        write_text(
            self.repo_root / "themes" / "default" / "theme.toml",
            "\n".join(
                [
                    'schema = 1',
                    'id = "default"',
                    'name = "Default"',
                    'description = "Fixture theme"',
                    "",
                    "[preview]",
                    'image = "assets/default.png"',
                    "",
                    "[assets]",
                    'wallpaper = "assets/default.png"',
                    'lockscreen_wallpaper = "assets/default.png"',
                    'wallpaper_dir = "~/Pictures/Wallpapers"',
                ]
            )
            + "\n",
        )
        write_text(self.repo_root / "themes" / "default" / "assets" / "default.png", "png")
        write_text(
            self.repo_root / "themes" / "_template" / "theme.toml",
            "\n".join(
                [
                    'schema = 1',
                    'id = "__THEME_ID__"',
                    'name = "__THEME_NAME__"',
                    'description = "Template"',
                ]
            )
            + "\n",
        )
        write_text(self.repo_root / "themes" / "_template" / "files" / ".gitkeep", "")
        self.manager = ThemeManager(
            self.repo_root,
            {
                "HOME": str(self.home),
                "XDG_STATE_HOME": str(self.home / ".local" / "state"),
            },
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_validate_passes_for_fixture(self) -> None:
        self.assertEqual(self.manager.validate(), [])

    def test_apply_theme_renders_placeholders(self) -> None:
        self.manager.apply_theme("default", persist=True, reload_apps=False)
        hyprlock = (self.manager.active_dir / "hypr" / "hyprlock.conf").read_text(encoding="utf-8")
        hyprpaper = (self.manager.active_dir / "hypr" / "hyprpaper.conf").read_text(encoding="utf-8")
        self.assertIn(str(self.repo_root / "themes" / "default" / "assets" / "default.png"), hyprlock)
        self.assertIn(str(self.home / "Pictures" / "Wallpapers"), hyprpaper)
        self.assertEqual(self.manager.current_theme_id(), "default")

    def test_new_theme_creates_scaffold(self) -> None:
        destination = self.manager.new_theme("forest-night")
        self.assertTrue((destination / "theme.toml").exists())
        self.assertTrue((destination / "files" / "hypr").is_dir())
        manifest = (destination / "theme.toml").read_text(encoding="utf-8")
        self.assertIn('id = "forest-night"', manifest)
        self.assertIn('name = "Forest Night"', manifest)

    def test_menu_label_uses_preview_image(self) -> None:
        label = self.manager.menu_label("default")
        self.assertIn("img:", label)
        self.assertIn("Fixture theme", label)


if __name__ == "__main__":
    unittest.main()
