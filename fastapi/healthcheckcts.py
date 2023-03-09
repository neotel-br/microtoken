from fastapi_healthcheck.domain import HealthCheckInterface
from fastapi_healthcheck.service import HealthCheckBase
from fastapi_healthcheck.enum import HealthCheckStatusEnum
from typing import List
from http.client import HTTPSConnection
from ssl import _create_unverified_context

TIMEOUT = 15


class HealthCheckCTS(HealthCheckBase, HealthCheckInterface):
    _tags: List[str]
    _connectionUri: str
    _healthyCode: int
    _unhealthyCode: int

    def __init__(
        self,
        connectionUri: str,
        alias: str,
        tags: List[str],
        healthyCode: int = 200,
        unhealthyCode: int = 500,
    ) -> None:
        self.setConnectionUri(connectionUri)
        self._alias = alias
        self._tags = tags
        self._healthyCode = healthyCode
        self._unhealthyCode = unhealthyCode

    def __checkHealth__(self) -> bool:
        context = _create_unverified_context()
        conn = HTTPSConnection(self._connectionUri, context=context, timeout=TIMEOUT)
        conn.request("GET", "/")
        r = conn.getresponse()

        if r.status == self._healthyCode:
            conn.close()
            return HealthCheckStatusEnum.HEALTHY
        conn.close()
        return HealthCheckStatusEnum.UNHEALTHY
