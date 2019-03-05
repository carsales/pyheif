#!/bin/bash

pipdeptree -f --warn silence | grep -P '^[\w0-9\-=.]+' > requirements-dev.txt

