import time
import json
import random

import redis

import config
from app.models import GeneratorPhase


class ResponseTimeGenerator:
    def __init__(self):
        self.timestamp = 0
        self.phase_counter = 0
        self.phase = GeneratorPhase.NORMAL
        self.transition = {
            GeneratorPhase.NORMAL: GeneratorPhase.RAMP_UP,
            GeneratorPhase.RAMP_UP: GeneratorPhase.HIGH,
            GeneratorPhase.HIGH: GeneratorPhase.RAMP_DOWN,
            GeneratorPhase.RAMP_DOWN: GeneratorPhase.NORMAL,
        }
        self.durations = {
            GeneratorPhase.NORMAL: 200,
            GeneratorPhase.RAMP_UP: 100,
            GeneratorPhase.HIGH: 200,
            GeneratorPhase.RAMP_DOWN: 100,
        }
        self.redis_client = redis.Redis(
            host=config.REDIS_HOST, port=config.REDIS_PORT, db=0
        )

    def _generate_response_time(self):
        """
        Generate response time based on the current phase
        """
        # Base 200 ms response time with some noise
        response_time = 200 + abs(random.gauss(0, 2.5))

        # Gradually increase response time during ramp-up phase
        if self.phase == GeneratorPhase.RAMP_UP:
            response_time += 0.25 * self.phase_counter

        # Sustained high response time during high phase with adde noise
        elif self.phase == GeneratorPhase.HIGH:
            response_time += 25 + abs(random.gauss(0, 2.5))

        # Gradually decrease response time during ramp-down phase
        elif self.phase == GeneratorPhase.RAMP_DOWN:
            response_time += 25 - 0.25 * self.phase_counter

        # Add some random spikes
        if random.random() > 0.99:
            response_time += abs(random.gauss(0, 10))

        # Transition to the next phase
        self.timestamp += 1
        self.phase_counter += 1
        if self.phase_counter > self.durations[self.phase]:
            self.phase = self.transition[self.phase]
            self.phase_counter = 0

        return response_time

    def start(self):
        """
        Generate response times and publish to Redis
        """
        while True:
            response_time = self._generate_response_time()
            data = {"response_time": response_time, "timestamp": self.timestamp}
            self.redis_client.publish("response_times", json.dumps(data))
            time.sleep(0.1)
