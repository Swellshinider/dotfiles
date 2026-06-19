from __future__ import annotations

import argparse
import fcntl
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib


SUPPORTED_FILES = (
    "alacritty/theme.toml",
    "gtk/gtk-3.0/settings.ini",
    "gtk/gtk-4.0/settings.ini",
    "hypr/animations.conf",
    "hypr/appearance.conf",
    "hypr/hyprlock.conf",
    "hypr/hyprpaper.conf",
    "kitty/theme.conf",
    "swaync/config.json",
    "swaync/style.css",
    "waybar/config.jsonc",
    "waybar/style.css",
    "wofi/style.css",
    "wlogout/layout",
    "wlogout/style.css",
)

SCAFFOLD_DIRS = (
    "alacritty",
    "gtk/gtk-3.0",
    "gtk/gtk-4.0",
    "hypr",
    "kitty",
    "swaync",
    "waybar",
    "wofi",
    "wlogout",
)

THEME_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROTECTED_THEME_IDS = {"default"}


def now_ts() -> float:
    return time.time()


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_quiet(command: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        env=env,
    )


def repo_root_from_module() -> Path:
    return Path(__file__).resolve().parents[1]


def launcher_path(repo_root: Path) -> Path:
    return repo_root / ".local" / "bin" / "themectl"


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as handle:
        handle.write(content)
        tmp_path = Path(handle.name)
    tmp_path.replace(path)


def atomic_write_json(path: Path, data: dict[str, Any]) -> None:
    atomic_write_text(path, json.dumps(data, indent=2, sort_keys=True) + "\n")


@dataclass
class Theme:
    theme_id: str
    path: Path
    manifest: dict[str, Any]

    @property
    def name(self) -> str:
        return str(self.manifest.get("name") or self.theme_id)

    @property
    def description(self) -> str:
        return str(self.manifest.get("description") or "").strip()


class ThemeManager:
    def __init__(self, repo_root: Path, env: dict[str, str] | None = None) -> None:
        self.repo_root = repo_root
        self.env = dict(env or os.environ)
        self.home = Path(self.env.get("HOME", str(Path.home()))).expanduser()
        self.state_home = Path(self.env.get("XDG_STATE_HOME", str(self.home / ".local" / "state"))).expanduser()
        self.themes_dir = self.repo_root / "themes"
        self.base_dir = self.themes_dir / "_base" / "files"
        self.template_dir = self.themes_dir / "_template"
        self.state_dir = self.state_home / "themectl"
        self.active_dir = self.state_dir / "active"
        self.state_file = self.state_dir / "state.json"
        self.preview_file = self.state_dir / "preview.json"
        self.lock_file = self.state_dir / "lock"
        self.launcher = launcher_path(repo_root)

    def ensure_state_dir(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file.touch(exist_ok=True)

    def lock(self) -> Any:
        self.ensure_state_dir()
        handle = self.lock_file.open("r+", encoding="utf-8")
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        return handle

    def read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def read_state(self) -> dict[str, Any]:
        return self.read_json(self.state_file)

    def write_state(self, state: dict[str, Any]) -> None:
        state = dict(state)
        state["updated_at"] = iso_now()
        atomic_write_json(self.state_file, state)

    def read_preview(self) -> dict[str, Any]:
        return self.read_json(self.preview_file)

    def write_preview(self, preview: dict[str, Any]) -> None:
        preview = dict(preview)
        preview["updated_at"] = iso_now()
        atomic_write_json(self.preview_file, preview)

    def current_theme_id(self) -> str:
        current = str(self.read_state().get("current_theme") or "default")
        return current

    def list_theme_ids(self) -> list[str]:
        if not self.themes_dir.exists():
            return []
        theme_ids: list[str] = []
        for child in sorted(self.themes_dir.iterdir()):
            if not child.is_dir() or child.name.startswith("_"):
                continue
            if (child / "theme.toml").exists():
                theme_ids.append(child.name)
        return theme_ids

    def load_theme(self, theme_id: str) -> Theme:
        theme_path = self.themes_dir / theme_id
        manifest_path = theme_path / "theme.toml"
        if not manifest_path.exists():
            raise ValueError(f"theme '{theme_id}' does not exist")
        manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_id = str(manifest.get("id") or theme_id)
        if manifest_id != theme_id:
            raise ValueError(f"theme '{theme_id}' has mismatched id '{manifest_id}'")
        return Theme(theme_id=theme_id, path=theme_path, manifest=manifest)

    def resolve_theme_path(self, theme: Theme, raw_path: str | None) -> str:
        if not raw_path:
            return ""
        if raw_path == "~":
            expanded = self.home
        elif raw_path.startswith("~/"):
            expanded = self.home / raw_path[2:]
        else:
            expanded = Path(os.path.expanduser(raw_path))
        if expanded.is_absolute():
            return str(expanded)
        return str((theme.path / raw_path).resolve())

    def theme_placeholders(self, theme: Theme) -> dict[str, str]:
        assets = theme.manifest.get("assets", {})
        if not isinstance(assets, dict):
            assets = {}
        preview = theme.manifest.get("preview", {})
        if not isinstance(preview, dict):
            preview = {}
        wallpaper = self.resolve_theme_path(theme, assets.get("wallpaper"))
        lockscreen = self.resolve_theme_path(theme, assets.get("lockscreen_wallpaper")) or wallpaper
        wallpaper_dir = self.resolve_theme_path(theme, assets.get("wallpaper_dir"))
        preview_image = self.resolve_theme_path(theme, preview.get("image")) or wallpaper
        return {
            "theme.id": theme.theme_id,
            "theme.name": theme.name,
            "theme.wallpaper": wallpaper,
            "theme.lockscreen_wallpaper": lockscreen,
            "theme.wallpaper_dir": wallpaper_dir,
            "theme.preview_image": preview_image,
            "home": str(self.home),
            "repo_root": str(self.repo_root),
            "state_dir": str(self.state_dir),
            "active_dir": str(self.active_dir),
        }

    def render_text(self, text: str, placeholders: dict[str, str]) -> str:
        rendered = text
        for key, value in placeholders.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", value)
        return rendered

    def source_file_for_theme(self, theme: Theme, relative_path: str) -> Path | None:
        theme_file = theme.path / "files" / relative_path
        if theme_file.exists():
            return theme_file
        base_file = self.base_dir / relative_path
        if base_file.exists():
            return base_file
        return None

    def build_active_tree(self, theme: Theme, target_dir: Path, preview_mode: bool) -> dict[str, Any]:
        placeholders = self.theme_placeholders(theme)
        for relative_path in SUPPORTED_FILES:
            source = self.source_file_for_theme(theme, relative_path)
            if source is None:
                continue
            destination = target_dir / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix in {".png", ".jpg", ".jpeg", ".webp", ".svg"}:
                shutil.copy2(source, destination)
                continue
            content = source.read_text(encoding="utf-8")
            destination.write_text(self.render_text(content, placeholders), encoding="utf-8")
        metadata = {
            "theme_id": theme.theme_id,
            "generated_at": iso_now(),
            "preview_mode": preview_mode,
        }
        atomic_write_json(target_dir / ".metadata.json", metadata)
        return metadata

    def replace_active_tree(self, staged_dir: Path) -> None:
        backup_dir = self.state_dir / "active.backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        if self.active_dir.exists():
            self.active_dir.replace(backup_dir)
        staged_dir.replace(self.active_dir)
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

    def apply_theme(self, theme_id: str, *, persist: bool, reload_apps: bool, preview_mode: bool = False) -> None:
        self.ensure_state_dir()
        theme = self.load_theme(theme_id)
        staged_dir = Path(tempfile.mkdtemp(prefix="active-", dir=self.state_dir))
        try:
            self.build_active_tree(theme, staged_dir, preview_mode)
            self.replace_active_tree(staged_dir)
        finally:
            if staged_dir.exists():
                shutil.rmtree(staged_dir, ignore_errors=True)
        if persist:
            state = self.read_state()
            state["current_theme"] = theme_id
            self.write_state(state)
        if reload_apps:
            self.reload_theme(theme)

    def preview_theme(self, theme_id: str, timeout_seconds: int) -> dict[str, Any]:
        current_theme = self.current_theme_id()
        if self.preview_file.exists():
            self.revert_preview(reload_apps=False)
        self.apply_theme(theme_id, persist=False, reload_apps=True, preview_mode=True)
        preview = {
            "token": str(uuid.uuid4()),
            "deadline": now_ts() + timeout_seconds,
            "previous_theme": current_theme,
            "preview_theme": theme_id,
            "timeout_seconds": timeout_seconds,
        }
        self.write_preview(preview)
        subprocess.Popen(
            [str(self.launcher), "_preview-watch", preview["token"]],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            env=self.env,
        )
        return preview

    def confirm_preview(self) -> str | None:
        preview = self.read_preview()
        if not preview:
            return None
        state = self.read_state()
        state["current_theme"] = preview["preview_theme"]
        self.write_state(state)
        self.preview_file.unlink(missing_ok=True)
        return str(preview["preview_theme"])

    def revert_preview(self, reload_apps: bool = True) -> str | None:
        preview = self.read_preview()
        if not preview:
            return None
        previous_theme = str(preview["previous_theme"])
        self.apply_theme(previous_theme, persist=False, reload_apps=reload_apps, preview_mode=False)
        self.preview_file.unlink(missing_ok=True)
        return previous_theme

    def watch_preview(self, token: str) -> int:
        while True:
            preview = self.read_preview()
            if not preview or preview.get("token") != token:
                return 0
            delay = float(preview["deadline"]) - now_ts()
            if delay <= 0:
                with self.lock():
                    latest = self.read_preview()
                    if latest and latest.get("token") == token and float(latest["deadline"]) <= now_ts():
                        self.revert_preview(reload_apps=True)
                return 0
            time.sleep(min(delay, 1.0))

    def ensure_initialized(self) -> None:
        self.ensure_state_dir()
        if not self.active_dir.exists():
            current = self.current_theme_id()
            self.apply_theme(current, persist=True, reload_apps=False, preview_mode=False)

    def wallpaper_candidates(self, theme: Theme) -> list[str]:
        placeholders = self.theme_placeholders(theme)
        candidates: list[str] = []
        wallpaper_dir = placeholders["theme.wallpaper_dir"]
        if wallpaper_dir:
            directory = Path(wallpaper_dir)
            if directory.is_dir():
                for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.PNG", "*.JPG", "*.JPEG", "*.WEBP"):
                    candidates.extend(str(path) for path in directory.rglob(pattern))
        if placeholders["theme.wallpaper"]:
            candidates.append(placeholders["theme.wallpaper"])
        return [candidate for candidate in candidates if Path(candidate).exists()]

    def next_wallpaper(self) -> str:
        theme = self.load_theme(self.current_theme_id())
        candidates = self.wallpaper_candidates(theme)
        if not candidates:
            raise ValueError(f"no wallpapers available for theme '{theme.theme_id}'")
        chosen = random.choice(candidates)
        if shutil.which("pgrep") and run_quiet(["pgrep", "-x", "hyprpaper"]).returncode != 0:
            self.launch("hyprpaper")
            time.sleep(1)
        subprocess.run(
            ["hyprctl", "hyprpaper", "wallpaper", f",{chosen}"],
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            env=self.env,
        )
        return chosen

    def launch(self, target: str) -> int:
        self.ensure_initialized()
        if target == "waybar":
            subprocess.Popen(
                ["waybar", "-c", str(self.active_dir / "waybar" / "config.jsonc"), "-s", str(self.active_dir / "waybar" / "style.css")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env=self.env,
            )
            return 0
        if target == "swaync":
            subprocess.Popen(
                ["swaync", "-c", str(self.active_dir / "swaync" / "config.json"), "-s", str(self.active_dir / "swaync" / "style.css")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env=self.env,
            )
            return 0
        if target == "hyprpaper":
            subprocess.Popen(
                ["hyprpaper", "--config", str(self.active_dir / "hypr" / "hyprpaper.conf")],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env=self.env,
            )
            return 0
        if target == "hyprlock":
            return subprocess.run(
                ["hyprlock", "--config", str(self.active_dir / "hypr" / "hyprlock.conf")],
                text=True,
                check=False,
                env=self.env,
            ).returncode
        if target == "wlogout":
            return subprocess.run(
                [
                    "wlogout",
                    "-b",
                    "4",
                    "--layout",
                    str(self.active_dir / "wlogout" / "layout"),
                    "--css",
                    str(self.active_dir / "wlogout" / "style.css"),
                ],
                text=True,
                check=False,
                env=self.env,
            ).returncode
        if target == "launcher":
            return subprocess.run(
                [
                    "wofi",
                    "--show",
                    "drun",
                    "--prompt",
                    "",
                    "--location",
                    "top_left",
                    "--xoffset",
                    "10",
                    "--yoffset",
                    "5",
                    "--width",
                    "800",
                    "--height",
                    "420",
                    "--style",
                    str(self.active_dir / "wofi" / "style.css"),
                ],
                text=True,
                check=False,
                env=self.env,
            ).returncode
        raise ValueError(f"unknown launch target '{target}'")

    def reload_theme(self, theme: Theme) -> None:
        if shutil.which("hyprctl"):
            run_quiet(["hyprctl", "reload", "config-only"], env=self.env)
        if shutil.which("pkill"):
            run_quiet(["pkill", "-SIGUSR2", "-x", "waybar"], env=self.env)
            if run_quiet(["pgrep", "-x", "hyprpaper"], env=self.env).returncode == 0:
                run_quiet(["pkill", "-x", "hyprpaper"], env=self.env)
                self.launch("hyprpaper")
        if shutil.which("swaync-client"):
            run_quiet(["swaync-client", "--reload-config"], env=self.env)
            run_quiet(["swaync-client", "--reload-css"], env=self.env)
        gtk = theme.manifest.get("gtk", {})
        if isinstance(gtk, dict) and shutil.which("gsettings"):
            if gtk.get("theme"):
                run_quiet(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", str(gtk["theme"])], env=self.env)
            if gtk.get("color_scheme"):
                run_quiet(
                    ["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", str(gtk["color_scheme"])],
                    env=self.env,
                )
            if gtk.get("icon_theme"):
                run_quiet(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", str(gtk["icon_theme"])], env=self.env)

    def theme_info(self, theme: Theme) -> dict[str, Any]:
        preview = theme.manifest.get("preview", {})
        if not isinstance(preview, dict):
            preview = {}
        assets = theme.manifest.get("assets", {})
        if not isinstance(assets, dict):
            assets = {}
        return {
            "id": theme.theme_id,
            "name": theme.name,
            "description": theme.description,
            "current": theme.theme_id == self.current_theme_id(),
            "preview_image": self.resolve_theme_path(theme, preview.get("image")),
            "wallpaper": self.resolve_theme_path(theme, assets.get("wallpaper")),
            "wallpaper_dir": self.resolve_theme_path(theme, assets.get("wallpaper_dir")),
        }

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.base_dir.exists():
            issues.append("themes/_base/files is missing")
        for relative_path in SUPPORTED_FILES:
            if not (self.base_dir / relative_path).exists():
                issues.append(f"themes/_base/files/{relative_path} is missing")
        seen_ids: set[str] = set()
        for theme_id in self.list_theme_ids():
            try:
                theme = self.load_theme(theme_id)
            except Exception as exc:  # pragma: no cover - defensive path
                issues.append(str(exc))
                continue
            if not THEME_ID_RE.match(theme.theme_id):
                issues.append(f"theme '{theme.theme_id}' must use lowercase kebab-case")
            if theme.theme_id in seen_ids:
                issues.append(f"duplicate theme id '{theme.theme_id}'")
            seen_ids.add(theme.theme_id)
            preview = theme.manifest.get("preview", {})
            if isinstance(preview, dict) and preview.get("image"):
                preview_path = Path(self.resolve_theme_path(theme, str(preview["image"])))
                if not preview_path.exists():
                    issues.append(f"theme '{theme.theme_id}' preview image is missing: {preview['image']}")
            files_root = theme.path / "files"
            if files_root.exists():
                for file_path in files_root.rglob("*"):
                    if file_path.is_dir():
                        continue
                    relative = file_path.relative_to(files_root).as_posix()
                    if relative.startswith("."):
                        continue
                    if relative not in SUPPORTED_FILES:
                        issues.append(f"theme '{theme.theme_id}' has unsupported file: files/{relative}")
        return issues

    def install(self) -> str:
        issues = self.validate()
        if issues:
            raise ValueError("\n".join(issues))
        self.ensure_initialized()
        current = self.current_theme_id()
        self.apply_theme(current, persist=True, reload_apps=False, preview_mode=False)
        return current

    def show_theme(self, theme_id: str) -> dict[str, Any]:
        return self.theme_info(self.load_theme(theme_id))

    def doctor(self) -> list[str]:
        current = self.current_theme_id()
        preview = self.read_preview()
        checks = [
            f"current theme: {current}",
            f"active tree: {'ok' if self.active_dir.exists() else 'missing'} ({self.active_dir})",
            f"preview: {'active' if preview else 'inactive'}",
        ]
        for binary in ("hyprctl", "hyprpaper", "hyprlock", "waybar", "swaync", "swaync-client", "wofi", "wlogout", "kitty", "alacritty"):
            checks.append(f"{binary}: {'found' if shutil.which(binary) else 'missing'}")
        return checks

    def new_theme(self, theme_id: str) -> Path:
        if not THEME_ID_RE.match(theme_id):
            raise ValueError("theme ids must use lowercase kebab-case")
        destination = self.themes_dir / theme_id
        if destination.exists():
            raise ValueError(f"theme '{theme_id}' already exists")
        shutil.copytree(self.template_dir, destination)
        (destination / "files" / ".gitkeep").unlink(missing_ok=True)
        for scaffold_dir in SCAFFOLD_DIRS:
            (destination / "files" / scaffold_dir).mkdir(parents=True, exist_ok=True)
        manifest_path = destination / "theme.toml"
        manifest = manifest_path.read_text(encoding="utf-8")
        manifest = manifest.replace("__THEME_ID__", theme_id)
        manifest = manifest.replace("__THEME_NAME__", theme_id.replace("-", " ").title())
        atomic_write_text(manifest_path, manifest)
        return destination

    def remove_theme(self, theme_id: str) -> None:
        if theme_id in PROTECTED_THEME_IDS:
            raise ValueError(f"theme '{theme_id}' is protected")
        if theme_id == self.current_theme_id():
            raise ValueError(f"theme '{theme_id}' is currently active")
        destination = self.themes_dir / theme_id
        if not destination.exists():
            raise ValueError(f"theme '{theme_id}' does not exist")
        shutil.rmtree(destination)

    def menu_label(self, theme_id: str) -> str:
        info = self.show_theme(theme_id)
        label = info["name"]
        if info["current"]:
            label += " [current]"
        if info["description"]:
            label += f" - {info['description']}"
        preview_image = info.get("preview_image")
        if preview_image:
            return f"img:{preview_image}:text:{label}"
        return label

    def run_wofi_menu(
        self,
        entries: list[str],
        *,
        prompt: str,
        pre_display_command: str | None = None,
        allow_images: bool = False,
    ) -> str | None:
        style_path = self.active_dir / "wofi" / "style.css"
        command = [
            "wofi",
            "--dmenu",
            "--cache-file",
            "/dev/null",
            "--prompt",
            prompt,
            "--width",
            "920",
            "--height",
            "540",
            "--insensitive",
        ]
        if style_path.exists():
            command.extend(["--style", str(style_path)])
        if pre_display_command:
            command.extend(["--pre-display-cmd", pre_display_command])
        if allow_images:
            command.extend(["--allow-images", "--parse-search"])
        process = subprocess.run(
            command,
            input="\n".join(entries) + "\n",
            text=True,
            capture_output=True,
            check=False,
            env=self.env,
        )
        if process.returncode != 0:
            return None
        selected = process.stdout.strip()
        return selected or None

    def menu_details(self, theme_id: str) -> None:
        info = self.show_theme(theme_id)
        lines = [
            f"Theme: {info['name']}",
            f"ID: {info['id']}",
            f"Description: {info['description'] or 'n/a'}",
            f"Preview: {info['preview_image'] or 'n/a'}",
            f"Wallpaper: {info['wallpaper'] or 'n/a'}",
            f"Wallpaper dir: {info['wallpaper_dir'] or 'n/a'}",
            "Close",
        ]
        self.run_wofi_menu(lines, prompt="Theme details")

    def menu_confirm_preview(self, timeout_seconds: int) -> None:
        selection = self.run_wofi_menu(["Keep preview", "Revert now"], prompt=f"Preview active ({timeout_seconds}s)")
        with self.lock():
            if selection == "Keep preview":
                self.confirm_preview()
            elif selection == "Revert now":
                self.revert_preview()

    def menu(self, timeout_seconds: int) -> int:
        self.ensure_initialized()
        theme_ids = self.list_theme_ids()
        pre_display = f"{self.launcher} menu-label %s"
        while True:
            theme_id = self.run_wofi_menu(theme_ids, prompt="Select theme", pre_display_command=pre_display, allow_images=True)
            if not theme_id:
                return 0
            action = self.run_wofi_menu(["Preview", "Apply", "Details"], prompt=f"Theme: {theme_id}")
            if action == "Preview":
                with self.lock():
                    self.preview_theme(theme_id, timeout_seconds)
                self.menu_confirm_preview(timeout_seconds)
                return 0
            if action == "Apply":
                with self.lock():
                    self.preview_file.unlink(missing_ok=True)
                    self.apply_theme(theme_id, persist=True, reload_apps=True, preview_mode=False)
                return 0
            if action == "Details":
                self.menu_details(theme_id)
                continue
            return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="themectl", description="Theme manager for the dotfiles repository.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("install")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--json", action="store_true")

    subparsers.add_parser("current")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("theme_id")
    show_parser.add_argument("--json", action="store_true")

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("theme_id")
    apply_parser.add_argument("--no-reload", action="store_true")

    preview_parser = subparsers.add_parser("preview")
    preview_parser.add_argument("theme_id")
    preview_parser.add_argument("--timeout", type=int, default=30)

    menu_parser = subparsers.add_parser("menu")
    menu_parser.add_argument("--timeout", type=int, default=30)

    subparsers.add_parser("validate")
    subparsers.add_parser("doctor")
    subparsers.add_parser("recover")

    new_parser = subparsers.add_parser("new")
    new_parser.add_argument("theme_id")

    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("theme_id")

    wallpaper_parser = subparsers.add_parser("wallpaper")
    wallpaper_subparsers = wallpaper_parser.add_subparsers(dest="wallpaper_command", required=True)
    wallpaper_subparsers.add_parser("next")

    launch_parser = subparsers.add_parser("launch")
    launch_parser.add_argument("target", choices=("launcher", "waybar", "swaync", "hyprpaper", "hyprlock", "wlogout"))

    label_parser = subparsers.add_parser("menu-label")
    label_parser.add_argument("theme_id")

    subparsers.add_parser("confirm-preview")
    subparsers.add_parser("revert-preview")

    watch_parser = subparsers.add_parser("_preview-watch")
    watch_parser.add_argument("token")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manager = ThemeManager(repo_root_from_module(), os.environ)

    try:
        if args.command == "install":
            current = manager.install()
            print(current)
            return 0
        if args.command == "list":
            themes = [manager.theme_info(manager.load_theme(theme_id)) for theme_id in manager.list_theme_ids()]
            if args.json:
                print(json.dumps(themes, indent=2))
            else:
                for theme in themes:
                    suffix = " [current]" if theme["current"] else ""
                    description = f" - {theme['description']}" if theme["description"] else ""
                    print(f"{theme['id']}{suffix}{description}")
            return 0
        if args.command == "current":
            print(manager.current_theme_id())
            return 0
        if args.command == "show":
            info = manager.show_theme(args.theme_id)
            if args.json:
                print(json.dumps(info, indent=2))
            else:
                for key, value in info.items():
                    print(f"{key}: {value}")
            return 0
        if args.command == "apply":
            with manager.lock():
                manager.preview_file.unlink(missing_ok=True)
                manager.apply_theme(args.theme_id, persist=True, reload_apps=not args.no_reload, preview_mode=False)
            print(args.theme_id)
            return 0
        if args.command == "preview":
            with manager.lock():
                preview = manager.preview_theme(args.theme_id, args.timeout)
            print(json.dumps(preview, indent=2))
            return 0
        if args.command == "menu":
            return manager.menu(args.timeout)
        if args.command == "validate":
            issues = manager.validate()
            if issues:
                for issue in issues:
                    print(issue, file=sys.stderr)
                return 1
            print("ok")
            return 0
        if args.command == "doctor":
            for line in manager.doctor():
                print(line)
            return 0
        if args.command == "recover":
            with manager.lock():
                reverted = manager.revert_preview(reload_apps=True)
                if reverted:
                    print(reverted)
                    return 0
                current = manager.current_theme_id()
                manager.apply_theme(current, persist=True, reload_apps=True, preview_mode=False)
                print(current)
                return 0
        if args.command == "new":
            destination = manager.new_theme(args.theme_id)
            print(destination)
            return 0
        if args.command == "remove":
            manager.remove_theme(args.theme_id)
            print(args.theme_id)
            return 0
        if args.command == "wallpaper":
            if args.wallpaper_command == "next":
                print(manager.next_wallpaper())
                return 0
        if args.command == "launch":
            return manager.launch(args.target)
        if args.command == "menu-label":
            print(manager.menu_label(args.theme_id))
            return 0
        if args.command == "confirm-preview":
            with manager.lock():
                confirmed = manager.confirm_preview()
            if confirmed:
                print(confirmed)
            return 0
        if args.command == "revert-preview":
            with manager.lock():
                reverted = manager.revert_preview(reload_apps=True)
            if reverted:
                print(reverted)
            return 0
        if args.command == "_preview-watch":
            return manager.watch_preview(args.token)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except tomllib.TOMLDecodeError as exc:
        print(f"invalid TOML: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
