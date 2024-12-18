from confluent_kafka import Consumer, Producer, KafkaException
import json
import logging
import signal
import sys
from collections import defaultdict

# -------------------------
# Kafka Configuration Setup
# -------------------------
KAFKA_BROKER = "localhost:29092"  # Kafka broker address
CONSUMER_TOPIC = "user-login"      # Kafka topic to consume messages from
PRODUCER_TOPIC = "processed-user-login"  # Kafka topic to send processed messages to
GROUP_ID = "user-login-processor-group"  # Consumer group ID for Kafka

# -------------------------
# Logging Configuration
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# -------------------------
# Kafka Consumer Settings
# -------------------------
consumer_conf = {
    "bootstrap.servers": KAFKA_BROKER,  # Kafka broker for consuming messages
    "group.id": GROUP_ID,              # Consumer group ID
    "auto.offset.reset": "earliest"   # Start reading from the earliest offset
}

# -------------------------
# Kafka Producer Settings
# -------------------------
producer_conf = {
    "bootstrap.servers": KAFKA_BROKER,  # Kafka broker for producing messages
    "linger.ms": 100,                   # Delay before sending messages to batch efficiently
    "batch.num.messages": 1000          # Maximum number of messages per batch
}

# -------------------------
# Global Variables for Insights
# -------------------------
processed_count = 0  # Tracks the number of processed messages
insights = defaultdict(int)  # Dictionary to store message insights

# -------------------------
# Graceful Shutdown Handler
# -------------------------
def handle_shutdown(signum, frame):
    """Handles graceful shutdown on receiving SIGINT or SIGTERM signals."""
    logger.info("Shutting down...")
    consumer.close()
    producer.flush()
    sys.exit(0)

# Bind the signal handlers for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# -------------------------
# Delivery Report Callback
# -------------------------
def delivery_report(err, msg):
    """Logs delivery status of a message after production to Kafka."""
    if err:
        logger.error(f"Message failed delivery: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# -------------------------
# Message Processing Function
# -------------------------
def process_message(message_value):
    """Processes a Kafka message: filters, transforms, and logs insights."""
    global processed_count  # Use the global counter to track messages
    try:
        # Parse the JSON-formatted message
        data = json.loads(message_value)
        processed_count += 1
        
        # Filtering: Only include messages where app_version is 2.0.0
        if data.get("app_version") == "2.0.0":
            logger.info(f"Filtered Message: {data}")
            insights['app_version_2.0.0'] += 1
            return json.dumps(data)
        
        # Aggregation: Track counts for different device types
        device_type = data.get("device_type")
        if device_type:
            insights[f"device_type:{device_type}"] += 1

        # Transformation: Add a 'processed' field to the message
        data['processed'] = True
        logger.info(f"Transformed Message: {data}")
        return json.dumps(data)

    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e} - Raw message: {message_value}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
    return None

# -------------------------
# Main Kafka Consumer/Producer Loop
# -------------------------
def main():
    """Main function: consumes, processes, and produces messages continuously."""
    global consumer, producer  # Kafka consumer and producer
    consumer = Consumer(consumer_conf)  # Initialize the Kafka consumer
    producer = Producer(producer_conf)  # Initialize the Kafka producer

    try:
        # Subscribe to the input Kafka topic
        consumer.subscribe([CONSUMER_TOPIC])
        logger.info(f"Subscribed to topic: {CONSUMER_TOPIC}")

        while True:
            # Poll for new messages with a timeout of 1 second
            msg = consumer.poll(timeout=1.0)
            
            if msg is None:
                continue  # No message received, continue polling
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                if msg.error().fatal():
                    raise KafkaException(msg.error())
                continue
            
            # Process the message
            processed_data = process_message(msg.value().decode("utf-8"))
            if processed_data:
                # Produce the transformed message to the output Kafka topic
                producer.produce(PRODUCER_TOPIC, value=processed_data, callback=delivery_report)
                producer.poll(0)  # Trigger the delivery callback immediately

            # Log insights periodically every 10 messages
            if processed_count % 10 == 0:
                logger.info(f"--- Insights so far: {dict(insights)}")

    except KeyboardInterrupt:
        logger.info("Stopping consumer and producer...")
    except KafkaException as e:
        logger.error(f"Kafka error: {e}")
    finally:
        # Clean up resources on exit
        consumer.close()
        producer.flush()
        logger.info("Consumer closed. Producer flushed.")
        logger.info(f"Final Insights: {dict(insights)}")

# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    """Program entry point: Starts the Kafka pipeline."""
    main()