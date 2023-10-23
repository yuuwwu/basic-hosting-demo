from __future__ import annotations

import datetime
import json
import logging
from enum import Enum
from typing import Any, Dict, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic.v1 import BaseSettings

from starlette import status
from prediction_service.core.data_models import (
    DefaultBadRequest,
    DefaultErrorResponse,
    StatusMessage,
    StatusResponse,
)

logger = logging.getLogger()


class FastAPIStateEnum(str, Enum):
    STARTED = "STARTED"
    INITIALIZING_APP = "INITIALIZING APP"
    INITIALIZING_SERVICES = "INITIALIZING SERVICES"
    UNHEALTHY = "UNHEALTHY"
    READY = "READY"


class DefaultException(Exception):
    def __init__(self, error: DefaultBadRequest):
        self.error = error


def default_exception_handler(request: Request, exc: DefaultException):
    return JSONResponse(
        status_code=exc.error.error.httpStatusCode, content=json.loads(exc.error.json())
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = {
        "detail": exc.errors(),
    }
    logger.error(f"Failed to validate input with response: {response}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(response),
    )


class FastAPIServiceBase:
    """
    TODO
    """

    def __init__(
        self,
        fast_api_options: Optional[Dict[Any, Any]] = None,
        service_name: Optional[str] = None,
        settings: BaseSettings = None,
        launch_initialize_after: float = 5.0,
    ):
        self._api_state = FastAPIStateEnum.STARTED
        self.service_name = service_name or self.__class__.__name__
        self.service_name = self.service_name.upper().replace(" ", "_")
        self.settings = settings
        self.fast_api_options = fast_api_options or {}
        self._initialize_app()
        self.subapps = []
        self.is_initialized = False

        # -- initialization job configuration.
        self.launch_initialize_after = launch_initialize_after
        self.scheduler = AsyncIOScheduler(job_defaults={"misfire_grace_time": 50})

        self._run_initialize()

        # Begin Scheduler
        launch_date = datetime.datetime.now() + datetime.timedelta(
            seconds=self.launch_initialize_after
        )
        logger.info(
            f"FAPI - {self.service_name} adding job initialize_app scheduler to be run at {launch_date}"
        )
        self.scheduler.add_job(
            self._run_initialize,
            "date",
            run_date=launch_date,
            id="initialize_app",
        )

        self.scheduler.start()

    @property
    def api_state(self):
        return self._api_state

    @api_state.setter
    def api_state(self, state: FastAPIStateEnum):
        self._api_state = state

    async def initialize(self, *args, **kwargs) -> None:
        """
        This method should be overridden in child classes to register models and data prep

        Args:
            *args: args required by the child class
            **kwargs: kwargs required by the child class

        Returns:
            None
        """
        pass

    def mount(self, path: str, app: FastAPIServiceBase, name: str = None):
        """
        Mount a subapi to this service.

        Args:
            path (str): The path to the subapi
            app (FastAPI): The subapi
            name (str): The name of the subapi

        Returns:

        """
        self.subapps.append(app)
        self.app.mount(path, app.app, name)

    def is_ready(self) -> bool:
        """
        Method to determine if the service is ready to begin serving requests.
        Returns:
            bool: True if the service has populated everything it needs from external storage, False otherwise

        """
        if not self.is_initialized:
            logger.warning(f"FAPI - Endpoint initialization has not run yet.")
            return False

        if self.api_state in [
            FastAPIStateEnum.PENDING_TERMINATION,
            FastAPIStateEnum.TERMINATED,
        ]:
            logger.warning(f"FAPI - Endpoint is in state {self.api_state}")
            return False

        return True

    async def _run_initialize(self):
        logger.info(
            f"FAPI - {self.service_name} begin initialize method routine ({self.initialize})"
        )
        self.api_state = FastAPIStateEnum.INITIALIZING_SERVICES
        await self.initialize()
        self.is_initialized = True

    def _initialize_app(self) -> None:
        self.api_state = FastAPIStateEnum.INITIALIZING_APP
        self.app = FastAPI(**self.fast_api_options)
        self.app.add_exception_handler(
            RequestValidationError, validation_exception_handler
        )
        self.app.add_exception_handler(DefaultException, default_exception_handler)
        self.app.add_api_route(
            path="/status", endpoint=self.get_endpoint_status, methods=["GET"]
        )

    async def get_endpoint_status(self, request: Request = None) -> StatusMessage:
        """
        Endpoint to return information about the status of the endpoint.  This is also able to be used
        as a Kubernetes liveness/readiness check.

        Returns:
            StatusResponse: StatusMessage with worker status
        Raises:
            DefaultBadRequest: If the endpoint is not ready.
        """
        subapps_ready = True
        for app in self.subapps:
            if not app.is_ready():
                logger.info(f"FAPI - Subapp: {app.service_name} not ready")
                subapps_ready = False
                break

        if not subapps_ready or not self.is_ready():
            bad_request = DefaultBadRequest(
                error=DefaultErrorResponse(
                    httpStatusCode=400,
                    httpMessage="BAD_REQUEST",
                    description="Endpoint not initialized",
                    api_state=self.api_state,
                    details="Endpoint not initialized",
                )
            )
            raise DefaultException(bad_request)

        self.api_state = FastAPIStateEnum.READY

        return StatusMessage(
            subapps=[app.service_name for app in self.subapps],
            api_state=self.api_state,
        )

    def default_error_response(
        self,
        http_status_code: int = 500,
        http_message: str = "InternalServerError",
        description: str = "InternalServerError",
        error_message: str = "Error message",
    ):
        error_response = DefaultErrorResponse(
            httpStatusCode=http_status_code,
            httpMessage=http_message,
            # api_state=self.api_state,
            description=description,
            details=error_message,
        )
        return DefaultBadRequest(error=error_response)
