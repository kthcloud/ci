from dotenv import load_dotenv
import os
import requests

load_dotenv()


def create_vm(token, body):
    url = os.getenv("godeploy_url")
    if not url:
        raise ValueError("Environment variable kthcloud_api_url not set")

    response = requests.post(
        url + "/vms",
        json=body,
        headers={"Authorization": "Bearer " + token["access_token"]},
    )

    if response.status_code == 200:
        return response.json()["id"]
    else:
        raise Exception("Error creating vm: " + response.text)
        return None


def get_vm(token, vm_id):
    url = os.getenv("godeploy_url")
    if not url:
        raise ValueError("Environment variable kthcloud_api_url not set")

    response = requests.get(
        url + "/vms/" + vm_id,
        headers={"Authorization": "Bearer " + token["access_token"]},
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error creating vm: " + response.text)
        return None


def get_vms(token):
    url = os.getenv("godeploy_url")
    if not url:
        raise ValueError("Environment variable kthcloud_api_url not set")

    response = requests.get(
        url + "/vms",
        headers={"Authorization": "Bearer " + token["access_token"]},
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error creating vm: " + response.text)
        return None


def update_vm(token, vm_id, body):
    url = os.getenv("godeploy_url")
    if not url:
        raise ValueError("Environment variable kthcloud_api_url not set")

    response = requests.post(
        url + "/vms/" + vm_id,
        json=body,
        headers={"Authorization": "Bearer " + token["access_token"]},
    )

    if response.status_code == 201:
        return response.json()["id"]
    else:
        raise Exception("Error creating vm: " + response.text)
        return None


def delete_vm(token, vm_id):
    url = os.getenv("godeploy_url")
    if not url:
        raise ValueError("Environment variable kthcloud_api_url not set")

    response = requests.delete(
        url + "/vms/" + vm_id,
        headers={"Authorization": "Bearer " + token["access_token"]},
    )

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Error creating vm: " + response.text)
        return None
