"""
AutoUV MOF Bridge for Blender
-----------------------------
A Blender add-on that integrates Ministry of Flat's UV unwrapping capabilities directly into Blender's workflow.
Provides professional-grade UV unwrapping with configurable parameters and advanced features.
"""

import bpy

class AutoUVPreferences(bpy.types.AddonPreferences):
    """Stores user preferences for the MOF integration"""
    bl_idname = __name__.split('.')[0]  # Gets 'auto_uv_mof_bridge'

    # Path to MOF executable directory
    folder_path: bpy.props.StringProperty(
        name="MOF Directory",
        description="Folder containing Ministry of Flat executables",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        """Draws preferences UI"""
        self.layout.prop(self, "folder_path")

def register():
    bpy.utils.register_class(AutoUVPreferences)

def unregister():
    bpy.utils.unregister_class(AutoUVPreferences)