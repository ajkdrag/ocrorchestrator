import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from .config.app_config import AppConfig
from starlette.exceptions import HTTPException as StarletteHTTPException
from .managers.processor import ProcessorManager
from .managers.secrets import setup_google_credentials
from .repos.factory import RepoFactory
from .routers import ocr_router
from .utils.logging import LoggerMiddleware
from .datamodels.api_io import AppException, AppResponse
from .utils.constants import ErrorCode

config_path = os.environ["CONFIG_PATH"]
log = structlog.get_logger()

log.info(f"Using starter config: {config_path}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("**** Starting application ****")
    setup_google_credentials()
    repo, content = RepoFactory.from_uri(config_path)
    config = AppConfig(**content)
    proc_manager = ProcessorManager(config, repo)
    app.state.proc_manager = proc_manager
    yield
    log.info("**** Shutting down application ****")
    proc_manager.cleanup()
    app.state.proc_manager = None


async def ocr_exception_handler(request: Request, exc: Exception):
    if not isinstance(exc, AppException):
        exc = AppException(
            ErrorCode.INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )
    log.error(
        f"Exception occurred: {exc.detail}",
        status_code=exc.status_code,
        status=exc.status,
        exc_info=True,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=AppResponse(
            status=exc.status,
            status_code=exc.status_code,
            message=exc.detail,
        ).dict(),
    )


async def rest_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=AppResponse(
            status="Unknown HTTP error",
            status_code=exc.status_code,
            message=exc.detail,
        ).dict(),
    )


app = FastAPI(lifespan=lifespan)
app.add_middleware(LoggerMiddleware)
app.include_router(ocr_router)
app.add_exception_handler(Exception, ocr_exception_handler)
app.add_exception_handler(HTTPException, ocr_exception_handler)
app.add_exception_handler(StarletteHTTPException, rest_exception_handler)


@app.get("/")
async def root():
    log.info("Root endpoint accessed")
    return {"message": "Hello Bigger Applications!"}
