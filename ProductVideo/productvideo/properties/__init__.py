import bpy
import os
from bpy.props import (
    StringProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
)
from bpy.types import PropertyGroup

from productvideo.utils.FileHandler import (
    writeJsonData,
    readJsonData,
    getFilesWithExtensions,
)


def updateImgageWidth(self, context):

    bpy.data.materials['LEDColorNew'].node_tree.nodes['Group'].node_tree.nodes[
        'img_width'].outputs['Value'].default_value = self.imgage_width


def updateNumberOfFrames(self, context):
    bpy.data.materials['LEDColorNew'].node_tree.nodes['Group'].node_tree.nodes[
        'total_frames'].outputs['Value'].default_value = self.number_of_frames



# Load VFX_COLLECTION_MAP and MOVEMENT_ACTION_MAP from JSON file
MAPS_JSON_PATH = os.path.join(os.path.dirname(__file__), "maps.json")
maps_data = readJsonData(MAPS_JSON_PATH)
VFX_COLLECTION_MAP = maps_data.get("VFX_COLLECTION_MAP", {})
MOVEMENT_ACTION_MAP = maps_data.get("MOVEMENT_ACTION_MAP", {})


MOVEMENTS = [(k, k, k) for k in MOVEMENT_ACTION_MAP.keys()]
VFX_SHOTS = [(k, k, k) for k in VFX_COLLECTION_MAP.keys()]

MOVEMENT_INTERPOLATIONS = [('BEZIER', 'BEZIER', 'BEZIER'),
                           ('LINEAR', 'LINEAR', 'LINEAR'),
                           ('CONSTANT', 'CONSTANT', 'CONSTANT')]


class ProductVideoAddonProperties(PropertyGroup):

    OBEJCT_NAME: StringProperty(name="OBEJCT_NAME",
                                description="OBEJCT_NAME",
                                default='')

    WAV_OUT_PATH: StringProperty(
        name="WAV_OUT_PATH",
        description="WAV_OUT_PATH",
        default=
        'C:\\Users\\saura\\OneDrive\\Documents\\Work\\Upwork\\LipSync\\Data\\speech.wav',
        subtype='FILE_PATH')

    ROOT_DIR_PATH: StringProperty(
        name="ROOT_DIR_PATH",
        description="ROOT_DIR_PATH",
        # default='/home/darkknight/Documents/Work/Upwork/HumanUV',
        subtype='DIR_PATH')

    MOVEMENT: EnumProperty(name='MOVEMENT',
                           description='MOVEMENT',
                           items=MOVEMENTS,
                           default='PRODUCT_360')

    MOVEMENT_SPEED: FloatProperty(name='MOVEMENT_SPEED',
                                  description='MOVEMENT_SPEED',
                                  default=1.0)

    MOVEMENT_INTERPOLATION: EnumProperty(name='MOVEMENT_INTERPOLATION',
                                         description='MOVEMENT_INTERPOLATION',
                                         items=MOVEMENT_INTERPOLATIONS,
                                         default='BEZIER')

    VFX_SHOT: EnumProperty(name='VFX_SHOT',
                           description='VFX_SHOT',
                           items=VFX_SHOTS,
                           default='None')

    VFX_SHOT_SPEED: FloatProperty(name='VFX_SHOT_SPEED',
                                  description='VFX_SHOT_SPEED',
                                  default=1.0)

    ENVIRONMENT_COLOR: bpy.props.FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        default=(1.0, 0.0, 0.0),  # Red color by default
        min=0.0,
        max=1.0,
        description="Choose a color")

    SOUNDS_DIR_PATH: StringProperty(
        name="SOUNDS_DIR_PATH",
        description="SOUNDS_DIR_PATH",
        default=
        'C:\\Users\\saura\\OneDrive\\Documents\\Work\\Upwork\\LipSync\\Data\\sounds',
        subtype='DIR_PATH')

    JSON_IN_PATH: StringProperty(
        name="JSON_IN_PATH",
        default=
        "E:\\Work\\Repos\\ProductVideoService\\GrBackend\\Data\\sample_input.json",
        subtype="FILE_PATH")

    JSON_OUT_PATH: StringProperty(
        name="JSON_OUT_PATH",
        default=
        "C:\\Users\\saura\\OneDrive\\Documents\\Work\\Upwork\\LipSync\\Data\\schema.json",
        subtype="FILE_PATH")

    SPEECH_FRAME_START: IntProperty(
        name="SPEECH_FRAME_START",
        description="SPEECH_FRAME_START",
        default=1,
    )

    SPEECH_FRAME_END: IntProperty(
        name="SPEECH_FRAME_END",
        description="SPEECH_FRAME_END",
        default=110,
    )


classes = (ProductVideoAddonProperties, )


def register():
    for clss in classes:
        bpy.utils.register_class(clss)

    bpy.types.Scene.productvideo_addon_properties = PointerProperty(
        type=ProductVideoAddonProperties)

    bpy.types.Action.include_animation = BoolProperty(
        name="include animation",
        description="include animation as dropdown in productvideo api",
        default=False)

    # print(bpy.types.Object.led_number)


def unregister():
    del bpy.types.Scene.productvideo_addon_properties
    # del bpy.types.Object.led_number

    for clss in classes:
        bpy.utils.unregister_class(clss)
