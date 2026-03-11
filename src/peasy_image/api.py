"""peasy-image API client — Access Peasy Image tools via REST API.

Usage::

    from peasy_image.api import PeasyImageAPI

    api = PeasyImageAPI()
    tools = api.list_tools()
"""

from __future__ import annotations

from typing import Any


class PeasyImageAPI:
    """REST API client for peasyimage.com."""

    def __init__(self, base_url: str = "https://peasyimage.com") -> None:
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        import httpx

        url = f"{self.base_url}{path}"
        response = httpx.get(url, params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()

    def list_tools(self) -> list[dict[str, Any]]:
        """List all image tools."""
        return self._get("/api/v1/tools/")  # type: ignore[no-any-return]

    def get_tool(self, slug: str) -> dict[str, Any]:
        """Get a specific tool by slug."""
        return self._get(f"/api/v1/tools/{slug}/")  # type: ignore[no-any-return]

    def list_glossary(self) -> list[dict[str, Any]]:
        """List all glossary terms."""
        return self._get("/api/v1/glossary/")  # type: ignore[no-any-return]

    def get_glossary_term(self, slug: str) -> dict[str, Any]:
        """Get a glossary term by slug."""
        return self._get(f"/api/v1/glossary/{slug}/")  # type: ignore[no-any-return]

    def list_guides(self) -> list[dict[str, Any]]:
        """List all guides."""
        return self._get("/api/v1/guides/")  # type: ignore[no-any-return]

    def get_guide(self, slug: str) -> dict[str, Any]:
        """Get a guide by slug."""
        return self._get(f"/api/v1/guides/{slug}/")  # type: ignore[no-any-return]

    def search(self, query: str) -> dict[str, Any]:
        """Search across tools, glossary, and guides."""
        return self._get("/api/v1/search/", params={"q": query})  # type: ignore[no-any-return]

    def openapi_spec(self) -> dict[str, Any]:
        """Get the OpenAPI 3.1.0 specification."""
        return self._get("/api/openapi.json")  # type: ignore[no-any-return]
