from threading import Thread

import typer

import config
from app import create_app, logger
from app.models import DetectorType
from app.detector.anomaly_detector import SMADetector, EMADetector
from app.generator.stream_generator import ResponseTimeGenerator

from app.visualizer import PyplotVisualizer


# Initialize command line app
app = create_app(config.ENVIRONMENT)


@app.command()
def main(
    detector_type: DetectorType = typer.Argument(
        DetectorType.SMA, help="Anomaly detector algorithm"
    )
):
    # Simple Moving Average (SMA) detector
    if detector_type == DetectorType.SMA:
        logger.info("Using SMA detector")
        detector = SMADetector()

    # Exponential Moving Average (EMA) detector
    elif detector_type == DetectorType.EMA:
        logger.info("Using EMA detector")
        detector = EMADetector()

    # Invalid detector type
    else:
        logger.error("Invalid detector type")
        raise typer.Abort()

    # Start the generator in a thread
    generator = ResponseTimeGenerator()
    rt_generator_thread = Thread(target=generator.start)
    rt_generator_thread.start()

    # Start the detector in another thread
    ma_generator_thread = Thread(target=detector.start)
    ma_generator_thread.start()

    # Start the visualizer in the main thread
    visualizer = PyplotVisualizer()
    visualizer.plot()


if __name__ == "__main__":
    app()
