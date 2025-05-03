VERSION="3.29.2"
if [[ ! -z $1 ]]; then
	VERSION="$1"
fi 
TAR_FILE="/tmp/flutter_linux_$VERSION.tar.xz"
FLUTTER_STABLE_URL="https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_$VERSION-stable.tar.xz"
TARGET_PATH="$HOME/.local/share/"
mkdir -p $TARGET_PATH

curl -I -sSL "$FLUTTER_STABLE_URL" > /dev/null
if [[ "$?" -ne "0" ]]; then
	echo "Release $VERSION-stable not found!"
	exit 1
fi

echo "Downloading Flutter $VERSION-stable"
if [[ ! -f "$TAR_FILE" ]]; then
	curl -SL "$FLUTTER_STABLE_URL" --output "$TAR_FILE"
fi
echo "Extracting to $TARGET_PATH"
tar -xvf "$TAR_FILE" -C "$TARGET_PATH"

echo "Exporting binaries to PATH"
USER_SHELL=$(basename $SHELL)
if [[ "$USER_SHELL" -eq "bash" ]]; then
	echo 'export PATH="$TARGET_PATH/flutter/bin:$PATH"' >> ~/.bash_profile
fi

if [[ "$USER_SHELL" -eq "zsh" ]]; then
	echo 'export PATH="$TARGET_PATH/flutter/bin:$PATH"' >> ~/.zshenv
fi

if [[ "$USER_SHELL" -eq "fish" ]]; then
	fish -c "fish_add_path -g -p $TARGET_PATH/flutter/bin"
fi

if [[ "$USER_SHELL" -eq "ksh" ]]; then
	echo 'export PATH="$TARGET_PATH/flutter/bin:$PATH"' >> ~/.profile
fi

echo "Done! As a next step, run \`flutter doctor\`"

