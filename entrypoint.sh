#!/bin/bash

echo "Starting service ..."

echo Running on local? "${localrun:-false}"
echo Num workers: "${workers:-1}"

if [ ${localrun:-false} == "true" ]; then
    # export CONFIG_PATH="gs://ocrorchestrator/configs/config_v2.yaml"
    export CONFIG_PATH="file://my-bucket/configs/config_v2.yaml"
    export GOOGLE_APPLICATION_CREDENTIALS="../secrets/calm-producer-428509-t9-998a14a70eb5.json"
fi

exec pdm run uvicorn --app-dir src ocrorchestrator.main:app --host 0.0.0.0 --port 8182 --workers ${workers:-1} --reload
