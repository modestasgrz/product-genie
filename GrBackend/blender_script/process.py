import json
import os
from typing import Any

import bpy  # type: ignore[import-not-found] # noqa: I001

print("######## running invoke_images ##########")


def make_folder_for_file(file_path: str) -> None:
    """
    Creates the directories for the given file path if they don't exist.

    :param file_path: The full file path where the directories need to be created
    """
    # Get the directory part of the file path
    directory = os.path.dirname(file_path)

    # Check if the directory exists, if not, create it
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"Directories created: {directory}")
        except OSError as e:
            print(f"Error: Could not create directories for {file_path}. {e}")
    else:
        print(f"Directories already exist: {directory}")


def read_json_file(file_path: str) -> dict[str, Any]:
    """
    Reads a JSON file from the given file path and returns the data as a dictionary.

    :param file_path: The path to the JSON file
    :return: Parsed data from the JSON file
    """
    try:
        with open(file_path) as json_file:
            data = json.load(json_file)
            return data  # type: ignore[no-any-return]
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
        raise
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {file_path}.")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise


STORE_DATA_PATH = os.getenv("STORE_DATA_PATH", default="")
SERVICE_SCHEMA_JSON_PATH = os.getenv("SERVICE_SCHEMA_JSON_PATH", default="")


def getSelfFilePath() -> str:
    return os.path.abspath(__file__)


def image_render_process(
    glb_file_path: str, json_file_path: str, out_file_path: str
) -> None:
    print(" --------- inside function ")

    productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties

    productvideo_addon_properties.JSON_IN_PATH = json_file_path

    bpy.data.scenes["Scene"].render.filepath = out_file_path

    bpy.ops.productvideo.import_json_animation()

    bpy.ops.object.import_productvideo_object(filepath=glb_file_path)

    bpy.ops.productvideo.apply_movement()

    bpy.ops.productvideo.apply_vfx_shot()

    bpy.ops.render.render(animation=True, use_viewport=True)


def main() -> None:
    import argparse
    import sys

    # asset_path = os.path.abspath('{}/BlenderNodes/Assets'.format(getTempDir()))

    # cmd = [
    #     blender_executable,
    #     '--background',
    #     '--python',
    # ]

    print(
        "Processing Cli-----------------> \n",
    )
    # log = logging.getLogger("Installing pillow -----------------> \n", cmd)

    # output = subprocess.check_output(cmd)

    # print("Installation Fininshed With -----------------> \n", output)

    argv = sys.argv

    # print(argv)

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1 :]  # get all args after "--"

    parser = argparse.ArgumentParser()
    # Add an argument

    parser.add_argument(
        "-j",
        "--json_file_path",
        dest="json_file_path",
        required=False,
        help="json path ",
    )

    parser.add_argument(
        "-x",
        "--glb_file_path",
        dest="glb_file_path",
        required=False,
        help="fbx path ",
    )
    parser.add_argument(
        "-v",
        "--out_file_path",
        dest="out_file_path",
        required=False,
        help="image path out",
    )
    parser.add_argument(
        "-f",
        "--function",
        type=str,
        required=True,
        dest="function",
        help="function",
    )

    # parser.add_argument(
    #     "-s",
    #     "--json_schema_path",
    #     dest="json_schema_path",
    #     required=False,
    #     help="json_schema_path ",
    # )

    # parser.add_argument(
    #     "-b",
    #     "--sound_files_dir",
    #     dest="sound_files_dir",
    #     required=False,
    #     help="sound_files_dir",
    # )

    # Parse the argument
    # args = parser.parse_args()
    # args, unknown = parser.parse_known_args()
    args = parser.parse_args(argv)

    if args.function == "process":
        image_render_process(
            args.glb_file_path, args.json_file_path, args.out_file_path
        )


if __name__ == "__main__":
    main()
