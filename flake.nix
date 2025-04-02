{
  description = "A simple flake for python stuff";

  inputs = {
    utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, nixpkgs, utils }: utils.lib.eachDefaultSystem (system:
    let
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
        ];

        packages = with pkgs; [
          python3
          pyright
          python313Packages.flake8
          thonny

          freecad
        ];
      };
    }
  );
}
