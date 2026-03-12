# TypeSlate Terminal


A distraction-free writing environment for the terminal. Built with [Textual](https://textual.textualize.io/).

TypeSlate Terminal brings focused, minimal writing to your terminal — no browser, no GUI, no distractions. Just open your terminal, type `typeslate`, and write.

<img width="2560" height="1504" alt="terminal-window" src="https://github.com/user-attachments/assets/0fe2959a-9c19-4e26-a502-cb5a2ca7c0ca" />

## Features

- **Distraction-free writing** — true fullscreen mode hides taskbar and terminal chrome
- **Multiple writing modes** — Free Write, Timer Mode, Word Count Goal
- **Session tracking** — words written, time spent, misspelled words per session
- **Lifetime statistics** — daily, weekly, monthly, and all-time word counts
- **File explorer** — browse and set your save folder from the sidebar
- **Templates** — load template files to start writing with pre-existing content
- **Resume last session** — pick up where you left off
- **Paste from clipboard** — start with clipboard content (won't count toward stats)
- **Misspelled word count** — shows how many words were misspelled at the end of each session
- **8 color themes** — Classic Dark, Warm Dark, DOS Green, Amber Terminal, DOS Blue, and more
- **Auto-save** — saves every 2 seconds while writing
- **Clipboard export** — text is copied to clipboard when your session ends
- **Cross-platform** — works on Windows, macOS, and Linux
- **Shared database** — stats sync with the desktop TypeSlate app

<img width="2560" height="1600" alt="fullscreen-writing-env" src="https://github.com/user-attachments/assets/8c8f13ac-7823-45b7-a0df-6a505b94fe4d" />


## Installation

Requires **Python 3.10** or higher.

### From PyPI

```bash
pip install typeslate-terminal
```

### From source

```bash
git clone https://github.com/josh-writes/typeslate-terminal.git
cd typeslate-terminal
pip install .
```

## Quick Start

After installing, run:

```bash
typeslate
```

Or run as a Python module:

```bash
python -m typeslate_terminal
```

## How It Works

### Home Screen

The home screen has three panels:

| Panel | What it does |
|-------|-------------|
| **Left — File Explorer** | Browse folders and templates. Click a folder to set it as your save location. Switch to Templates mode to load a file as a starting point. |
| **Center — Setup** | Choose your writing mode, pick a theme, and toggle options like Show Word Count, Paste from Clipboard, Resume Last Session, or Start from Template. |
| **Right — Statistics** | View your daily, weekly, and lifetime word counts, recent sessions, and access settings for exporting/importing data. |

Press **Start Writing** to enter fullscreen writing mode.

### Writing Mode

Once in a session, the screen goes fullscreen — just you and your words.

| Key | Action |
|-----|--------|
| `Escape` | End session |
| `Ctrl+P` | Pause / Resume |
| `Ctrl+S` | Save now |
| `Ctrl+Q` | Force end (no confirmation) |

When you end a session:
- Your text is **saved to a file** in your chosen folder
- Your text is **copied to the clipboard**
- Session stats (words, time, misspelled words) are **recorded to the database**

### Writing Modes

| Mode | Description |
|------|-------------|
| **Free Write** | Write with no goal — end whenever you want |
| **Timer Mode** | Write for a set number of minutes |
| **Word Count** | Write until you hit a word count goal |

## Themes

Choose from 8 built-in themes:

- Classic Dark
- Warm Dark
- DOS Green
- Amber Terminal
- DOS Blue
- Classic Light
- Warm Light
- Warm DOS

Your theme selection is saved between sessions.

## Data Storage

TypeSlate Terminal stores its database and settings in your platform's standard data directory:

| Platform | Location |
|----------|----------|
| **Windows** | `%LOCALAPPDATA%\TypeSlate\` |
| **macOS** | `~/Library/Application Support/TypeSlate/` |
| **Linux** | `~/.local/share/TypeSlate/` |

The database is shared with the [desktop TypeSlate app](https://typeslate.com), so your stats stay unified across both versions.

## Stats Settings

Access via the **Settings** button in the stats panel:

- **Export to CSV** — export all sessions as a CSV file
- **Export Database** — back up your stats as a `.tsdb` file
- **Import Database** — restore stats from a `.tsdb` backup
- **Reset Stats** — clear all session history (with confirmation)

## Dependencies

- [Textual](https://textual.textualize.io/) — terminal UI framework
- [pyspellchecker](https://github.com/barrust/pyspellchecker) — spell checking

## License

[MIT](LICENSE)

## Typeslate
[typeslate.com](https://typeslate.com)

If you want to say thanks, I love coffee...
 [![Ko-fi](https://img.shields.io/badge/Support-Ko--fi-ff5e5b?logo=ko-fi&logoColor=white)](https://ko-fi.com/typeslate)

 
