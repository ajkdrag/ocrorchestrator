# OCR Orchestrator Service

## Overview

The OCR Orchestrator Service is a versatile, FastAPI-based solution designed to serve various OCR (Optical Character Recognition) usecases. It provides a unified interface for processing different types of document images, including cheques, payslips, bank statements, passports, and utility bills.

## Key Features

- Modular architecture supporting multiple OCR processors
- Configurable tasks for different document types and extraction needs
- Support for both online (real-time) and offline processing
- Integration with various AI models and external APIs
- Extensible design for easy addition of new processors and tasks

## Setup

The project uses PDM to manage dependencies. To install the project:

```pdm install --no-self --no-lock```

## Quickstart

Run the script to start the Uvicorn server. 
Gradio UI will be available at http://localhost:8000/ocrorchestrator/ui.
FastAPI Swagger will be available at http://localhost:8000/docs

```
localrun=true bash entrypoint.sh
```

## Folder Structure

```
src/ocrorchestrator/
├── __init__.py
├── config/
│   └── app_config.py
├── datamodels/
│   └── api_io.py
├── managers/
│   └── processor.py
├── processors/
│   ├── __init__.py
│   ├── api.py
│   ├── base.py
│   ├── factory.py
│   ├── gradio.py
│   ├── llm.py
│   └── pytorch.py
├── repos/
│   ├── __init__.py
│   ├── base.py
│   ├── factory.py
│   ├── gcs.py
│   └── local.py
├── routers.py
├── deps.py
├── main.py
├── ui.py
└── utils/
    ├── constants.py
    ├── img.py
    ├── logging.py
    ├── mixins.py
    └── misc.py
```

## Technical Details

### Core Components

1. **FastAPI Service**: The main entry point, handling HTTP requests and responses.
2. **Processor Manager**: Manages the lifecycle of processors and routes requests to the appropriate processor.
3. **Processor Factory**: Creates processor instances based on configuration.
4. **App Config**: Loads and manages the application configuration from YAML files.
5. **Repos**: Handles data storage and retrieval (supports both GCS and local storage).

### Processors

The service uses a modular processor architecture. Current processor types include:

1. **LLMProcessor**: Utilizes large language models (e.g., GPT) for text extraction and analysis.
2. **DocumentValidationProcessor**: Uses PyTorch models for document validation tasks.
3. **ApiProcessor**: Integrates with external OCR APIs.
4. **GradioProcessor**: Leverages Gradio-based models for specific tasks.

### Adding New Processors

To add a new processor:

1. Create a new file in the `processors/` directory (e.g., `new_processor.py`).
2. Define your processor class, inheriting from `BaseProcessor`:

```python
from .base import BaseProcessor

class NewProcessor(BaseProcessor):
    def __init__(self, task_config, general_config, repo):
        super().__init__(task_config, general_config, repo)
        # Initialize any specific attributes

    def _setup(self):
        # Implement any setup logic (e.g., loading models)

    def _process(self, req: OCRRequest) -> Dict[str, Any]:
        # Implement the main processing logic
        # Return the extracted information as a dictionary
```

3. Update `processors/__init__.py` to import your new processor.
4. Update `processors/factory.py` to include the new processor in the creation logic.

### Using Mixins

The project uses mixins to share common functionality across processors. Key mixins include:

- **TorchClassifierMixin**: Provides methods for loading and using PyTorch classifiers.
- **VertexAILangchainMixin**: Offers methods for interacting with VertexAI and Langchain.

To use a mixin in a new processor:

```python
from ..utils.mixins import TorchClassifierMixin
from .base import BaseProcessor

class NewClassifierProcessor(BaseProcessor, TorchClassifierMixin):
    def __init__(self, task_config, general_config, repo):
        super().__init__(task_config, general_config, repo)
        # Mixin-specific initialization

    def _setup(self):
        # Use mixin methods for setup
        self.load_model(self.task_config.model, self.task_config.checkpoint)

    def _process(self, req: OCRRequest) -> Dict[str, Any]:
        # Use mixin methods in processing
        result = self.predict(req.image)
        return {"classification": result}
```

### Configuration

The service uses a YAML configuration file to define processors and their parameters. To add a new processor to the configuration:

```yaml
categories:
  new_category:
    new_task:
      processor: NewProcessor
      model: "path_to_model"
      prompt_template: "path_to_prompt.txt"
      fields:
        - field1
        - field2
      params:
        - param1: value1
        - param2: value2
```

## How to Use the Service

### 1. Setup

Ensure you have the necessary dependencies installed and the service is running. The IT department can provide you with the service endpoint.

### 2. Making a Request

To use the OCR service, send a POST request to the `/predict` endpoint with the following JSON structure:

```json
{
  "image": "base64_encoded_image_string",
  "category": "document_type",
  "task": "specific_task",
  "fields": ["field1", "field2", "field3"]
}
```

- `image`: The document image encoded as a base64 string
- `category`: The type of document (e.g., "cheque", "payslip", "passport")
- `task`: The specific task to perform (e.g., "extract_details", "validate")
- `fields`: List of fields to extract (if applicable)

### 3. Interpreting the Response

The service will respond with a JSON object containing:

```json
{
  "status": "OK",
  "status_code": 200,
  "message": {
    "field1": "extracted_value1",
    "field2": "extracted_value2",
    "field3": "extracted_value3"
  }
}
```

## Supported Integrations/Processors

1. **LLM Processor**: Uses large language models for text extraction and analysis
2. **Document Validation Processor**: Employs PyTorch models for document validation
3. **API Processor**: Integrates with external OCR APIs
4. **Gradio Processor**: Utilizes Gradio-based models for certain tasks
