# utils
import os
import ensurepip
import subprocess
from pathlib import Path
# Make it work for Python 2+3 and with Unicode
try:
    to_unicode = unicode
except NameError:
    to_unicode = str


def intallDependancies(deps):
    for install_name, import_name in deps:
        try:
            i = __import__(import_name)
            print(i)
        except Exception:

            ensurepip.bootstrap()
            os.environ.pop("PIP_REQ_TRACKER", None)

            try:
                import bpy
                binary_path_python = Path(bpy.app.binary_path_python)
            except AttributeError:
                import sys
                binary_path_python = Path(sys.executable)

            target_path = os.path.dirname(binary_path_python)
            target_path = os.path.join(target_path, "../lib")
            p_version = ''
            for p_file in os.listdir(target_path):
                if p_file.startswith("python"):
                    p_version = p_file

            target_path = os.path.join(target_path, p_version, "site-packages")

            cmd = [
                binary_path_python, '-m', 'pip', 'install',
                '--force-reinstall', install_name
            ]  # , '--target', target_path

            print("Installing dependancy -----------------> \n", install_name)
            # log = logging.getLogger("Installing pillow -----------------> \n", cmd)

            output = subprocess.check_output(cmd)

            print("Installation Fininshed With -----------------> \n", output)


if '__main__' == __name__:
    intallDependancies([
        ['chumpy', 'chumpy'],
        ['scipy', 'scipy'],
        ['opencv-python', 'cv2'],
        ['pandas', 'pandas'],
        ['pillow', 'PIL'],
    ])
