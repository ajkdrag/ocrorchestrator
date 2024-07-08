import base64
import json
import os
from pathlib import Path

import structlog
from kubernetes import client, config

from ..utils.constants import GCP_ENV_VAR

log = structlog.get_logger()


def is_k8s_env():
    return "KUBERNETES_SERVICE_HOST" in os.environ


def verify_google_credentials():
    if GCP_ENV_VAR in os.environ:
        creds_path = os.environ[GCP_ENV_VAR]
        if os.path.exists(creds_path):
            try:
                with open(creds_path, "r") as f:
                    json.load(f)
                log.info(f"{GCP_ENV_VAR} successfully set and validated")
            except json.JSONDecodeError:
                log.error(f"Invalid JSON in {GCP_ENV_VAR} file: {creds_path}")
        else:
            log.error(f"{GCP_ENV_VAR} file not found: {creds_path}")
    else:
        log.warning(f"{GCP_ENV_VAR} not set")


def setup_google_credentials():
    GCP_ENV_VAR = "GOOGLE_APPLICATION_CREDENTIALS"

    if GCP_ENV_VAR in os.environ:
        log.info(f"{GCP_ENV_VAR} is already set")
    elif is_k8s_env():
        log.info("Running in Kubernetes environment")

        secret_name = os.environ["secret-name"]
        secret_namespace = os.environ["secret-namespace"]
        sa_filename = os.environ["sa-filename"]

        try:
            config.load_incluster_config()
            v1 = client.CoreV1Api()
            secret = v1.read_namespaced_secret(secret_name, secret_namespace)

            creds_b64 = secret.data[sa_filename]

            if creds_b64:
                creds_json = base64.b64decode(creds_b64).decode("utf-8")
                creds_file = Path(f"/tmp/{GCP_ENV_VAR}.json")
                creds_file.write_text(creds_json)
                os.environ[GCP_ENV_VAR] = str(creds_file)
                log.info(f"Set {GCP_ENV_VAR} to {creds_file}")
            else:
                log.warning(f"{GCP_ENV_VAR} not found in the secret")
        except Exception as e:
            log.error(f"Error reading Kubernetes secret: {str(e)}")
    else:
        log.warning(f"Not in Kubernetes and {GCP_ENV_VAR} not set")
        return

    verify_google_credentials()
