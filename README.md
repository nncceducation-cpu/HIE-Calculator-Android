# HIE Calculator — Android shell (Capacitor)

A thin native Android wrapper around the live **HIE Calculator** web app. The UI
is served from GitHub Pages (`https://nncceducation-cpu.github.io/HIE-Calculator/`),
so any change committed to the **HIE-Calculator** repo reaches this app the next
time it is opened — no rebuild, no Play upload.

This bundle exists only to:
1. Meet Google Play's target-API requirement (targets API 35), so the app can
   still be updated after 31 Aug 2026.
2. Give us a signing key we control (Play App Signing is enabled on the listing,
   so a new *upload* key is fine after a one-time upload-key reset).

Package: `com.hiecalc` · versionName 2.1 · versionCode 4 (last Play upload was 3).

## One-time setup

1. **Create a GitHub repo** named `HIE-Calculator-Android` under
   `nncceducation-cpu` and push these files to `main`.

2. **Add four repository secrets** (Settings → Secrets and variables → Actions):
   - `ANDROID_KEYSTORE_BASE64` — contents of `keystore_base64.txt`
   - `ANDROID_KEYSTORE_PASSWORD` — the keystore password
   - `ANDROID_KEY_ALIAS` — `hiecalc-upload`
   - `ANDROID_KEY_PASSWORD` — the same password

3. **Register the new upload key with Play** (required because this is a new key):
   Play Console → HIE Calculator → Test and release → App signing →
   **Request upload key reset** → upload `upload_certificate.pem`. Google
   activates it (usually within a day). Existing installs are unaffected —
   Google re-signs every upload with the original app-signing key.

## Building a release

Actions → **Android build (signed .aab + .apk)** → Run workflow →
version_code `4`, version_name `2.1`. Download the `hie-android` artifact; the
`.aab` goes to Play (closed testing), the `.apk` is for sideload testing.

## Launcher icon

If `assets/icon-only.png` (1024×1024) and `assets/splash.png` are present, the
CI generates the icon set automatically. If not, the app ships with the default
Capacitor icon. Drop the current app icon into `assets/` to keep the launcher
icon identical to the published app.

## Signing material — keep offline, never commit

`release.keystore`, its password, and `upload_certificate.pem` are delivered
separately. Store them somewhere safe (password manager). They are gitignored
and must never be committed.
