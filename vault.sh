#!/usr/bin/env bash
set -euo pipefail

export VAULT_ADDR="http://127.0.0.1:8200"
export VAULT_TOKEN=root
# Start vault server locally

function vault_running() {
    curl --output /dev/null --silent --head --fail $VAULT_ADDR
}

function start_vault() {
    if vault_running
    then
        echo 'Vault already running'
    else
        echo 'Starting vault'
        vault server -dev -dev-root-token-id $VAULT_TOKEN &

        until vault_running; do
            echo "Waiting for vault server to start"
            sleep 2
        done
    fi
}

function status_vault() {
    if vault_running
    then
        echo 'Vault is running'
    else
        echo 'Vault is not running'
    fi
}

function stop_vault() {
    if vault_running
    then
        echo 'Stopping vault'
        pgrep -f vault | xargs kill
    else
        echo 'Vault not running'
    fi
}

function configure_transits() {
    curl --output /dev/null \
         --silent \
         --header "X-Vault-Token: $VAULT_TOKEN" \
         --request POST \
         --data '{"type":"transit"}' \
         $VAULT_ADDR/v1/sys/mounts/transit
    curl --output /dev/null \
         --silent \
         --header "X-Vault-Token: $VAULT_TOKEN" \
         --request POST \
         $VAULT_ADDR/v1/transit/keys/orders

    curl --output /dev/null \
         --silent \
         --header "X-Vault-Token: $VAULT_TOKEN" \
         --request PUT \
         --data '{"policy": "path \"transit/encrypt/orders\" {\n   capabilities = [ \"update\" ]\n}\n\npath \"transit/decrypt/orders\" {\n   capabilities = [ \"update\" ]\n}\n"}' \
         $VAULT_ADDR/v1/sys/policies/acl/app-orders
}

function create_token() {
    configure_transits

    export APP_ORDER_TOKEN=$(curl --silent \
                                  --header "X-Vault-Token: $VAULT_TOKEN" \
                                  --request POST  \
                                  --data '{ "policies": ["app-orders"] }' \
                                  $VAULT_ADDR/v1/auth/token/create | jq -r '.auth | .client_token')

    echo "export APP_ORDER_TOKEN=$APP_ORDER_TOKEN"
}

if [ $# == 0 ]; then
    echo 'Setting up everything'
    start_vault
    create_token
elif [ $1 = 'start' ]; then
    start_vault
elif [ $1 = 'status' ]; then
    status_vault
elif [ $1 = 'stop' ]; then
    stop_vault
elif [ $1 = 'token' ]; then
    create_token
fi
