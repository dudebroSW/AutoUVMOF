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

        # Clean Up Mesh
        if props.sanitize_original_mesh:          
            # Store the original mode and ensure the object is active and selected
            original_mode = obj.mode
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            
            # Switch to Edit mode if not already in it
            if original_mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            
            # Delete loose geometry
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete_loose()
            
            # Merge vertices (remove doubles) with the given threshold
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.remove_doubles(threshold=0.0001)
            
            # Remove custom split normals
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            
            # Switch to Object mode to recalc normals and apply auto smoothing
            bpy.ops.object.mode_set(mode='OBJECT')
            obj.data.calc_normals()
            obj.data.use_auto_smooth = True
            obj.data.auto_smooth_angle = math.radians(30)
            
            # Restore the original mode if necessary
            if original_mode == 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')

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

        orig_mesh = obj.data
        mof_mesh = mof_obj.data
        mof_uv_layer = mof_mesh.uv_layers[0] if mof_mesh.uv_layers else None

        # Edge Sharpness Transfer
        if props.copy_processed_sharps and not props.replace_original_mesh:
            if len(orig_mesh.edges) == len(mof_mesh.edges):
                sharp_map = {
                    tuple(sorted(e.vertices)): e.use_edge_sharp
                    for e in mof_mesh.edges
                }
                for e in orig_mesh.edges:
                    key = tuple(sorted(e.vertices))
                    if key in sharp_map:
                        e.use_edge_sharp = sharp_map[key]
            else:
                self.report({'WARNING'}, "Unable to copy processed edge sharps. Polygon loop indices mismatch between original and processed meshes.")

        # Clean Up Processed Mesh
        if props.sanitize_processed_mesh:          
            # Store the original mode and ensure the object is active and selected
            original_mode = obj.mode
            bpy.context.view_layer.objects.active = mof_obj
            mof_obj.select_set(True)
            
            # Switch to Edit mode if not already in it
            if original_mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            
            # Remove custom split normals
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            
            # Switch to Object mode to disable sharp edges
            bpy.ops.object.mode_set(mode='OBJECT')
            for e in mof_mesh.edges:
                e.use_edge_sharp = False
            
            # Restore the original mode if necessary
            if original_mode == 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
        
        # UV Data Transfers
        # Copy processed MOF UV back to original mesh
        if props.copy_processed_uvs and not props.replace_original_mesh:
            if mof_uv_layer is not None:
                # Check if the number of polygons in the original and processed meshes are the same
                if len(orig_mesh.polygons) != len(mof_mesh.polygons):
                    self.report({'WARNING'}, "Unable to copy processed UVs. Number of polygons in original and processed meshes do not match.")
                else:
                    # Check if each polygon in both meshes has the same number of loop indices
                    for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                        if len(poly_o.loop_indices) != len(poly_m.loop_indices):
                            self.report({'WARNING'}, f"Unable to copy processed UVs. Polygon with index {poly_o.index} has different loop indices in original and processed meshes.")
                            break
                    else:
                        # Proceed with UV copy if everything matches
                        new_uv = orig_mesh.uv_layers.new(name="mof_uv_layer")
                        for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                            for l_o, l_m in zip(poly_o.loop_indices, poly_m.loop_indices):
                                new_uv.data[l_o].uv = mof_uv_layer.data[l_m].uv

                
        # Copy original UV layers to MOF mesh
        if props.copy_source_uvs:
            error_found = False
            for orig_uv in orig_mesh.uv_layers:
                if "mof_uv_layer" in orig_uv.name:
                    continue  # Skip uv layers that were copied back to the original mesh

                # Check if the number of polygons in the original and processed meshes are the same
                if len(orig_mesh.polygons) != len(mof_mesh.polygons):
                    self.report({'WARNING'}, "Unable to copy source UVs. Number of polygons in original and processed meshes do not match.")
                    error_found = True
                    break  # Exit the loop to prevent further UV copying
                
                # Check for any mismatch in loop indices length across all polygons
                index_mismatch_found = False
                for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                    if len(poly_o.loop_indices) != len(poly_m.loop_indices):
                        index_mismatch_found = True
                        error_found = True
                        break  # Exit the loop as we only need to report one mismatch

                if index_mismatch_found:
                    self.report({'WARNING'}, "Unable to copy source UVs. Polygon loop indices mismatch between original and processed meshes.")
                    break
                else:
                    # Copy UV data from original to MOF mesh
                    mof_uv = mof_mesh.uv_layers.new(name=orig_uv.name)
                    for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                        for l_o, l_m in zip(poly_o.loop_indices, poly_m.loop_indices):
                            mof_uv.data[l_m].uv = orig_uv.data[l_o].uv

            # Move MOF UV layer to end
            if mof_uv_layer is not None and not error_found:
                final_uv = mof_mesh.uv_layers.new(name="mof_uv_layer")
                for poly in mof_mesh.polygons:
                    for li in poly.loop_indices:
                        final_uv.data[li].uv = mof_mesh.uv_layers.active.data[li].uv
                mof_mesh.uv_layers.remove(mof_mesh.uv_layers.active)

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