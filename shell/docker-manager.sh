#! /bin/bash

NAME="$0"
ACTION="$1"

disable() {
    systemctl status docker.service | grep running
    IS_DOCKER_ENABLED="$?"

    if [[ "$IS_DOCKER_ENABLED" == "0" ]]; then
        echo "Disabling Docker..."
        systemctl disable --now docker.service
        systemctl disable --now containerd.service
        systemctl disable --now docker.socket

        echo "Docker is now disabled"
    fi
}

enable() {

    systemctl status docker.service | grep running
    IS_DOCKER_ENABLED="$?"


    if [[ "$IS_DOCKER_ENABLED" == "1" ]]; then
        echo "Enabling Docker..."
        systemctl enable --now docker.service
        systemctl enable --now containerd.service
        systemctl enable --now docker.socket
        echo "Docker is now enabled"
    fi

}


if [[ -z $ACTION ]]; then
    echo "Usage: $NAME [up/down]"
    exit 1
fi

if [[ "$ACTION" == "up" ]]; then
    enable
elif [[ "$ACTION" == "down" ]]; then
    disable
else
    echo "Usage: $NAME [up/down]"
    exit 1
fi

