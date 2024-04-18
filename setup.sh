#!/usr/bin/env bash
set -e

# setup nix
if command -v nix >/dev/null; then
    echo "nix is already installed on this system."
else
    echo "Installing nix package manager"
    curl -L https://nixos.org/nix/install | sh
    source ~/.nix-profile/etc/profile.d/nix.sh
fi

# setup direnv
if command -v direnv >/dev/null; then
    echo "direnv is already installed on this system."
else
    echo "Installing direnv"
    nix-env -f '<nixpkgs>' -iA direnv nix-direnv
fi

direnv allow
