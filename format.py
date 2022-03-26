#!/usr/bin/env python
# -*- coding: utf-8 -*-
from glob import glob
from sys import argv
import subprocess
import os


def clang_format(dirs: tuple):
    origin = []
    for dir in dirs:
        for dirpath, dirnames, filenames in os.walk(dir):
            origin += glob(dirpath + "/*.[ch]", recursive=True)
            origin += glob(dirpath + "/*.[ch][ch]", recursive=True)
            origin += glob(dirpath + "/*.[ch][ch][ch]", recursive=True)
    result = []
    for i in range(len(origin)):
        if 'system' in origin[i]:
            continue
        result.append(origin[i].replace('\\', '/'))
    try:
        subp = subprocess.Popen(
            ['clang-format', '--verbose', '-style=file', '-i'] + result
        )
        subp.wait()
    except Exception as e:
        print(e)


def _trim_trailing_whitespace(filename: str):
    with open(filename, "r", encoding="UTF-8", errors='ignore') as f:
        text = f.read()
    while "\n\n\n\n" in text:
        text = text.replace("\n\n\n\n", "\n\n\n")
    while " \n" in text or "\t\n" in text:
        text = text.replace(" \n", '\n')
        text = text.replace("\t\n", '\n')
    while text[-1] == '\n':
        text = text[:-1]
    text += '\n'
    with open(filename, "wb") as f:
        f.write(text.encode("UTF-8"))


def trim_trailing_whitespace(dirs: tuple):
    origin = glob("*.*", recursive=True) + ["Makefile"]
    for dir in dirs:
        for dirpath, dirnames, filenames in os.walk(dir):
            origin += glob(dirpath + "/*.*", recursive=True)
    for file in origin:
        _trim_trailing_whitespace(file.replace('\\', '/'))


dirs = set()
if os.path.exists("Inc"):
    dirs.add("Inc")
if os.path.exists("Src"):
    dirs.add("Src")
if os.path.exists("Core"):
    dirs.add("Core")
for dir in argv[1:]:
    if os.path.exists(dir):
        dirs.add(dir)
clang_format(tuple(dirs))
if os.path.exists("Drivers"):
    dirs.add("Drivers")
trim_trailing_whitespace(tuple(dirs))
