import itertools
import logging
import os

import bpy
from bpy.types import (
    Operator,
)

from productvideo.utils.FileHandler import (
    readJsonData,
)

# AnimationLibrary = importlib.import_module("animationlibrary")


def getMinMaxActoin(action):
    smallest_x = action.frame_range[0]
    largest_x = action.frame_range[1]

    return smallest_x, largest_x


def getLastFrame(context, animation_id):
    action = bpy.data.actions.get(animation_id)
    min_max = getMinMaxActoin(action)
    last_frame = int(context.scene.frame_current + min_max[1] - min_max[0])
    print(
        f"adding animation {animation_id} from {context.scene.frame_current} to {last_frame}"
    )
    return last_frame


def setAnimationSpeech(context, anim):
    # return

    productvideo_addon_properties = context.scene.productvideo_addon_properties

    productvideo_addon_properties.SPEECH_STRING = anim["text"]

    sound_name = f"speech.{str(hash(productvideo_addon_properties.SPEECH_STRING))}"

    # generate temp file afterwards

    productvideo_addon_properties.WAV_OUT_PATH = (
        productvideo_addon_properties.WAV_OUT_PATH.replace(
            ".wav", f".{str(hash(productvideo_addon_properties.SPEECH_STRING))}.wav"
        )
    )

    productvideo_addon_properties.KERNEL = "Azure"

    productvideo_addon_properties.VOICE = anim["voice"]

    productvideo_addon_properties.SPEECH_FRAME_START = anim["start_frame"]

    # select armature here

    bpy.ops.productvideo.convert_text_to_speech(kernel="Azure")

    bpy.ops.productvideo.add_speech_to_sequencer()

    seq = context.scene.sequence_editor.sequences_all[sound_name]

    bpy.ops.productvideo.make_animation_from_audio()

    return seq.frame_final_end


def setSettings(context, dct):
    context.scene.frame_end = dct["end_frame"]
    context.scene.frame_start = dct["start_frame"]


def hex_to_rgb(hex_color):
    # Remove the hash (#) if present
    hex_color = hex_color.lstrip("#")

    # Convert hex to RGB (values between 0 and 255)
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    # Convert RGB to Blender's color format (values between 0 and 1)
    return [c / 255.0 for c in rgb]


class ImportJsonAnimationOperator(Operator):
    """JsonSpeechAnimationDataOperator Operator Tooltip"""

    bl_idname = "productvideo.import_json_animation"
    bl_label = "Import Json Animation"
    bl_description = "Import Json Animation"
    bl_context = "object"
    log = logging.getLogger(__name__)

    def execute(self, context):
        self.log.info(f"executing: {self.bl_idname}")

        productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties

        # neongen_obj_props = None
        # if context.object:
        #     neongen_obj_props = context.object.neongen_props

        json_filepath = bpy.path.abspath(productvideo_addon_properties.JSON_IN_PATH)

        dct = readJsonData(json_filepath)

        # addJsonText(neongen_props, dct)

        productvideo_addon_properties.MOVEMENT = dct["MOVEMENT"]["NAME"]
        productvideo_addon_properties.MOVEMENT_SPEED = dct["MOVEMENT"]["SPEED"]

        productvideo_addon_properties.VFX_SHOT = dct["VFX_SHOT"]["NAME"]
        productvideo_addon_properties.ENVIRONMENT_COLOR = hex_to_rgb(
            dct["ENVIRONEMENT"]["BACKGOUND_COLOR"]
        )
        productvideo_addon_properties.ROTATION_DIRECTION = dct["MOVEMENT"][
            "ROTATION_DIRECTION"
        ]

        # selection_from_list(context, dct["variants"])
        # setSettings(context, dct["settings"])

        # end_frame = create_animation_from_json(context, dct["animations"])

        # add_sound(context,
        #           dct['background_sounds']['selected'],
        #           1,
        #           volume=dct['background_sounds']['volume'])

        # if context.scene.frame_end == context.scene.frame_start:
        #     context.scene.frame_end = end_frame

        return {"FINISHED"}


def addVideo(context, episode_path):
    if not bpy.context.scene.sequence_editor:
        bpy.context.scene.sequence_editor_create()
    return bpy.context.scene.sequence_editor.sequences.new_movie(
        os.path.basename(episode_path), episode_path, 5, 1
    )


def removeVideo(context, video):
    bpy.context.scene.sequence_editor.sequences.remove(video)


def selection_from_list(context, selectionDict):
    combinator_props = context.scene.combinator_props

    for axis, current_combination in enumerate(combinator_props.COBINATIONS_LIST):
        current_combination.CURRENT_SELECTED_OPTION = selectionDict[
            current_combination.name
        ]

    bpy.ops.scene.show_selections_operator()


def combination_option_generator(context, selectionDict):
    combinator_props = context.scene.combinator_props
    no_batch = True

    option_lists = []

    for axis, current_combination in enumerate(combinator_props.COBINATIONS_LIST):
        selection = selectionDict[current_combination.name]

        if selection != "ALL":
            option_lists.append([selection])

        if selection == "ALL":
            no_batch = False

            option_lists.append(
                [option.name for option in current_combination.OPTIONS_GROUP]
            )

    for combination in itertools.product(*option_lists):
        # print(,combination)
        for key, current_combination in zip(
            combination, combinator_props.COBINATIONS_LIST, strict=False
        ):
            current_combination.CURRENT_SELECTED_OPTION = key

        bpy.ops.scene.show_selections_operator()
        print("#######     # ### inside product iterator")
        yield not no_batch

    # if no_batch:
    #     bpy.ops.scene.show_selections_operator()
    #     print("#######     # ### inside default yield single")
    #     yield False


def render_video(context, suffix=""):
    bpy.context.scene.render.filepath = bpy.context.scene.render.filepath.replace(
        ".mp4", f"{suffix}_temp.mp4"
    )

    bpy.data.scenes["Scene"].render.use_sequencer = False

    bpy.ops.render.render(animation=True, use_viewport=True)

    in_vid_file = bpy.data.scenes["Scene"].render.filepath

    video = addVideo(context, in_vid_file)

    bpy.context.scene.render.filepath = bpy.context.scene.render.filepath.replace(
        f"{suffix}_temp.mp4", f"{suffix}.mp4"
    )

    bpy.data.scenes["Scene"].render.use_sequencer = True

    bpy.ops.render.render(animation=True, use_viewport=True)
    # print("video rendering : ", bpy.context.scene.render.filepath)

    bpy.context.scene.render.filepath = bpy.context.scene.render.filepath.replace(
        f"{suffix}.mp4", ".mp4"
    )

    removeVideo(context, video)

    # bpy.ops.wm.save_as_mainfile(
    #     filepath=bpy.context.scene.render.filepath.replace(
    #         ".mp4", "_{}.blend".format(suffix)))


def import_json_selection_operator(context):
    combinator_props = context.scene.combinator_props

    json_filepath = bpy.path.abspath(combinator_props.JSON_IN_PATH)

    dct = readJsonData(json_filepath)

    # selection_from_list(context, dct["variants"])
    combination_option_iterator = combination_option_generator(context, dct["variants"])

    for ret, is_batch in enumerate(combination_option_iterator):
        print(
            "selctions",
            [
                current_combination.CURRENT_SELECTED_OPTION
                for axis, current_combination in enumerate(
                    combinator_props.COBINATIONS_LIST
                )
            ],
        )

        render_video(context, str(ret) if is_batch else "")


class VideoGenerateProcessOperator(Operator):
    """VideoGenerateOperator Operator Tooltip"""

    bl_idname = "productvideo.video_generate_process"
    bl_label = "Video Generate Process"
    bl_description = "Video Generate Process"
    bl_context = "object"
    log = logging.getLogger(__name__)

    def execute(self, context):
        self.log.info(f"executing: {self.bl_idname}")

        productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties

        bpy.ops.productvideo.import_json_animation()

        bpy.ops.productvideo.apply_movement()

        bpy.ops.productvideo.apply_vfx_shot()

        # bpy.ops.productvideo.video_generate_process()

        bpy.ops.render.render(animation=True, use_viewport=True)

        return {"FINISHED"}


class CombinationGenerateProcessOperator(Operator):
    """CombinationGenerateOperator Operator Tooltip"""

    bl_idname = "productvideo.combination_generate_process"
    bl_label = "Combination Generate Process"
    bl_description = "Combination Generate Process"
    bl_context = "object"
    log = logging.getLogger(__name__)

    def execute(self, context):
        self.log.info(f"executing: {self.bl_idname}")

        productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties

        bpy.ops.productvideo.import_json_animation()

        for vfx_scene in list(
            bpy.data.scenes["Scene"]
            .productvideo_addon_properties.bl_rna.properties["MOVEMENT"]
            .enum_items
        ):
            for movement in list(
                bpy.data.scenes["Scene"]
                .productvideo_addon_properties.bl_rna.properties["VFX_SHOT"]
                .enum_items
            ):
                bpy.context.scene.productvideo_addon_properties.VFX_SHOT = (
                    vfx_scene.name
                )
                bpy.context.scene.productvideo_addon_properties.MOVEMENT = movement.name

                bpy.ops.productvideo.apply_movement()

                bpy.ops.productvideo.apply_vfx_shot()

        bpy.ops.render.render(animation=True, use_viewport=True)

        return {"FINISHED"}


class CheckAllCombinationsOperator(Operator):
    """VideoGenerateOperator Operator Tooltip"""

    bl_idname = "productvideo.check_all_combinations"
    bl_label = "Check All Combinations"
    bl_description = "Check All Combinations"
    bl_context = "object"
    log = logging.getLogger(__name__)

    def execute(self, context):
        self.log.info(f"executing: {self.bl_idname}")

        productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties

        # bpy.ops.productvideo.import_json_animation()

        for movement in list(
            productvideo_addon_properties.bl_rna.properties["MOVEMENT"].enum_items
        ):
            try:
                bpy.context.scene.productvideo_addon_properties.MOVEMENT = movement.name
                bpy.ops.productvideo.apply_movement()
            except Exception:
                self.log.error(f"Error applying movement {movement.name}")

        for vfx_scene in list(
            productvideo_addon_properties.bl_rna.properties["VFX_SHOT"].enum_items
        ):
            try:
                bpy.context.scene.productvideo_addon_properties.VFX_SHOT = (
                    vfx_scene.name
                )
                bpy.ops.productvideo.apply_vfx_shot()

            except Exception:
                self.log.error(f"Error setting VFX shot {vfx_scene.name}")
        # bpy.ops.productvideo.video_generate_process()

        # bpy.ops.render.render(animation=True, use_viewport=True)

        return {"FINISHED"}


classes = (
    ImportJsonAnimationOperator,
    VideoGenerateProcessOperator,
    CombinationGenerateProcessOperator,
    CheckAllCombinationsOperator,
)
