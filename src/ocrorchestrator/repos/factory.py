import structlog

from ..datamodels.api_io import AppException
from ..repos import BaseRepo, GCSRepo, LocalRepo
from ..utils.constants import ErrorCode

log = structlog.get_logger()


class RepoFactory:
    @staticmethod
    def create_repo(name: str, **kwargs) -> BaseRepo:
        try:
            if name == "gcs":
                return GCSRepo(**kwargs)
            elif name == "local":
                return LocalRepo(**kwargs)
            else:
                raise AppException(
                    ErrorCode.REPO_INITIALIZATION_ERROR,
                    f"Unknown repo: {name}",
                )
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            log.error(
                f"Failed to init repository with kwargs: {kwargs}",
                exc_info=True,
                repo=name,
            )
            raise AppException(
                ErrorCode.REPO_INITIALIZATION_ERROR,
                f"Failed to initialize {name} repo: {str(e)}",
            )
