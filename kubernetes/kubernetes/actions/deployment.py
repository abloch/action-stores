import time
import threading
from . import actionstore as action_store
from .clients import get_apps_client
from pydantic import BaseModel
from typing import Optional


class Deployment(BaseModel):
    deployment_name: Optional[str] = None
    namespace: Optional[str] = "default"


@action_store.kubiya_action()
def rollout_restart_deployment(params: Deployment):
    api_client = get_apps_client()

    def patch_deployment():
        nonlocal api_response
        api_response = api_client.patch_namespaced_deployment(
            name=params.deployment_name,
            namespace=params.namespace,
            body={
                "spec": {
                    "template": {"metadata": {"labels": {"date": str(time.time())}}}
                }
            },
        )

    api_response = None
    thread = threading.Thread(target=patch_deployment)
    thread.start()
    thread.join(timeout=10)

    ret = {"status": "success"}

    return ret


@action_store.kubiya_action()
def list_deployment(params: Deployment):
    api_client = get_apps_client()
    api_response = api_client.list_namespaced_deployment(params.namespace)
    return [item.metadata.name for item in api_response.items]
