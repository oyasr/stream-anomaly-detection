import config
from app import create_app, logger
from app.detector.anomaly_detector import SMADetector
from app.generator.stream_generator import ResponseTimeGenerator


# Initialize command line app
app = create_app(config.ENVIRONMENT)


@app.command()
def detect():
    logger.info("Anomaly detector started")
    sma_detector = SMADetector()
    sma_detector.start()


@app.command()
def generate():
    logger.info("Stream generator started")
    rt_generator = ResponseTimeGenerator()
    rt_generator.start()


if __name__ == "__main__":
    app()
