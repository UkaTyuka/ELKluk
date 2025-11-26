from fastapi import FastAPI, Request
import logging
import json
import time
import os

app = FastAPI(title="ELK Demo API")

# ------------------- JSON ЛОГИ -------------------

logger = logging.getLogger("api_logger")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

handler = logging.StreamHandler()

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)

handler.setFormatter(JsonFormatter())
logger.addHandler(handler)

# ------------------- MIDDLEWARE ДЛЯ ВРЕМЕНИ -------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)

    logger.info("request", extra={"extra": {
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "response_time_ms": duration
    }})

    return response

# ------------------- ENDPOINTS -------------------

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/info")
async def info():
    load = round((time.time() % 100) / 10, 2)
    logger.info("info called", extra={"extra": {
        "endpoint": "/info",
        "fake_load": load
    }})
    return {"version": "1.0.0", "load": load}

@app.get("/")
async def root():
    return {"message": "Hello from ELK API!"}
