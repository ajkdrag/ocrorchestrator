import os
from contextlib import asynccontextmanager

import gradio as gr
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .config.app_config import AppConfig
from .datamodels.api_io import AppException, AppResponse
from .managers.processor import ProcessorManager
from .managers.secrets import setup_google_credentials
from .repos.factory import RepoFactory
from .routers import ocr_router
from .ui import create_gradio_interface
from .utils.constants import ErrorCode
from .utils.logging import LoggerMiddleware

config_path = os.environ["CONFIG_PATH"]
log = structlog.get_logger()

log.info(f"Using starter config: {config_path}")

setup_google_credentials()
repo, content = RepoFactory.from_uri(config_path)
config = AppConfig(**content)
proc_manager = ProcessorManager(config, repo)

@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("**** Starting application ****")
    proc_manager._initialize()
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

print(proc_manager)
gr_interface = create_gradio_interface(proc_manager)
app = gr.mount_gradio_app(app, gr_interface, path="/ui")

@app.get("/")
async def root():
    log.info("Root endpoint accessed")
    return {"message": "Hello Bigger Applications!"}
