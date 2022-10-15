# Config
import os
import subprocess
import typer
from csgo import csgo_app


app = typer.Typer(
    no_args_is_help=True,
)
app.add_typer(csgo_app, name="csgo")


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
    user: str = typer.Option("%SteamUser%", prompt=True, help="Steam username"),
    pwd: str = typer.Option(
        "%SteamPass%", prompt=True, hide_input=True, help="Steam password"
    ),
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


if __name__ == "__main__":
    app()
