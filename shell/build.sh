#! /bin/bash

TARGET_NAME=$(basename $(pwd))

if [[ ! -z $1 ]]; then
    TARGET_NAME="$1"
fi

install() {
    if [[ -f "$TARGET_NAME" ]]; then
        echo "Moving '$TARGET_NAME' to '$HOME/.bin/$TARGET_NAME'"
        mv $TARGET_NAME ~/.bin/
        return 0
    fi
    return 1
}

go_build() {
    echo "[Go] Searching dependencies..."
    go mod tidy
    local MAIN_FILE="main.go"
    if [[ ! -f "main.go" ]]; then
        echo "[Go] No main.go found, searching..."
        MAIN_FILE="./cmd/main.go"
        if [[ ! -f "./cmd/main.go" ]]; then
            MAIN_FILE=$(find . -type f -name "main.go" | head -n 1)
            if [[ -z "$MAIN_FILE" ]]; then
                echo "No main.go found! Exiting..."
                return 1
            fi
        fi
        echo "[Go] Found main file in $MAIN_FILE"
    fi
    echo "[Go] Building application '$TARGET_NAME'..."
    echo "[Go] executing go build -ldflags='-s -w -extldflags \"-static\"' -o $TARGET_NAME $MAIN_FILE"
    go build -ldflags='-s -w -extldflags "-static"' -o "$TARGET_NAME" $MAIN_FILE
    return $?
}

make_build() {
    echo "[Make] Searching for configuration scripts"
    if [[ -f "configure" ]]; then
        bash ./configure
    elif [[ -f "configure.sh" ]]; then
        bash ./configure.sh
    fi
    echo "[Make] Building project..."
    echo -n "[Make] "
    make BINARY=$TARGET_NAME build
    echo "[Make] Installing..."
    echo -n "[Make] "
    make BINARY=$TARGET_NAME install
    return $?
}

build() {
    if [[ -f "go.mod" ]]; then
        go_build || exit 1
        install || exit 1
        return $?
    elif [[ -f "Makefile" ]]; then
        make_build
        return $?
    fi
    echo "No suitable build system found."
    return 1
}

build || exit 1
echo "Done!"
