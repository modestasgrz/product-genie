import bpy


class MessageBoxOperator(bpy.types.Operator):
    bl_idname = "ui.show_message_box"
    bl_label = "Minimal Operator"

    def execute(self, context):
        # this is where I send the message
        self.report({'INFO'}, "This is a test")
        return {'FINISHED'}


def ShowMessageBox(message="nested object selected",
                   title="Message Box",
                   icon='ERROR'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
