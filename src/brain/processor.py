import json
import zlib
from confluent_kafka import Consumer, KafkaException
from icecream import ic

class FlowConsumer:
    def __init__(self, bootstrap_servers: str, topic: str):
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'brain-group',
            'auto.offset.reset': 'earliest'
        }
        self.consumer = Consumer(self.conf)
        self.consumer.subscribe([topic])
        ic(f"Subscribed to {topic}")

    def poll(self, timeout=1.0):
        msg = self.consumer.poll(timeout)
        if msg is None:
            return None
        if msg.error():
            ic(f"Consumer error: {msg.error()}")
            return None
        
        value = msg.value()
        if not value:
            return None

        try:
            return json.loads(value.decode('utf-8'))
        except Exception as e:
            # 只在非空且确实无法解析时记录
            if value.strip():
                ic(f"Parse error: {e} | Raw: {value[:50]}")
            return None

    def close(self):
        self.consumer.close()

class FeatureExtractor:
    @staticmethod
    def extract(flow: dict) -> dict:
        # 将流量 metadata 转换为数值特征
        # 使用 adler32 哈希将 IP 转为数值特征，增加模型输入熵
        src_ip_hash = zlib.adler32(flow.get("src_ip", "0.0.0.0").encode())
        dst_ip_hash = zlib.adler32(flow.get("dst_ip", "0.0.0.0").encode())
        
        return {
            "src_ip": src_ip_hash,
            "dst_ip": dst_ip_hash,
            "src_port": flow.get("src_port", 0),
            "dst_port": flow.get("dst_port", 0),
            "proto": 1 if flow.get("proto") == "TCP" else 2 if flow.get("proto") == "UDP" else 0
        }
