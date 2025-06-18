import os
import random
import string
import subprocess
from pathlib import Path

from src import FileHandler

TEMP_DIRECTORY = (
    Path(__file__).parent.parent / "temp_dir"
)  # * Used tempfile.gettempdir() initially


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    return_code = popen.wait()
    if return_code:
        for stdout_line in iter(popen.stdout.readline, ""):
            print(stdout_line)
        raise subprocess.CalledProcessError(return_code, cmd)

    popen.stdout.close()


def image_render_process(
    glb_file,
    json_file_path,
    out_file_path,
    blend_file=os.getenv("BLENDER_RING_FILE", default=None),
):
    command = [
        os.getenv("BLENDER_APP", default=None),
        blend_file,
        "--background",
        "--python",
        os.getenv("BLENDER_SCRIPT_FILE", default=None),
        "--",
        "--json_file_path=" + json_file_path,
        "--glb_file_path=" + glb_file,
        "--out_file_path=" + out_file_path,
        "--function=" + "process",
    ]
    print("blender process strated", command)

    try:
        for path in execute(command):
            print(path, end="")
    # process.wait()
    except Exception:
        pass

    if os.path.exists(out_file_path):
        print("File exists")
        print("blender process finished")
        return True

    return False


def renderImageProcess(glb_file, json):
    uniqueFilename = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=12)
    )

    try:
        os.mkdir(TEMP_DIRECTORY)
    except FileExistsError:
        pass

    json_file_path = os.path.join(TEMP_DIRECTORY, "in_" + uniqueFilename + ".json")

    FileHandler.writeJsonData(json_file_path, json)

    video_out_path = os.path.join(TEMP_DIRECTORY, "out_" + uniqueFilename + ".mov")

    image_render_process(
        glb_file,
        json_file_path,
        video_out_path,
        blend_file=os.getenv("BLENDER_BASE_FILE", default=None),
    )
    # blend_file="E:/Work/Repos/ProductVideoService/ProductVideo/productvideo/Data/base1.blend")

    return video_out_path
