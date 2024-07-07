import os

import structlog

from ..datamodels.api_io import AppException
from ..repos import BaseRepo, GCSRepo, LocalRepo
from ..utils.constants import PROJ_ROOT, ErrorCode

log = structlog.get_logger()


class RepoFactory:
    @staticmethod
    def create_repo(
        name: str,
        remote_path: str = None,
        **kwargs,
    ) -> BaseRepo:
        try:
            local_dir = PROJ_ROOT.joinpath("data/local").as_posix()
            remote = os.environ.get("REMOTE_PATH", remote_path)
            local = os.environ.get("LOCAL_DIR", local_dir)

            if name == "gcs":
                return GCSRepo(remote, local, **kwargs)
            elif name == "local":
                return LocalRepo(remote, remote, **kwargs)
            else:
                raise AppException(
                    ErrorCode.REPO_INITIALIZATION_ERROR,
                    f"Unknown repo: {name}",
                )
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            error_code = ErrorCode.REPO_INITIALIZATION_ERROR
            log.error(
                f"Failed to init repository with kwargs: {kwargs}",
                status_code=error_code.status_code,
                status=error_code.name,
                exc_info=True,
                repo=name,
            )
            raise AppException(
                error_code,
                f"Failed to initialize {name} repo: {str(e)}",
            )
