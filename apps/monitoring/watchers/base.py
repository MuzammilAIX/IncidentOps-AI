"""Base class for all watchers."""
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BaseWatcher(ABC):
    """Base watcher — subclasses implement run()."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def run(self) -> dict:
        """Run one cycle of the watcher. Return summary dict."""
        ...

    def safe_run(self) -> dict:
        """Run with error handling — logs but doesn't raise."""
        try:
            return self.run()
        except Exception as e:
            self.logger.exception("Watcher %s failed: %s", self.__class__.__name__, e)
            return {"error": str(e)}
