#!/bin/env python

import os, subprocess, shutil, sys


target_filename = "resume.tex"
if len(sys.argv) > 1:
    target_filename = sys.argv[1]

target_noext, _ = os.path.splitext(target_filename)
target_path = os.path.join(os.getcwd(), target_filename)
build_dir = os.path.join(os.getcwd(), f"build")
os.makedirs(build_dir, exist_ok=True)

shutil.copy(target_path, os.path.join(build_dir, f"{target_noext}.tex"))
os.chdir(build_dir)

subprocess.run(f"xelatex {target_noext}.tex", shell=True)
