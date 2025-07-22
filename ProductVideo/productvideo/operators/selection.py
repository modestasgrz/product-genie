import logging
import os

import bpy
from bpy.props import (
    BoolProperty,
    EnumProperty,
    StringProperty,
)
from bpy.types import (
    Operator,
)
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector


def getOverrideContextForObjects(objs, bones, mode="POSE"):
    override_context = {
        "active_object": objs[0],
        "object": objs[0],
        "edit_object": [],
        "selected_bases": [],
        "selected_editable_objects": objs,
        "selected_objects": objs,
        # 'area': area,
        "selected_pose_bones_from_active_object": bones,
        "selected_pose_bones": bones,
        # 'region': region,
    }
    # if mode == 'EDIT':
    #     override_context['edit_object'] = objs[0]

    bpy.ops.object.mode_set(override_context, mode=mode)
    return override_context


def shifBonestAnimationData(obj, selected_pose_bones, shift):
    selected_pose_bones_string = []

    for bone in selected_pose_bones:
        bone_name = f'pose.bones["{bone.name}"].'
        selected_pose_bones_string.append(bone_name + "location")
        selected_pose_bones_string.append(bone_name + "rotation_quaternion")
        selected_pose_bones_string.append(bone_name + "rotation_euler")
        selected_pose_bones_string.append(bone_name + "scale")

    # keyframes = []

    # num_keyframes = []
    anim = obj.animation_data
    if anim is not None and anim.action is not None:
        for fcu in anim.action.fcurves:
            if fcu.data_path in selected_pose_bones_string:
                for keyframe in fcu.keyframe_points:
                    keyframe.co.x += shift


# Use shared MOVEMENT_ACTION_MAP from properties/maps.json
from productvideo.utils.FileHandler import readJsonData

MAPS_JSON_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "properties", "maps.json"
)
maps_data = readJsonData(MAPS_JSON_PATH)
MOVEMENT_ACTION_MAP = maps_data.get("MOVEMENT_ACTION_MAP", {})


def reverse_action_fcurves(action):
    if action:
        for fcurve in action.fcurves:
            # Assuming rotation is on Z-axis for simplicity, adjust as needed
            if (
                "rotation_euler" in fcurve.data_path and fcurve.array_index == 2
            ):  # Z-axis rotation
                for keyframe in fcurve.keyframe_points:
                    keyframe.co.y *= -1  # Reverse the rotation value
            elif "rotation_quaternion" in fcurve.data_path:
                # Reversing quaternion rotation is more complex, might involve conjugating
                # For now, a simple negation of the W component might work for some cases,
                # but a proper quaternion reversal involves more math.
                # This is a simplified approach.
                if fcurve.array_index == 0:  # W component
                    for keyframe in fcurve.keyframe_points:
                        keyframe.co.y *= -1


def changeActionInterpolation(action, interpolation="LINEAR"):
    if action:
        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = (
                    interpolation  # Options: 'BEZIER', 'LINEAR', 'CONSTANT'
                )
        # print(f"Interpolation changed for action '{action.name}'.")
    # else:
    # print(f"Action '{action.name}' not found.")


class ApplyMovementAnimationOperator(Operator):
    """Apply Movement Animation Operator Tooltip"""

    bl_idname = "productvideo.apply_movement"
    bl_label = "Apply Movement"
    bl_description = "Apply Movement"
    log = logging.getLogger(__name__)

    def execute(self, context):
        self.log.info(f"executing: {self.bl_idname}")

        productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties

        scene = context.scene

        obj = context.object

        camera = scene.camera
        # Ensure the object has an animation data block

        camera_action = MOVEMENT_ACTION_MAP[productvideo_addon_properties.MOVEMENT][
            "CAMERA"
        ]
        object_action = MOVEMENT_ACTION_MAP[productvideo_addon_properties.MOVEMENT][
            "OBJECT"
        ]

        # Create a new action or get an existing action

        if camera_action:
            if camera_action in bpy.data.actions:
                camera_action = bpy.data.actions[camera_action]
            else:
                # action = bpy.data.actions.new(name="CAMERA_DUTCH_ANGLE_ZOOM_IN")
                pass

            if camera.animation_data is None:
                camera.animation_data_create()

            # Create a new NLA track if one doesn't exist
            nla_tracks = camera.animation_data.nla_tracks
            if len(nla_tracks) == 0:
                nla_track = camera.animation_data.nla_tracks.new()
            else:
                nla_track = nla_tracks[0]

            nla_track.name = "My NLA Track"

            changeActionInterpolation(
                camera_action, productvideo_addon_properties.MOVEMENT_INTERPOLATION
            )

            for strip in list(nla_track.strips):
                nla_track.strips.remove(strip)

            # Add a new NLA strip and assign the action to it
            nla_strip = nla_track.strips.new(
                camera_action.name, start=1, action=camera_action
            )

            # Optional: Adjust NLA strip settings
            nla_strip.frame_end = camera_action.frame_range[
                1
            ]  # End frame based on the action's length
            nla_strip.action = camera_action  # Link the action to the strip

            nla_strip.scale = 1.0 / productvideo_addon_properties.MOVEMENT_SPEED

            # print(
            #     f"NLA Strip '{nla_strip.name}' created for action '{camera_action.name}'"
            # )

        if object_action:
            if object_action in bpy.data.actions:
                object_action = bpy.data.actions[object_action]
            else:
                # action = bpy.data.actions.new(name="CAMERA_DUTCH_ANGLE_ZOOM_IN")
                pass

            if obj.animation_data is None:
                obj.animation_data_create()
            # Create a new NLA track if one doesn't exist

            nla_tracks = obj.animation_data.nla_tracks
            if len(nla_tracks) == 0:
                nla_track = obj.animation_data.nla_tracks.new()
            else:
                nla_track = nla_tracks[0]

            nla_track.name = "My NLA Track"

            changeActionInterpolation(
                object_action, productvideo_addon_properties.MOVEMENT_INTERPOLATION
            )

            for strip in list(nla_track.strips):
                nla_track.strips.remove(strip)

            # Add a new NLA strip and assign the action to it
            nla_strip = nla_track.strips.new(
                object_action.name, start=1, action=object_action
            )

            # Optional: Adjust NLA strip settings
            nla_strip.frame_end = object_action.frame_range[
                1
            ]  # End frame based on the action's length
            nla_strip.action = object_action  # Link the action to the strip

            nla_strip.scale = 1.0 / productvideo_addon_properties.MOVEMENT_SPEED

            if productvideo_addon_properties.ROTATION_DIRECTION == "COUNTER_CLOCKWISE":
                reverse_action_fcurves(object_action)

        bpy.data.materials["GRADIENT"].node_tree.nodes["RGB"].outputs[0].default_value[
            0
        ] = productvideo_addon_properties.ENVIRONMENT_COLOR[0]
        bpy.data.materials["GRADIENT"].node_tree.nodes["RGB"].outputs[0].default_value[
            1
        ] = productvideo_addon_properties.ENVIRONMENT_COLOR[1]
        bpy.data.materials["GRADIENT"].node_tree.nodes["RGB"].outputs[0].default_value[
            2
        ] = productvideo_addon_properties.ENVIRONMENT_COLOR[2]

        return {"FINISHED"}


# Use shared VFX_COLLECTION_MAP from properties/maps.json
VFX_COLLECTION_MAP = maps_data.get("VFX_COLLECTION_MAP", {})

# [
# 'WATER_SPLASH',#Water splash
# 'SPARKLES_OVERLAY',#Sparkles overlay effect
# 'SNOWING_OVERLAY',#Snowing overlay effect
# 'FIRE_BURST_OVERLAY',#Fire burst overlay
# 'SCREEN_FROST_OVERLAY',#Screen frost overlay
# 'GIFT_BOX_ROLL',#Gift box roll next to product
# 'LIGHTING',#Lighting
# ],


class ApplyVFXShotOperator(Operator):
    """Apply Movement Animation Operator Tooltip"""

    bl_idname = "productvideo.apply_vfx_shot"
    bl_label = "Apply VFX Shot"
    bl_description = "Apply VFX Shot"
    log = logging.getLogger(__name__)

    def execute(self, context):
        self.log.info(f"executing: {self.bl_idname}")

        productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties

        scene = context.scene

        obj = context.object

        camera = scene.camera

        for vfx_key, vfx_collection in VFX_COLLECTION_MAP.items():
            if vfx_collection in bpy.data.collections:
                # parent_obj = bpy.data.objects[options_group.name]

                hide = vfx_key != productvideo_addon_properties.VFX_SHOT

                # for obj in collectionIterator(parent_obj):

                collection = bpy.data.collections[vfx_collection]

                collection.hide_viewport = hide
                collection.hide_render = hide

        return {"FINISHED"}


def get_combined_bounding_box(objects):
    # Initialize min and max vectors to extreme values
    min_coords = Vector((float("inf"), float("inf"), float("inf")))
    max_coords = Vector((float("-inf"), float("-inf"), float("-inf")))

    # Loop through each object and calculate the world-space bounding box
    for obj in objects:
        # Ensure the object has a bounding box
        if obj.type == "MESH":
            # Get bounding box corners in local space and transform to world space
            bbox_world = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

            # Update min and max coordinates
            for corner in bbox_world:
                min_coords = Vector(
                    (
                        min(min_coords.x, corner.x),
                        min(min_coords.y, corner.y),
                        min(min_coords.z, corner.z),
                    )
                )
                max_coords = Vector(
                    (
                        max(max_coords.x, corner.x),
                        max(max_coords.y, corner.y),
                        max(max_coords.z, corner.z),
                    )
                )

    # Calculate the dimensions of the combined bounding box
    combined_dimensions = max_coords - min_coords
    return combined_dimensions, (max_coords + min_coords) / 2.0


class ImportProductObject(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""

    bl_idname = "object.import_productvideo_object"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Product Object"

    # ImportHelper mixin class uses this
    filename_ext = ".glb"

    filter_glob: StringProperty(
        default="*.glb",
        options={"HIDDEN"},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting: BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type: EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(
            ("OPT_A", "First Option", "Description one"),
            ("OPT_B", "Second Option", "Description two"),
        ),
        default="OPT_A",
    )

    def set_origin_to_geometry(self, obj):
        # Calculate the bounding box center
        bbox_center = (
            sum(
                (mathutils.Vector(corner) for corner in obj.bound_box),
                mathutils.Vector(),
            )
            / 8
        )

        # Convert the bounding box center to world space
        world_bbox_center = obj.matrix_world @ bbox_center

        # Get the local transformation matrix for origin shifting
        new_origin_matrix = obj.matrix_world.copy()
        new_origin_matrix.translation = world_bbox_center

        # Apply the new transformation (set origin without bpy.ops)
        obj.data.transform(obj.matrix_world.inverted() @ new_origin_matrix)
        obj.matrix_world = new_origin_matrix

    def execute(self, context):
        old_objs = set(context.scene.objects)

        # bpy.ops.import_scene.glb(filepath=self.filepath, directory='', use_manual_orientation=True, axis_forward='Y', axis_up='Z')

        bpy.ops.import_scene.gltf(
            filepath=self.filepath,
            # filter_glob="*.glb;*.gltf",  # Filter file types
            # import_pack_images=True,     # Pack images as PNGs
            # import_shading='NORMALS',     # Set shading to NORMALS or MESHES
            # import_materials=True,        # Import materials
            # merge_vertices=False,         # Do not merge vertices
        )

        imported_objs = set(context.scene.objects) - old_objs
        # print("Imported:", imported_objs)

        combined_dimensions, bbox_center = get_combined_bounding_box(imported_objs)

        max_dimension = max(
            combined_dimensions[0], combined_dimensions[1], combined_dimensions[2]
        )

        for obj in imported_objs:
            obj.rotation_mode = "XYZ"

            world_bbox_center = obj.matrix_world @ bbox_center
            # Get the local transformation matrix for origin shifting
            new_origin_matrix = obj.matrix_world.copy()
            new_origin_matrix.translation = -bbox_center

            # Apply the new transformation (set origin without bpy.ops)

            if obj.data:
                obj.data.transform(obj.matrix_world.inverted() @ new_origin_matrix)
                obj.matrix_world = new_origin_matrix

                obj.location = Vector((0, 0, 0))

                obj.scale *= 0.1815 / max_dimension

        return {"FINISHED"}


classes = (
    # ConvertTextToSpeechOperator,
    # AddSpeechToSequencerOperator,
    ImportProductObject,
    ApplyMovementAnimationOperator,
    ApplyVFXShotOperator,
)
