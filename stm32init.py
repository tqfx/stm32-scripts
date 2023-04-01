#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, glob, json, argparse, subprocess

# Target configuration directory
tgt = ".vscode"
# Source configuration directory
vsc = "stm32init"

parser = argparse.ArgumentParser()
parser.add_argument("-W", action="append", nargs="*", default=[])
parser.add_argument("--indent", type=int, default=4)
args = parser.parse_known_args()


def findtool(tool):
    if "win" in sys.platform:
        find = "where"
    elif "linux" in sys.platform:
        find = "which"
    else:
        raise SystemError
    subp = subprocess.Popen(
        [find, tool], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="UTF-8"
    )
    subp.wait()
    return subp.stdout.read().split()


def dealdir(dirname):
    '''
    Add delimiter

    Args:
        dirname: The path to process
    Returns:
        The path after being processed
    '''

    if dirname[-1] not in ("/", "\\"):
        dirname += "/"
    return dirname


# Get the current path
cwd = os.getcwd().replace("\\", "/")
# Get the path to the execution file
pwd = os.path.split(os.path.relpath(sys.argv[0]))[0].replace("\\", "/")

# Add delimiter
pwd = dealdir(pwd)
cwd = dealdir(cwd)
vsc = dealdir(vsc)
tgt = dealdir(tgt)


def launch(filename="launch.json"):
    '''
    Set launch.json
    '''

    with open(pwd + vsc + filename, "r", encoding="UTF-8") as f:
        root = json.load(f)
    prop = root["configurations"][0]
    config = prop["configFiles"][0]

    # Get project name and set .elf name
    iocs = glob.glob(r"{}*.ioc".format(cwd))
    if iocs:
        f = open(iocs[0], "r", encoding="UTF-8")
        texts = f.read().split("\n")
        f.close()
        for text in texts:
            if "ProjectName" in text:
                prop["executable"] = "build/%s.elf" % text.split("=")[-1]
                break
    else:
        sys.stderr.write("missing *.ioc\n")

    # Get the configuration file for the directory where the execution file resides and set .cfg name
    for path in (cwd, pwd + "../", pwd):
        cfgs = glob.glob(r"{}*.cfg".format(path))
        if cfgs:
            config = os.path.relpath(cfgs[0]).replace("\\", "/")
            sys.stdout.write("config: %s\n" % config)
            break
        if path == pwd:
            sys.stderr.write("missing *.cfg\n")

    prop["configFiles"] = [config]
    with open(cwd + tgt + filename, "w", encoding="UTF-8") as f:
        json.dump(root, f, ensure_ascii=True, indent=args[0].indent)

    return config


def tasks(filename="tasks.json"):
    '''
    Set tasks.json
    '''

    with open(pwd + vsc + filename, "r", encoding="UTF-8") as f:
        root = json.load(f)

    with open(cwd + tgt + filename, "w", encoding="UTF-8") as f:
        json.dump(root, f, ensure_ascii=True, indent=args[0].indent)


def c_cpp_properties(filename="c_cpp_properties.json"):
    '''
    Set c_cpp_properties.json
    '''

    with open(pwd + vsc + filename, "r", encoding="UTF-8") as f:
        root = json.load(f)

    prop = root["configurations"][0]
    tools = findtool("arm-none-eabi-gcc")
    if [] != tools:
        prop["compilerPath"] = tools[0].replace("\\", "/")
        sys.stdout.write("tool: %s\n" % prop["compilerPath"])
    else:
        sys.stderr.write("missing arm-none-eabi-gcc\n")

    # Set STM32 MCU macro
    try:
        asms = glob.glob(r"{}startup*.s".format(cwd))
        asm = os.path.split(asms[0])[-1]
        sys.stdout.write("start: %s\n" % asm)
        mcu = os.path.splitext(asm)[0].split("_")[-1]
        mcu = mcu.upper().replace("X", "x")
        prop["defines"] += [mcu]
    except IndexError:
        sys.stderr.write("missing startup*.s\n")

    with open(cwd + tgt + filename, "w", encoding="UTF-8") as f:
        json.dump(root, f, ensure_ascii=True, indent=args[0].indent)


def make(filename="Makefile", config="openocd.cfg", user="build.mk"):
    '''
    Set Makefile
    '''

    openocd = "\topenocd -f " + config + " -c init -c halt -c "
    cmd = "flash:\n" + openocd + '"program $(BUILD_DIR)/$(TARGET).elf verify reset exit"\n'
    cmd += "reset:\n" + openocd + "reset -c shutdown\n"

    if user not in os.listdir():
        text_user = "# C defines\n"
        for flag in sorted({i for j in args[0].W for i in j}):
            text_user += "C_DEFS += -W{}\n".format(flag)
        text_user += "# C includes\nC_INCLUDES +=\n"
        text_user += "# C sources\nC_SOURCES += $(wildcard *.c)\n"
        text_user += "# AS defines\nAS_DEFS +=\n"
        text_user += "# ASM sources\nASM_SOURCES +=\n"
        text_user += "# link flags\nLDFLAGS += -u_printf_float\n"
        with open(user, "wb") as f:
            f.write(text_user.encode("UTF-8"))

    with open(filename, "r", encoding="UTF-8") as f:
        text = f.read()

    # Set inlcude user' Makefile
    if user not in text:
        text_inc = "-include {}\n".format(user)
        text_src = "# default "
        text = text.replace(text_src, "{}\n{}".format(text_inc, text_src))

    # Deal with the end
    end = "EOF"
    texts = text.split(end)
    text = texts[0] + end
    if " ***" in texts[-1]:
        text += " ***"
    text += "\n" + cmd

    with open(filename, "wb") as f:
        f.write(text.encode("UTF-8"))


if "__main__" == __name__:
    if not os.path.exists(tgt):
        os.mkdir(tgt)
    c_cpp_properties()
    make(config=launch())
    tasks()
