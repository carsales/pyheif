#!/bin/bash

pipdeptree -f --warn silence | ggrep -P '^[\w0-9\-=.]+' > requirements-dev.txt

