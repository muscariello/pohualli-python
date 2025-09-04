# Desktop Bundles

This project can be packaged into a native-like desktop application using **Briefcase**. The desktop build launches the FastAPI web interface locally and opens your default browser.

## Why Briefcase?
- Produces platform‑specific bundles (.app on macOS, MSI/exe on Windows, AppImage/Flatpak/Snap options on Linux)
- Uses a Python runtime isolated from any system install
- Keeps a clean separation between source and distributable artifacts

## Added Launcher
The module `pohualli/desktop_app.py` is the Briefcase entry point. It:
1. Finds a free local port
2. Starts the FastAPI app via Uvicorn
3. Opens the system default browser to the local URL

## Prerequisites
Install development extras (includes Briefcase):
```bash
pip install -e .[dev,web]
```
(Or use `pipx install briefcase` if you prefer a global Briefcase.)

## Install Options Summary
- PyPI (library + CLI): `pip install pohualli` (add `[web]` for UI)
- Desktop bundle (macOS/Windows): download artifact from CI or Release and run the app directly (no Python needed)

Latest release downloads: https://github.com/muscariello/pohualli-python/releases

macOS first-run approval (unsigned/ad-hoc): Control-click the app, choose Open, then confirm. Subsequent launches are normal.

Windows SmartScreen: Click “More info” → “Run anyway” if warned (unsigned build).

## Build Steps (macOS / Linux)
```bash
briefcase create   # Generate platform project structure
briefcase build    # Build the distributable bundle
briefcase run      # Launch the packaged app
```
Artifacts appear under `build/` and `dist/`.

## Windows Notes
On Windows the steps are identical. To produce an MSI installer you can then run:
```bash
briefcase package
```
(Signing the installer requires a code signing certificate—optional but recommended for SmartScreen reputation.)

## Updating the App
After changing code:
```bash
briefcase build
briefcase run
```
If dependencies (or briefcase config) changed, re-run `briefcase create` first.

## Data Files / Templates
Templates (`pohualli/templates/*.html`) are included by packaging metadata. The Briefcase bundle uses the installed package so no extra step is required.

## Troubleshooting
| Issue | Fix |
|-------|-----|
| Browser does not open | Navigate manually to the printed http://127.0.0.1:<port> |
| Port in use | The launcher selects a free ephemeral port; rare collisions can be solved by re-running |
| Missing templates | Ensure editable install with `-e .` before building, or clean previous build directories |
| Uvicorn not found | Confirm `web` extra installed (`pip install -e .[web]`) |

## Alternative: Single Executable
If you only need a CLI binary, consider `pyinstaller --onefile pohualli/cli.py` (faster build). Briefcase is preferred for a cohesive multi-platform experience.

## Next Steps
- Optional: add code signing / notarization instructions
- Optional: add a system tray wrapper or electron shell (out of scope for now)

