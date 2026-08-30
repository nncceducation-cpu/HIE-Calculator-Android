#!/usr/bin/env python3
"""
Patches the Capacitor-generated android/ project for a signed Play release.

android/ is regenerated from scratch on every CI run (it is gitignored), so
every change we need has to be reapplied here rather than committed. Three
things are wrong with the stock Capacitor 6 output:

  1. It targets SDK 34. Google Play requires new bundles to target a recent API
     level; from 31 Aug 2026 an app whose target API is not within one year of
     the latest release can no longer be updated. The release build now targets API 36.
  2. compileSdk 36 needs a current Android Gradle Plugin. Capacitor 6 ships 8.2.1,
     so AGP and the Gradle wrapper both move up too.
  3. There is no signing config at all - the stock release buildType is unsigned.

This is a thin remote-URL WebView wrapper: no camera, no extra permissions
beyond INTERNET (which Capacitor includes by default).

Reads from the environment:
  ANDROID_VERSION_CODE   monotonically increasing integer; Play rejects reuse
  ANDROID_VERSION_NAME   e.g. 2.1
  KEYSTORE_PATH / KEYSTORE_PASSWORD / KEY_ALIAS / KEY_PASSWORD

Idempotent: safe to run twice.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANDROID = ROOT / "android"

TARGET_SDK = "36"
AGP_VERSION = "8.9.1"
GRADLE_VERSION = "8.11.1"

VERSION_CODE = os.environ.get("ANDROID_VERSION_CODE", "5")
VERSION_NAME = os.environ.get("ANDROID_VERSION_NAME", "2.2")

failures = []


def edit(path: Path, fn):
    if not path.exists():
        failures.append(f"missing: {path.relative_to(ROOT)}")
        return
    before = path.read_text()
    after = fn(before)
    path.write_text(after)
    print(f"  patched {path.relative_to(ROOT)}")


# 1 -- SDK levels
def sdks(t: str) -> str:
    t = re.sub(r"compileSdkVersion\s*=\s*\d+", f"compileSdkVersion = {TARGET_SDK}", t)
    t = re.sub(r"targetSdkVersion\s*=\s*\d+", f"targetSdkVersion = {TARGET_SDK}", t)
    return t


edit(ANDROID / "variables.gradle", sdks)

# 2 -- Android Gradle Plugin + Gradle wrapper
edit(
    ANDROID / "build.gradle",
    lambda t: re.sub(
        r"com\.android\.tools\.build:gradle:[\d.]+",
        f"com.android.tools.build:gradle:{AGP_VERSION}",
        t,
    ),
)
edit(
    ANDROID / "gradle/wrapper/gradle-wrapper.properties",
    lambda t: re.sub(r"gradle-[\d.]+-all\.zip", f"gradle-{GRADLE_VERSION}-all.zip", t),
)

# 3 -- signing config + version, injected into app/build.gradle
SIGNING = """    signingConfigs {
        release {
            storeFile file(System.getenv("KEYSTORE_PATH"))
            storePassword System.getenv("KEYSTORE_PASSWORD")
            keyAlias System.getenv("KEY_ALIAS")
            keyPassword System.getenv("KEY_PASSWORD")
        }
    }
"""


def app_gradle(t: str) -> str:
    t = re.sub(r"versionCode\s+\d+", f"versionCode {VERSION_CODE}", t)
    t = re.sub(r'versionName\s+"[^"]*"', f'versionName "{VERSION_NAME}"', t)
    if "signingConfigs {" not in t:
        t = t.replace("    buildTypes {", SIGNING + "    buildTypes {", 1)
    if "signingConfig signingConfigs.release" not in t:
        t = t.replace(
            "        release {\n            minifyEnabled false",
            "        release {\n            signingConfig signingConfigs.release\n            minifyEnabled false",
            1,
        )
    return t


edit(ANDROID / "app/build.gradle", app_gradle)

# -- verify, loudly.
checks = {
    ANDROID / "variables.gradle": [
        f"targetSdkVersion = {TARGET_SDK}",
        f"compileSdkVersion = {TARGET_SDK}",
    ],
    ANDROID / "build.gradle": [f"com.android.tools.build:gradle:{AGP_VERSION}"],
    ANDROID / "gradle/wrapper/gradle-wrapper.properties": [f"gradle-{GRADLE_VERSION}-all.zip"],
    ANDROID / "app/build.gradle": [
        "signingConfigs {",
        "signingConfig signingConfigs.release",
        f"versionCode {VERSION_CODE}",
        f'versionName "{VERSION_NAME}"',
    ],
}

print("\nverifying:")
for path, needles in checks.items():
    text = path.read_text() if path.exists() else ""
    for needle in needles:
        if needle in text:
            print(f"  ok   {needle}")
        else:
            failures.append(f"{path.relative_to(ROOT)}: expected {needle!r}")

if failures:
    print("\nFAILED:")
    for f in failures:
        print("  " + f)
    sys.exit(1)

print("\nandroid/ patched: API %s, AGP %s, signed release, version %s (%s)"
      % (TARGET_SDK, AGP_VERSION, VERSION_NAME, VERSION_CODE))
