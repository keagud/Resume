#!/bin/env python

import os, subprocess, shutil, sys
from pathlib import Path


target_filename = "resume.tex"
if len(sys.argv) > 1:
    target_filename = sys.argv[1]

target_noext, _ = os.path.splitext(target_filename)
target_path = os.path.join(os.getcwd(), target_filename)
build_dir = os.path.join(os.getcwd(), f"build")
os.makedirs(build_dir, exist_ok=True)

fonts_dir = Path("./fonts").resolve().absolute()

build_fonts_dir = Path(build_dir).joinpath("fonts")

if build_fonts_dir.exists() and build_fonts_dir.is_symlink():
    build_fonts_dir.unlink()



build_fonts_dir.symlink_to(fonts_dir, target_is_directory=True)

shutil.copy(target_path, os.path.join(build_dir, f"{target_noext}.tex"))

os.chdir(build_dir)


subprocess.run(f"xelatex {target_noext}.tex", shell=True).check_returncode()


shutil.copy(f"{target_noext}.pdf", "..")




