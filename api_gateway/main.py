import logging
import asyncio
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from clients.kafka_client import KafkaManager
from routers.auth_service import router as auth_router
from routers.pm_service import router as pm_router
from routers.task_service import router as task_router
from routers.analytics_service import router as analytics_router
from routers.websocket import router as ws_router, ws_manager

logger = logging.getLogger(__name__)


def on_kafka_update(msg_bytes: bytes):
    try:
        data = json.loads(msg_bytes.decode("utf-8"))
        user_ids = data.get("users", [])
        message = data.get("message", "No message")

        loop = asyncio.get_event_loop()
        for user_id in user_ids:
            loop.create_task(ws_manager.send_personal(user_id, message))

    except Exception as e:
        print("[on_kafka_update] Ошибка:", e)


async def lifespan(app: FastAPI):
    settings = get_settings()

    await asyncio.sleep(3)

    app.state.kafka_manager = KafkaManager(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        update_topic="notifications_update",
        on_update=on_kafka_update,
    )
    try:
        await asyncio.wait_for(app.state.kafka_manager.start(), timeout=15)
    except asyncio.TimeoutError:
        logger.error("⏰ KafkaManager.start() timed out")
        raise
    except Exception as e:
        logger.exception("Failed to start KafkaManager: %s", e)
        raise

    yield

    try:
        await app.state.kafka_manager.stop()
    except Exception as e:
        logger.warning("KafkaManager shutdown failed: %s", e)


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(pm_router, prefix="/api/v1/pm")
app.include_router(task_router, prefix="/api/v1", tags=["task"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(ws_router, prefix="/api/v1/ws", tags=["websocket"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
