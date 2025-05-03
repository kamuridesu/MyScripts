#! /bin/bash

if [[ -z "$1" ]]; then
    echo "Missing username"
    exit 1
fi

ACTION="$2"

USER_ID=$(id -u "$1")

setup() {
    iptables -N USER_RESTRICT
    iptables -A OUTPUT -m owner --uid-owner $USER_ID -j USER_RESTRICT
    iptables -A USER_RESTRICT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    iptables -A USER_RESTRICT -o lo -j ACCEPT
    iptables -A USER_RESTRICT -o wg0 -j ACCEPT
    iptables -A USER_RESTRICT -j DROP

    ip6tables -N USER_RESTRICT_V6
    ip6tables -A OUTPUT -m owner --uid-owner $USER_ID -j USER_RESTRICT_V6
    ip6tables -A USER_RESTRICT_V6 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    ip6tables -A USER_RESTRICT_V6 -o lo -j ACCEPT
    ip6tables -A USER_RESTRICT_V6 -o wg0 -j ACCEPT
    ip6tables -A USER_RESTRICT_V6 -p udp --dport 53 -j ACCEPT
    ip6tables -A USER_RESTRICT_V6 -p tcp --dport 53 -j ACCEPT
    ip6tables -A USER_RESTRICT_V6 -j DROP
    iptables-save -f /etc/iptables/iptables.rules
    ip6tables-save -f /etc/iptables/ip6tables.rules
    systemctl restart iptables
}

delete() {
    iptables -D OUTPUT -m owner --uid-owner $USER_ID -j USER_RESTRICT
    iptables -F USER_RESTRICT
    iptables -X USER_RESTRICT
    ip6tables -D OUTPUT -m owner --uid-owner $USER_ID -j USER_RESTRICT_V6
    ip6tables -F USER_RESTRICT_V6
    ip6tables -X USER_RESTRICT_V6
    
    iptables-save -f /etc/iptables/iptables.rules
    ip6tables-save -f /etc/iptables/ip6tables.rules
  
    systemctl restart iptables
}

if [[ ! -z "$ACTION" ]]; then
    if [[ "$ACTION" == "setup" ]]; then
        setup || exit 1
        exit 0
    fi
fi
delete

