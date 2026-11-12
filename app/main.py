import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.log import get_logger, setup_logging
from app.middleware import RequestLogMiddleware, register_exception_handlers
from app.router import api_router
from app.utils.net import get_ip_address

setup_logging()
logger = get_logger("app")


def create_app() -> FastAPI:
    application = FastAPI(title=config.APP_NAME)

    if config.CORS_ENABLED:
        origins = config.CORS_ORIGINS
        # 浏览器不允许 credentials + Access-Control-Allow-Origin: *
        application.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials="*" not in origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    application.add_middleware(RequestLogMiddleware)
    register_exception_handlers(application)
    application.include_router(api_router)
    return application


app = create_app()


def run() -> None:
    host = "0.0.0.0"
    port = config.APP_PORT
    local = f"http://localhost:{port}"
    lan = f"http://{get_ip_address()}:{port}"
    print(f"app started at address\n{local}\n{lan}", flush=True)
    logger.info("starting %s env=%s port=%s", config.APP_NAME, config.APP_ENV, port)
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=config.IS_DEV,
        log_level=config.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    run()
