"""TypeSlate Terminal - Main application built with Textual."""

import os
from datetime import datetime
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    Input,
    Label,
    Rule,
    Select,
    Static,
    TextArea,
    Tree,
)
from textual.widgets.tree import TreeNode

from typeslate_terminal import database

TITLE_ART = "Ｔｙｐｅｓｌａｔｅ－  Ｔｅｒｍｉｎａｌ"

# ---------------------------------------------------------------------------
# Theme definitions  (bg, fg, accent)
# ---------------------------------------------------------------------------
THEMES = {
    "Classic Dark": ("#1e1e1e", "#d4d4d4", "#569cd6"),
    "Warm Dark": ("#1a1410", "#e8dcc6", "#c8a86e"),
    "DOS Green": ("#0a0a0a", "#00ff00", "#00cc00"),
    "Amber Terminal": ("#0a0800", "#ffb000", "#cc8c00"),
    "DOS Blue": ("#000030", "#c0c0c0", "#6080c0"),
    "Classic Light": ("#f5f5f5", "#1e1e1e", "#0060c0"),
    "Warm Light": ("#f8f4e3", "#1e1e1e", "#8b6914"),
    "Warm DOS": ("#1a0d00", "#ffcc66", "#cc9933"),
}


# ---------------------------------------------------------------------------
# Home Screen - IDE-like layout with file tree, setup, and stats
# ---------------------------------------------------------------------------
class HomeScreen(Screen):
    BINDINGS = [
        Binding("ctrl+b", "toggle_sidebar", "Toggle Sidebar", show=True),
        Binding("ctrl+r", "focus_sidebar", "Focus Files", show=True),
        Binding("ctrl+e", "focus_center", "Focus Setup", show=True),
        Binding("ctrl+t", "focus_stats", "Focus Stats", show=True),
        Binding("ctrl+o", "change_folder", "Change Folder", show=True),
    ]

    DEFAULT_CSS = """
    HomeScreen {
        layout: vertical;
    }

    /* ── Main 3-panel layout ── */
    #home-layout {
        layout: horizontal;
        height: 1fr;
    }

    /* ── Left panel: File Explorer ── */
    #file-panel {
        width: 30;
        border: solid #3a3a3a;
        background: #1a1a1a;
        padding: 0;
    }
    #file-panel:focus-within {
        border: solid #4ec965;
    }
    #file-panel-title {
        text-align: center;
        text-style: bold;
        color: #4ec965;
        background: #1a1a1a;
        width: 100%;
        padding: 0 1;
    }
    #sidebar-mode-bar {
        height: 1;
        background: #252525;
        layout: horizontal;
        padding: 0;
    }
    #sidebar-mode-bar Button {
        min-width: 12;
        height: 1;
        margin: 0;
        padding: 0 1;
        border: none;
        color: #808080;
        background: #252525;
    }
    #sidebar-mode-bar Button:hover {
        background: #333333;
    }
    #sidebar-mode-bar .sidebar-mode-active {
        color: #4ec965;
        text-style: bold;
    }
    /* folder-path-label removed — replaced by nav-bar breadcrumb */
    #file-tree {
        background: #1a1a1a;
        padding: 0;
        scrollbar-size: 1 1;
    }
    #file-tree:focus {
        background: #1a1a1a;
    }
    #file-tree > .tree--cursor {
        background: #2d5a2d;
        color: #ffffff;
    }
    #file-tree > .tree--highlight {
        background: #333333;
    }
    #nav-bar {
        height: 1;
        background: #252525;
        padding: 0 1;
        layout: horizontal;
    }
    #nav-bar Button {
        min-width: 4;
        height: 1;
        margin: 0;
        padding: 0 1;
        background: #252525;
        border: none;
        color: #a0a0a0;
    }
    #nav-bar Button:hover {
        background: #333333;
    }
    #nav-bar #breadcrumb {
        color: #808080;
        margin-left: 1;
        width: 1fr;
    }

    /* ── Center panel: Setup / Controls ── */
    #center-panel {
        width: 1fr;
        border: solid #3a3a3a;
        background: #1e1e1e;
        padding: 2 1 0 1;
        align: center top;
    }
    #center-panel:focus-within {
        border: solid #d4a843;
    }
    #center-content {
        width: 100%;
        height: auto;
        max-height: 100%;
    }

    /* Header area */
    #app-title {
        text-align: center;
        text-style: bold;
        color: #d4a843;
        width: 100%;
        content-align: center middle;
        height: auto;
        padding: 1 0 0 0;
    }

    /* Mode + Theme side by side */
    #setup-row {
        height: auto;
        layout: horizontal;
        margin: 1 1;
    }
    #mode-section {
        width: 1fr;
        padding: 0 1;
        height: auto;
    }
    #mode-section-title {
        text-style: bold;
        color: #c0c0c0;
    }
    #goal-input {
        display: none;
        margin-top: 0;
    }
    .goal-visible {
        display: block !important;
    }
    #theme-section {
        width: 1fr;
        padding: 0 1;
        height: auto;
    }
    #theme-section-title {
        text-style: bold;
        color: #c0c0c0;
    }

    #active-folder-label {
        color: #808080;
        text-style: italic;
        text-align: center;
        margin: 1 1;
    }
    #options-grid {
        height: auto;
        margin: 1 1;
        layout: grid;
        grid-size: 2 2;
        grid-gutter: 1;
    }
    #options-grid Checkbox {
        width: 100%;
        height: auto;
        margin: 0;
    }
    #preload-status {
        color: #4ec965;
        text-style: italic;
        text-align: center;
        margin: 0;
    }

    /* Start button */
    #start-btn {
        dock: bottom;
        margin: 1 1;
        width: 100%;
    }

    /* ── Right panel: Statistics ── */
    #stats-panel {
        width: 36;
        border: solid #3a3a3a;
        background: #1a1a1a;
        padding: 0;
    }
    #stats-panel:focus-within {
        border: solid #569cd6;
    }
    #stats-panel-title {
        text-align: center;
        text-style: bold;
        color: #569cd6;
        background: #1a1a1a;
        width: 100%;
        padding: 0 1;
    }
    #stats-scroll {
        padding: 0 1;
        scrollbar-size: 1 1;
    }
    #stats-settings-btn {
        dock: bottom;
        width: 100%;
        min-width: 10;
        margin: 0 1 1 1;
        max-height: 3;
        background: #333333;
        color: #999999;
        border: none;
        text-style: none;
    }
    #stats-settings-btn:hover {
        background: #444444;
        color: #d4d4d4;
    }
    #stats-settings-panel {
        display: none;
        height: auto;
        padding: 0 1;
        background: #1a1a1a;
    }
    #stats-settings-panel .settings-heading {
        text-style: bold;
        color: #569cd6;
        margin-bottom: 1;
    }
    .settings-btn {
        width: 100%;
        min-height: 1;
        height: auto;
        max-height: 3;
        margin: 0 0 0 0;
        padding: 0 1;
        border: none;
        text-style: none;
        background: #333333;
        color: #d4d4d4;
    }
    .settings-btn:hover {
        background: #444444;
    }
    #reset-stats-btn {
        color: #cc4444;
    }

    /* Stats sections */
    .stats-section-header {
        text-style: bold;
        color: #569cd6;
        margin-top: 1;
    }
    .stats-row {
        color: #a0a0a0;
    }
    .stats-value {
        color: #d4d4d4;
        text-style: bold;
    }
    .stats-divider {
        color: #333333;
        margin: 0;
    }

    /* Recent sessions */
    .session-entry {
        color: #808080;
    }
    """

    def __init__(self):
        super().__init__()
        self._sidebar_visible = True
        self._sidebar_mode = "folders"  # "folders" or "templates"
        self._initial_content: str = ""
        self._initial_word_count: int = 0

    def compose(self) -> ComposeResult:

        with Horizontal(id="home-layout"):
            # ── Left: File Explorer / Templates ──
            with Vertical(id="file-panel"):
                yield Label("File Explorer", id="file-panel-title")
                with Horizontal(id="sidebar-mode-bar"):
                    yield Button("Folders", id="sidebar-folders-btn", classes="sidebar-mode-active")
                    yield Button("Templates", id="sidebar-templates-btn")
                with Horizontal(id="nav-bar"):
                    yield Button("<", id="nav-up")
                    yield Label("", id="breadcrumb")
                yield Tree("Root", id="file-tree")

            # ── Center: Setup ──
            with Vertical(id="center-panel"):
                with Vertical(id="center-content"):
                    yield Static(TITLE_ART, id="app-title")

                    with Horizontal(id="setup-row"):
                        # Mode (left)
                        with Vertical(id="mode-section"):
                            yield Label("Mode", id="mode-section-title")
                            mode_options = [
                                ("Free Write", "free"),
                                ("Timer Mode", "timer"),
                                ("Word Count Mode", "wordcount"),
                            ]
                            yield Select(mode_options, value="free", id="mode-select")
                            with Horizontal(id="goal-input"):
                                yield Label("Goal: ")
                                yield Input(placeholder="minutes or words", id="goal-value", type="integer")

                        # Theme (right)
                        with Vertical(id="theme-section"):
                            yield Label("Theme", id="theme-section-title")
                            current_theme = database.get_last_theme()
                            theme_options = [(name, name) for name in THEMES]
                            yield Select(theme_options, value=current_theme, id="theme-select")

                    yield Label("", id="active-folder-label")
                    with Container(id="options-grid"):
                        yield Checkbox("Show Word Count", value=False, id="show-wc-checkbox")
                        yield Checkbox("Paste from Clipboard", value=False, id="clipboard-checkbox")
                        yield Checkbox("Resume Last Session", value=False, id="resume-checkbox")
                        yield Checkbox("Start from Template", value=False, id="template-checkbox")
                    yield Label("", id="preload-status")
                yield Button("Start Writing", variant="primary", id="start-btn")

            # ── Right: Statistics ──
            with Vertical(id="stats-panel"):
                yield Label("Statistics", id="stats-panel-title")
                yield VerticalScroll(id="stats-scroll")
                with Vertical(id="stats-settings-panel"):
                    yield Label("Settings", classes="settings-heading")
                    yield Button("Export to CSV", id="export-excel-btn", classes="settings-btn")
                    yield Button("Export Database", id="export-db-btn", classes="settings-btn")
                    yield Button("Import Database", id="import-db-btn", classes="settings-btn")
                    yield Button("Reset Stats", id="reset-stats-btn", classes="settings-btn", variant="error")
                    yield Button("Back", id="settings-back-btn", classes="settings-btn")
                yield Button("Settings", id="stats-settings-btn")

    def on_mount(self):
        self._folders_path = database.get_save_folder()
        self._templates_path = database.get_templates_folder()
        self._current_folder = self._folders_path
        self._navigate_to(self._current_folder)
        self._populate_stats()

    def _navigate_to(self, folder: str):
        """Navigate the file explorer to show the contents of a folder."""
        if not os.path.isdir(folder):
            self.notify("Folder not found", severity="error")
            return

        self._current_folder = folder
        if self._sidebar_mode == "folders":
            self._folders_path = folder
            database.set_save_folder(folder)
        else:
            self._templates_path = folder
            database.set_templates_folder(folder)

        tree = self.query_one("#file-tree", Tree)
        tree.clear()

        folder_name = os.path.basename(folder) or folder
        tree.root.set_label(folder_name)
        tree.root.data = folder

        # Update breadcrumb
        self.query_one("#breadcrumb", Label).update(self._shorten_path(folder))

        # List contents — folders first, then files (flat, one level)
        try:
            entries = sorted(os.listdir(folder), key=lambda e: e.lower())
        except PermissionError:
            tree.root.add_leaf("(permission denied)")
            tree.root.expand()
            return

        folders = []
        files = []
        for entry in entries:
            full = os.path.join(folder, entry)
            if entry.startswith("."):
                continue
            if os.path.isdir(full):
                folders.append((entry, full))
            elif os.path.isfile(full):
                files.append((entry, full))

        for name, full in folders:
            tree.root.add_leaf(f"  {name}/", data={"type": "folder", "path": full})

        # In templates mode, also show files so they can be selected
        if self._sidebar_mode == "templates":
            for name, full in files:
                tree.root.add_leaf(f"  {name}", data={"type": "file", "path": full})
            if not folders and not files:
                tree.root.add_leaf("(empty)")
        else:
            if not folders:
                tree.root.add_leaf("(no subfolders)")

        tree.root.expand()

        # Update active folder label in center panel
        try:
            self.query_one("#active-folder-label", Label).update(
                f"Folder: {self._shorten_path(folder)}"
            )
        except Exception:
            pass

    def _shorten_path(self, path: str) -> str:
        home = os.path.expanduser("~")
        if path.startswith(home):
            return "~" + path[len(home):]
        return path

    def _populate_stats(self):
        stats_scroll = self.query_one("#stats-scroll", VerticalScroll)

        stats = database.get_period_stats()
        all_stats = database.load_stats()

        widgets = []

        # Daily
        widgets.append(Label("Daily", classes="stats-section-header"))
        widgets.append(Label(f"  Today        {stats['today']:>8,} words", classes="stats-row"))
        widgets.append(Label(f"  Yesterday    {stats['yesterday']:>8,} words", classes="stats-row"))
        widgets.append(Rule(line_style="heavy", classes="stats-divider"))

        # Weekly/Monthly
        widgets.append(Label("This Period", classes="stats-section-header"))
        widgets.append(Label(f"  Last 7 days  {stats['week']:>8,} words", classes="stats-row"))
        widgets.append(Label(f"  Last 30 days {stats['month']:>8,} words", classes="stats-row"))
        widgets.append(Rule(line_style="heavy", classes="stats-divider"))

        # Lifetime
        widgets.append(Label("Lifetime", classes="stats-section-header"))
        widgets.append(Label(f"  Total words  {stats['total']:>8,}", classes="stats-value"))
        widgets.append(Label(f"  Sessions     {stats['session_count']:>8,}", classes="stats-row"))
        widgets.append(Label(f"  Best session {stats['largest_session']:>8,} words", classes="stats-row"))

        if stats["session_count"] > 0:
            avg = stats["total"] // stats["session_count"]
            widgets.append(Label(f"  Average      {avg:>8,} words", classes="stats-row"))

        widgets.append(Rule(line_style="heavy", classes="stats-divider"))

        # Recent sessions
        widgets.append(Label("Recent Sessions", classes="stats-section-header"))
        for s in all_stats["sessions"][:8]:
            try:
                dt = datetime.fromisoformat(s["timestamp"]).strftime("%b %d %H:%M")
            except (ValueError, TypeError):
                dt = s["timestamp"][:16] if s["timestamp"] else "?"
            dur_min = s["duration"] / 60
            widgets.append(
                Label(
                    f"  {dt}  {s['word_count']:>5,}w  {dur_min:>3.0f}m",
                    classes="session-entry",
                )
            )

        stats_scroll.mount(*widgets)

    def _refresh_stats(self):
        stats_scroll = self.query_one("#stats-scroll", VerticalScroll)
        stats_scroll.remove_children()
        self._populate_stats()

    # ── Mode selection logic ──

    @on(Select.Changed, "#mode-select")
    def mode_changed(self, event: Select.Changed):
        goal_input = self.query_one("#goal-input")
        inp = self.query_one("#goal-value", Input)
        if event.value == "timer":
            goal_input.add_class("goal-visible")
            inp.placeholder = "minutes"
            inp.value = ""
        elif event.value == "wordcount":
            goal_input.add_class("goal-visible")
            inp.placeholder = "word count"
            inp.value = ""
        else:
            goal_input.remove_class("goal-visible")

    # ── File tree interaction ──

    @on(Tree.NodeSelected, "#file-tree")
    def on_file_selected(self, event: Tree.NodeSelected):
        data = event.node.data
        if not data or not isinstance(data, dict):
            return

        if data["type"] == "folder":
            self._navigate_to(data["path"])
        elif data["type"] == "file" and self._sidebar_mode == "templates":
            # Load file as template — content won't count toward stats
            try:
                with open(data["path"], "r", encoding="utf-8") as f:
                    content = f.read()
                self._initial_content = content
                self._initial_word_count = len(content.split()) if content.strip() else 0
                fname = os.path.basename(data["path"])
                self.query_one("#preload-status", Label).update(f"Template: {fname}")
                self.notify(f"Template loaded: {fname}", timeout=2)
            except Exception as e:
                self.notify(f"Could not read file: {e}", severity="error")

    @on(Button.Pressed, "#nav-up")
    def go_up(self):
        parent = os.path.dirname(self._current_folder)
        if parent and parent != self._current_folder:
            self._navigate_to(parent)

    # ── Sidebar mode toggle ──

    @on(Button.Pressed, "#sidebar-folders-btn")
    def switch_to_folders(self):
        self._sidebar_mode = "folders"
        self.query_one("#sidebar-folders-btn").add_class("sidebar-mode-active")
        self.query_one("#sidebar-templates-btn").remove_class("sidebar-mode-active")
        self.query_one("#file-panel-title", Label).update("File Explorer")
        self._navigate_to(self._folders_path)

    @on(Button.Pressed, "#sidebar-templates-btn")
    def switch_to_templates(self):
        self._sidebar_mode = "templates"
        self.query_one("#sidebar-templates-btn").add_class("sidebar-mode-active")
        self.query_one("#sidebar-folders-btn").remove_class("sidebar-mode-active")
        self.query_one("#file-panel-title", Label).update("Templates")
        self._navigate_to(self._templates_path)

    # ── Paste from clipboard ──

    def _clear_preload(self):
        """Clear any preloaded content and uncheck all preload checkboxes."""
        self._initial_content = ""
        self._initial_word_count = 0
        self.query_one("#preload-status", Label).update("")

    def _uncheck_preload_except(self, keep_id: str):
        """Uncheck all preload checkboxes except the given one."""
        for cid in ("#clipboard-checkbox", "#resume-checkbox", "#template-checkbox"):
            if cid != keep_id:
                cb = self.query_one(cid, Checkbox)
                if cb.value:
                    cb.value = False

    @on(Checkbox.Changed, "#clipboard-checkbox")
    def paste_from_clipboard(self, event: Checkbox.Changed):
        if not event.value:
            self._clear_preload()
            return
        self._uncheck_preload_except("#clipboard-checkbox")
        try:
            import subprocess
            import sys
            if sys.platform == "win32":
                result = subprocess.run(
                    ["powershell", "-command", "Get-Clipboard"],
                    capture_output=True, text=True, timeout=5,
                )
                clipboard_text = result.stdout.strip()
            elif sys.platform == "darwin":
                result = subprocess.run(
                    ["pbpaste"], capture_output=True, text=True, timeout=5,
                )
                clipboard_text = result.stdout.strip()
            else:
                result = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-o"],
                    capture_output=True, text=True, timeout=5,
                )
                clipboard_text = result.stdout.strip()

            if clipboard_text:
                self._initial_content = clipboard_text
                self._initial_word_count = len(clipboard_text.split())
                self.query_one("#preload-status", Label).update(
                    f"Clipboard ({self._initial_word_count} words)"
                )
                self.notify("Clipboard preloaded. Will NOT affect your stats.", timeout=3)
            else:
                self.query_one("#clipboard-checkbox", Checkbox).value = False
                self.notify("Clipboard is empty", severity="warning")
        except Exception:
            self.query_one("#clipboard-checkbox", Checkbox).value = False
            self.notify("Could not access clipboard", severity="error")

    @on(Checkbox.Changed, "#resume-checkbox")
    def resume_last_session(self, event: Checkbox.Changed):
        if not event.value:
            self._clear_preload()
            return
        self._uncheck_preload_except("#resume-checkbox")
        try:
            last_path = database.get_last_session_path()
            if not last_path or not os.path.isfile(last_path):
                self.query_one("#resume-checkbox", Checkbox).value = False
                self.notify("No previous session found", severity="warning")
                return
            with open(last_path, "r", encoding="utf-8") as f:
                content = f.read()
            if content.strip():
                self._initial_content = content
                self._initial_word_count = len(content.split())
                fname = os.path.basename(last_path)
                self.query_one("#preload-status", Label).update(
                    f"Resumed: {fname} ({self._initial_word_count} words)"
                )
                self.notify("Last session loaded. Will NOT affect your stats.", timeout=3)
            else:
                self.query_one("#resume-checkbox", Checkbox).value = False
                self.notify("Previous session file is empty", severity="warning")
        except Exception:
            self.query_one("#resume-checkbox", Checkbox).value = False
            self.notify("Could not load last session", severity="error")

    @on(Checkbox.Changed, "#template-checkbox")
    def start_from_template(self, event: Checkbox.Changed):
        if not event.value:
            self._clear_preload()
            return
        self._uncheck_preload_except("#template-checkbox")
        # Switch sidebar to templates mode so user can pick a file
        self._sidebar_mode = "templates"
        self.query_one("#sidebar-folders-btn").remove_class("sidebar-mode-active")
        self.query_one("#sidebar-templates-btn").add_class("sidebar-mode-active")
        self._navigate_to(database.get_templates_folder())
        self.query_one("#preload-status", Label).update("Select a template from the sidebar")
        self.notify("Pick a template file from the sidebar", timeout=3)

    # ── Change folder ──

    def action_change_folder(self):
        self.app.push_screen(
            FolderInputScreen(),
            callback=self._on_folder_changed,
        )

    def _on_folder_changed(self, folder: str | None):
        if folder and os.path.isdir(folder):
            self._navigate_to(folder)

    # ── Start writing ──

    @on(Button.Pressed, "#start-btn")
    def start_writing_btn(self):
        self._do_start()

    def _do_start(self):
        mode_val = self.query_one("#mode-select", Select).value
        if mode_val == Select.BLANK or mode_val == "free":
            mode = "free"
            goal = 0
        elif mode_val == "timer":
            mode = "timer"
            val = self.query_one("#goal-value", Input).value.strip()
            if not val.isdigit() or int(val) == 0:
                self.notify("Enter a valid number of minutes", severity="error")
                return
            goal = int(val) * 60
        else:
            mode = "wordcount"
            val = self.query_one("#goal-value", Input).value.strip()
            if not val.isdigit() or int(val) == 0:
                self.notify("Enter a valid word count goal", severity="error")
                return
            goal = int(val)

        theme_name = self.query_one("#theme-select", Select).value
        if theme_name and theme_name != Select.BLANK:
            database.save_theme(theme_name)

        show_wc = self.query_one("#show-wc-checkbox", Checkbox).value

        self.dismiss({
            "mode": mode,
            "goal": goal,
            "theme": theme_name,
            "show_wc": show_wc,
            "initial_content": self._initial_content,
            "initial_word_count": self._initial_word_count,
        })

    # ── Stats settings ──

    @on(Button.Pressed, "#stats-settings-btn")
    def open_stats_settings(self):
        panel = self.query_one("#stats-settings-panel")
        scroll = self.query_one("#stats-scroll")
        panel.display = True
        scroll.display = False
        self.query_one("#stats-settings-btn").display = False

    @on(Button.Pressed, "#settings-back-btn")
    def close_stats_settings(self):
        panel = self.query_one("#stats-settings-panel")
        scroll = self.query_one("#stats-scroll")
        panel.display = False
        scroll.display = True
        self.query_one("#stats-settings-btn").display = True

    @on(Button.Pressed, "#export-excel-btn")
    def export_excel(self):
        try:
            import csv
            stats = database.load_stats()
            sessions = stats["sessions"]
            if not sessions:
                self.notify("No sessions to export", severity="warning")
                return
            save_dir = database.get_save_folder()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(save_dir, f"typeslate_sessions_{ts}.csv")
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Word Count", "Duration (s)", "Timestamp", "Misspelled Words"])
                for s in sessions:
                    writer.writerow([s["word_count"], s["duration"], s["timestamp"], s["misspelled_words"]])
            self.notify(f"Exported to {filepath}", timeout=5)
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")

    @on(Button.Pressed, "#export-db-btn")
    def export_db(self):
        try:
            import zipfile
            db_path = database.get_db_path()
            save_dir = database.get_save_folder()
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_path = os.path.join(save_dir, f"typeslate_backup_{ts}.tsdb")
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(db_path, "stats.db")
            self.notify(f"Exported to {zip_path}", timeout=5)
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")

    @on(Button.Pressed, "#import-db-btn")
    def import_db(self):
        self.app.push_screen(
            FileInputScreen("Import Database", "Enter path to .tsdb file:"),
            callback=self._on_import_db,
        )

    def _on_import_db(self, filepath: str | None):
        if not filepath:
            return
        try:
            import zipfile
            if not os.path.isfile(filepath):
                self.notify("File not found", severity="error")
                return
            db_path = database.get_db_path()
            with zipfile.ZipFile(filepath, "r") as zf:
                if "stats.db" not in zf.namelist():
                    self.notify("Invalid .tsdb file", severity="error")
                    return
                zf.extract("stats.db", os.path.dirname(db_path))
            self._refresh_stats()
            self.close_stats_settings()
            self.notify("Database imported successfully", timeout=5)
        except Exception as e:
            self.notify(f"Import failed: {e}", severity="error")

    @on(Button.Pressed, "#reset-stats-btn")
    def reset_stats(self):
        self.app.push_screen(
            ConfirmEndScreen("Reset ALL statistics? This cannot be undone."),
            callback=self._on_reset_confirmed,
        )

    def _on_reset_confirmed(self, confirmed: bool):
        if not confirmed:
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions")
            cursor.execute("DELETE FROM total_stats")
            conn.commit()
            conn.close()
            self._refresh_stats()
            self.close_stats_settings()
            self.notify("Statistics reset", timeout=3)
        except Exception as e:
            self.notify(f"Reset failed: {e}", severity="error")

    # ── Navigation actions ──

    def action_toggle_sidebar(self):
        panel = self.query_one("#file-panel")
        self._sidebar_visible = not self._sidebar_visible
        panel.display = self._sidebar_visible

    def action_focus_sidebar(self):
        try:
            self.query_one("#file-tree", Tree).focus()
        except Exception:
            pass

    def action_focus_center(self):
        try:
            self.query_one("#mode-select", RadioSet).focus()
        except Exception:
            pass

    def action_focus_stats(self):
        try:
            self.query_one("#stats-scroll", VerticalScroll).focus()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Folder Input Screen (modal to type/paste a folder path)
# ---------------------------------------------------------------------------
class FolderInputScreen(ModalScreen[str | None]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    FolderInputScreen {
        align: center middle;
    }
    #folder-input-container {
        width: 60;
        height: auto;
        background: #252525;
        border: double #4ec965;
        padding: 1 2;
    }
    #folder-input-container Label {
        color: #d4d4d4;
        margin-bottom: 1;
    }
    #folder-path-input {
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        current = database.get_save_folder()
        with Vertical(id="folder-input-container"):
            yield Label("Set File Explorer Folder")
            yield Label("Enter the full path to the folder you want to browse:")
            yield Input(value=current, id="folder-path-input")
            with Horizontal():
                yield Button("OK", variant="primary", id="folder-ok")
                yield Button("Cancel", id="folder-cancel")

    @on(Button.Pressed, "#folder-ok")
    def ok(self):
        path = self.query_one("#folder-path-input", Input).value.strip()
        if path and os.path.isdir(path):
            self.dismiss(path)
        else:
            self.notify("Folder not found. Enter a valid path.", severity="error")

    @on(Button.Pressed, "#folder-cancel")
    def cancel(self):
        self.dismiss(None)

    def action_cancel(self):
        self.dismiss(None)


# ---------------------------------------------------------------------------
# File Input Screen (modal to type/paste a file path)
# ---------------------------------------------------------------------------
class FileInputScreen(ModalScreen[str | None]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    FileInputScreen {
        align: center middle;
    }
    #file-input-container {
        width: 60;
        height: auto;
        background: #252525;
        border: double #4ec965;
        padding: 1 2;
    }
    #file-input-container Label {
        color: #d4d4d4;
        margin-bottom: 1;
    }
    #file-path-input {
        margin-bottom: 1;
    }
    """

    def __init__(self, title: str = "Select File", prompt: str = "Enter file path:"):
        super().__init__()
        self._title = title
        self._prompt = prompt

    def compose(self) -> ComposeResult:
        with Vertical(id="file-input-container"):
            yield Label(self._title)
            yield Label(self._prompt)
            yield Input(id="file-path-input")
            with Horizontal():
                yield Button("OK", variant="primary", id="file-ok")
                yield Button("Cancel", id="file-cancel")

    @on(Button.Pressed, "#file-ok")
    def ok(self):
        path = self.query_one("#file-path-input", Input).value.strip()
        if path:
            self.dismiss(path)
        else:
            self.notify("Enter a file path", severity="error")

    @on(Button.Pressed, "#file-cancel")
    def cancel(self):
        self.dismiss(None)

    def action_cancel(self):
        self.dismiss(None)



# ---------------------------------------------------------------------------
# Session Complete Screen
# ---------------------------------------------------------------------------
class SessionCompleteScreen(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss", "OK")]

    DEFAULT_CSS = """
    SessionCompleteScreen {
        align: center middle;
    }
    #session-complete-container {
        width: 50;
        height: auto;
        background: #252525;
        border: double #d4a843;
        padding: 1 2;
    }
    #session-complete-container .sc-heading {
        text-align: center;
        text-style: bold;
        color: #d4a843;
        margin-bottom: 1;
    }
    #session-complete-container Label {
        color: #d4d4d4;
    }
    """

    def __init__(self, word_count: int, duration: float, misspelled: int):
        super().__init__()
        self.word_count = word_count
        self.duration = duration
        self.misspelled = misspelled

    def compose(self) -> ComposeResult:
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        with Vertical(id="session-complete-container"):
            yield Label("Session Complete", classes="sc-heading")
            yield Label(f"  Words written:    {self.word_count:,}")
            yield Label(f"  Time spent:       {minutes}m {seconds}s")
            yield Label(f"  Misspelled words: {self.misspelled}")
            yield Label("")
            yield Button("OK", variant="primary", id="sc-ok")

    @on(Button.Pressed, "#sc-ok")
    def close(self):
        self.dismiss()


# ---------------------------------------------------------------------------
# End Session Confirmation
# ---------------------------------------------------------------------------
class ConfirmEndScreen(ModalScreen[bool]):
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    DEFAULT_CSS = """
    ConfirmEndScreen {
        align: center middle;
    }
    #confirm-container {
        width: 44;
        height: auto;
        background: #252525;
        border: double #cc4444;
        padding: 1 2;
    }
    #confirm-container Label {
        text-align: center;
        color: #d4d4d4;
        margin-bottom: 1;
    }
    """

    def __init__(self, message: str = "End your writing session?"):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-container"):
            yield Label(self.message)
            with Horizontal():
                yield Button("Yes", variant="error", id="confirm-yes")
                yield Button("No", variant="primary", id="confirm-no")

    @on(Button.Pressed, "#confirm-yes")
    def yes(self):
        self.dismiss(True)

    @on(Button.Pressed, "#confirm-no")
    def no(self):
        self.dismiss(False)

    def action_cancel(self):
        self.dismiss(False)


# ---------------------------------------------------------------------------
# Goal Reached Screen
# ---------------------------------------------------------------------------
class GoalReachedScreen(ModalScreen):
    BINDINGS = [Binding("escape", "dismiss", "Continue")]

    DEFAULT_CSS = """
    GoalReachedScreen {
        align: center middle;
    }
    #goal-container {
        width: 50;
        height: auto;
        background: #252525;
        border: double #4ec965;
        padding: 1 2;
    }
    #goal-container Label {
        text-align: center;
        color: #d4d4d4;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="goal-container"):
            yield Label("Goal Reached!")
            yield Label("You can keep writing or press Escape to end.")
            yield Button("Continue Writing", variant="primary", id="goal-ok")

    @on(Button.Pressed, "#goal-ok")
    def close(self):
        self.dismiss()


# ---------------------------------------------------------------------------
# Writing Screen - TRUE fullscreen, just like desktop TypeSlate
# No header, no footer, no chrome. Just you and the words.
# ---------------------------------------------------------------------------
class WritingScreen(Screen):
    BINDINGS = [
        Binding("escape", "end_session", "End Session", show=False),
        Binding("ctrl+p", "toggle_pause", "Pause", show=False),
        Binding("ctrl+q", "force_end", "Force End", show=False),
        Binding("ctrl+s", "save_now", "Save", show=False),
    ]

    DEFAULT_CSS = """
    WritingScreen {
        layout: vertical;
        background: #1a1410;
        padding: 0;
        margin: 0;
    }
    #writing-area {
        width: 1fr;
        height: 1fr;
        border: none;
        padding: 0;
        margin: 0;
    }
    /* Strip all TextArea internal chrome */
    #writing-area .text-area--cursor-line {
        background: transparent;
    }
    /* Minimal status line — same bg as editor, nearly invisible */
    #writing-status {
        dock: bottom;
        height: 1;
        padding: 0 2;
        margin: 0;
    }
    #writing-status Label {
        margin: 0 2;
    }
    #timer-label {
        dock: left;
    }
    #wc-label {
        dock: right;
    }
    #pause-label {
        text-style: bold;
        dock: right;
        margin-right: 2;
    }
    """

    word_count: reactive[int] = reactive(0)
    timer_remaining: reactive[int] = reactive(0)
    paused: reactive[bool] = reactive(False)
    goal_reached: reactive[bool] = reactive(False)

    def __init__(
        self, mode: str, goal: int, theme_name: str, show_wc: bool = False,
        initial_content: str = "", initial_word_count: int = 0,
    ):
        super().__init__()
        self.mode = mode
        self.goal = goal
        self.theme_name = theme_name
        self.show_wc = show_wc
        self.initial_content = initial_content
        self.initial_word_count = initial_word_count
        self.start_time: datetime | None = None
        self.filename: str | None = None

    def compose(self) -> ComposeResult:
        # No Header, no Footer — pure fullscreen like desktop TypeSlate
        yield TextArea(id="writing-area", language=None, show_line_numbers=False, soft_wrap=True)
        with Horizontal(id="writing-status"):
            yield Label("", id="timer-label")
            yield Label("", id="pause-label")
            yield Label("", id="wc-label")

    def on_mount(self):
        self._enter_fullscreen()
        self._apply_theme()
        self._start_session()

    def _enter_fullscreen(self):
        """Make the terminal go true fullscreen — no tabs, no taskbar."""
        import sys
        if sys.platform == "win32":
            try:
                import ctypes
                VK_F11 = 0x7A
                KEYEVENTF_KEYUP = 0x0002
                ctypes.windll.user32.keybd_event(VK_F11, 0, 0, 0)
                ctypes.windll.user32.keybd_event(VK_F11, 0, KEYEVENTF_KEYUP, 0)
                self._was_fullscreened = True
            except Exception:
                self._was_fullscreened = False
        else:
            # xterm-compatible terminals
            sys.stdout.write("\x1b[9;1t")
            sys.stdout.flush()
            self._was_fullscreened = True

    def _exit_fullscreen(self):
        """Restore the terminal from fullscreen."""
        import sys
        if sys.platform == "win32":
            if getattr(self, "_was_fullscreened", False):
                try:
                    import ctypes
                    VK_F11 = 0x7A
                    KEYEVENTF_KEYUP = 0x0002
                    ctypes.windll.user32.keybd_event(VK_F11, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(VK_F11, 0, KEYEVENTF_KEYUP, 0)
                    self._was_fullscreened = False
                except Exception:
                    pass
        else:
            if getattr(self, "_was_fullscreened", False):
                sys.stdout.write("\x1b[9;0t")
                sys.stdout.flush()
                self._was_fullscreened = False

    def _apply_theme(self):
        bg, fg, accent = THEMES.get(self.theme_name, THEMES["Warm Dark"])

        # Screen background
        self.styles.background = bg

        # Text area — fill entire screen
        ta = self.query_one("#writing-area", TextArea)
        ta.styles.background = bg
        ta.styles.color = fg

        # Status line — subtle, same bg as editor with dimmed text
        status = self.query_one("#writing-status")
        status.styles.background = bg
        status.styles.color = accent

        # Pause label in red regardless of theme
        pause = self.query_one("#pause-label", Label)
        pause.styles.color = "#cc4444"

    def _start_session(self):
        self.start_time = datetime.now()

        save_folder = database.get_save_folder()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = os.path.join(save_folder, f"TypeSlate_Autosave_{timestamp}.txt")
        database.save_last_session_path(self.filename)

        # Preload template/clipboard content
        if self.initial_content:
            ta = self.query_one("#writing-area", TextArea)
            ta.insert(self.initial_content)

        if self.mode == "timer":
            self.timer_remaining = self.goal
            self._tick_timer()

        # Show or hide word count
        if self.show_wc:
            self.query_one("#wc-label", Label).update("Words: 0")
        else:
            self.query_one("#wc-label", Label).display = False

        # Hide the entire status bar if nothing to show
        if not self.show_wc and self.mode != "timer":
            self.query_one("#writing-status").display = False

        self._do_autosave()
        self.query_one("#writing-area", TextArea).focus()

    def _tick_timer(self):
        if self.timer_remaining > 0 and not self.paused:
            self.timer_remaining -= 1
            minutes, seconds = divmod(self.timer_remaining, 60)
            self.query_one("#timer-label", Label).update(f"{minutes}:{seconds:02d}")
            self.set_timer(1.0, self._tick_timer)
        elif self.timer_remaining <= 0 and self.mode == "timer" and not self.goal_reached:
            self.goal_reached = True
            self.app.push_screen(GoalReachedScreen())
            self.query_one("#timer-label", Label).update("Time's up!")

    def _do_autosave(self):
        if self.filename:
            try:
                ta = self.query_one("#writing-area", TextArea)
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write(ta.text)
            except Exception:
                pass
        self.set_timer(2.0, self._do_autosave)

    @on(TextArea.Changed, "#writing-area")
    def on_text_changed(self, event: TextArea.Changed):
        text = event.text_area.text
        total = len(text.split()) if text.strip() else 0
        self.word_count = max(0, total - self.initial_word_count)

    def watch_word_count(self, count: int):
        if self.show_wc:
            try:
                self.query_one("#wc-label", Label).update(f"Words: {count:,}")
            except Exception:
                pass
        if self.mode == "wordcount" and self.goal > 0 and count >= self.goal and not self.goal_reached:
            self.goal_reached = True
            self.app.push_screen(GoalReachedScreen())

    def watch_paused(self, is_paused: bool):
        try:
            pause_label = self.query_one("#pause-label", Label)
            ta = self.query_one("#writing-area", TextArea)
            if is_paused:
                pause_label.update("PAUSED")
                ta.read_only = True
            else:
                pause_label.update("")
                ta.read_only = False
        except Exception:
            pass

    def action_toggle_pause(self):
        self.paused = not self.paused
        if not self.paused and self.mode == "timer" and self.timer_remaining > 0:
            self._tick_timer()

    def action_save_now(self):
        if self.filename:
            try:
                ta = self.query_one("#writing-area", TextArea)
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write(ta.text)
                self.notify("Saved", timeout=1)
            except Exception as e:
                self.notify(f"Save failed: {e}", severity="error")

    def action_end_session(self):
        if self.mode == "free" or self.goal_reached:
            self.app.push_screen(
                ConfirmEndScreen("End your writing session?"),
                callback=self._on_confirm_end,
            )
        else:
            self.notify("Goal not reached. Ctrl+Q to force end, Ctrl+P to pause.", severity="warning")

    def action_force_end(self):
        self.app.push_screen(
            ConfirmEndScreen("End session early? Progress will still be saved."),
            callback=self._on_confirm_end,
        )

    def _on_confirm_end(self, confirmed: bool | None):
        if confirmed:
            self._finalize_session()

    @work(thread=True)
    def _finalize_session(self):
        ta = self.query_one("#writing-area", TextArea)
        text = ta.text
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        misspelled = database.analyze_text(text)

        # Copy text to clipboard (same as desktop TypeSlate)
        try:
            import subprocess
            if os.name == "nt":
                process = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
                process.communicate(text.encode("utf-16le"))
            elif os.name == "posix":
                # Try xclip, xsel, or pbcopy (macOS)
                for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["pbcopy"]]:
                    try:
                        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
                        process.communicate(text.encode("utf-8"))
                        break
                    except FileNotFoundError:
                        continue
        except Exception:
            pass

        # Final save
        if self.filename:
            try:
                with open(self.filename, "w", encoding="utf-8") as f:
                    f.write(text)
            except Exception:
                pass

        wc = self.word_count
        database.save_session(wc, duration, misspelled)
        self.app.call_from_thread(self._show_complete, wc, duration, misspelled)

    def _show_complete(self, wc: int, duration: float, misspelled: int):
        self._exit_fullscreen()
        self.app.push_screen(
            SessionCompleteScreen(wc, duration, misspelled),
            callback=lambda _: self.dismiss(None),
        )


# ---------------------------------------------------------------------------
# Main App
# ---------------------------------------------------------------------------
class TypeSlateApp(App):
    TITLE = "TypeSlate"

    CSS = """
    Screen {
        background: #1e1e1e;
    }
    """

    def __init__(self):
        super().__init__()
        database.initialize_db()

    def on_mount(self):
        self._show_home()

    def _show_home(self):
        self.push_screen(HomeScreen(), callback=self._on_home_done)

    def _on_home_done(self, result):
        if result is None:
            self._show_home()
            return
        self.push_screen(
            WritingScreen(
                mode=result["mode"],
                goal=result["goal"],
                theme_name=result["theme"] if result["theme"] != Select.BLANK else "Warm Dark",
                show_wc=result.get("show_wc", False),
                initial_content=result.get("initial_content", ""),
                initial_word_count=result.get("initial_word_count", 0),
            ),
            callback=lambda _: self._show_home(),
        )
