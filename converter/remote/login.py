from requests import Session
from os import environ

USER = environ.get('KSI_USER')
PASSWORD = environ.get('KSI_PASSWORD')


def get_session(backend_url: str) -> Session:
    assert USER is not None
    assert PASSWORD is not None

    s = Session()

    r = s.post(f"{backend_url}/auth", data={
        'username': USER,
        'password': PASSWORD,
        'grant_type': 'password'
    })

    assert r.ok

    s.headers.update({
        'Authorization': f"Bearer {r.json()['access_token']}"
    })
    return s
