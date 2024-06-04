# PII Detection and Anonymiser

This is a service that helps you detect and anonymise PII.

## Prerequisites

Run `./setup.sh` to install all dependencies. This will install [direnv](https://github.com/direnv/direnv/blob/master/docs/installation.md) and [nix](https://nixos.org/download.html) then simply run `direnv allow` to install all build dependencies.

Alternatively, make sure you have [python 3.11](https://www.python.org/downloads/) and [poetry](https://python-poetry.org/docs/#installation) setup on your machine.

Also make sure tesseract is installed in the system. It is needed for detecting pii in images. Follow these steps to install tesseract [Tesseract installation](https://tesseract-ocr.github.io/tessdoc/Installation.html)

## Getting Started

To get started, run the following:

```
poetry install
poetry run python -m unittest tests/**.py
```

## Troubleshooting

There is a chance that `direnv allow` will not load the environment correctly and silently fail. This is observable when you attempt to run `poetry install`, as you will get a `command not found` error in the shell.
To fix this, you need to run the nix commands directly. Run the following:

```
nix --extra-experimental-features 'nix-command flakes' develop
```
This command will create a new Shell instance which has the Nix dependencies loaded. You will need to run commands through this prompt.

