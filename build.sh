#!/bin/bash

docker build -f docker/Dockerfile.manylinux2014 --build-arg PYPI_USERNAME --build-arg PYPI_PASSWORD .
