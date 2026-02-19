# linux-desktop — OpenClaw Linux GUI Automation Skill

Full GUI automation for Linux X11 desktops. This skill gives the OpenClaw agent the ability to capture screenshots, inspect windows, click, type, send hotkeys, scroll, manage windows, and use vision AI to locate UI elements by description.

This is the Linux equivalent of the macOS **Peekaboo** skill.

## Requirements

- Linux with X11 session (XFCE, GNOME on X11, KDE on X11, i3, openbox, etc.)
- `DISPLAY` environment variable set (usually `:0`)
- `OPENAI_API_KEY` for vision features

## Installation

```bash
cd linux-desktop/
bash install.sh
```

This installs: `xdotool`, `wmctrl`, `scrot`, `x11-utils`, `imagemagick`, `python3`, `pip3`, `openai`, `pillow`.

Supported package managers: apt (Debian/Ubuntu), dnf (Fedora/RHEL), pacman (Arch).

## Tools

| Script | Purpose |
|--------|---------|
| `capture.sh` | Take screenshots (full screen or specific window) |
| `inspect.sh` | List windows, get window details (JSON output) |
| `click.sh` | Mouse click at coordinates (left/right/middle, single/double) |
| `type.sh` | Type text into the focused window |
| `hotkey.sh` | Send keyboard shortcuts (ctrl+c, alt+F4, etc.) |
| `scroll.sh` | Scroll up/down at current or specified position |
| `window.sh` | Window management (focus, minimize, maximize, close, move, resize) |
| `vision.py` | Use GPT-4 Vision API to find UI elements or describe the screen |

## Quick Start

```bash
# Take a screenshot
bash capture.sh

# List all open windows
bash inspect.sh

# Click at coordinates
bash click.sh --x 500 --y 300

# Type text
bash type.sh "Hello world"

# Send Ctrl+C
bash hotkey.sh "ctrl+c"

# Find a UI element using vision AI
SHOT=$(bash capture.sh | tail -1)
python3 vision.py --image "$SHOT" --find "Save button" --json
```

## Testing

```bash
bash test.sh
```

## OpenClaw Integration

Place the `linux-desktop/` folder in your OpenClaw skills directory:

```bash
cp -r linux-desktop/ ~/.openclaw/workspace/skills/linux-desktop/
```

Restart the OpenClaw gateway. The agent will read `SKILL.md` to learn how to use the skill.

## Limitations

- **X11 only** — does not work on Wayland sessions
- Some applications with custom rendering may resist automation
- Vision features require an OpenAI API key
