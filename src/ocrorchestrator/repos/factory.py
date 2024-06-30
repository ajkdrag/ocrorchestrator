from ..repos import BaseRepo, GCSRepo, LocalRepo


class RepoFactory:
    @staticmethod
    def create_repo(name: str, **kwargs) -> BaseRepo:
        if name == "gcs":
            return GCSRepo(**kwargs)
        elif name == "local":
            return LocalRepo(**kwargs)
        else:
            raise ValueError(f"Unknown repo: {name}")
