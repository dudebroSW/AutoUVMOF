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
        """Operator availability check:
        Returns True if all selected objects are mesh.
        """
        selected = context.selected_objects
        return bool(selected) and all(obj.type == 'MESH' for obj in selected)

    def execute(self, context):
        """Main execution method unwrapping meshes"""
        props = context.scene.autouv_props
        addon_name = __name__.split('.')[0]

        # Validate MOF executable
        cmd_path = os.path.join(
            context.preferences.addons[addon_name].preferences.folder_path,
            "UnWrapConsole3.exe"
        )
        if not os.path.isfile(cmd_path):
            self.report({'ERROR'}, "MOF executable not found in configured directory")
            return {'CANCELLED'}

        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if not selected_meshes:
            self.report({'ERROR'}, "No mesh selected")
            return {'CANCELLED'}

        temp_dir = bpy.app.tempdir
        
        # Begin progress reporting
        wm = bpy.context.window_manager
        total_meshes = len(selected_meshes)
        wm.progress_begin(0, total_meshes)

        # Process each selected mesh individually
        for i, obj in enumerate(selected_meshes):
            # Deselect all objects then select only the current mesh
            for ob in context.selected_objects:
                ob.select_set(False)
            obj.select_set(True)
            context.view_layer.objects.active = obj

            # Temporary file paths (per mesh)
            orig_obj = os.path.join(temp_dir, f"{obj.name}.obj")
            new_obj = os.path.join(temp_dir, f"{obj.name}_unpacked.obj")

            # -----------------------------
            # Clean Up Original Mesh
            # -----------------------------
            if props.sanitize_original_mesh:
                original_mode = obj.mode
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                if original_mode != 'EDIT':
                    bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.delete_loose()
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.remove_doubles(threshold=0.00015)
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
                bpy.ops.object.mode_set(mode='OBJECT')
                obj.data.calc_normals()
                obj.data.use_auto_smooth = True
                obj.data.auto_smooth_angle = math.radians(35)
                if original_mode == 'EDIT':
                    bpy.ops.object.mode_set(mode='EDIT')

            # -----------------------------
            # Export Original Mesh
            # -----------------------------
            bpy.ops.wm.obj_export(
                filepath=orig_obj,
                export_selected_objects=True,
                export_materials=False,
            )

            # -----------------------------
            # Build MOF Command Parameters & Execute
            # -----------------------------
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
            os.system(f'{cmd_path} {orig_obj} {new_obj} {" ".join(params)}')

            # -----------------------------
            # Import Processed Mesh
            # -----------------------------
            pre_import = set(bpy.data.objects)
            bpy.ops.wm.obj_import(filepath=new_obj)
            mof_obj = (set(bpy.data.objects) - pre_import).pop()

            orig_mesh = obj.data
            mof_mesh = mof_obj.data
            mof_uv_layer = mof_mesh.uv_layers[0] if mof_mesh.uv_layers else None

            # -----------------------------
            # Edge Sharpness Transfer
            # -----------------------------
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
                    self.report({'WARNING'}, "Unable to copy processed edge sharps. Mesh edge counts do not match.")

            # -----------------------------
            # Clean Up Processed Mesh
            # -----------------------------
            if props.sanitize_processed_mesh:
                original_mode = obj.mode
                bpy.context.view_layer.objects.active = mof_obj
                mof_obj.select_set(True)
                if original_mode != 'EDIT':
                    bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.customdata_custom_splitnormals_clear()
                bpy.ops.object.mode_set(mode='OBJECT')
                for e in mof_mesh.edges:
                    e.use_edge_sharp = False
                if original_mode == 'EDIT':
                    bpy.ops.object.mode_set(mode='EDIT')

            # -----------------------------
            # UV Data Transfers
            # -----------------------------
            # Copy processed MOF UV back to original mesh
            if props.copy_processed_uvs and not props.replace_original_mesh:
                if mof_uv_layer is not None:
                    if len(orig_mesh.polygons) != len(mof_mesh.polygons):
                        self.report({'WARNING'}, "Unable to copy processed UVs. Number of polygons do not match.")
                    else:
                        mismatch_found = False
                        for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                            if len(poly_o.loop_indices) != len(poly_m.loop_indices):
                                self.report({'WARNING'}, f"Unable to copy processed UVs. Polygon {poly_o.index} has mismatched loop indices.")
                                mismatch_found = True
                                break
                        if not mismatch_found:
                            new_uv = orig_mesh.uv_layers.new(name="mof_uv_layer")
                            for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                                for l_o, l_m in zip(poly_o.loop_indices, poly_m.loop_indices):
                                    new_uv.data[l_o].uv = mof_uv_layer.data[l_m].uv

            # Copy original UV layers to MOF mesh
            if props.copy_source_uvs:
                error_found = False
                for orig_uv in orig_mesh.uv_layers:
                    if "mof_uv_layer" in orig_uv.name:
                        continue  # Skip uv layers already copied back
                    if len(orig_mesh.polygons) != len(mof_mesh.polygons):
                        self.report({'WARNING'}, "Unable to copy source UVs. Number of polygons do not match.")
                        error_found = True
                        break
                    index_mismatch_found = False
                    for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                        if len(poly_o.loop_indices) != len(poly_m.loop_indices):
                            index_mismatch_found = True
                            error_found = True
                            break
                    if index_mismatch_found:
                        self.report({'WARNING'}, "Unable to copy source UVs. Polygon loop indices mismatch between original and processed meshes.")
                        break
                    else:
                        mof_uv = mof_mesh.uv_layers.new(name=orig_uv.name)
                        for poly_o, poly_m in zip(orig_mesh.polygons, mof_mesh.polygons):
                            for l_o, l_m in zip(poly_o.loop_indices, poly_m.loop_indices):
                                mof_uv.data[l_m].uv = orig_uv.data[l_o].uv

                # Move the new MOF UV layer to the end (if no error)
                if mof_uv_layer is not None and not error_found:
                    final_uv = mof_mesh.uv_layers.new(name="mof_uv_layer")
                    # Copy active UV data to the new layer
                    for poly in mof_mesh.polygons:
                        for li in poly.loop_indices:
                            final_uv.data[li].uv = mof_mesh.uv_layers.active.data[li].uv
                    mof_mesh.uv_layers.remove(mof_mesh.uv_layers.active)

            # -----------------------------
            # Mesh Replacement Logic
            # -----------------------------
            if props.replace_original_mesh:
                correction = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
                mof_mesh.transform(correction)
                mof_mesh.update()
                mof_mesh.materials.clear()
                for mat in orig_mesh.materials:
                    mof_mesh.materials.append(mat)
                obj.data = mof_mesh
                bpy.data.objects.remove(mof_obj)
                if orig_mesh.users == 0:
                    bpy.data.meshes.remove(orig_mesh)
                obj.select_set(True)
                context.view_layer.objects.active = obj

            # -----------------------------
            # Cleanup Temporary Files
            # -----------------------------
            try:
                os.remove(orig_obj)
                os.remove(new_obj)
            except Exception as e:
                self.report({'WARNING'}, f"Cleanup error: {str(e)}")
                
            # Update progress after processing mesh
            wm.progress_update(i + 1)
            
        # End progress
        wm.progress_end()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(AutoUV)

def unregister():
    bpy.utils.unregister_class(AutoUV)
