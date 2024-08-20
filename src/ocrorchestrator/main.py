from contextlib import asynccontextmanager

import gradio as gr
import gradio.route_utils
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .datamodels.api_io import AppException, AppResponse
from .deps import proc_manager
from .routers import ocr_router
from .ui import create_gradio_interface
from .utils.constants import ErrorCode
from .utils.logging import LoggerMiddleware

APP_NAME = "ocrorchestrator"
log = structlog.get_logger()


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


gr_interface = create_gradio_interface(proc_manager)
app = gr.mount_gradio_app(
    app,
    gr_interface,
    path=f"/{APP_NAME}/ui",
)


@app.api_route(f"/{APP_NAME}", methods=["GET", "POST"])
async def root():
    return "200"


@app.get(f"/{APP_NAME}/")
async def rootget():
    return "200"
