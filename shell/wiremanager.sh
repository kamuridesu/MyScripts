#! /bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

CONF_PATH="/etc/wireguard"
DEFAULT_CONF="$CONF_PATH/wg0.conf"

get_all_confs() {
    echo "$(ls $CONF_PATH)"
}

get_random_config() {
    local prefix="$1"
    local confs="$(get_all_confs)"
    echo $(echo "$confs" | grep "$prefix" | shuf -n 1)
}

iface_up() {
    local name="$1"
    echo "Enabling interface $name"
    if [[ -L "$DEFAULT_CONF" ]]; then
        echo "Found exiting default config, removing"
        rm "$DEFAULT_CONF"
    fi
    echo "$name" | grep ".conf" 2>&1 > /dev/null
    if [[ "$?" != "0" ]]; then
        name="$name.conf"
    fi
    local new_conf="$CONF_PATH/$name"
    if [[ ! -f "$new_conf" ]]; then
        echo "No interface with name $name found, looked at path $new_conf"
        exit 1
    fi
    ln -s "$CONF_PATH/$name" "$DEFAULT_CONF"
    systemctl start wg-quick@wg0 || exit 1
    journalctl -u wg-quick@wg0 | tail -n 20
}

iface_down() {
    echo "Disabling wireguard"
    systemctl stop wg-quick@wg0.service
    journalctl -u wg-quick@wg0 | tail -n 5
}

usage() {
    echo "usage: $0 [-r] [-i interface] {up,down}" 1>&2
}

usage_and_exit() {
    usage
    exit 1
}

random=false
interface=""
action=""
while getopts ":ri:" opt "$@"; do
    case ${opt} in
        r )
            random=true
            ;;
        i )
            interface=$OPTARG
            ;;
        \? )
            usage_and_exit
            ;;
        : )
            usage_and_exit
            ;;
    esac
done

shift $((OPTIND - 1))


if [[ "$1" != "up" && "$1" != "down" ]]; then
    echo "Error: Action must be either 'up' or 'down'" >&2
    exit 1
fi

action="$1"

if [[ "$action" == "down" ]]; then
    iface_down
    exit 0
fi

if [[ -z "$interface" && action != "down" ]]; then
    echo "Error: -i <interface> is required" >&2
    exit 1
fi

selected_interface="$interface"
if [[ "$random" == true ]]; then
    selected_interface=$(get_random_config "$interface")
fi

if [[ "$action" == "up" ]]; then
    iface_down
    iface_up $selected_interface
fi

