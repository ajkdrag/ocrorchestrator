from abc import ABC, abstractmethod


class BaseArtifact(ABC):
    def __init__(self, location: str):
        self.location = location
