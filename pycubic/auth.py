#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Module implementing a low level wrapper for the LK authentication Auth API."""

import time
import logging
import aiohttp

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class AuthClient:
    """Authenticated HTTP client for the LK Systems CubicSecure API.

    This client handles token authentication with automatic token refresh 
    capabilities. It manages login, token storage, and ensures all requests
    include valid authentication headers.

    Args:
        base_url: The base URL for the LK Systems CubicSecure API. 

    Raises:
        aiohttp.ClientResponseError: If any HTTP request fails. 

    Examples:
        >>> client = AuthClient('https://link2.lk.nu')
        >>> await client.login('user@example.com', 'password')
        >>> response = await client.request('GET', '/some/endpoint')
    """

    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session = aiohttp.ClientSession()  # TODO: Set base URL here!
        self._access_token = None
        self._refresh_token = None
        self._access_token_expire = None
        self._refresh_token_expire = None

    async def login(self, email: str, password: str):
        """Authenticate with the LK API and store the tokens."""
        url = f'{self._base_url}/auth/auth/login'
        payload = {'email': email, 'password': password}
        async with self._session.post(url, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                self._access_token = data.get('accessToken')
                self._refresh_token = data.get('refreshToken')
                self._access_token_expire = data.get('accessTokenExpire')
                self._refresh_token_expire = data.get('refreshTokenExpire')
                return data
            else:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f'Login failed: {await response.text()}',
                    headers=response.headers
                )

    def is_access_token_expired(self) -> bool:
        """Check if access token is expired or close to expiring."""
        if not self._access_token_expire:
            return True
        # Add additional time before actual expiry to compensate for clock drift.
        return time.time() + 60 > self._access_token_expire

    @property
    def access_token_expire(self):
        """Get the access token expiry time."""
        return self._access_token_expire

    async def is_current_token_valid(self):
        """Check if the current access token is still valid."""
        if not self._access_token:
            return False

        url = f'{self._base_url}/auth/validate/token'
        headers = {'Authorization': f'Bearer {self._access_token}'}
        async with self._session.get(url, headers=headers) as response:
            return response.status == 200

    # TODO: Set check_server to False for testing only!
    async def _ensure_valid_access_token(self, check_server: bool = False):
        """Ensure we have a valid access token, refresh if needed."""
        if self.is_access_token_expired():
            await self.refresh_token()
            return

        if check_server and not await self.is_current_token_valid():
            await self.refresh_token()

    async def get_user_id(self) -> str:
        """Get the current user ID."""
        user = await self.request('GET', '/auth/auth/user')
        return user['userId']

    async def refresh_token(self) -> None:
        """Refresh the access token using the stored refresh token."""
        if not self._refresh_token:
            raise ValueError('No refresh token available. Please login first.')

        url = f'{self._base_url}/auth/auth/refresh'
        headers = {'Authorization': f'Bearer {self._access_token}'}
        payload = {'refreshToken': self._refresh_token}
        async with self._session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                self._access_token = data.get('accessToken')
                self._refresh_token = data.get('refreshToken')
                self._access_token_expire = data.get('accessTokenExpire')
                self._refresh_token_expire = data.get('refreshTokenExpire')
            else:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f'Token refresh failed: {await response.text()}',
                    headers=response.headers
                )

    async def request(self, method: str, endpoint: str, **kwargs) -> dict:
        """ Make an authenticated request, auto-refreshing token if needed.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional arguments to pass to aiohttp request.

        Returns:
            dict: Parsed JSON response from the API.
        """
        await self._ensure_valid_access_token()
        headers = dict(kwargs.get('headers', {}))
        headers['Authorization'] = f'Bearer {self._access_token}'
        kwargs['headers'] = headers

        url = f'{self._base_url}/{endpoint.lstrip("/")}'
        logger.debug(f'Making request to {url} with method {method}')
        async with self._session.request(method, url, **kwargs) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status,
                    message=f'Failed to execute request {response.status} - {await response.text()}',
                    headers=response.headers
                )

    async def close(self):
        """Close the HTTP session."""
        await self._session.close()
