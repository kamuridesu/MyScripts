#! /bin/bash

TARGET_NAME=$(basename $(pwd))

if [[ ! -z $1 ]]; then
    TARGET_NAME="$1"
fi

go_build() {
    echo "[Go] Searching dependencies..."
    go mod tidy
    echo "[Go] Building application '$TARGET_NAME'..."
    echo "[Go] executing go build -ldflags='-s -w -extldflags \"-static\"' -o $TARGET_NAME"
    go build -ldflags='-s -w -extldflags "-static"' -o "$TARGET_NAME"
}

install() {
    if [[ -f "$TARGET_NAME" ]]; then
        echo "Moving '$TARGET_NAME' to '$HOME/.bin/$TARGET_NAME'"
        mv $TARGET_NAME ~/.bin/
        return 0
    fi
    return 1
}

build() {
    if [[ -f "go.mod" ]]; then
        go_build
        return 0
    fi
    echo "No suitable build system found."
    return 1
}

build || exit 1
install || exit 1
echo "Done!"
