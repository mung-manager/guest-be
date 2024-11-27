#!/bin/bash

OPTIONS=("local" "test" "dev" "prod")

echo "Which settings would you like to run?"
PS3="Please select the desired number: "

select opt in "${OPTIONS[@]}"
do
    case $opt in
        "local")
            ENVIRONMENT="config.django.local"
            break
            ;;
        "test")
            ENVIRONMENT="config.django.test"
            break
            ;;
        "dev")
            ENVIRONMENT="config.django.dev"
            break
            ;;
        "prod")
            ENVIRONMENT="config.django.prod"
            break
            ;;
        *) echo "Invalid option. Please try again.";;
    esac
done

echo "Setting DJANGO_SETTINGS_MODULE to $ENVIRONMENT"

export DJANGO_SETTINGS_MODULE=$ENVIRONMENT

sudo docker-compose up --build -d
