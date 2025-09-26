#!/usr/bin/env python3
# -*- coding: utf-8 -*

"""Example script to demonstrate usage of the pycubic API wrapper."""

import asyncio
from pycubic import AuthClient, UserClient, CubicClient, CubicAccessClient

try:
    from secret import EMAIL, PASSWORD
except ImportError:
    print("Please create a secret.py file with your EMAIL and PASSWORD.")
    exit(1)


async def main():
    client = AuthClient(base_url='https://link2.lk.nu')
    try:
        await client.login(email=EMAIL, password=PASSWORD)
        print(
            f'Logged in, access token expires in {client.access_token_expire} seconds')

        user_client = UserClient(client)
        structure = await user_client.get_structure()
        # Assuming we want to interact with the first device in the first real estate
        serial_number = structure[0]['realestateMachines'][0]['identity']

        cubic_client = CubicClient(client, serial_number)
        measurement = await cubic_client.get_measurement()
        print(f'Total volume today: {measurement['volumeTotalDay']} l')

        cubic_access_client = CubicAccessClient(client, serial_number)
        valve_state = await cubic_access_client.get_valve()
        print('Valve state:', valve_state)

    except Exception as e:
        print('Error:', e)
    finally:
        print('Closing client...')
        await client.close()

if __name__ == '__main__':
    asyncio.run(main())
