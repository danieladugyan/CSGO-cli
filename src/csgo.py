import typer
from util import init_telnet, listen, run, verify_connection

tn_host = "127.0.0.1"
tn_port = 2121
cfg_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive\\csgo\\cfg\\"


csgo_app = typer.Typer(
    help="Make sure CS:GO is running with this launch option: -netconport "
    + str(tn_port),
    no_args_is_help=True,
)


@csgo_app.command()
def server():
    """
    Interactive session that responds to triggers in-game.
    """
    listen(tn_host, tn_port, cfg_path)


@csgo_app.command()
def exec(cmd: str):
    """
    Send a single command to the CS:GO client.
    """
    tn = init_telnet(tn_host, tn_port)
    verify_connection(tn)
    run(tn, cmd)


@csgo_app.command()
def map(map: str):
    """Open a CS:GO map."""
    exec(f"map {map}")


@csgo_app.command()
def connect(
    ip: str = typer.Argument(..., help="192.168.0.1:27015"),
    psw: str = typer.Argument(..., help="password"),
):
    """Connect to a CS:GO server."""
    exec(f"connect {ip}; password {psw}")


@csgo_app.command()
def fix_audio():
    """Refresh CS:GO audio output device."""
    exec(
        "incrementvar windows_speaker_config 0 1 1;incrementvar windows_speaker_config 0 1 1"
    )
