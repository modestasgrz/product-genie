
# ProductVideoService Project Structure & Key Files

This repository contains two main components:

- **GrBackend**: Gradio app (Python backend for UI and orchestration)
- **ProductVideo**: Blender addon (Python scripts for animation, VFX, and rendering)

---

## Key Files and Their Purpose

### GrBackend/Data/base1.blend
This Blender file contains all the setup for VFX shots and movements. All action and collection names referenced in the code and `maps.json` must exist in this file (with fake user enabled for actions).

### maps.json
This JSON file (should exist at both `ProductVideo/properties/maps.json` and `GrBackend/maps.json`) contains the list of movements and VFX shots, mapping them to their respective action/collection names. Each movement has a camera and object action name; each VFX shot has a collection name. These must match the names in `base1.blend`.

**Note:**
- If the Blender addon is installed via ZIP, the addon location will be:
  `C:\Users\<user_name>\AppData\Roaming\Blender Foundation\Blender\<blender_version_number>\scripts\addons\productvideo`
  and `maps.json` will be relative to this.

### ProductVideo/scripts/process.py
This script runs inside Blender's Python environment and calls the addon's internal functions. It is executed by the Gradio app using a subprocess (Popen). 

**process.py overview:**
- Handles CLI arguments for file paths and function selection.
- Sets up Blender scene properties and triggers import, animation, and rendering via the addon.
- Can be run in Blender background mode for automation.

**Key functions:**
- `make_folder_for_file(file_path)`: Ensures output directories exist.
- `read_json_file(file_path)`: Loads and parses a JSON file.
- `image_render_process(glb_file_path, json_file_path, out_file_path)`: Main entry for rendering; sets up scene, imports animation/object, applies movement and VFX, and renders.
- `main()`: CLI entry point; parses arguments and calls the appropriate function.

---

### GrBackend/config.yaml
YAML configuration file for environment variables and service settings. Loaded at app startup.

set the follwing paths in config.yaml

```sh
  BLENDER_APP: <path_to_blender.exe>
  BLENDER_SCRIPT_FILE: "path/to/ProductVideoService/ProductVideo/scripts/process.py"
  BLENDER_BASE_FILE: "path/to/ProductVideoService/GrBackend/Data/base1.blend"
```

---

## Other Important Files

### GrBackend/app.py
- Main entry for the Gradio web UI.
- Loads config, sets up UI, and triggers Blender rendering via subprocess.
- Loads movement and VFX mappings from `maps.json` for dropdowns.

---

## Usage

To render using Blender in background mode:

```sh
"C:/Program Files/Blender/blender.exe" --background "<path_to_blend_file>" --python "ProductVideo/scripts/process.py" -- -x <glb_file_path> -j <json_file_path> -v <out_file_path> -f process
```

---

## Summary

- All movement and VFX mappings are centralized in `maps.json` for consistency.
- The Gradio app and Blender addon both read from this file.
- All action/collection names must exist in the main `.blend` file.

## 🔧 Installing the Blender Addon

### 📦 Option 1: Install via ZIP

1. **Package the Addon:**
   - Open a terminal.
   - Navigate to your addon directory where `package.py` exists:
     ```bash
     cd path/to/ProductVideo/
     python package.py
     ```
   - This will create a ZIP file in the `dist/` folder.

2. **Install in Blender:**
   - Open Blender → `Edit > Preferences > Add-ons`
   - Click **Install**, then select the `.zip` file from the `dist/` folder.
   - Enable the addon after installation.

---

### 🖥️ Option 2: Run via VSCode with Blender Extension

1. **Open the Addon in VSCode:**
   - Open the folder: `ProductVideo/productvideo/` in VSCode.

2. **Run the Addon in Blender:**
   - Press `Ctrl + Shift + P` to open the Command Palette.
   - Type and select: **Blender: Build & Start**
   - Blender will launch with the addon loaded in development mode.




## ▶️ Running the Gradio App

Make sure that conda environment is deactivate
Use:
```sh
conda deactivate
```
If needed

1. Open GrBackend folder
2. Delete .venv directory if it exists. If it is hidden, on macOS you can see it by pressing Command + Shift + . (period)
3. Add "Data" directory with ".blend" file inside it.
4. Set your entities paths in:
```sh
GrBackend/config.yaml
```
5. Copy path of GrBackend folder
6. . Using terminal navigate to GrBackend folder, path should be pasted in between commas (")
```sh
cd "<copied path of GrBackend folder>"
```
7. Create new python environment:
```sh
python3 -m venv .venv
```
8. Activate new python environment:
```sh
source .venv/bin/activate
```
9. Install all required dependencies from requirements.txt 
by : 
```sh
pip install -r requirements.txt 
```
10. To start the Gradio web UI, run the following command in your terminal from the GrBackend directory:
```sh
python app.py
```

in above file "generate_file" is main entrypoint function

This will launch the Gradio interface in your browser.  
**Note:**  
- Ensure the paths in config.yaml are set correctly before starting.
- The app will use the configuration and environment variables defined in config.yaml.

---

