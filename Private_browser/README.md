# Private Dev Browser – README  
*(Single-file, ultra-private developer browser)*

**File:** `private-dev-browser.py`  
**Engine:** Chromium (via Qt WebEngine – Qt 6)  
**Size:** ~140 lines  
**Persistence:** Absolutely none (everything lives only in RAM)

### What it is
A minimal, distraction-free, always-private browser built for developers.  
No history, no cookies, no cache, no localStorage, no passwords, no crash reports — nothing ever touches the disk.

Perfect for:
- Testing websites in a completely clean environment
- Scraping / automation without leftover sessions
- Paranoid browsing
- Quick debugging with full Chromium DevTools

### Features
- Full Chromium DevTools (detached window) on F12 or button
- DuckDuckGo search directly from the URL bar
- Dark VS Code-style theme
- Back / Forward / Reload + URL bar only — no bloat
- 100 % in-memory profile (true private browsing every time)

### Requirements
```bash
# Arch Linux / Manjaro / EndeavourOS
sudo pacman -S python-pyqt6 python-pyqt6-webengine

# Debian / Ubuntu / Pop!_OS
sudo apt install python3-pyqt6 python3-pyqt6-webengine

# Fedora
sudo dnf install python3-pyqt6 qt6-qtwebengine

# openSUSE
sudo zypper in python3-qt6 python3-qtwebengine6
```

### How to run (any Linux machine)
```bash
# 1. Save the script as private-dev-browser.py
# 2. Make it executable (optional)
chmod +x private-dev-browser.py

# 3. Run it
python3 private-dev-browser.py
```

That’s it. No virtualenv, no pip, no extra dependencies beyond the system Qt6 packages.

### Shortcuts
- **Dev/Tools** → Open/close full Chromium Developer Tools  
- **Enter** in URL bar → navigate or search with DuckDuckGo  
- Buttons: Back ←, Forward →, Reload ↻, DevTools

### Portability
Just copy the single `private-dev-browser.py` file to any other Linux machine that has PyQt6 + Qt WebEngine installed and run it. Works the same everywhere.

Enjoy your permanently clean, permanently private, developer-focused browser.
