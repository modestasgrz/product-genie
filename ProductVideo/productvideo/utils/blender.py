# utils
import os
import bpy


def setCuda():
    try:
        bpy.context.scene.render.engine = 'CYCLES'
        # bpy.context.scene.cycles.device = 'CPU'
        # force rendering to GPU
        bpy.context.scene.cycles.device = 'GPU'
        cpref = bpy.context.preferences.addons['cycles'].preferences
        cpref.compute_device_type = 'CUDA'
        # Use GPU devices only
        cpref.get_devices()
        for device in cpref.devices:
            device.use = True if device.type == 'CUDA' else False
        print("############## CUDA Enabled ############ ")
        # pass
    except Exception:
        pass


def get_pose_index_from_frame(poselib, frame):
    """Get the pose index of the pose with the specified frame."""
    for i, pose in enumerate(poselib.pose_markers):
        if pose.frame == frame:
            return i


def applyTexture(context, filepath):
    print("Texture", filepath)
    if os.path.basename(filepath) not in bpy.data.images:
        bpy.ops.image.open(filepath=filepath,
                           directory=os.path.dirname(filepath),
                           files=[{
                               "name": os.path.basename(filepath)
                           }],
                           relative_path=True,
                           show_multiview=False)

    # print("Textures", list(bpy.data.images))

    bpy.data.materials['BaseSMPLMaterial'].node_tree.nodes[
        'Image Texture'].image = bpy.data.images[os.path.basename(filepath)]


def applyHDRI(context, filepath):
    print("HDRI", filepath)

    image_name = os.path.basename(filepath)
    if image_name not in bpy.data.images:
        bpy.ops.image.open(filepath=filepath,
                           directory=os.path.dirname(filepath),
                           files=[{
                               "name": image_name,
                           }],
                           relative_path=True,
                           show_multiview=False)
    # print("Textures", list(bpy.data.images))
    bpy.data.worlds['BaseWorld'].node_tree.nodes[
        'Environment Texture'].image = bpy.data.images[os.path.basename(
            filepath)]


def appendBaseMaterial(context, root_path):

    if 'BaseTextureMaterial' not in bpy.data.materials:

        material_path = os.path.join(root_path, 'base.blend', "Material")

        print(material_path)

        bpy.ops.wm.append(filename='BaseTextureMaterial',
                          directory=str(material_path))

    if 'BaseWorld' not in bpy.data.worlds:

        material_path = os.path.join(root_path, 'base.blend', "World")

        bpy.ops.wm.append(filename='BaseWorld', directory=str(material_path))

        print(material_path)

        context.scene.world = bpy.data.worlds['BaseWorld']


def appendBaseFile(context, root_path):

    base_path = os.path.join(root_path, 'base.blend')

    bpy.ops.wm.append(filename='base.blend', directory=str(base_path))


# def getBBCenter():
#     minx, miny, minz = (999999.0, ) * 3
#     maxx, maxy, maxz = (-999999.0, ) * 3
#     for
#     return


def renderWithCamera(context, camera_name, out_filename):
    bpy.context.scene.camera = bpy.context.scene.objects[camera_name]
    bpy.context.scene.render.filepath = out_filename
    bpy.ops.render.render(write_still=True)


# def get_thumbnail(name):
#     p = paths.get_addon_thumbnail_path(name)
#     name = '.%s' % name
#     img = bpy.data.images.get(name)
#     if img == None:
#         img = bpy.data.images.load(p)
#         image_utils.set_colorspace(img, 'sRGB')
#         img.name = name
#         img.name = name

#     return img
if '__main__' == __name__:

    setCuda()
