URL="https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2024.3.1.13/android-studio-2024.3.1.13-linux.tar.gz"
curl -I "$URL" > /dev/null
if [[ "$?" -ne "0" ]]; then
	echo "Invalid url"
	exit 1
fi
TMP_PATH="/tmp/android-studio.tar.gz"
echo "Downloading Android Studio"
curl -SL "$URL" --output "$TMP_PATH"
TARGET_PATH="$HOME/.local/share"
echo "Unpacking..."
tar -xvf "$TMP_PATH" -C "$TARGET_PATH"
echo "Running studio.sh"
bash -c "$TARGET_PATH/android-studio/bin/studio.sh"
echo "Done!"
