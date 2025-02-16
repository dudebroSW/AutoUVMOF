"""
AutoUV MOF Bridge for Blender
-----------------------------
A Blender add-on that integrates Ministry of Flat's UV unwrapping capabilities directly into Blender's workflow.
Provides professional-grade UV unwrapping with configurable parameters and advanced features.
"""

import bpy
import os
import math
import mathutils
from bpy import context

# Add-on metadata shown in Blender's preferences
bl_info = {
    "name": "AutoUV MOF Bridge (for Blender)",
    "description": "Automate professional UV unwrapping with Ministry of Flat’s engine, directly in Blender",
    "blender": (2, 80, 0),  # Minimum Blender version requirement
    "category": "UV",
    "location": "View Editor > N-Panel > AutoUV MOF Bridge",
    "version": (0, 0, 1),
    "author": "dudebroSW",
    "doc_url": "https://www.quelsolaar.com/ministry_of_flat/",
    "tracker_url": "https://github.com/dudebroSW/AutoUVMOF/",
}


class AutoUVPreferences(bpy.types.AddonPreferences):
    """Stores user preferences for the MOF integration"""
    bl_idname = __name__

    # Path to MOF executable directory
    folder_path: bpy.props.StringProperty(
        name="MOF Directory",
        description="Folder containing Ministry of Flat executables",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        """Draws preferences UI"""
        layout = self.layout
        layout.prop(self, "folder_path")


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
    
    # Replace Original Mesh Param
    replace_original_mesh: bpy.props.BoolProperty(
        name="Replace Original Mesh",
        description="Replace original geometry with processed version",
        default=False
    )


class AutoUVPanel(bpy.types.Panel):
    """UI Panel in 3D Viewport sidebar"""
    bl_label = "AutoUV MOF Bridge"
    bl_idname = "OBJECT_PT_autouv"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AutoUV MOF Bridge"

    def draw(self, context):
        """Draws the panel UI"""
        layout = self.layout
        props = context.scene.autouv_props
        
        # Check if exactly one mesh is selected and active
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        valid = (
            len(selected_meshes) == 1 and (context.active_object is not None and context.active_object.type == 'MESH')
        )

        # Drop-down Inputs
        split = layout.split(factor=0.4, align=True)
        split.label(text="Resolution:")
        split.prop(props, "resolution", text="")

        # Boolean Inputs
        layout.prop(props, "separate_hard_edges")
        layout.prop(props, "use_normals")
        layout.prop(props, "overlap_identical")
        layout.prop(props, "overlap_mirrored")
        layout.prop(props, "world_scale")
        
        # Numerical Inputs
        layout.prop(props, "aspect_ratio", text="Aspect Ratio")
        layout.prop(props, "texture_density", text="Texture Density")
        layout.prop(props, "udims", text="UDIM Tiles")

        layout.label(text="Seam Direction Center:")
        layout.prop(props, "seam_center", text="")

        # Collapsible Advanced Settings
        box = layout.box()
        row = box.row()
        row.prop(props, "show_advanced",
                text="Advanced Settings",
                emboss=False,
                icon='TRIA_DOWN' if props.show_advanced else 'TRIA_RIGHT')
        
        if props.show_advanced:
            box.prop(props, "replace_original_mesh")

        # Operator Button
        row = layout.row()
        row.enabled = valid
        row.operator("object.autouv", text="Auto UV Unwrap")


class AutoUV(bpy.types.Operator):
    """Main operator handling UV unwrapping workflow"""
    bl_idname = "object.autouv"
    bl_label = "Auto UV Unwrap"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        """Operator availability check"""
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        """Main execution method"""
        obj = context.active_object
        props = context.scene.autouv_props

        # Temporary file paths
        temp_dir = bpy.app.tempdir
        orig_obj = os.path.join(temp_dir, f"{obj.name}.obj")
        new_obj = os.path.join(temp_dir, f"{obj.name}_unpacked.obj")

        # Validate MOF executable
        cmd_path = os.path.join(
            context.preferences.addons[__name__].preferences.folder_path,
            "UnWrapConsole3.exe"
        )
        if not os.path.isfile(cmd_path):
            self.report({'ERROR'}, "MOF executable not found in configured directory")
            return {'CANCELLED'}

        # Export original mesh
        bpy.ops.wm.obj_export(
            filepath=orig_obj,
            export_selected_objects=True,
            export_materials=False,
        )

        # Build MOF command parameters
        params = [
            f"-separate {props.separate_hard_edges!s}",
            f"-resolution {props.resolution}",
            f"-aspect {props.aspect_ratio:.6f}",
            f"-normals {props.use_normals!s}",
            f"-udims {props.udims}",
            f"-overlap {props.overlap_identical!s}",
            f"-mirror {props.overlap_mirrored!s}",
            f"-worldscale {props.world_scale!s}",
            f"-density {props.texture_density}",
            f"-center {' '.join(f'{c:.6f}' for c in props.seam_center)}"
        ]
        
        # Execute MOF command
        os.system(f'{cmd_path} {orig_obj} {new_obj} {" ".join(params)}')

        # Import processed mesh
        pre_import = set(bpy.data.objects)
        bpy.ops.wm.obj_import(filepath=new_obj)
        mof_obj = (set(bpy.data.objects) - pre_import).pop()

        # UV Data Transfer
        orig_mesh = obj.data
        mof_mesh = mof_obj.data
        
        # Copy original UV layers to MOF mesh
        for orig_uv in orig_mesh.uv_layers:
            if "mof_uv_layer" in orig_uv.name:
                continue
                
            mof_uv = mof_mesh.uv_layers.new(name=orig_uv.name)
            for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                for l_o, l_m in zip(poly_o.loop_indices, poly_m.loop_indices):
                    mof_uv.data[l_m].uv = orig_uv.data[l_o].uv

        # Finalize MOF UV layer
        final_uv = mof_mesh.uv_layers.new(name="mof_uv_layer")
        for poly in mof_mesh.polygons:
            for li in poly.loop_indices:
                final_uv.data[li].uv = mof_mesh.uv_layers.active.data[li].uv
        mof_mesh.uv_layers.remove(mof_mesh.uv_layers.active)

        # Copy UVs back to original mesh
        new_uv = orig_mesh.uv_layers.new(name="mof_uv_layer")
        for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
            for l_o, l_m in zip(poly_o.loop_indices, poly_m.loop_indices):
                new_uv.data[l_o].uv = final_uv.data[l_m].uv

        # Edge Sharpness Transfer
        if len(orig_mesh.edges) == len(mof_mesh.edges):
            sharp_map = {
                tuple(sorted(e.vertices)): e.use_edge_sharp
                for e in mof_mesh.edges
            }
            for e in orig_mesh.edges:
                key = tuple(sorted(e.vertices))
                if key in sharp_map:
                    e.use_edge_sharp = sharp_map[key]

        # Mesh Replacement Logic
        if props.replace_original_mesh:
            # Transform Correction
            correction = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
            mof_mesh.transform(correction)
            mof_mesh.update()

            # Material Transfer
            mof_mesh.materials.clear()
            for mat in orig_mesh.materials:
                mof_mesh.materials.append(mat)

            # Replace Mesh Data
            obj.data = mof_mesh
            bpy.data.objects.remove(mof_obj)
            
            if orig_mesh.users == 0:
                bpy.data.meshes.remove(orig_mesh)
            
            # Set mesh as selected
            obj.select_set(True)
            context.view_layer.objects.active = obj

        # Cleanup
        os.remove(orig_obj)
        os.remove(new_obj)
        
        return {'FINISHED'}


def register():
    """Register classes and properties"""
    classes = (AutoUVPreferences, AutoUVProperties, AutoUVPanel, AutoUV)
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.autouv_props = bpy.props.PointerProperty(type=AutoUVProperties)


def unregister():
    """Unregister classes and properties"""
    classes = (AutoUVPreferences, AutoUVProperties, AutoUVPanel, AutoUV)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.autouv_props


if __name__ == "__main__":
    register()