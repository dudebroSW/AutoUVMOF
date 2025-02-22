"""
AutoUV MOF Bridge for Blender
-----------------------------
A Blender add-on that integrates Ministry of Flat's UV unwrapping capabilities directly into Blender's workflow.
Provides professional-grade UV unwrapping with configurable parameters and advanced features.
"""

import bpy

class AutoUVProperties(bpy.types.PropertyGroup):
    """Stores all properties for the UV unwrapping operation"""
    # Resolution Param
    resolution: bpy.props.EnumProperty(
        name="Resolution",
        description="Texture resolution (determines island spacing)",
        items=[(str(2**i), str(2**i), "") for i in range(5, 13)],  # 32-4096
        default='1024',
    )

    # Aspect Ratio Param
    aspect_ratio: bpy.props.FloatProperty(
        name="Aspect Ratio",
        description="Width/height ratio for non-square textures",
        default=1.0,
        min=0.001,
        max=1000.0,
        step=0.1,
        precision=6
    )

    # Separate Hard Edges Param
    separate_hard_edges: bpy.props.BoolProperty(
        name="Separate Hard Edges",
        description="Guarantees hard edges are separated for baking",
        default=False
    )

    # Use Normals Param
    use_normals: bpy.props.BoolProperty(
        name="Use Normals",
        description="Use mesh normals for polygon classification",
        default=False
    )

    # UDIMs Param
    udims: bpy.props.IntProperty(
        name="UDIMs",
        description="Number of UDIM tiles for texture splitting",
        default=1,
        min=1,
        max=100
    )
 
    # Overlap Identical Parts Param 
    overlap_identical: bpy.props.BoolProperty(
        name="Overlap Identical Parts",
        description="Overlap identical geometry in UV space",
        default=False
    )
  
    # Overlap Mirrored Parts Param  
    overlap_mirrored: bpy.props.BoolProperty(
        name="Overlap Mirrored Parts",
        description="Overlap mirrored geometry in UV space",
        default=False
    )
    
    # World Scale UVs Param
    world_scale: bpy.props.BoolProperty(
        name="World Scale UVs",
        description="Scale UVs to real-world dimensions",
        default=False
    )

    # Texture Density Param    
    texture_density: bpy.props.IntProperty(
        name="Texture Density",
        description="Pixels per unit in world scale mode",
        default=1024,
        min=1
    )
    
    # Seam Direction Center Param  
    seam_center: bpy.props.FloatVectorProperty(
        name="Seam Direction Center",
        description="World-space center point for seam orientation",
        subtype='XYZ',
        default=(0.0, 0.0, 0.0)
    )
    
    # Show Advanced Settings Param
    show_advanced: bpy.props.BoolProperty(
        name="Show Advanced Settings",
        default=True
    )
    
    # Clean Up Mesh Param
    sanitize_original_mesh: bpy.props.BoolProperty(
        name="Sanitize Original Mesh",
        description="Sanitizes the selected mesh before unwrapping.\nDeletes loose vertices and edges, merges vertices in close proximity (within 0.0001m distance), removes custom split normal data, recalculates normals, and applies default auto smoothing",
        default=False
    )
    
    # Replace Original Mesh Param
    replace_original_mesh: bpy.props.BoolProperty(
        name="Replace Original Mesh",
        description="Replace original geometry with processed version",
        default=False
    )
    
    # Copy Source UVs Param
    copy_source_uvs: bpy.props.BoolProperty(
        name="Copy Source UVs",
        description="Attempts to copy UV layers from selected mesh onto processed MOF mesh",
        default=False
    )
    
    # Copy Processed UVs Param
    copy_processed_uvs: bpy.props.BoolProperty(
        name="Copy Processed UVs",
        description="Attempts to copy UV layers from processed MOF mesh back onto selected mesh.\nIgnored when 'Replace Original Mesh' is toggled",
        default=False
    )

    # Copy Processed Edge Sharps Param
    copy_processed_sharps: bpy.props.BoolProperty(
        name="Copy Processed Edge Sharps",
        description="Attempts to edges marked sharp from processed MOF mesh back onto selected mesh.\nIgnored when 'Replace Original Mesh' is toggled",
        default=False
    )

def register():
    bpy.utils.register_class(AutoUVProperties)
    bpy.types.Scene.autouv_props = bpy.props.PointerProperty(type=AutoUVProperties)

def unregister():
    del bpy.types.Scene.autouv_props
    bpy.utils.unregister_class(AutoUVProperties)