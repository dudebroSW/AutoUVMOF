"""
AutoUV MOF Bridge for Blender
-----------------------------
A Blender add-on that integrates Ministry of Flat's UV unwrapping capabilities directly into Blender's workflow.
Provides professional-grade UV unwrapping with configurable parameters and advanced features.
"""

import bpy

class AutoUVPanel(bpy.types.Panel):
    """UI Panel in 3D Viewport sidebar"""
    bl_label = "AutoUV MOF Bridge"
    bl_idname = f"{__name__.split('.')[0]}.panels"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AutoUV MOF Bridge"

    def draw(self, context):
        """Draws the panel UI"""
        layout = self.layout
        props = context.scene.autouv_props
        
        # Get all selected meshes
        selected = context.selected_objects
        valid = bool(selected) and all(obj.type == 'MESH' for obj in selected)
        
        # Determine button text based on the number of selected meshes
        if len(selected) > 1:
            button_text = "Auto UV Unwrap (Batch)"
        else:
            button_text = "Auto UV Unwrap"

        # (Other UI properties and controls...)
        split = layout.split(factor=0.4, align=True)
        split.label(text="Resolution:")
        split.prop(props, "resolution", text="")

        layout.prop(props, "separate_hard_edges")
        layout.prop(props, "use_normals")
        layout.prop(props, "overlap_identical")
        layout.prop(props, "overlap_mirrored")
        layout.prop(props, "world_scale")
        layout.prop(props, "aspect_ratio", text="Aspect Ratio")
        layout.prop(props, "texture_density", text="Texture Density")
        layout.prop(props, "udims", text="UDIM Tiles")
        layout.label(text="Seam Direction Center:")
        layout.prop(props, "seam_center", text="")

        # Advanced Settings (collapsible)
        box = layout.box()
        row = box.row()
        row.prop(props, "show_advanced",
                 text="Advanced Settings",
                 emboss=False,
                 icon='TRIA_DOWN' if props.show_advanced else 'TRIA_RIGHT')
        
        if props.show_advanced:
            box.prop(props, "sanitize_original_mesh")
            box.prop(props, "sanitize_processed_mesh")
            box.prop(props, "replace_original_mesh")
            box.prop(props, "copy_source_uvs")
            box.prop(props, "copy_processed_uvs")
            box.prop(props, "copy_processed_sharps")

        # Operator Button
        row = layout.row()
        row.enabled = valid
        row.operator(f"{__name__.split('.')[0]}.autouvmof", text=button_text)

def register():
    bpy.utils.register_class(AutoUVPanel)

def unregister():
    bpy.utils.unregister_class(AutoUVPanel)
