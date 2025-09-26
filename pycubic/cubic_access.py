#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Module implementing a low level wrapper for the LK authentication CubicAccess API."""

import logging

from .auth import AuthClient

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class CubicAccessClient:
    def __init__(self, client: 'AuthClient', serial_number: str) -> None:
        self._client = client
        self._serial_number = serial_number

    async def get_valve(self) -> dict:
        """Get the user's structure."""
        endpoint = f'control/cubic/secure/{self._serial_number}/valve'
        return await self._client.request('GET', endpoint)


    async def open_valve(self) -> dict:
        """Open the valve."""
        return await self.set_valve_state(True)

    async def close_valve(self) -> dict:
        """Close the valve."""
        return await self.set_valve_state(False)

    async def set_valve_state(self, state: bool) -> dict:
        """Set the valve state."""
        endpoint = f'control/cubic/secure/{self._serial_number}/valve/{"open" if state else "close"}'
        return await self._client.request('POST', endpoint)
