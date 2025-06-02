from typing import Protocol

class Formatter(Protocol):
    def format(self, data): ...

class HTMLFormatter(Formatter):
    def format(self, data): ...

class PDFFormatter(Formatter):
    def format(self, data): ...