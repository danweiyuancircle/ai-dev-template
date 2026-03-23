import typer

app = typer.Typer(
    name="ait",
    help="AI dev config management — manage rules, skills, MCP, templates across machines and projects.",
    no_args_is_help=True,
)


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
