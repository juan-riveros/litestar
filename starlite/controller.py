from typing import TYPE_CHECKING, Dict, List, Optional

from typing_extensions import Type

from starlite.exceptions import ImproperlyConfiguredException
from starlite.response import Response
from starlite.types import (
    AFTER_REQUEST_HANDLER,
    BEFORE_REQUEST_HANDLER,
    Guard,
    ResponseHeader,
)
from starlite.utils import normalize_path

if TYPE_CHECKING:  # pragma: no cover
    from starlite.handlers import BaseRouteHandler
    from starlite.provide import Provide
    from starlite.routing import Router


class Controller:
    __slots__ = (
        "dependencies",
        "owner",
        "path",
        "response_headers",
        "response_class",
        "before_request",
        "after_request",
    )

    dependencies: Optional[Dict[str, "Provide"]]
    owner: "Router"
    path: str
    response_headers: Optional[Dict[str, ResponseHeader]]
    response_class: Optional[Type[Response]]
    guards: Optional[List[Guard]]
    # connection-lifecycle hook handlers
    before_request: Optional[BEFORE_REQUEST_HANDLER]
    after_request: Optional[AFTER_REQUEST_HANDLER]

    def __init__(self, owner: "Router"):
        if not hasattr(self, "path") or not self.path:
            raise ImproperlyConfiguredException("Controller subclasses must set a path attribute")

        for key in [
            "dependencies",
            "response_headers",
            "response_class",
            "guards",
            "before_request",
            "before_websocket",
            "after_request",
            "after_websocket",
        ]:
            if not hasattr(self, key):
                setattr(self, key, None)

        self.path = normalize_path(self.path)
        self.owner = owner
        for route_handler in self.get_route_handlers():
            route_handler.owner = self

    def get_route_handlers(self) -> List["BaseRouteHandler"]:
        """
        Returns a list of route handlers defined on the controller
        """
        from starlite.handlers import (  # pylint: disable=import-outside-toplevel
            BaseRouteHandler,
        )

        return [
            getattr(self, f_name)
            for f_name in dir(self)
            if f_name not in dir(Controller) and isinstance(getattr(self, f_name), BaseRouteHandler)
        ]
