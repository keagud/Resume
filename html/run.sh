#!/bin/bash

prettier . --write &&\
../.venv/bin/python3 build_html.py
