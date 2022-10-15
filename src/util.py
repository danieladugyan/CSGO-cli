import sys
from telnetlib import Telnet
import psutil
import signal
import emoji
from termcolor import colored
from time import sleep
from os import path


def await_csgo():
    """Make sure cs:go is running before trying to connect"""
    if not processExists("csgo.exe"):
        print_e(":information: Waiting for csgo to start... ")
        while not processExists("csgo.exe"):
            sleep(0.25)
        sleep(10)


def init_telnet(tn_host, tn_port) -> Telnet:
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


def listen(tn_host, tn_port, cfg_path):
    tn = init_telnet(tn_host, tn_port)
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
