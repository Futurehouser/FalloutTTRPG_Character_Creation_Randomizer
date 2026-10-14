#!/usr/bin/env bash
# Builds and signs WastelandRecruit.apk with the Android SDK build tools (no Gradle needed).
# Works in Git Bash on Windows and on Linux (the GitHub Action).
#
# Signing key (never stored in the repository), taken from the first that exists:
#   1. environment variables WR_KEYSTORE (path to .jks) and WR_KS_PASS (its password)
#   2. ~/.wasteland-recruit/signing.properties  with lines  KEYSTORE=...  and  KS_PASS=...
set -euo pipefail
cd "$(dirname "$0")"

SDK="${ANDROID_HOME:-${LOCALAPPDATA:-}/Android/Sdk}"
BT="$SDK/build-tools/34.0.0"
JAR="$SDK/platforms/android-34/android.jar"
PY="${PYTHON:-python}"
OUT=build
# the build tools are .bat/.exe on Windows and plain files on Linux
tool() { for t in "$BT/$1.bat" "$BT/$1.exe" "$BT/$1"; do [ -f "$t" ] && { echo "$t"; return; }; done; echo "missing build tool: $1" >&2; exit 1; }

# version from web/version.js: "4.1.2" -> versionCode 40102
VERSION=$(sed -n 's/^const APP_VERSION = "\([0-9.]*\)".*/\1/p' ../web/version.js)
IFS=. read -r MA MI PA <<< "$VERSION"
CODE=$(( ${MA:-0} * 10000 + ${MI:-0} * 100 + ${PA:-0} ))
echo "Wasteland Recruit $VERSION (versionCode $CODE)"

if [ -z "${WR_KEYSTORE:-}" ] || [ -z "${WR_KS_PASS:-}" ]; then
    PROPS="$HOME/.wasteland-recruit/signing.properties"
    [ -f "$PROPS" ] || { echo "No signing key: set WR_KEYSTORE/WR_KS_PASS or create $PROPS" >&2; exit 1; }
    WR_KEYSTORE=$(sed -n 's/^KEYSTORE=//p' "$PROPS" | tr -d '\r')
    WR_KS_PASS=$(sed -n 's/^KS_PASS=//p' "$PROPS" | tr -d '\r')
fi
export WR_KS_PASS

rm -rf "$OUT" && mkdir -p "$OUT/res" "$OUT/gen" "$OUT/classes" "$OUT/dex"

echo "0/6 copying the shared web app (../web) into the assets"
rm -rf app/assets/www && mkdir -p app/assets && cp -r ../web app/assets/www

echo "1/6 compiling resources"
"$(tool aapt2)" compile --dir app/res -o "$OUT/res/res.zip"

echo "2/6 linking manifest, resources and web assets"
"$(tool aapt2)" link -o "$OUT/base.apk" -I "$JAR" --manifest app/AndroidManifest.xml \
    --version-code "$CODE" --version-name "$VERSION" --replace-version \
    -A app/assets --java "$OUT/gen" "$OUT/res/res.zip" --auto-add-overlay

echo "3/6 compiling Java"
javac -nowarn -source 11 -target 11 -encoding UTF-8 -classpath "$JAR" -d "$OUT/classes" \
    $(find app/src "$OUT/gen" -name '*.java') 2>&1 | grep -v "bootstrap classpath" || true

echo "4/6 converting to dex"
"$(tool d8)" --release --lib "$JAR" --min-api 26 --output "$OUT/dex" $(find "$OUT/classes" -name '*.class')

echo "5/6 packaging"
"$PY" - "$OUT/base.apk" "$OUT/dex/classes.dex" "$OUT/unsigned.apk" <<'EOF'
import sys, zipfile
base, dex, out = sys.argv[1:]
# rewrite the archive cleanly; resources.arsc must stay uncompressed for Android 11+
with zipfile.ZipFile(base) as src, zipfile.ZipFile(out, "w") as dst:
    for info in src.infolist():
        ct = zipfile.ZIP_STORED if info.filename == "resources.arsc" else info.compress_type
        dst.writestr(zipfile.ZipInfo(info.filename, info.date_time), src.read(info.filename), compress_type=ct)
    dst.write(dex, "classes.dex", compress_type=zipfile.ZIP_DEFLATED)
EOF
"$(tool zipalign)" -f -p 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"

echo "6/6 signing"
"$(tool apksigner)" sign --ks "$WR_KEYSTORE" --ks-pass env:WR_KS_PASS --key-pass env:WR_KS_PASS \
    --out WastelandRecruit.apk "$OUT/aligned.apk"
rm -f WastelandRecruit.apk.idsig
"$(tool apksigner)" verify WastelandRecruit.apk && echo "Built: $(pwd)/WastelandRecruit.apk"
