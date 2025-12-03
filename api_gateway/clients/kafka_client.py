import asyncio
import json
import logging
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from typing import Callable, Optional, Awaitable

logger = logging.getLogger(__name__)


class KafkaManager:
    def __init__(
        self,
        bootstrap_servers: str,
        update_topic: str,
        on_update: Optional[Callable[[bytes], Awaitable[None]]] = None
    ):
        self.bootstrap_servers = bootstrap_servers
        self.update_topic = update_topic
        self.on_update = on_update

        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.task_consumer: Optional[asyncio.Task] = None

    async def start(self):
        # Initialize and start producer
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()

        # Initialize and start consumer with a group_id
        self.consumer = AIOKafkaConsumer(
            self.update_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id="notification_group",  # Required for proper partition assignment
            auto_offset_reset="earliest",
            enable_auto_commit=True
        )
        await self.consumer.start()

        # Run the consumption loop in background
        self.task_consumer = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self):
        try:
            while True:
                # Wait for new messages in batches
                result = await self.consumer.getmany(timeout_ms=1000)
                for tp, messages in result.items():
                    for message in messages:
                        logger.info(f"[Kafka] Received: {message.value}")

                        if self.on_update:
                            try:
                                await self.on_update(message.value)
                            except Exception as e:
                                logger.error(f"[Kafka] on_update failed: {e}")
        except asyncio.CancelledError:
            logger.warning("[Kafka] Consumer task was cancelled.")
        except Exception as e:
            logger.exception(f"[Kafka] Unexpected error in consumer loop: {e}")

    async def stop(self):
        if self.task_consumer:
            self.task_consumer.cancel()
            try:
                await self.task_consumer
            except asyncio.CancelledError:
                logger.info("[Kafka] Consumer task cancelled cleanly")

        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()

    async def send_notifications(self, value: str):
        # Send message to "notifications_send" topic
        await self.producer.send_and_wait("notifications_send", value.encode("utf-8"))

    async def send_logging(self, value: str):
        # Send message to "logging" topic
        await self.producer.send_and_wait("logging", value.encode("utf-8"))
