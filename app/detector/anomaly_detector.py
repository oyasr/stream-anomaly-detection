import json
from collections import deque
from abc import ABC, abstractmethod

import redis
import numpy as np

import config
from app import logger


class AnomalyDetector(ABC):
    def __init__(self):
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST, port=config.REDIS_PORT, db=0
        )

    @abstractmethod
    def _detect_anomaly(self, value: float) -> bool:
        pass

    def start(self):
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe("response_times")

        for message in pubsub.listen():
            if message["type"] != "message":
                continue
            data = json.loads(message["data"])
            response_time = data["response_time"]

            if self._detect_anomaly(response_time):
                logger.warning(f"Anomaly detected: {response_time}")
                anomaly = True
            else:
                logger.info(f"Normal value: {response_time}")
                anomaly = False

            data = {
                "response_time": response_time,
                "timestamp": data["timestamp"],
                "anomaly": anomaly,
            }
            self.redis_client.publish("anomalies", json.dumps(data))


class SMADetector(AnomalyDetector):
    def __init__(self, threshold: float = 2, window_size: int = 25):
        super().__init__()
        self.threshold = threshold
        self.window_size = window_size
        self.data_stream = deque(maxlen=window_size)

    def _detect_anomaly(self, value: float) -> bool:
        # Append the value to the stream
        self.data_stream.append(value)

        if len(self.data_stream) >= self.window_size:
            # Calculate new moving average and standard deviation
            avg = np.mean(self.data_stream)
            std = np.std(self.data_stream)

            # Calculate the z-score
            z_score = (value - avg) / (std if std > 0 else 1)

            # Check if the z-score is above the threshold
            if abs(z_score) > self.threshold:
                return True

        return False


class EMADetector(AnomalyDetector):
    def __init__(self, alpha: float = 0.08, threshold: float = 2.2):
        super().__init__()
        self.ema = None
        self.variance = 0
        self.alpha = alpha
        self.threshold = threshold

    def _detect_anomaly(self, value: float) -> bool:
        # Initialize EMA with the first value
        if self.ema is None:
            self.ema = value
            return False

        # Update EMA
        self.ema = self.alpha * value + (1 - self.alpha) * self.ema

        self.variance = (1 - self.alpha) * (
            self.variance + self.alpha * (value - self.ema) ** 2
        )
        std = np.sqrt(self.variance)

        if (
            self.ema + std * self.threshold < value
            or self.ema - std * self.threshold > value
        ):
            return True

        return False
