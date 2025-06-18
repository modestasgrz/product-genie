import bpy

from productvideo.operators import (selection, animations)

classes = selection.classes + animations.classes  # + io.classes + combine.classes


def register():
    for clss in classes:
        bpy.utils.register_class(clss)


def unregister():
    for clss in classes:
        bpy.utils.unregister_class(clss)
