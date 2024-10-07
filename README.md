# PII Detection and Anonymiser

This is a python app to detect and anonymise PII data using Named Entity Recognition with Flair-based Embeddings built on top of [Presidio](https://github.com/microsoft/presidio).

## Prerequisites

Run `./setup.sh` to install all dependencies. This will install [direnv](https://github.com/direnv/direnv/blob/master/docs/installation.md) and [nix](https://nixos.org/download.html) then simply run `direnv allow` to install all build dependencies.

Alternatively, make sure you have [python 3.11](https://www.python.org/downloads/) and [poetry](https://python-poetry.org/docs/#installation) setup on your machine.

## Getting Started

To get started, run the following:

```
poetry install --no-interaction --no-root
poetry run pytest
```

### Demo

You can run this as an api or using the cli. You can find the [API demo here](https://www.loom.com/share/ad8b37451ea54dcda8716cb5c6f11e94).

You can run the API using the following command:
```
poetry run python src/app.py
```

To run the cli locally, run any of the following commands:

```sh
alias pii='poetry run python src/cli.py'

# simple text analyze and anonymize
pii analyze --text "My name is Don Stark and my phone number is 212-555-5555"
pii anonymize --text "My name is Don Stark and my phone number is 212-555-5555"

# standard streams
pii analyze < sample.txt
cat sample.txt | pii analyze
cat sample.txt | pii analyze | pii anonymize
cat sample.txt | pii analyze | curl curl -X POST -H "Content-Type: application/json" --data-binary @- http://localhost:5001/anonymize
cat sample.txt | pii analyze | pii anonymize --vaulturl "http://127.0.0.1:8200" --vaultkey "orders"
cat sample.txt | pii analyze | pii anonymize --vaulturl "http://127.0.0.1:8200" --vaultkey "orders" | pii deanonymize --vaulturl "http://127.0.0.1:8200" --vaultkey "orders"

# vault integration
./vault.sh # start and configure vault server and transit secret engine keys
pii anonymize --vaulturl "http://127.0.0.1:8200" --vaultkey "orders" --text "My name is Don Stark and my phone number is 212-555-5555"

# help
pii --help
```

## Use cases

* Detecting if PII is present in any of your files, text or structured data like json, etc.
* Anonymizing/Deanonymizing PII data before sending to services like OpenAI, Anthropic, etc. for training or inference.

## Troubleshooting

There is a chance that `direnv allow` will not load the environment correctly and silently fail. This is observable when you attempt to run `poetry install`, as you will get a `command not found` error in the shell.
To fix this, you need to run the nix commands directly. Run the following:

```
nix --extra-experimental-features 'nix-command flakes' develop
```
This command will create a new Shell instance which has the Nix dependencies loaded. You will need to run commands through this prompt.
