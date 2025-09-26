#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Module implementing a low level wrapper for the LK authentication User API."""

import logging

from .auth import AuthClient

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class UserClient:
    def __init__(self, client: 'AuthClient'):
        self._client = client
        self._user_id = None

    async def _get_user_data(self, data_type: str, bypass: bool = False) -> dict:
        """Generic method to get user data by type."""
        if not self._user_id:
            self._user_id = await self._client.get_user_id()
            logger.debug(f'Fetched user ID: {self._user_id}')
        endpoint = f'service/users/user/{self._user_id}/{data_type}/{1 if bypass else 0}'
        logger.debug(f'Fetching user data from endpoint: {endpoint}')
        return await self._client.request('GET', endpoint)

    async def get_structure(self, bypass: bool = False) -> dict:
        """Get the user's structure."""
        return await self._get_user_data('structure', bypass)

    async def get_information(self, bypass: bool = False) -> dict:
        """Get the user's information."""
        return await self._get_user_data('information', bypass)
