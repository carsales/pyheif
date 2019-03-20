#!/bin/bash

docker build -f docker/Dockerfile.manylinux2010 --build-arg PYPI_USERNAME --build-arg PYPI_PASSWORD .
