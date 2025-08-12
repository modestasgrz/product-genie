import os

import bpy  # noqa: I001

addon_zip_path = os.path.join(os.getcwd(), "productvideo-1.0.11.zip")
# The module name is usually the main folder name inside the zip file
addon_module_name = "productvideo"

try:
    # Install the addon from the specified .zip file
    bpy.ops.preferences.addon_install(filepath=addon_zip_path)
    # Enable the addon
    bpy.ops.preferences.addon_enable(module=addon_module_name)
    # Save user preferences so the addon remains enabled
    bpy.ops.wm.save_userpref()
    print(f"Successfully installed and enabled addon: {addon_module_name}")

except Exception as e:
    print(f"Error installing addon: {e}")
    # Exit with a non-zero status code to fail the Docker build if installation fails
    exit(1)
