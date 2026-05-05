from abc import ABC, abstractmethod


class Observer(ABC):
    @abstractmethod
    def update(self, data):
        pass


class Subject:

    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, data=None):
        for observer in self._observers:
            observer.update(data)