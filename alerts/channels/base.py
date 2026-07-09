from abc import ABC, abstractmethod
from ..models import AlertEvent

class BaseChannel(ABC):
    @abstractmethod
    def send(self, event: AlertEvent):
        """
        Dispatch the alert event to the channel destination.
        """
        pass
