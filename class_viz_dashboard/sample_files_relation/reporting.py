from abc import ABC, abstractmethod
from typing import Dict, Protocol, final


class Formatter(Protocol):
    """Dependency interface"""

    def format(self, data: Dict[str, str]) -> str: ...


@final
class HTMLFormatter:
    """Dependency implementation"""

    def format(self, data: Dict[str, str]) -> str:
        return f"<h1>{data['title']}</h1><p>{data['content']}</p>"


@final
class PDFFormatter:
    """Dependency implementation"""

    def format(self, data: Dict[str, str]) -> str:
        return f"PDF: {data['title']}\n{data['content']}"


@final
class Report:
    """Depends on Formatter (dependency relationship)"""

    def generate(self, formatter: Formatter) -> str:
        """Dependency injection"""
        return formatter.format(self.data)

    @property
    def data(self) -> Dict[str, str]:
        return {"title": "Annual Report", "content": "..."}