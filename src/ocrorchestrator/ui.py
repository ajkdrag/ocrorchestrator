import base64
from pathlib import Path
import json
import gradio as gr
from .managers.processor import ProcessorManager
from .config.app_config import AppConfig
from .datamodels.api_io import OCRRequest, OCRRequestOffline
from .routers import predict, predict_offline
from .deps import get_processor
from .utils.img import pil_to_base64
from typing import Any, Dict, List


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
                upload_mode = gr.Radio(
                    ["Single Image", "Multiple Files"],
                    label="Upload Mode",
                    value="Single Image",
                )

                with gr.Group() as single_image_group:
                    image_input = gr.Image(type="pil", label="Upload Single Image")

                with gr.Group(visible=False) as multiple_files_group:
                    file_input = gr.File(
                        label="Upload Multiple Files (max 5)",
                        file_count="multiple",
                        file_types=["image", "pdf"],
                    )

                category_input = gr.Dropdown(
                    choices=config_data["categories"],
                    label="Category",
                    value=default_category,
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

        def toggle_upload_mode(mode):
            return (
                gr.Group(visible=(mode == "Single Image")),
                gr.Group(visible=(mode == "Multiple Files")),
            )

        upload_mode.change(
            toggle_upload_mode,
            inputs=[upload_mode],
            outputs=[single_image_group, multiple_files_group],
        )

        async def process_single_input(
            image: Any,
            category: str,
            task: str,
            fields: str,
            save_options: str,
        ) -> Dict[str, Any]:
            fields = json.loads(fields) if fields else None
            save_options = json.loads(save_options) if save_options else None
            req_dict = {
                "image": pil_to_base64(image),
                "category": category,
                "task": task,
                "fields": fields,
                "save_options": save_options,
            }
            req = OCRRequest(**req_dict)
            processor = get_processor(req, manager)
            result = await predict(req, processor)
            return result.dict()

        async def process_multiple_inputs(
            files: List[Any],
            category: str,
            task: str,
            fields: str,
            save_options: str,
        ) -> List[Dict[str, Any]]:
            results = []
            fields = json.loads(fields) if fields else None
            save_options = json.loads(save_options) if save_options else None
            for file in files:
                with open(file.name, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode()
                req_dict = {
                    "image": image_data,
                    "category": category,
                    "task": task,
                    "fields": fields,
                    "save_options": save_options,
                }
                req = OCRRequest(**req_dict)
                processor = get_processor(req, manager)
                result = await predict(req, processor)
                results.append(result.dict())
            return {"results": results}

        async def process_input(
            mode: str,
            image: Any,
            files: List[Any],
            category: str,
            task: str,
            fields: str,
            save_options: str,
        ) -> Dict[str, Any]:
            if mode == "Single Image" and image is not None:
                return await process_single_input(
                    image, category, task, fields, save_options
                )
            elif mode == "Multiple Files" and files:
                return await process_multiple_inputs(
                    files, category, task, fields, save_options
                )
            else:
                return {
                    "error": "No input provided. Please upload an image or multiple files."
                }

        submit_btn.click(
            process_input,
            inputs=[
                upload_mode,
                image_input,
                file_input,
                category_input,
                task_input,
                fields_input,
                save_options_input,
            ],
            outputs=[output],
        )

        def clear_inputs():
            return (
                "Single Image",  # Reset to Single Image mode
                None,  # Clear single image input
                None,  # Clear multiple files input
                default_category,
                default_task,
                "",  # Clear fields input
                "",  # Clear save options input
                None,  # Clear output
            )

        clear_btn.click(
            clear_inputs,
            outputs=[
                upload_mode,
                image_input,
                file_input,
                category_input,
                task_input,
                fields_input,
                save_options_input,
                output,
            ],
        )

    return interface
