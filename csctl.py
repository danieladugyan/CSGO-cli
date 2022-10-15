import os
import subprocess
import sys
from telnetlib import Telnet
from typing import Optional
import psutil
import signal
import emoji
from termcolor import colored
from time import sleep
from os import path

import typer

# Config
tn_host = "127.0.0.1"
tn_port = 2121
cfg_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\csgo\\cfg\\"


def await_csgo():
    """Make sure cs:go is running before trying to connect"""
    if not processExists("csgo.exe"):
        print_e(":information: Waiting for csgo to start... ")
        while not processExists("csgo.exe"):
            sleep(0.25)
        sleep(10)


def init_telnet() -> Telnet:
    """Initialize csgo telnet connection"""
    await_csgo()
    print_e(":information: Trying " + tn_host + ":" + str(tn_port) + "...")
    try:
        tn = Telnet(tn_host, tn_port)
    except ConnectionRefusedError:
        # Retry in 30 seconds
        sleep(30)
        pass
    try:
        tn = Telnet(tn_host, tn_port)
    except ConnectionRefusedError:
        print_e(
            ":x: Connection refused. Make sure you have the following launch option set:"
        )
        print(colored("  -netconport " + str(tn_port), attrs=["bold"]))
        sys.exit(1)

    return tn


def verify_connection(tn: Telnet):
    tn.write(b"echo CSCTL Active, use exectn instruction_file to execute commands\n")
    tn.read_until(b"commands")
    print_e(":heavy_check_mark: Successfully Connected")


def signal_handler(signal, frame):
    print("\nquitting...")
    sys.exit(0)


# Print with emojis
def print_e(message):
    print(colored(emoji.emojize(message, use_aliases=True), attrs=["bold"]))


# List PIDs of processes matching processName
def processExists(processName):
    procList = []
    for proc in psutil.process_iter(["name"]):
        if proc.info["name"].lower() == processName.lower():
            return True
    return False


# Runs commands on the csgo console
def run(txn, command):
    cmd_s = command + "\n"
    txn.write(cmd_s.encode("utf-8"))
    sleep(0.005)


signal.signal(signal.SIGINT, signal_handler)


def listen():
    tn = init_telnet()
    verify_connection(tn)

    while True:
        print_e(":information: Listening for command from console")
        # Capture console output until we encounter our exec string
        tn.read_until(b"exectn ")

        # Parse output and get filename
        instr_fname = tn.read_eager().decode("utf-8")
        instr_fname = instr_fname.replace("\n", " ").replace("\r", "")
        if path.exists(instr_fname) or path.exists(cfg_path + instr_fname):
            # Execute instructions from file
            if path.exists(cfg_path + instr_fname):
                instr_fname = cfg_path + instr_fname
            for line in open(instr_fname, "r"):
                sspl = line.split(" ")
                if sspl[0] == "delay":
                    delay_time = sspl[1].replace("\n", " ").replace("\r", "")
                    print_e(":sparkle: sleeping for " + str(delay_time) + " seconds")
                    sleep(float(sspl[1]))
                else:
                    line = line.replace("\n", " ").replace("\r", "")
                    print_e(":sparkle: exec " + str(line))
                    run(tn, str(line))
        else:
            run(tn, "echo File not found: " + str(instr_fname))

        print_e(":heavy_check_mark: Instructions complete")


app = typer.Typer(
    help="Make sure you set up CS:GO to receive connections with this launch option: -netconport "
    + str(tn_port),
    no_args_is_help=True,
)


@app.command()
def server():
    """
    Interactive session that responds to triggers in-game.
    """
    listen()


@app.command()
def con(cmd: str):
    """
    Send a single command to the CS:GO client.
    """
    tn = init_telnet()
    verify_connection(tn)
    run(tn, cmd)


@app.command()
def open_url(url: str):
    """
    Open an URL in its default application.
    """
    typer.launch(url)


@app.command()
def shell(cmd: str):
    """
    Execute a command in the OS's default shell.
    """
    subprocess.run(cmd, shell=True)


@app.command()
def launch_csgo(
    user: str = typer.Argument("%SteamUser%", help="Steam username"),
    pwd: str = typer.Argument("%SteamPass%", help="Steam password"),
):
    """
    Starts Steam, logs in a user and launches CS:GO.
    """
    user = os.path.expandvars(user)
    pwd = os.path.expandvars(pwd)
    cmd = [
        "D:/Program Files (x86)/Steam/steam.exe",
        "-noreactlogin",
        "-login",
        user,
        "-pass",
        pwd,
        "-applaunch",
        "730",
        "-tickrate",
        "128",
        "-netconport",
        "2121",
    ]

    subprocess.run(cmd, shell=True)
    print(subprocess.list2cmdline(cmd))


@app.command()
def open_map(map: str):
    """Open a CS:GO map."""
    con(f"map {map}")


if __name__ == "__main__":
    app()
