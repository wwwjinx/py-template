from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from app import config
from app.router import api_router

app = FastAPI(title=config.APP_NAME)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "ok", "app": config.APP_NAME}


def run() -> None:
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.APP_PORT,
        reload=config.APP_ENV == "dev",
    )


if __name__ == "__main__":
    run()