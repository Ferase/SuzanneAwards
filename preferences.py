"""
Addon preferences, shown under Edit > Preferences > Add-ons > SuzanneAwards.
"""



import bpy



class ACHIEVEMENT_AP_preferences(bpy.types.AddonPreferences):
    # Get the package name
    bl_idname = __package__

    volume: bpy.props.FloatProperty(
        name="Unlock sound volume",
        description="Volume of the achievement unlock sound.",
        default=0.5,
        min=0.0,
        max=1.0,
        subtype="FACTOR",
    )

    def draw(self, context: bpy.types.Context):
        """Draw the preferences panel."""

        layout = self.layout
        layout.prop(self, "volume", slider=True)



def get_prefs() -> "ACHIEVEMENT_AP_preferences":
    """Convenience accessor so other modules (sound.py) don't need to
    repeat the bpy.context.preferences.addons[...] lookup themselves."""

    return bpy.context.preferences.addons[__package__].preferences



classes = (ACHIEVEMENT_AP_preferences,)

def register():
    """Register preferences."""

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    """Unregister preferences."""

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)