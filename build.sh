#!/bin/bash

echo "Pypi password for $PYPI_USERNAME: "
read -s password

docker build -f docker/Dockerfile.manylinux2014 --build-arg PYPI_USERNAME --build-arg PYPI_PASSWORD=$password .

