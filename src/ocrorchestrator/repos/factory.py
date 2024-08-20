import os
from typing import Any
from urllib.parse import urlparse

import structlog

from ..datamodels.api_io import AppException
from ..repos import BaseRepo, GCSRepo, LocalRepo
from ..utils.constants import LOCAL_DIR, LOCAL_REPO, ErrorCode

log = structlog.get_logger()


class RepoFactory:
    def from_uri(
        uri: str,
        download=False,
        read_prefix=True,
    ) -> tuple[BaseRepo, Any]:
        try:
            parsed_uri = urlparse(uri)
            scheme = parsed_uri.scheme
            base = parsed_uri.netloc
            prefix = parsed_uri.path.lstrip("/")

            if scheme == "gs":
                repo = GCSRepo(base, LOCAL_DIR)
            elif scheme in {"file"}:
                homedir = os.path.join(LOCAL_REPO, base)
                repo = LocalRepo(homedir, homedir)
            else:
                raise AppException(
                    ErrorCode.REPO_INITIALIZATION_ERROR,
                    f"Unknown scheme: {scheme}",
                )
            if not read_prefix:
                return repo, prefix
            if download:
                return repo, repo.download_obj(prefix)
            else:
                return repo, repo.get_obj(prefix)
        except Exception as e:
            if isinstance(e, AppException):
                raise e
            error_code = ErrorCode.REPO_INITIALIZATION_ERROR
            log.error(
                f"Failed to init repository from uri: {uri}",
                status_code=error_code.status_code,
                status=error_code.name,
                exc_info=True,
            )
            raise AppException(
                error_code,
                f"Failed to initialize repo: {str(e)}",
            ) from e