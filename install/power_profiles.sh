#!/usr/bin/env bash
set -euo pipefail

resolve_script_path() {
  if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    printf '%s\n' "${BASH_SOURCE[0]}"
    return 0
  fi

  if [[ -n "${ZSH_VERSION:-}" ]]; then
    eval 'printf "%s\n" "${(%):-%x}"'
    return 0
  fi

  return 1
}

script_path="$(resolve_script_path)"
script_dir="$(cd -- "$(dirname -- "$script_path")" && pwd)"
assets_dir="$script_dir/assets"

if [[ ! -d "$assets_dir" ]]; then
  printf 'power_profiles.sh: assets directory not found: %s\n' "$assets_dir" >&2
  exit 1
fi

echo "================================"
echo "     Power Profile Setup        "
echo "================================"

sudo install -Dm755 "$assets_dir/power-profile-apply" /usr/local/libexec/power-profile-apply
sudo install -Dm644 "$assets_dir/power-profile-restore.service" /etc/systemd/system/power-profile-restore.service
sudo install -Dm440 "$assets_dir/power-profile.sudoers" /etc/sudoers.d/power-profile
sudo install -d -m755 /var/lib/power-profile

if ! sudo test -f /var/lib/power-profile/current; then
  printf 'balanced\n' | sudo tee /var/lib/power-profile/current >/dev/null
fi

sudo systemctl daemon-reload
sudo systemctl enable power-profile-restore.service
sudo /usr/local/libexec/power-profile-apply restore

echo "Power profile helper installed."
