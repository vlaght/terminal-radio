{ lib
, python3
, ffmpeg
, portaudio
, mkPoetryApplication
, defaultPoetryOverrides
}:

mkPoetryApplication {
  projectDir = ./.;
  python = python3;
  preferWheels = true;
  documentationDirectory = false;

  overrides = defaultPoetryOverrides.extend (final: prev: {
    sounddevice = prev.sounddevice.overridePythonAttrs (old: {
      buildInputs = (old.buildInputs or [ ]) ++ [
        final.setuptools
        portaudio
      ];
      nativeBuildInputs = (old.nativeBuildInputs or []) ++ [ portaudio ];
      preBuild = ''
        export PORTAUDIO_PATH="${portaudio}"
      '';
    });
  });

  doCheck = false;

  makeWrapperArgs = [
    "--prefix" "PATH" ":" "${lib.makeBinPath [ ffmpeg ]}"
    "--prefix" "LD_LIBRARY_PATH" ":" "${lib.makeLibraryPath [ portaudio ]}"
    "--prefix" "DYLD_LIBRARY_PATH" ":" "${lib.makeLibraryPath [ portaudio ]}"
  ];

  propagatedBuildInputs = [
    ffmpeg
    portaudio
  ];

  meta = with lib; {
    description = "A terminal-based internet radio player";
    homepage = "https://github.com/vlaght/terminal-radio";
    license = licenses.mit;
    maintainers = with maintainers; [ vlaght ];
    platforms = platforms.all;
  };
}
