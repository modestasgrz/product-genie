

import bpy
import os
import json


print("######## running invoke_images ##########")

def make_folder_for_file(file_path):
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

def read_json_file(file_path):
    """
    Reads a JSON file from the given file path and returns the data as a dictionary.
    
    :param file_path: The path to the JSON file
    :return: Parsed data from the JSON file
    """
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        print(f"Error: The file at {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {file_path}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


STORE_DATA_PATH = os.getenv("STORE_DATA_PATH", default='')
SERVICE_SCHEMA_JSON_PATH = os.getenv("SERVICE_SCHEMA_JSON_PATH", default='')

def getSelfFilePath():
    return os.path.abspath(__file__)


def image_render_process(glb_file_path,json_file_path, out_file_path):
    
    print(' --------- inside function ')
    
    productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties

    productvideo_addon_properties.JSON_IN_PATH = json_file_path

    bpy.data.scenes["Scene"].render.filepath = out_file_path
    
    bpy.ops.productvideo.import_json_animation()
    
    bpy.ops.object.import_productvideo_object(filepath=glb_file_path)
    
    bpy.ops.productvideo.apply_movement()
    
    bpy.ops.productvideo.apply_vfx_shot()

    bpy.ops.render.render(animation=True, use_viewport=True)

    file_store_path = glb_file_path.replace('.glb','.blend')
    
    # bpy.ops.wm.save_as_mainfile(filepath=file_store_path)


def main():
    import sys
    import argparse

    # asset_path = os.path.abspath('{}/BlenderNodes/Assets'.format(getTempDir()))

    # cmd = [
    #     blender_executable,
    #     '--background',
    #     '--python',
    # ]

    print("Processing Cli-----------------> \n", )
    # log = logging.getLogger("Installing pillow -----------------> \n", cmd)

    # output = subprocess.check_output(cmd)

    # print("Installation Fininshed With -----------------> \n", output)

    argv = sys.argv

    # print(argv)

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = ("Run blender in background mode with this script:"
                  "  blender file.blend --background --python " + __file__ +
                  " -- [options]")
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
        image_render_process(args.glb_file_path,args.json_file_path, args.out_file_path)


if __name__ == "__main__":
    main()
    
    
# "C:/Program Files/BlenderOctane/blender.exe" --background "D:\\Users\\saura\\Documents\\Work\\Repos\\JewellaryRendering\\BlenderAddon\\ArceltonJewelleryAddon\\arceltonjewelleryaddon\\Data\\base_service.blend"  --python "D:/Users/saura/Documents/Work/Repos/JewellaryRendering/BlenderAddon/ArceltonJewelleryAddon/scripts/invoke_images.py"  -- --fbx_file_path="D:/Users/saura/Documents/Work/Repos/JewellaryRendering/RenderAsService/GrBackend/Data/sample_ring.fbx" --out_file_path="D:/Users/saura/Documents/Work/Repos/JewellaryRendering/RenderAsService/GrBackend/Data/sdfjdfbn.png" --function="process"

# "C:/Program Files/BlenderOctane/blender.exe" --background --python-console "D:\\Users\\saura\\Documents\\Work\\Repos\\JewellaryRendering\\BlenderAddon\\ArceltonJewelleryAddon\\arceltonjewelleryaddon\\Data\\base_service.blend"
    
