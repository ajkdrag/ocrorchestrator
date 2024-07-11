#!/bin/bash

echo "Starting service ..."

echo Running on local? "${localrun:-false}"
echo Num workers: "${workers:-1}"

if [ ${localrun:-false} == "true" ]; then
    export REMOTE_PATH_OLD="ocrorchestrator"
    export CONFIG_PATH="gs://ocrorchestrator/configs/config_v1.yaml"
    export GOOGLE_APPLICATION_CREDENTIALS="../../secrets/calm-producer-428509-t9-b428a168489d.json"
fi

exec pdm run uvicorn --app-dir src ocrorchestrator.main:app --host 0.0.0.0 --port 8181 --workers ${workers:-1}
