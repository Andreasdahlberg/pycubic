#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Module implementing a low level wrapper for the LK authentication Cubic API."""

import logging

from .auth import AuthClient

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class CubicClient:
    """Client for interacting with the Cubic API endpoints."""

    def __init__(self, client: 'AuthClient', serial_number: str) -> None:
        self._client = client
        self._serial_number = serial_number

    async def get_measurement(self, bypass: bool = False) -> dict:
        """Get measurement data."""
        endpoint = f'service/cubic/secure/{self._serial_number}/measurement/{1 if bypass else 0}'
        logger.debug(f'Fetching measurement data from endpoint: {endpoint}')
        return await self._client.request('GET', endpoint)

    async def get_configuration(self, bypass: bool = False) -> dict:
        """Get configuration data."""
        endpoint = f'service/cubic/secure/{self._serial_number}/configuration/{1 if bypass else 0}'
        logger.debug(f'Fetching configuration data from endpoint: {endpoint}')
        return await self._client.request('GET', endpoint)
