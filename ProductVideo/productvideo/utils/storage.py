# utils
import os
import bpy


def getLibraryDataPath():
    return bpy.path.abspath(os.path.join(os.path.dirname(__file__), "../Data"))
