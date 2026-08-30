# Addon metadata
bl_info = {
    "name": "Suzanne Awards",
    "author": "Ferase",
    "version": (0, 3),
    "blender": (4, 0, 0),
    "location": "View3D > N-Panel > Achievements",
    "description": "Tracks user actions and unlocks achievements",
    "category": "System",
}



import bpy

from . import preferences
from . import state
from . import exp
from . import playtime
from . import manager
from . import toast
from . import ui
from . import sound
from . import daily

from .sources import operator_poll
from .sources import undo_redo_watch
from .sources import file_watch
from .sources import render_watch

# Modules to initialize (daily's register() only sets up its periodic
# timer - its load() runs separately below, before init_achievements())
_modules = (preferences, playtime, ui, toast, sound, operator_poll, undo_redo_watch, file_watch, render_watch)



def register():
    """Register states, manager, and modules on addon load."""

    state.load()
    exp.load()
    daily.load()  # must run before manager.init_achievements() - see daily.py
    manager.init_achievements()
    for mod in _modules:
        if hasattr(mod, "register"):
            mod.register()

def unregister():
    """Tear down modules on addon disable."""

    for mod in reversed(_modules):
        if hasattr(mod, "unregister"):
            mod.unregister()
