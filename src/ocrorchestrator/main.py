from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config.app_config import AppConfig
from .datamodels.api_io import AppException, AppResponse
from .managers.processor import ProcessorManager
from .repos.factory import RepoFactory
from .routers import ocr_router
from .utils.logging import LoggerMiddleware

# constants
PKG_ROOT = Path(__file__).parent
PROJ_ROOT = PKG_ROOT.parent.parent
config_path = "configs/config_v1.yaml"

log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("**** Starting application ****")
    base_path = PROJ_ROOT.joinpath("data/my-bucket").as_posix()
    repo = RepoFactory.create_repo("local", base_path=base_path)
    config = AppConfig(**repo.get_yaml(config_path))
    proc_manager = ProcessorManager(config, repo)
    app.state.repo = repo
    app.state.config = config
    app.state.proc_manager = proc_manager
    yield
    log.info("**** Shutting down application ****")
    app.state.repo = None
    app.state.config = None
    app.state.proc_manager = None


async def ocr_exception_handler(request: Request, exc: AppException):
    log.error(f"Exception occurred: {exc.detail}", status_code=exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=AppResponse(
            status=exc.status,
            status_code=exc.status_code,
            message=exc.detail,
        ).dict(),
    )


app = FastAPI(lifespan=lifespan)
app.add_middleware(LoggerMiddleware)
app.include_router(ocr_router)
app.add_exception_handler(AppException, ocr_exception_handler)


@app.get("/")
async def root():
    log.info("Root endpoint accessed")
    return {"message": "Hello Bigger Applications!"}
