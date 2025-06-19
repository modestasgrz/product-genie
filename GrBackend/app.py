# import numpy as np
# from scipy import interpolate
import json
import os
from pathlib import Path

import gradio as gr
import yaml
from llm_service_domain.ollama import OllamaLLMService
from src.apiProcess import renderImageProcess
from src.schemas import ShotCompositionParams
from utils.config import Config
from utils.exceptions import JSONDecodeRetranslateError, ShotCompositionException

# Path to your YAML configuration file

# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)

# Get the directory containing the current file
current_directory = os.path.dirname(current_file_path)

# If you want the path to another file adjacent to the current file (e.g., 'config.yaml'):
yaml_file = os.path.join(current_directory, "config.yaml")

# Load the YAML file
with open(yaml_file, "r") as file:
    config = yaml.safe_load(file)

# Set the environment variables
for key, value in config.get("environment", {}).items():
    os.environ[key] = value

# Verify the environment variables have been set
print("BLENDER_APP", os.getenv("BLENDER_APP"))
print("BLENDER_SCRIPT_FILE", os.getenv("BLENDER_SCRIPT_FILE"))  # prints: True
print("BLENDER_BASE_FILE", os.getenv("BLENDER_BASE_FILE"))  # prints: True


schema = None


def _load_prompting_template(prompt_template_path: str | Path | None = None) -> str:
    if prompt_template_path is None:
        prompt_template_path = "assets/prompting_template_v2.txt"

    with open(prompt_template_path, "r") as f:
        return str.strip(f.read())


MODEL = "qwen2.5:7b"
LLM_TRY_COUNT_LIMIT = 3
OLLAMA_SERVICE = OllamaLLMService(
    config=Config(config_path=Path(__file__).parent / "configs/llm_config.json")
)
PROMPTING_TEMPLATE = _load_prompting_template(
    prompt_template_path=Path(__file__).parent / "assets/prompting_template_v3.txt"
)


def jsonFromInputs(
    movement,
    vfx_shot,
    environment_color,
    movement_speed,
    movement_interpolation,
    vfx_shot_speed,
    vfx_shot_interpolation,
):
    return {
        "MOVEMENT": {
            "NAME": movement,
            "SPEED": movement_speed,
            "INTERPOLATION": movement_interpolation,
        },
        "ENVIRONEMENT": {"BACKGOUND_COLOR": environment_color},
        "VFX_SHOT": {
            "NAME": vfx_shot,
            "SPEED": vfx_shot_speed,
            "INTERPOLATION": vfx_shot_interpolation,
        },
    }


def seperate_args(*args):
    glb_path = args[0]
    glb_name = args[0].orig_name
    movement = args[1]
    vfx_shot = args[2]
    environment_color = args[3]

    movement_speed = args[4]
    movement_interpolation = args[5]
    vfx_shot_speed = args[6]
    vfx_shot_interpolation = args[7]

    return (
        glb_path,
        glb_name,
        movement,
        vfx_shot,
        environment_color,
        movement_speed,
        movement_interpolation,
        vfx_shot_speed,
        vfx_shot_interpolation,
    )


def json_create(*args):
    kwarg = seperate_args(*args)

    json = jsonFromInputs(*kwarg)

    return json


def call_llm_analysis_decode(*args):
    prompt = PROMPTING_TEMPLATE % args[1]
    llm_try_count = 0
    while llm_try_count < LLM_TRY_COUNT_LIMIT:
        try:
            llm_output = OLLAMA_SERVICE.call(llm_prompt=prompt, model=MODEL)
            print(f"LLM Output:\n{llm_output}")  #! DEBUG
            shot_composition_params = ShotCompositionParams(**json.loads(llm_output))
            break
        except (json.JSONDecodeError, JSONDecodeRetranslateError) as e:
            llm_try_count += 1
            msg = f"""
            Failed to decode full LLM output to JSON object.
            LLM Output: {llm_output},
            Full error message: {e!s},
            Retrying... Retries left: {LLM_TRY_COUNT_LIMIT - llm_try_count}
            """
            print(msg)
        except Exception as e:
            llm_try_count += 1
            msg = f"""
            An error occured.
            Full error message: {e!s},
            Retrying... Retries left: {LLM_TRY_COUNT_LIMIT - llm_try_count}
            """
            print(msg)

    if llm_try_count >= LLM_TRY_COUNT_LIMIT:
        raise ShotCompositionException(
            "LLM Service retry count exceeded. LLM might be working improperly."
        )

    return jsonFromInputs(
        movement=shot_composition_params.movement,
        vfx_shot=shot_composition_params.vfx_shot,
        environment_color=args[2],
        movement_speed=shot_composition_params.movement_speed,
        movement_interpolation=shot_composition_params.movement_interpolation,
        vfx_shot_speed=shot_composition_params.vfx_shot_speed,
        vfx_shot_interpolation=shot_composition_params.vfx_shot_interpolation,
    )


def generate_file(*args):
    # json_generation_data = json_create(*args)
    json_generation_data = call_llm_analysis_decode(*args)
    video_out_path = renderImageProcess(args[0].name, json_generation_data)
    return video_out_path


# def video_out(*args):
# def image_out(*args):
#     json = json_create(*args)
#     image_path = renderImageProcess(args[0].name, json)
#     return image_path


# Use shared MOVEMENT_ACTION_MAP and VFX_COLLECTION_MAP from ProductVideo/productvideo/properties/maps.json

maps_json_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "ProductVideo",
    "productvideo",
    "properties",
    "maps.json",
)
with open(maps_json_path, "r") as f:
    maps_data = json.load(f)
MOVEMENT_ACTION_MAP = maps_data.get("MOVEMENT_ACTION_MAP", {})
VFX_COLLECTION_MAP = maps_data.get("VFX_COLLECTION_MAP", {})


with gr.Blocks(title="Product Video Service") as block:
    # schema = None

    with gr.Row():
        # * Input Column
        with gr.Column():
            # gr.Markdown("""
            #             ### Please upload your FBX file below
            #             Instructions:
            #             - Keep Ring Vertical and its origin at world origin
            #             - Layer Names for rings :
            #                 Center Stone
            #                 Main Metal
            #                 Rhodium
            #                 Side Stone
            #             """)

            FILE_INPUT = gr.File(
                label="Upload glb", elem_id="upload_glb", visible=True, type="filepath"
            )

            # # * Manual parameters input
            # with gr.Row():
            #     MOVEMENT = gr.Dropdown(
            #         [k for k in MOVEMENT_ACTION_MAP.keys()],
            #         label="Movement",
            #         interactive=True,
            #         visible=True,
            #         value="ZOOM_IN",
            #     )

            #     MOVEMENT_SPEED = gr.Slider(
            #         0.0, 2.0, value=1.2, label="Movement Speed", interactive=True
            #     )

            #     MOVEMENT_INTERPOLATION = gr.Dropdown(
            #         [
            #             "None",
            #             "BEZIER",
            #             "LINEAR",
            #             "CONSTANT",
            #         ],
            #         label="Movement Interpolation",
            #         interactive=True,
            #         visible=True,
            #         value="BEZIER",
            #     )

            # with gr.Row():
            #     VFX_SHOT = gr.Dropdown(
            #         [k for k in VFX_COLLECTION_MAP.keys()],
            #         label="Vfx Shot",
            #         interactive=True,
            #         visible=True,
            #         value="VFX_BERRY_FLOAT",
            #     )

            #     VFX_SHOT_SPEED = gr.Slider(
            #         0.0,
            #         2.0,
            #         value=1.0,
            #         label="Vfx Shot Speed",
            #         interactive=True,
            #         visible=False,
            #     )

            #     VFX_SHOT_INTERPOLATION = gr.Dropdown(
            #         [
            #             "None",
            #             "BEZIER",
            #             "LINEAR",
            #             "CONSTANT",
            #         ],
            #         label="Vfx Shot Interpolation",
            #         interactive=True,
            #         visible=False,
            #         value="BEZIER",
            #     )

            PROMPT_INPUT = gr.TextArea(
                label="Describe the scene in detail",
                placeholder="Camera zooming into the bottle while water sprinkles on the screen",
            )

            ENVIRONMENT_COLOR = gr.ColorPicker(
                label="Environment color", value="#ff0000"
            )

            GENERATE_FILE_BUTTON = gr.Button(value="Generate")
            # RENDER_BUTTON = gr.Button(value="Render")

        # * Output Column
        with gr.Column():
            # FILE_OUTPUT = gr.Image()
            OUTPUT_VIDEO = gr.Video()

            OUTPUT_VIDEO_FILE = gr.File(
                label="Download Video", elem_id="download_section", visible=False
            )

    GENERATE_FILE_BUTTON.click(
        generate_file,
        inputs=[
            FILE_INPUT,
            PROMPT_INPUT,
            ENVIRONMENT_COLOR,
        ],
        outputs=OUTPUT_VIDEO,
    )

    is_debug = os.getenv("GRADIO_DEBUG", default="") != ""

    if is_debug:
        block.launch(
            debug=True,
            server_port=int(os.getenv("SERVICE_PORT")),
            server_name="0.0.0.0",
            share=True,
        )

    else:
        block.launch(
            auth=("admin", "987654"),
            debug=True,
            server_port=int(os.getenv("SERVICE_PORT")),
            server_name="0.0.0.0",
        )
