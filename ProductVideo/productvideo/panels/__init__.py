import bpy
from bpy.types import Panel

class ProductVideoPanel(Panel):
    """ProductVideo Panel """
    bl_label = "ProductVideo"
    bl_idname = "OBJECT_PT_product_video_panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        
        productvideo_addon_properties = bpy.context.scene.productvideo_addon_properties
        
        layout = self.layout
        row = layout.row(align=True)
        row.prop(productvideo_addon_properties, "JSON_IN_PATH")

        row = layout.row(align=True)
        row.prop(productvideo_addon_properties, "MOVEMENT")
        
        row = layout.row(align=True)
        row.prop(productvideo_addon_properties, "MOVEMENT_SPEED")
        
        row = layout.row(align=True)
        row.prop(productvideo_addon_properties, "MOVEMENT_INTERPOLATION")
        
        row = layout.row(align=True)
        row.prop(productvideo_addon_properties, "VFX_SHOT")
        
        row = layout.row(align=True)
        row.prop(productvideo_addon_properties, "ENVIRONMENT_COLOR")

        # row = layout.row(align=True)
        # row.prop(bpy.data.materials["BackgroundPlaneMaterial"].node_tree.nodes["Principled BSDF"].inputs[0], "default_value")
        
        

        row = layout.row(align=True)
        # row.prop(productvideo_addon_properties, "VOICE")
        row.prop(context.scene.render, "filepath")

        row = layout.row()
        row.operator("object.import_productvideo_object")


        row = layout.row()
        row.operator("productvideo.check_all_combinations")

        # row = layout.row(align=True)
        # row.prop(productvideo_addon_properties, "SPEECH_FRAME_START")
        # row.prop(productvideo_addon_properties, "SPEECH_FRAME_END")

        # row = layout.row()
        # row.operator("productvideo.add_speech_to_sequencer")

        # row = layout.row(align=True)
        # row.prop(productvideo_addon_properties, "SOUNDS")

        # row = layout.row()
        # row.operator("productvideo.add_sound_to_sequencer")

        row = layout.row()
        row.operator("productvideo.apply_movement")
        
        row = layout.row()
        row.operator("productvideo.apply_vfx_shot")

        row = layout.row()
        row.operator("productvideo.import_json_animation")
        
        # row = layout.row(align=True)
        # row.prop(productvideo_addon_properties, "SPEECH_FRAME_START")

        row = layout.row()
        row.operator("productvideo.video_generate_process")

        # row = layout.row()
        # row.operator("productvideo.lipsync_process_batch")

classes = (
    ProductVideoPanel,
) 
def register():
    for clss in classes:
        bpy.utils.register_class(clss)


def unregister():
    for clss in classes:
        bpy.utils.unregister_class(clss)
