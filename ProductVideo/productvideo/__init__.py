bl_info = {
    'name': 'Product Video',
    'author': 'saurabh jadhav',
    'version': (1, 0, 11),
    'blender': (3, 1, 2),
    'location': '',
    'description': '',
    'warning': '',
    'wiki_url': '',
    'support': 'COMMUNITY',
    'category': 'Animation'
}

__version__ = '.'.join(map(str, bl_info['version']))

# Handle Reload Scripts
if 'reload' in locals():
    import importlib as il
    il.reload(reload)
    reload.all()

import productvideo.reload as reload
from productvideo.utils.deps import intallDependancies


def register():
    from . import patch
    patch.add_local_modules_to_path()

    intallDependancies([
    ])

    from productvideo import properties
    from productvideo import operators
    from productvideo import panels

    properties.register()
    operators.register()
    panels.register()


def unregister():
    from productvideo import panels
    from productvideo import operators
    from productvideo import properties

    panels.unregister()
    operators.unregister()
    properties.unregister()


if __name__ == '__main__':
    register()
