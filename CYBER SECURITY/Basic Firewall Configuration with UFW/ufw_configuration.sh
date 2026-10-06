#!/usr/bin/env bash
set -Eeuo pipefail

readonly REQUIRED_CONFIRMATION="APPLY"

fail() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

if [[ "${EUID}" -ne 0 ]]; then
    fail "Run with sudo: sudo bash ufw_configuration.sh"
fi

if [[ ! -r /etc/os-release ]]; then
    fail "Cannot identify this Linux distribution (/etc/os-release is unavailable)."
fi

# shellcheck disable=SC1091
source /etc/os-release
case "${ID:-}" in
    ubuntu|debian|kali)
        ;;
    *)
        fail "This script supports Ubuntu, Debian, and Kali Linux only (detected: ${ID:-unknown})."
        ;;
esac

command -v apt-get >/dev/null 2>&1 || fail "apt-get is required to install UFW."

if [[ -n "${SSH_CONNECTION:-}" ]]; then
    read -r _ _ _ ssh_local_port <<< "${SSH_CONNECTION}"
    if [[ "${ssh_local_port:-}" != "22" ]]; then
        fail "The current SSH session is not on TCP/22. Use the VM console or adapt the SSH rule before continuing."
    fi
fi

cat <<'WARNING'
This will change the firewall on THIS Linux machine:
  Default incoming: deny
  Default outgoing: allow
  Allow incoming TCP/22 (SSH)
  Deny incoming TCP/80 (HTTP)
  Allow incoming TCP/443 (HTTPS)
  Deny incoming TCP/3306 (MySQL)

Existing UFW rules are not reset, but the default policies will be changed.
Do not continue over a remote session unless you have verified the SSH port
and have console access in case connectivity is interrupted.
WARNING

read -r -p "Type APPLY to continue: " confirmation
[[ "${confirmation}" == "${REQUIRED_CONFIRMATION}" ]] || fail "Confirmation did not match. No firewall changes were made."

if ! command -v ufw >/dev/null 2>&1; then
    printf 'UFW is not installed; installing it with apt-get...\n'
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y ufw
fi

command -v ufw >/dev/null 2>&1 || fail "UFW installation did not provide the ufw command."

printf '\nCurrent UFW rules (review before proceeding):\n'
ufw status numbered
read -r -p "Type APPLY RULES to apply this configuration: " rules_confirmation
[[ "${rules_confirmation}" == "APPLY RULES" ]] || fail "Confirmation did not match. No firewall rules were changed."

printf 'Applying default firewall policies...\n'
ufw default deny incoming
ufw default allow outgoing

printf 'Applying inbound service rules...\n'
ufw allow 22/tcp comment 'Allow SSH administration'
ufw deny 80/tcp comment 'Block unencrypted HTTP'
ufw allow 443/tcp comment 'Allow HTTPS'
ufw deny 3306/tcp comment 'Block direct MySQL access'

printf 'Enabling UFW...\n'
ufw --force enable

printf '\nFinal firewall status:\n'
ufw status verbose
