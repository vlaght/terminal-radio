{
  description = "A terminal-based internet radio player";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        p2nix = poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
      in
      {
        packages.default = pkgs.callPackage ./default.nix {
          inherit (p2nix) mkPoetryApplication defaultPoetryOverrides;
          python3 = pkgs.python310;
          ffmpeg = pkgs.ffmpeg;
          portaudio = pkgs.portaudio;
        };

        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python310
            poetry
            ffmpeg
            portaudio
          ];

          shellHook = ''
            export PYTHONPATH=${pkgs.python310}/lib/python3.10/site-packages:$PYTHONPATH
            export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [ pkgs.portaudio ]}:$LD_LIBRARY_PATH
            export DYLD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [ pkgs.portaudio ]}:$DYLD_LIBRARY_PATH
            echo "Development environment ready!"
          '';
        };
      }
    );
}
