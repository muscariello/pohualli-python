# Desktop Apps

Pohualli desktop UI is implemented with Flutter and uses the Python JSON-RPC backend.

## Architecture

- Frontend: `flutter/pohualli_desktop`
- Backend process: `pohualli-rpc` (bundled as `pohualli-rpc-bin` in release artifacts)
- Build workflow: `.github/workflows/flutter-desktop.yml`

## Local Development

```bash
cd flutter/pohualli_desktop
flutter pub get
flutter run -d macos      # or: flutter run -d windows
```

If host platform folders are missing, generate them:

```bash
flutter create . --platforms=macos,windows
```

## Release Artifacts

For tags `v*.*.*`, the Flutter Desktop workflow publishes:

- macOS zip (`PohualliDesktop-<version>-macOS.zip`) when notarization secrets are set
- macOS unsigned zip (`PohualliDesktop-<version>-macOS-unsigned.zip`) when secrets are missing
- Windows zip (`PohualliDesktop-<version>-windows.zip`)

## macOS First Run

If you install an unsigned build:

1. Move `PohualliDesktop.app` to `/Applications` (optional).
2. Control-click the app and select Open.
3. Confirm Open in the Gatekeeper dialog.

## Windows First Run

If SmartScreen warns on unsigned binaries, select More info and Run anyway.
