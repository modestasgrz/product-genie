import bmesh
import bpy
from mathutils import Vector
from bpy_extras import object_utils
from bpy_extras.object_utils import world_to_camera_view


def checkObjectBBInsideCamera(orig_obj):
    is_inside = True
    for corner in orig_obj.bound_box:
        vertex = orig_obj.matrix_world @ Vector(corner)
        cam = world_to_camera_view(bpy.context.scene, bpy.context.scene.camera,
                                   vertex)
        if not (cam[0] >= 0.00 and cam[0] <= 1.0 and cam[1] >= 0.0
                and cam[1] <= 1.0):
            is_inside = False

    return is_inside


def focusObjectInsideCamera(orig_obj, delta=[0, 0, 0, -1], camera=None):
    camera = camera or bpy.context.scene.camera
    bpy.context.view_layer.update()
    while not checkObjectBBInsideCamera(orig_obj):
        camera.location += Vector(delta[:3])
        try:
            camera.lens += delta[3]
        except Exception:
            pass
        bpy.context.view_layer.update()


# from blender templates
def add_box(width, height, depth):
    """
    This function takes inputs and returns vertex and face arrays.
    no actual mesh data creation is done here.
    """

    verts = [
        (+1.0, +1.0, -1.0),
        (+1.0, -1.0, -1.0),
        (-1.0, -1.0, -1.0),
        (-1.0, +1.0, -1.0),
        (+1.0, +1.0, +1.0),
        (+1.0, -1.0, +1.0),
        (-1.0, -1.0, +1.0),
        (-1.0, +1.0, +1.0),
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (4, 0, 3, 7),
    ]

    # apply size
    for i, v in enumerate(verts):
        verts[i] = v[0] * width, v[1] * depth, v[2] * height

    return verts, faces


def groupBoundingBox(selected_objects):
    minx, miny, minz = (999999.0, ) * 3
    maxx, maxy, maxz = (-999999.0, ) * 3
    location = [
        0.0,
    ] * 3
    for obj in selected_objects:
        for v in obj.bound_box:
            v_world = obj.matrix_world @ Vector((v[0], v[1], v[2]))

            if v_world[0] < minx:
                minx = v_world[0]
            if v_world[0] > maxx:
                maxx = v_world[0]

            if v_world[1] < miny:
                miny = v_world[1]
            if v_world[1] > maxy:
                maxy = v_world[1]

            if v_world[2] < minz:
                minz = v_world[2]
            if v_world[2] > maxz:
                maxz = v_world[2]

    verts_loc, faces = add_box((maxx - minx) / 2, (maxz - minz) / 2,
                               (maxy - miny) / 2)
    mesh = bpy.data.meshes.new("BoundingBox")
    bm = bmesh.new()
    for v_co in verts_loc:
        bm.verts.new(v_co)

    bm.verts.ensure_lookup_table()

    for f_idx in faces:
        bm.faces.new([bm.verts[i] for i in f_idx])

    bm.to_mesh(mesh)
    mesh.update()
    location[0] = minx + ((maxx - minx) / 2)
    location[1] = miny + ((maxy - miny) / 2)
    location[2] = minz + ((maxz - minz) / 2)
    bbox = object_utils.object_data_add(bpy.context, mesh, operator=None)
    # does a bounding box need to display more than the bounds??
    bbox.location = location
    bbox.display_type = 'BOUNDS'
    bbox.hide_render = False
    return bbox
