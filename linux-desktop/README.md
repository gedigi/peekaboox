# linux-desktop — OpenClaw Linux GUI Automation Skill

Full GUI automation for Linux X11 desktops. This skill gives the OpenClaw agent the ability to capture screenshots, inspect windows, click, type, send hotkeys, scroll, and manage windows. The agent uses its own vision to locate UI elements on screen.

This is the Linux equivalent of the macOS **Peekaboo** skill.

## Requirements

- Linux with X11 session (XFCE, GNOME on X11, KDE on X11, i3, openbox, etc.)
- `DISPLAY` environment variable set (usually `:0`)

## Installation

```bash
cd linux-desktop/
bash install.sh
```

This installs: `xdotool`, `wmctrl`, `scrot`, `x11-utils`, `imagemagick`.

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

The agent uses its own vision to interpret screenshots — no separate vision script or API key needed.

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

# Take a screenshot, then look at it yourself to find UI elements
SHOT=$(bash capture.sh | tail -1)
# (read the image file to identify element positions, then click)
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
