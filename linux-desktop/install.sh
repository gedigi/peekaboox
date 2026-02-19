#!/bin/bash
# install.sh — Install dependencies for the linux-desktop OpenClaw skill
# Supports apt (Debian/Ubuntu), dnf (Fedora/RHEL), and pacman (Arch)
set -e

echo "Installing linux-desktop skill dependencies..."

# Warn if running under Wayland
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    echo "WARNING: Wayland session detected. This skill requires X11." >&2
    echo "Log out and select an X11/Xorg session at login to use this skill." >&2
fi

# Detect package manager and install system packages
if command -v apt-get &>/dev/null; then
    sudo apt-get update -q
    sudo apt-get install -y xdotool wmctrl scrot x11-utils imagemagick python3 python3-venv python3-pip
elif command -v dnf &>/dev/null; then
    sudo dnf install -y xdotool wmctrl scrot xorg-x11-utils ImageMagick python3 python3-pip
elif command -v pacman &>/dev/null; then
    sudo pacman -S --noconfirm xdotool wmctrl scrot xorg-xwininfo imagemagick python python-pip
else
    echo "ERROR: Unsupported package manager. Install manually: xdotool wmctrl scrot" >&2
    exit 1
fi

# Install Python dependencies (PEP 668-safe) in a local virtual environment
VENV_DIR="${PWD}/.venv"

if command -v python3 >/dev/null 2>&1; then
    echo "Setting up Python virtual environment at ${VENV_DIR} ..."
    python3 -m venv "${VENV_DIR}"
    "${VENV_DIR}/bin/pip" install --quiet --upgrade pip
    "${VENV_DIR}/bin/pip" install --quiet anthropic pillow
    echo "Python deps installed in venv."
    echo "Use: source ${VENV_DIR}/bin/activate"
else
    echo "WARNING: python3 not found in PATH; skipping Python package install." >&2
fi

echo ""
echo "Installation complete."
echo "Test with: xdotool getactivewindow"
echo "Make sure DISPLAY is set (e.g., export DISPLAY=:0)"
