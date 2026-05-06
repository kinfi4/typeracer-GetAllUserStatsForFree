import os

import requests
from dotenv import load_dotenv

load_dotenv()

_LOGIN_URL = 'https://data.typeracer.com/pit/login'


def create_session() -> requests.Session:
    session = requests.Session()

    if not has_credentials():
        return session

    response = session.post(
        _LOGIN_URL,
        data={
            'username': os.getenv('TYPERACER_USERNAME'),
            'password': os.getenv('TYPERACER_PASSWORD'),
            'continueURL': '',
        },
    )

    if not response.ok:
        raise RuntimeError(
            f'TypeRacer login failed (HTTP {response.status_code}). Check your credentials in .env.'
        )

    print('[Auth]: Logged in successfully.')
    return session


def has_credentials() -> bool:
    return bool(os.getenv('TYPERACER_USERNAME') and os.getenv('TYPERACER_PASSWORD'))
