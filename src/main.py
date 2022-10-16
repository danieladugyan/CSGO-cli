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
    user: str = typer.Argument("%SteamUser%", help="Steam username"),
    psw: str = typer.Argument("%SteamPass%", help="Steam password"),
    steam_install_dir: str = typer.Argument(
        "C:/Program Files (x86)/Steam/steam.exe", help="Steam install dir"
    ),
):
    """
    Starts Steam, logs in the user defined in the environment
    variables and launches CS:GO.
    """
    user = os.path.expandvars(user)
    psw = os.path.expandvars(psw)
    cmd = [
        steam_install_dir,
        "-noreactlogin",
        "-login",
        user,
        psw,
        "-applaunch",
        "730",
        "-novid",
        "-console",
        "-tickrate",
        "128",
        "-netconport",
        "2121",
    ]

    print(subprocess.list2cmdline(cmd))
    subprocess.Popen(cmd)


if __name__ == "__main__":
    app()
