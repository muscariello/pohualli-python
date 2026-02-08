# Pohualli Desktop (Flutter)

Native macOS/Windows desktop UI that talks to the Python engine via `pohualli-rpc` over stdin/stdout JSON-RPC.

Release artifacts are self-contained: CI bundles a compiled `pohualli-rpc-bin` inside the app package, so end users do not need a separate Python installation.

## Local run
1. Install Flutter stable.
2. Ensure `pohualli-rpc` is available on `PATH` (for example with `pip install -e .` from repository root).
3. From this folder:
   - `flutter create . --platforms=macos,windows`
   - `flutter pub get`
   - `flutter run -d macos` or `flutter run -d windows`

## Build
- macOS: `flutter build macos --release`
- Windows: `flutter build windows --release`

## Notes
- RPC protocol is newline-delimited JSON-RPC.
- The app first tries a bundled backend executable (`pohualli-rpc-bin`) and falls back to `pohualli-rpc` on `PATH` for development.
- The Flutter app sends `health`, `list_correlations`, `convert`, `derive_autocorr`, `search_range`, and `quit` requests.

## CI / Release
- Workflow: `.github/workflows/flutter-desktop.yml`
- Builds on macOS + Windows.
- On version tags (`v*.*.*`), artifacts are attached to the GitHub Release:
  - `PohualliDesktop-<version>-macOS.zip` (notarized when Apple secrets are configured)
  - `PohualliDesktop-<version>-macOS-unsigned.zip` (fallback when secrets are missing)
  - `PohualliDesktop-<version>-windows.zip`

### Required GitHub secrets for macOS notarization
- `APPLE_SIGNING_CERT_BASE64`: Base64-encoded `.p12` signing certificate
- `APPLE_SIGNING_CERT_PASSWORD`: Password for the `.p12` certificate
- `APPLE_SIGNING_IDENTITY`: Codesign identity name (for example, `Developer ID Application: ...`)
- `APPLE_ID`: Apple account email used for notarization
- `APPLE_APP_SPECIFIC_PASSWORD`: App-specific password for Apple ID
- `APPLE_TEAM_ID`: Apple Developer Team ID
- `APPLE_KEYCHAIN_PASSWORD` (optional): Custom temporary keychain password in CI
