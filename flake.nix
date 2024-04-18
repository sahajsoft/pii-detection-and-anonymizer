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
        nativeBuildInputs = with pkgs; [ stdenv python3 poetry ];
        buildInputs = with pkgs; [ ];

        # see https://github.com/nix-community/poetry2nix/tree/master#api for more functions and examples.
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; })
          mkPoetryApplication;
      in {
        inherit nativeBuildInputs buildInputs;

        packages = {
          myapp = mkPoetryApplication {
            projectDir = self;
            python = pkgs.python3;
          };
          default = self.packages.${system}.myapp;
        };

        devShells = {
          default = pkgs.mkShell {
            packages = nativeBuildInputs ++ buildInputs;
            LD_LIBRARY_PATH = if pkgs.stdenv.isLinux then
              "${pkgs.stdenv.cc.cc.lib}/lib:/run/opengl-driver/lib:/run/opengl-driver-32/lib:${pkgs.libGL}/lib:/nix/store/2if9iy5cy0bicwafllpa2aiq30v26app-glib-2.78.1/lib"
            else
              "$LD_LIBRARY_PATH";
          };
          CI = pkgs.mkShell {
            packages = nativeBuildInputs ++ buildInputs ++ [ pkgs.nodejs_20 ];
          };
        };
      });
}
