import json
from collections import deque

import redis
import numpy as np
import matplotlib.pyplot as plt


# User tkinter backend for matplotlib
plt.switch_backend("TkAgg")

# Turn on interactive mode
plt.ion()


class PyplotVisualizer:
    def __init__(self):
        # Initialize deque objects to store data
        self.anomalies = deque(maxlen=500)
        self.timestamps = deque(maxlen=500)
        self.response_times = deque(maxlen=500)

        self.fig, self.ax = plt.subplots()

        # Initialize line and scatter plot objects
        (self.line,) = self.ax.plot([], [], label="Response Time", color="blue")
        self.scatter = self.ax.scatter([], [], color="red", label="Anomalies")

        # Set axis labels and title once
        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel("Response Time (ms)")
        self.ax.set_title("Real-Time Response Times")
        self.ax.legend()

        self.redis_client = redis.Redis(host="localhost", port=6379, db=0)

    def plot(self):
        # Subscribe to the "anomalies" channel on Redis
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe("anomalies")

        while True:
            for message in pubsub.listen():
                # Load message data
                if message["type"] != "message":
                    continue
                data = json.loads(message["data"])

                # Append new message data to the deque objects
                self.anomalies.append(data["anomaly"])
                self.timestamps.append(data["timestamp"])
                self.response_times.append(data["response_time"])

                # Update the line plot for response times
                self.line.set_data(self.timestamps, self.response_times)

                # Update scatter plot for anomalies
                anomaly_indices = [
                    i for i, anomaly in enumerate(self.anomalies) if anomaly
                ]
                anomaly_times = np.array(self.timestamps)[anomaly_indices]
                anomaly_response_times = np.array(self.response_times)[anomaly_indices]

                self.scatter.set_offsets(np.c_[anomaly_times, anomaly_response_times])

                # Adjust plot limits dynamically
                self.ax.relim()
                self.ax.autoscale_view()

                # Redraw the plot efficiently
                self.fig.canvas.draw_idle()
                self.fig.canvas.flush_events()

                plt.pause(0.01)
