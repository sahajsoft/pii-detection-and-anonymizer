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
          presidio-vault = [ "poetry" ];
          safetensors = [ "maturin" ];
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
            preferWheels = true;
          };
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true;
          overlays = [
            poetry2nix.overlays.default
            (final: _: { myapp = final.callPackage myapp { }; })
          ];
        };
        # build docker using nix to have smaller images. Inspiration from
        # https://lucabrunox.github.io/2016/04/cheap-docker-images-with-nix_15.html
        buildImage = pkgs.dockerTools.buildLayeredImage {
          name = "pii";
          tag = "latest";
          created = "now";
          config.Entrypoint = [ "${pkgs.myapp}/bin/cli" ];
        };
      in
      {
        packages.default = pkgs.myapp;
        packages.dockerImage = buildImage;

        apps.default = {
          type = "app";
          program = "${pkgs.myapp}/bin/cli";
        };

        devShells = {
          # Shell for app dependencies.
          #
          #     nix develop
          #
          # Use this shell for developing your app.
          default = pkgs.mkShell {
            inputsFrom = [ pkgs.myapp ];
            packages = [
              pkgs.docker
              pkgs.jq
              pkgs.vault
            ];
          };

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
