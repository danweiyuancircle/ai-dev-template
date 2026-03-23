import typer

from ait.commands.install import install
from ait.commands.list_cmd import list_resources
from ait.commands.profiles import list_profiles
from ait.commands.show import show_resource
from ait.commands.update import update

app = typer.Typer(
    name="ait",
    help="AI dev config management — manage rules, skills, MCP, templates across machines and projects.",
    no_args_is_help=True,
)

app.command("install")(install)
app.command("list")(list_resources)
app.command("profiles")(list_profiles)
app.command("show")(show_resource)
app.command("update")(update)


def version_callback(value: bool) -> None:
    if value:
        from ait import __version__
        typer.echo(f"ait {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-v", callback=version_callback, is_eager=True),
) -> None:
    """AIT — AI dev config management CLI."""


if __name__ == "__main__":
    app()
