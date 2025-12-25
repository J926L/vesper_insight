use rdkafka::config::ClientConfig;
use rdkafka::producer::{FutureProducer, FutureRecord};
use std::time::Duration;
use tokio;

#[tokio::test]
async fn test_kafka_connectivity() {
    let producer: FutureProducer = ClientConfig::new()
        .set("bootstrap.servers", "localhost:19092")
        .set("message.timeout.ms", "1000")
        .create()
        .expect("Producer creation failed");

    let record = FutureRecord::to("raw_metrics")
        .payload("test_message")
        .key("test_key");

    let result = producer.send(record, Duration::from_secs(1)).await;

    assert!(result.is_ok(), "Failed to send message to Redpanda at localhost:19092. Is it running?");
}
