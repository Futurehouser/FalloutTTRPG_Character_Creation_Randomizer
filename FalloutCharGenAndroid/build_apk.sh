#!/usr/bin/env bash
# Builds and signs WastelandRecruit.apk with the Android SDK build tools (no Gradle needed).
# Run from Git Bash:  bash build_apk.sh
set -euo pipefail
cd "$(dirname "$0")"

SDK="${ANDROID_HOME:-$LOCALAPPDATA/Android/Sdk}"
BT="$SDK/build-tools/34.0.0"
JAR="$SDK/platforms/android-34/android.jar"
OUT=build
rm -rf "$OUT" && mkdir -p "$OUT/res" "$OUT/gen" "$OUT/classes" "$OUT/dex"

echo "1/6 compiling resources"
"$BT/aapt2" compile --dir app/res -o "$OUT/res/res.zip"

echo "2/6 linking manifest, resources and web assets"
"$BT/aapt2" link -o "$OUT/base.apk" -I "$JAR" --manifest app/AndroidManifest.xml \
    -A app/assets --java "$OUT/gen" "$OUT/res/res.zip" --auto-add-overlay

echo "3/6 compiling Java"
javac -nowarn -source 11 -target 11 -encoding UTF-8 -classpath "$JAR" -d "$OUT/classes" \
    $(find app/src "$OUT/gen" -name '*.java') 2>&1 | grep -v "bootstrap classpath" || true

echo "4/6 converting to dex"
"$BT/d8.bat" --release --lib "$JAR" --min-api 26 --output "$OUT/dex" $(find "$OUT/classes" -name '*.class')

echo "5/6 packaging"
python - "$OUT/base.apk" "$OUT/dex/classes.dex" "$OUT/unsigned.apk" <<'EOF'
import sys, zipfile
base, dex, out = sys.argv[1:]
# rewrite the archive cleanly; resources.arsc must stay uncompressed for Android 11+
with zipfile.ZipFile(base) as src, zipfile.ZipFile(out, "w") as dst:
    for info in src.infolist():
        ct = zipfile.ZIP_STORED if info.filename == "resources.arsc" else info.compress_type
        dst.writestr(zipfile.ZipInfo(info.filename, info.date_time), src.read(info.filename), compress_type=ct)
    dst.write(dex, "classes.dex", compress_type=zipfile.ZIP_DEFLATED)
EOF
"$BT/zipalign.exe" -f -p 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"

echo "6/6 signing"
KS=keystore/wasteland.jks
if [ ! -f "$KS" ]; then
    mkdir -p keystore
    keytool -genkeypair -keystore "$KS" -alias wasteland -keyalg RSA -keysize 2048 -validity 10000 \
        -storepass wasteland -keypass wasteland -dname "CN=Wasteland Recruit, O=Personal" >/dev/null 2>&1
fi
"$BT/apksigner.bat" sign --ks "$KS" --ks-pass pass:wasteland --key-pass pass:wasteland \
    --out WastelandRecruit.apk "$OUT/aligned.apk"
"$BT/apksigner.bat" verify WastelandRecruit.apk && echo "Built: $(pwd)/WastelandRecruit.apk"
