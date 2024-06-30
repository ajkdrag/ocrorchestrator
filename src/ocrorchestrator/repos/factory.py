from ..datamodels.api_io import AppException
from ..repos import BaseRepo, GCSRepo, LocalRepo
from ..utils.constants import ErrorCode


class RepoFactory:
    @staticmethod
    def create_repo(name: str, **kwargs) -> BaseRepo:
        if name == "gcs":
            return GCSRepo(**kwargs)
        elif name == "local":
            return LocalRepo(**kwargs)
        else:
            raise AppException(
                ErrorCode.INITIALIZATION_ERROR,
                f"Unknown repo: {name}",
            )
