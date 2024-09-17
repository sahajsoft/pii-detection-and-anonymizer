{
  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config.allowUnfree = true; # needed for vault
        };
        nativeBuildInputs = with pkgs; [ stdenv python311 poetry tesseract ];
        buildInputs = with pkgs; [ vault jq ];

        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
          mkPoetryApplication;
      in {
        inherit nativeBuildInputs buildInputs;

        packages = {
          myapp = mkPoetryApplication {
            projectDir = self;
            python = pkgs.python311;
          };
          default = self.packages.${system}.myapp;
        };

        devShells = {
          default = pkgs.mkShell {
            packages = nativeBuildInputs ++ buildInputs;
            LD_LIBRARY_PATH = if pkgs.stdenv.isLinux then
              "${pkgs.stdenv.cc.cc.lib}/lib:/run/opengl-driver/lib:/run/opengl-driver-32/lib"
            else
              "$LD_LIBRARY_PATH";
          };
        };
      });
}
