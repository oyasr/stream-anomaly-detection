# Data Stream Anomaly Detector
This project is a data stream anomaly detector that simulates a stream of response times from a server, detects anomalies in the stream, and visualizes the anomalies in real-time.

## Project Overview
### Architecture
The project consists of four main components:
1. **Data Stream Generator**: Simulates a stream of response times from a web server.
2. **Anomaly Detector**: Detects anomalies in the stream of response times.
3. **Anomaly Visualizer**: Visualizes the datastream and anomalies detected by the anomaly detector in real-time.
4. **Redis**: A Redis server is used as a message broker for the above services to communincate asynchronously.

More details about each component later in the document.

### Project Structure
```
├── stream-anomaly-detection/
        ├── app/
        |    ├── detector/
        |    |    ├── __init__.py
        |    |    ├── anomaly_detector.py
        |    ├── generator/
        |    |    ├── __init__.py
        |    |    ├── stream_generator.py
        |    ├── __init__.py
        |    ├── logger.py
        |    ├── models.py
        |    ├── visualizer.py
        ├── requirements/
        |    ├── development.txt
        |    ├── production.txt
        ├── config.py
        ├── main.py
```
The application's entry point is the `main.py` file.

### Prerequisites and Local Development
Developers using this project should already have [Python3](https://www.python.org/downloads/) and [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/) installed on their local machines.
After creating a virtual environment, install the project dependencies by running `pip install -r requirements/development.txt`. All required packages are included in the requirements file.
Make sure to have a Redis server running on your local machine on the default port `6379` before running the application.
To run the application locally, execute the following command:
```python
python3 main.py [detector_type]:[sma|ema] [default: sma]
```
The `detector_type` argument specifies the type of anomaly detector to use. The available options are `sma` (default) for Simple Moving Average and `ema` for Exponential Moving Average (More on this later).
> For detailed usage instructions, run `python3 main.py --help`.

If everything is set up correctly, you should see a live visualization of the data stream and anomalies detected similar to the image below. The application will also log the anomalies detected in the stream.
![alt text](https://i.ibb.co/g9fKg8q/Screenshot-2024-10-03-222959.png)
```
2024-10-03 22:29:03,605 - INFO - Normal value: 200.93815208912315
2024-10-03 22:29:03,705 - INFO - Normal value: 200.59508932162285
2024-10-03 22:29:03,806 - INFO - Normal value: 201.1867602606972
2024-10-03 22:29:04,008 - INFO - Normal value: 201.8970608791532
2024-10-03 22:29:04,109 - WARNING - Anomaly detected: 208.25010080577752
2024-10-03 22:29:04,210 - INFO - Normal value: 202.29940921701288
2024-10-03 22:29:04,311 - INFO - Normal value: 205.64124229480947
2024-10-03 22:29:04,412 - INFO - Normal value: 200.9113353330986
2024-10-03 22:29:04,614 - INFO - Normal value: 205.17589101027596
2024-10-03 22:29:04,715 - INFO - Normal value: 202.91864172711882
```
Now lets dive into the details of each component.

## Data Stream Generator
The data stream generator simulates a stream of response times for a web server.
The ResponseTimeGenerator class is responsible for generating response times based on different phases and publishing them to a Redis channel.

The ResponseTimeGenerator class has the following features:
- It maintains a timestamp and phase counter to keep track of the current phase.
- It defines 4 different phases (NORMAL, RAMP_UP, HIGH, RAMP_DOWN) and their corresponding durations.
- It generates response times based on the current phase, with some noise and random spikes.
- It transitions to the next phase after a certain duration.
- It publishes the generated response times to a Redis channel.

This implementation ensures that the data stream simulates real-world scenarios where the response times fluctuate based on the server's load, incorporating seasonal patterns and random spikes.

## Anomaly Detector
The anomaly detector is responsible for detecting anomalies and unusual patterns in the stream of response times, while still being able to adapt to seasonal patterns in real-time.
So choosing an algorithm that satisfies these requirements and still be fast and efficient is crucial. The factors that were considered when choosing the algorithm are:
- **Efficiency**: The algorithm should be able to process the data stream in real-time.
- **Adaptability**: The algorithm should be able to adapt to seasonal patterns and changes in the data stream.
- **Simplicity**: The algorithm should be fairly simple and easy to implement.

### Simple Moving Average (SMA)
Moving Average is a calculation used to smooth the data by creating a new series of averages from a subset of the data points. In other words, this algorithm calculates the mean of the n latest data points. 

\[
   \text{SMA}_n = \frac{1}{n} \sum_{i=1}^{n} x_i
\]

#### Window Size
This means that the algorithm requires a parameter `n` or window size to be set, which is the number of data points to consider when calculating the average. The larger the window size, the smoother the data will be, but it will also be less sensitive to changes in the data stream. On the other hand, a smaller window size will be more sensitive to changes but will also be more noisy.

#### Anomaly Detection
The algorithm detects anomalies by comparing the current data point with the moving average. If the current data point is significantly different from the moving average, it is considered an anomaly. The threshold for detecting anomalies can be set based on the standard deviation of the data points.

#### Using Z-Score
The Z-score is a measurement that describes how many standard deviations a data point is from the mean of a dataset. It indicates whether a data point is above or below the mean, and by how much. The formula for calculating the Z-score for a data point 𝑥 is:

\[
Z = \frac{x - \mu}{\sigma}
\]

Where:
- 𝑥 is the data point,
- 𝜇 is the mean of the dataset,
- 𝜎 is the standard deviation of the dataset.

If a new response time has a high Z-score, say greater 2 (**95.4**% of the dataset), this indicates that the response time is unusually high (or low) compared to recent data, potentially signaling an anomaly such as a spike.

#### Drawbacks
- **Equal Weighting**: SMA assigns the same weight to all data points in the window, regardless of how recent or old they are. This can be problematic because more recent data may be more relevant for detecting trends or changes.
- **Lag Effect**: SMA tends to lag behind actual changes in the data, especially when using a larger window size. This is because it averages out fluctuations, causing a delay in responding to sudden shifts or trends.
- **Ignoring Data Outside Window**: SMA only considers the most recent data points within the window, ignoring older data points that may still be relevant for detecting anomalies.

### Exponential Moving Average (EMA)
To address the drawbacks of SMA, we can use Exponential Moving Average (EMA) instead. EMA is a type of moving average that gives more weight to recent data points, making it more responsive to changes in the data stream.
The EMA is calculated using a smoothing factor 𝛼, which determines the weight given to the most recent data point. The formula for calculating the EMA at time 𝑡 is:

\[
   \text{EMA}_t = \alpha \cdot x_t + (1 - \alpha) \cdot \text{EMA}_{t-1}
\]


#### Smoothing Factor
The smoothing factor 𝛼 is a value between 0 and 1 that determines how much weight to give to the most recent data point. A higher 𝛼 gives more weight to recent data points, making the EMA more responsive to changes. A lower 𝛼 gives more weight to older data points, making the EMA smoother.

#### Anomaly Detection
Similar to SMA, the EMA algorithm detects anomalies by comparing the current data point with the EMA. If the current data point is significantly different from the EMA, it is considered an anomaly. The threshold for detecting anomalies can be set based on the standard deviation of the data points.


#### Drawbacks
- **Smoothing Factor Sensitivity**: The choice of the smoothing factor 𝛼 can significantly impact the performance of EMA. A higher 𝛼 makes the EMA more responsive to changes but also more sensitive to noise. A lower 𝛼 makes the EMA smoother but less responsive to changes.
- **Lack of Historical Data**: EMA may not perform well when there is not enough historical data to establish a trend. This can lead to false positives or negatives when detecting anomalies.


### Algorithms Conclusion
Both SMA and EMA have their strengths and weaknesses, and the choice between them depends on the specific requirements of the anomaly detection task. SMA is simple and easy to implement, but it may not be as responsive to changes in the data stream. EMA is more responsive and adaptive, but it requires tuning the smoothing factor 𝛼 and may be sensitive to noise.


## Visualizer Service
The anomaly visualizer is responsible for visualizing the data stream and anomalies detected by the anomaly detector in real-time. It uses the `matplotlib` library to create a live plot that updates as new data points are received.
It subscribes to the Redis channel where the response times and anomalies are published by the anomaly detector and updates the plot accordingly.
The visualizer service is very efficient and can handle a high volume of data points in real-time. It makes use of `matplotlib` features to only update the parts of the plot that have changed, reducing the computational overhead of redrawing the entire plot.


## Redis Server
A Redis server is used as a message broker for the data stream generator, anomaly detector, and visualizer services to communicate asynchronously. The code makes use of **Redis Pub/Sub** messaging protocol whih is described by Redis as:
> Redis Pub/Sub is an extremely lightweight messaging protocol designed for broadcasting live notifications within a system. It’s ideal for propagating short-lived messages when low latency and huge throughput are critical.

This allows the services to communicate in real-time without blocking each other, ensuring that the data stream is processed efficiently and anomalies are detected and visualized as soon as they occur.

## Bonus: Containerization
Each component of the system (aside from the visualizer) has its own Dockerfile and can be built and run as a separate container. The `docker-compose.yml` file is used to define the services and their dependencies, allowing the entire system to be run with a single command.
```
docker-compose up
```
This command will build/pull and run three containers: `stream-generator`, `anomaly-detector`, and `redis-server`.
This facilitates the deployment and scaling of the system in a containerized environment, making it easier to manage and maintain the services. It also ensures that the services are isolated and can be run on any platform that supports Docker, regardless of the underlying environment.

> The visualizer service is not containerized as it requires a GUI to display the plot, which is not supported in a Docker environment. However, anomaly updates are still logged to the console for monitoring purposes. Also, an alternative approach could be to use a web-based visualization tool that can be accessed from a browser, allowing the visualizer to run in a container.


## Future Improvements
- **Dynamic Parameter Selection**: Implement a mechanism to dynamically adjust the parameters of the anomaly detector based on the characteristics of the data stream. This could involve automatically tuning the window size or smoothing factor based on the data distribution.
- **Deviation For Amount of Time**: Sometimes, a response time may be high for a short period of time, but it may not be considered an anomaly. Implement a mechanism to detect anomalies based on the duration of the deviation from the normal response time.
- **Real-Time Alerts**: Implement a mechanism to send real-time alerts or notifications when anomalies are detected. This could involve integrating with messaging services such as Slack or email to notify users of potential issues.
- **Scalability**: Design the system to be scalable and able to handle large volumes of data streams. This could involve using an advanced message broker such as Apache Kafka.
- **User Interface**: Develop a user interface for configuring the anomaly detection parameters, visualizing the data stream, and interacting with the system. This could involve creating a web-based dashboard or application that allows users to monitor and analyze the data stream in real-time.



