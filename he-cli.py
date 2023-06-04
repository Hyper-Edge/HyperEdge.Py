from cookiecutter.main import cookiecutter
import typer


he_app = typer.Typer()


@he_app.command()
def create_project():
    cookiecutter('he-sdk-template')


if __name__ == "__main__":
    he_app()
