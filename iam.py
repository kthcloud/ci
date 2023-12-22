from dotenv import load_dotenv
import os
import requests

load_dotenv()


def get_oidc_token(username, password):
    client_id = os.getenv("oidc_resource")
    client_secret = os.getenv("oidc_secret")
    token_url = os.getenv("oidc_auth_server_url")

    if not client_id:
        raise ValueError("Environment variable oidc_resource not set")

    if not client_secret:
        raise ValueError("Environment variable oidc_secret not set")

    if not token_url:
        raise ValueError("Environment variable oidc_auth_server_url not set")

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    response = requests.post(token_url, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error getting token: " + response.text)
        return None
