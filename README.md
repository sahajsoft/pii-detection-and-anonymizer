# PII Detection and Anonymiser

This is a python app to detect and anonymise PII data using Named Entity Recognition with Flair-based Embeddings built on top of [Presidio](https://github.com/microsoft/presidio).

## Getting Started

You can use docker to install the app (follow instructions
[here](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry#authenticating-to-the-container-registry)
to authenticate):

```sh
docker pull ghcr.io/sahajsoft/pii
```

To use, it's best to add an alias:

```sh
alias pii=docker run --rm -i ghcr.io/sahajsoft/pii
```

Then you can use `pii` as found below in sample commands.

## Usage

To run the CLI locally, run any of the following commands:

```sh
# alias for easier calls
alias pii='poetry run python -m pii_detection_and_anonymizer'
# alias for docker
alias pii=docker run --rm -i ghcr.io/sahajsoft/pii

# text
echo "My name is Don Stark and my phone number is 212-555-5555" | pii analyze
echo "My name is Don Stark and my phone number is 212-555-5555" | pii analyze | pii anonymize

# text files
pii analyze < sample.txt
cat sample.txt | pii analyze
cat sample.txt | pii analyze | pii anonymize
cat sample.txt | pii analyze | curl curl -X POST -H "Content-Type: application/json" --data-binary @- http://localhost:5001/anonymize
cat sample.txt | pii analyze | pii anonymize --vaulturl "http://127.0.0.1:8200" --vaultkey "orders"
cat sample.txt | pii analyze | pii anonymize --vaulturl "http://127.0.0.1:8200" --vaultkey "orders" | pii deanonymize --vaulturl "http://127.0.0.1:8200" --vaultkey "orders"

# csv files
cat sample.csv | pii analyze --csv
cat sample.csv | pii analyze --csv | pii anonymize
cat sample.csv | pii analyze --csv | pii anonymize | jq -r '.text'
cat sample.csv | pii analyze --csv | pii anonymize | jq -r '.text' > anonymized.csv

# vault integration
./vault.sh # start and configure vault server and transit secret engine keys
echo "My name is Don Stark and my phone number is 212-555-5555" | pii anonymize --vaulturl "http://127.0.0.1:8200" --vaultkey "orders"

# help
pii --help
```

## Use cases

* Detecting if PII is present in any of your files, text or structured data like json, etc.
* Anonymizing/Deanonymizing PII data before sending to services like OpenAI, Anthropic, etc. for training or inference.

## Development

### Prerequisites

Run `./setup.sh` to install all dependencies. This will install [direnv](https://github.com/direnv/direnv/blob/master/docs/installation.md) and [nix](https://nixos.org/download.html) then simply run `direnv allow` to install all build dependencies.

Alternatively, make sure you have [python 3.11](https://www.python.org/downloads/) and [poetry](https://python-poetry.org/docs/#installation) setup on your machine.

### Running the app

To get started, run the following:

```
poetry install --no-interaction --no-root
poetry run pytest
```

### Troubleshooting

There is a chance that `direnv allow` will not load the environment correctly and silently fail. This is observable when you attempt to run `poetry install`, as you will get a `command not found` error in the shell.
To fix this, you need to run the nix commands directly. Run the following:

```
nix --extra-experimental-features 'nix-command flakes' develop
```
This command will create a new Shell instance which has the Nix dependencies loaded. You will need to run commands through this prompt.
