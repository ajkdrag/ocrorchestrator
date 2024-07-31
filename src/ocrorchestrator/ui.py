import json
import gradio as gr
from .managers.processor import ProcessorManager
from .config.app_config import AppConfig
from .datamodels.api_io import OCRRequest
from .routers import predict
from .deps import get_processor
from .utils.img import pil_to_base64
from typing import Any, Dict


def get_categories_and_tasks(config: AppConfig) -> Dict[str, Any]:
    print(config)
    categories = list(config.categories.keys())
    tasks = {cat: list(tasks.keys()) for cat, tasks in config.categories.items()}
    return {"categories": categories, "tasks": tasks}


def create_gradio_interface(manager: ProcessorManager):
    config_data = get_categories_and_tasks(manager.app_config)
    default_category = config_data["categories"][0]
    default_task = config_data["tasks"][default_category][0]

    with gr.Blocks(theme=gr.themes.Soft()) as interface:
        gr.Markdown("# OCR Service")

        with gr.Row():
            with gr.Column(scale=1):
                image_input = gr.Image(type="pil", label="Upload Image")
                category_input = gr.Dropdown(
                    choices=config_data["categories"], label="Category", value=default_category
                )
                task_input = gr.Dropdown(
                    choices=config_data["tasks"]["default"],
                    label="Task",
                    value=default_task,
                )

                def update_tasks(category):
                    return gr.Dropdown(choices=config_data["tasks"].get(category, []))

                category_input.change(
                    update_tasks,
                    inputs=[category_input],
                    outputs=[task_input],
                )

                fields_input = gr.TextArea(
                    label="Fields (JSON format)",
                    placeholder='[{"name": "field1", "description": "Description 1"}]',
                    value="",
                )
                save_options_input = gr.TextArea(
                    label="Save Options (JSON format)",
                    placeholder='{"path": "/path/to/save", "format": "json"}',
                    value="",
                )

            with gr.Column(scale=1):
                output = gr.JSON(label="Output")

        submit_btn = gr.Button("Submit")
        clear_btn = gr.Button("Clear")

        async def process_input(
            image: str,
            category: str,
            task: str,
            fields: str,
            save_options: str,
        ):
            fields = json.loads(fields) if fields else None
            save_options = json.loads(save_options) if save_options else None
            req_dict = {
                "image": pil_to_base64(image),
                "category": category,
                "task": task,
                "fields": fields,
                "save_options": None,
            }
            req = OCRRequest(**req_dict)
            processor = get_processor(req, manager)
            result = await predict(req, processor)
            return result.dict()

        submit_btn.click(
            process_input,
            inputs=[
                image_input,
                category_input,
                task_input,
                fields_input,
                save_options_input,
            ],
            outputs=[output],
        )

        clear_btn.click(
            lambda: (None, default_category, default_task, None, None, None),
            outputs=[
                image_input,
                category_input,
                task_input,
                fields_input,
                save_options_input,
                output,
            ],
        )

    return interface
