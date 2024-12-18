Kafka Pipeline: Consumer, Transformation, and Insights
======================================================

This project implements a Kafka pipeline using Python that consumes messages, processes them (transformation, filtering, and aggregations), and generates real-time insights. The transformed data is produced to a new Kafka topic, ensuring scalability, fault tolerance, and efficiency.

* * * * *

Installation
------------

Use Docker and Python to set up the Kafka environment and run the application.

### Prerequisites

1.  **Install Docker and Docker Compose**

    -   Download and install Docker by following the official guide: [Install Docker](https://docs.docker.com/get-docker/).

    -   Install Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/).

    Verify installation with:

    ```
    docker --version
    docker-compose --version
    ```

2.  **Install Python 3.8+**

    -   Install Python by following the official guide: [Install Python](https://www.python.org/downloads/).

    Verify installation with:

     ```
    python3 --version
    pip --version
    ```

3.  Install the required Python packages:

    ```
    pip install confluent-kafka

    ```

### Run Kafka Environment

Start the Kafka and Zookeeper services using Docker Compose:

```
docker compose up --build

```

This will set up the following services:

-   **Zookeeper**: Manages Kafka brokers.
-   **Kafka**: The message broker that handles topics `user-login` and `processed-user-login`.
-   **Data Generator**: Produces sample messages to the `user-login` topic.

### Verify Kafka Setup

Check if topics exist:

```
kafka-topics --describe --topic user-login --bootstrap-server localhost:29092

```

* * * * *

Usage
-----

Run the Kafka pipeline by executing `main.py`. The script consumes messages, processes them, and produces results to a new Kafka topic.

```
python3 main.py

```

### Message Schema

Messages consumed from the topic `user-login` have the following schema:

```
{
    "user_id": "uuid",
    "app_version": "string",
    "device_type": "string",
    "ip": "string",
    "locale": "string",
    "timestamp": "epoch"
}

```

### Real-time Insights

The application processes data and generates periodic insights. Example insights include:

1.  **Device Type Distribution**:

    ```
    Insights so far: {'device_type:android': 317, 'device_type:iOS': 308}

    ```

2.  **App Version Counts**:

    ```
    Insights on App Versions: {'2.3.0': 500, '2.2.0': 120}

    ```

3.  **Locale (Region) Distribution**:

    ```
    Insights on Locales: {'TX': 200, 'NY': 180, 'AL': 150}

    ```

4.  **Traffic Analysis**:

    ```
    Peak Traffic Insights:
    2024-12-17 18:47: 120 messages
    2024-12-17 18:48: 150 messages

    ```

* * * * *

Design Choices
--------------

### 1\. **Kafka for Streaming**

Kafka's distributed, fault-tolerant architecture ensures reliable message consumption and production.

### 2\. **Message Processing**

-   **Filter**: Processes only relevant messages (e.g., `app_version` = `2.0.0`).
-   **Transform**: Adds a `processed: True` flag to messages.
-   **Aggregate**: Generates insights for device types, app versions, and message distribution.

### 3\. **Efficiency**

-   Kafka Producer is optimized with batching settings:
    -   `linger.ms`: Delays sending small batches for better throughput.
    -   `batch.num.messages`: Groups messages together for efficiency.

### 4\. **Fault Tolerance**

-   Errors are logged without halting the pipeline.
-   Kafka guarantees message durability.

### 5\. **Scalability**

-   Increase Kafka partitions for load distribution.
-   Add multiple consumers to the same group for parallel processing.

* * * * *

How It Works
------------

1.  **Input Topic**:

    -   The `user-login` topic contains raw messages.
2.  **Processing**:

    -   Messages are consumed and processed using the `process_message` function.
    -   Insights are generated and logged periodically.
3.  **Output Topic**:

    -   Transformed messages are produced to the `processed-user-login` topic.
4.  **Insights**:

    -   Aggregated insights are logged every 10 messages.

* * * * *

Production Deployment
---------------------

### How to Deploy

1.  **Containerize the Application**: Use Docker to package the Python application:

    ```
    FROM python:3.9
    WORKDIR /app
    COPY . .
    RUN pip install confluent-kafka
    CMD ["python3", "main.py"]

    ```

2.  **Deploy to Kubernetes**:
    -   Run Kafka brokers as StatefulSets.
    -   Deploy Python consumers/producers as Deployments.
    - **New to Kubernetes?** Refer to this [Kubernetes Beginner's Guide](https://kubernetes.io/docs/tutorials/kubernetes-basics/) for an introduction.

3.  **Monitoring**:
    -   Integrate **Prometheus** and **Grafana** to monitor Kafka metrics and consumer lag.

### Components to Make it Production Ready

-   **Monitoring**: Add Kafka Exporter for Prometheus.
-   **Message Validation**: Use Schema Registry to enforce message formats.
-   **Error Handling**: Implement a Dead Letter Queue (DLQ) for failed messages.
-   **Security**:
    -   Enable SSL/TLS for Kafka.
    -   Use SASL authentication for clients.
-   **High Availability**:
    -   Use replication for Kafka brokers.
    -   Load balance consumers and producers.

### Scalability for Growing Datasets

-   **Horizontal Scaling**: Increase partitions and add consumers for parallel processing.
-   **Partitioning**: Use a partition key (e.g., `user_id`) to distribute load evenly.
-   **Kafka Connect**: Integrate with external systems for data sinks.
-   **Storage Optimization**: Use Kafka log compaction to retain only the latest data.

* * * * *

Contributing
------------

Pull requests are welcome. For significant changes, please open an issue to discuss your ideas. Ensure tests and documentation are updated.

* * * * *

License
-------

[MIT](https://choosealicense.com/licenses/mit/)

* * * * *

Additional Questions
--------------------

### 1\. How would you deploy this application in production?

-   Containerize the application using Docker.
-   Deploy Kafka brokers and consumers in a Kubernetes cluster.
-   Use monitoring tools (e.g., Prometheus, Grafana) for observability.

### 2\. What other components would you want to add to make this production ready?

-   **Schema Registry**: Enforce message validation.
-   **Dead Letter Queue (DLQ)**: Capture unprocessable messages.
-   **Security**: Implement SSL/TLS and SASL authentication.
-   **Monitoring**: Add Kafka lag monitoring and alerting systems.
-   **Load Balancing**: Ensure Kafka consumers and producers are horizontally scaled.

### 3\. How can this application scale with a growing dataset?

-   Increase Kafka partitions to distribute load.
-   Add consumers to the same group for parallel processing.
-   Use partition keys to ensure even distribution of messages.
-   Implement Kafka Connect for integration with external storage or analytics systems.

* * * * *