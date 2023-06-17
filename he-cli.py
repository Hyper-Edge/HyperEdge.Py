from cookiecutter.main import cookiecutter
import typer
import json

he_app = typer.Typer()

@he_app.command()
def create_project(
    template: str = typer.Option('he-sdk-template', help='The cookiecutter template to use, a directory containing the project template or the URL to a Git repository.'),
    checkout: str = typer.Option(None, help='The branch, tag or commit ID to checkout after clone.'),
    no_input: bool = typer.Option(False, help='A boolean flag indicating whether to prompt the user for manual configuration.'),
    extra_context: str = typer.Option(None, help='A string of a JSON dictionary that overrides default and user configuration.'),
    replay: bool = typer.Option(False, help=' A flag indicating whether to read inputs from a saved replay file instead of prompting the user for input. '),
    overwrite_if_exists: bool = typer.Option(False, help='A boolean flag indicating whether to overwrite existing files in the output directory if they have the same name as generated files.'),
    output_dir: str = typer.Option('.', help='The output directory where the generated project will be saved.'),
    config_file: str = typer.Option(None, help='The path to the user configuration file.'),
    default_config: bool = typer.Option(False, help= 'A boolean flag indicating whether to use default values rather than a user configuration file.'),
    password: str = typer.Option(None, help='The password to use when extracting the repository.'),
    directory: str = typer.Option(None, help='A relative path to a specific directory within the template repository.'),
    skip_if_file_exists: bool = typer.Option(False, help='A boolean flag indicating whether to skip file generation if the file already exists in the output directory.'),
    accept_hooks: bool = typer.Option(True, help='A boolean flag indicating whether to accept pre- and post-generation hooks defined in the template.'),
):
    """
    Scaffold your new game project from a template.
    """
    extra_context = json.loads(extra_context) if extra_context else None
    
    cookiecutter(
        template=template,
        checkout=checkout,
        no_input=no_input,
        extra_context=extra_context,
        replay=replay,
        overwrite_if_exists=overwrite_if_exists,
        output_dir=output_dir,
        config_file=config_file,
        default_config=default_config,
        password=password,
        directory=directory,
        skip_if_file_exists=skip_if_file_exists,
        accept_hooks=accept_hooks,
    )

if __name__ == "__main__":
    he_app()
