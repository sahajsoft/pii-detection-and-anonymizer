{
  description = "Application packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05-small";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      poetry2nix,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let

        pypkgs-build-requirements = {
          conllu = [ "setuptools" ];
          janome = [ "setuptools" ];
          pptree = [ "setuptools" ];
          confection = [ "setuptools" ];
          ftfy = [ "hatchling" ];
          segtok = [ "setuptools" ];
          wikipedia-api = [ "setuptools" ];
        };
        p2n-overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend (
          final: prev:
          builtins.mapAttrs (
            package: build-requirements:
            (builtins.getAttr package prev).overridePythonAttrs (old: {
              buildInputs =
                (old.buildInputs or [ ])
                ++ (builtins.map (
                  pkg: if builtins.isString pkg then builtins.getAttr pkg prev else pkg
                ) build-requirements);
            })
          ) pypkgs-build-requirements
        );
        myapp =
          { poetry2nix, lib }:
          poetry2nix.mkPoetryApplication {
            projectDir = self;
            overrides = p2n-overrides;
            preferWheels = false;
          };
        pkgs = import nixpkgs {
          inherit system;
          overlays = [
            poetry2nix.overlays.default
            (final: _: { myapp = final.callPackage myapp { }; })
          ];
        };
      in
      {
        packages.default = pkgs.myapp;
        devShells = {
          # Shell for app dependencies.
          #
          #     nix develop
          #
          # Use this shell for developing your app.
          default = pkgs.mkShell { inputsFrom = [ pkgs.myapp ]; };

          # Shell for poetry.
          #
          #     nix develop .#poetry
          #
          # Use this shell for changes to pyproject.toml and poetry.lock.
          poetry = pkgs.mkShell { packages = [ pkgs.poetry ]; };
        };
        legacyPackages = pkgs;
      }
    );
}
