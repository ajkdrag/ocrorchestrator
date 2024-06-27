## Input format

```json
{
  "image": "base64_encoded_string",
  "category": "string",
  "task_type": "string",
  "fields": ["string"]
}
```

- `image`: Base64 encoded image string
- `category`: Document/Domain category (e.g., "bank_cheque", "proof_of_funds")
- `task_type`: Type of task ("extraction", "validation", or "classification")
- `fields`: Array of fields to process or return, depending on the task_type

Examples:

For classification, model will always give `class` and `confidence`.
For validation, model will always give `is_valid` and `reason`.
For extraction, model will give all fields specified in config.
If we only want subset of whatever model is capturing,
use the `outputs` attribute and pass whatever fields are required. 


1. Extraction:


```json
{
  "image": "base64_encoded_string",
  "category": "bank_cheque",
  "task_type": "extraction",
  "outputs": ["name", "net_amount"]
}
```

2. Validation:

```json
{
  "image": "base64_encoded_string",
  "category": "proof_of_funds",
  "task_type": "validation",
  "outputs": ["is_valid", "reason"]
}
```

3. Classification:

```json
{
  "image": "base64_encoded_string",
  "category": "proof_of_funds",
  "task_type": "classification",
  "outputs": ["class", "confidence"]
}
```

## Sample config file

```yaml
official_check:
    validation:
        processor: llm
        handler: gemini-1.5-pro
        extra_kwargs:
        prompt_template: doc_validation_v1.txt
        invalid: ['blank', 'blurred', 'dirty']
    classification:
    extraction:
        processor: microservice
        handler: http://myextservice/predict/
        extra_kwargs: {'entity': 'payee'}
        prompt_template:
        fields: ['account_no', 'routing_no']
proof_of_funds:
    validation:
        processor: custom
        handler: DocValidationProcessor
        extra_kwargs: {'model': 'pof_val_v1.pt'}
        prompt_template:
        classes: ['valid', 'invalid']
    classification:
        processor: llm
        handler: gemini-pro-vision
        extra_kwargs: 
        prompt_template: doc_classification_v2.txt
        classes: ['bank statement', 'payslip', 'invoice']
    extraction:
        processor: llm
        handler: gemini-pro-vision
        extra_kwargs: 
        prompt_template: doc_extraction_v2.txt
        fields: ['name', 'document_date', 'net_amount', 'currency']
```

## Folder Structure

```bash
├── notebooks
├── notes.md
├── pdm.lock
├── __pycache__
├── pyproject.toml
├── README.md
├── src
│   └── ocrorchestrator
│       ├── config
│       │   └── app_config.py
│       ├── __init__.py
│       ├── main.py
│       ├── processors
│       │   ├── base.py
│       │   ├── custom.py
│       │   ├── factory.py
│       │   ├── __init__.py
│       │   ├── llm.py
│       │   └── microservice.py
│       ├── __pycache__
│       └── utils
│           ├── artifacts.py
│           └── gcs.py
└── tests
    ├── __init__.py
    └── __pycache__
```


## Refresh mechanism

When a refresh is triggered (prompt file is updated, new model updated etc):

- ArtifactManager clears its cached prompts and models, then reinitializes
- ProcessorFactory clears its existing processors
- AppConfig updates its internal configuration


The ProcessorFactory reinitializes by:

- Getting the updated configuration from ArtifactManager
- Iterating through the configuration
- Creating new processor instances based on the updated configuration


This ensures that all components are using the most up-to-date configuration, prompts, and models after a refresh.
This design allows for dynamic updates to the system's configuration and processing logic without requiring a full restart of the application.
It's particularly useful in environments where configurations or models might need to be updated frequently or on-the-fly.

