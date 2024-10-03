import typer

from app.logger import Logger
from app.models import Environment


# App logger
logger = Logger()


def create_app(env: Environment) -> typer.Typer:
    """
    Application factory function

    :param env: the runtime environment
    :return: a Typer application instance
    """
    app = typer.Typer(name="Anomaly Detector")
    logger.init_app(env)
    return app
