{
  description = "Artist Playist";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {inherit system;};

        pythonEnv = pkgs.python3.withPackages (ps:
          with ps; [
            spotipy
            python-dotenv
          ]);

        spotify-script = pkgs.writeShellApplication {
          name = "run-spotify-script";
          runtimeInputs = [pythonEnv];
          text = ''
            python "${./main.py}" "$@"
          '';
        };
      in {
        packages.default = spotify-script;

        apps.default = {
          type = "app";
          program = "${spotify-script}/bin/run-spotify-script";
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [pythonEnv];
        };
      }
    );
}
