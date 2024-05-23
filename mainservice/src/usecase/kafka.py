from aiokafka import AIOKafkaProducer
import asyncio, json

async def get_producer(servers: str) -> AIOKafkaProducer:
    aioproducer = AIOKafkaProducer(bootstrap_servers=servers)
    return aioproducer

async def send_producer_kafka(producer: AIOKafkaProducer, data_for_kafka: dict, topic: str) -> None:
    await producer.start()
    try:
        await asyncio.wait_for(producer.send(topic, json.dumps(data_for_kafka).encode("ascii")), timeout=3)
    finally:
        await producer.stop()
