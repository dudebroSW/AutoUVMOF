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


class AutoUV(bpy.types.Operator):
    """Main operator handling UV unwrapping workflow"""
    bl_idname = f"{__name__.split('.')[0]}.autouvmof"
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
        
        addon_name = __name__.split('.')[0]

        # Validate MOF executable
        cmd_path = os.path.join(
            context.preferences.addons[addon_name].preferences.folder_path,
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
    bpy.utils.register_class(AutoUV)

def unregister():
    bpy.utils.unregister_class(AutoUV)