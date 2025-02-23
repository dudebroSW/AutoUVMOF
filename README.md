# AutoUV MOF Bridge (for Blender)

[![Blender Version](https://img.shields.io/badge/Blender-3.6.4+-orange)](https://www.blender.org/) [![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

Professional UV unwrapping integration between Blender and Ministry of Flat (MOF). This add-on lets you use MOF directly in Blender to unwrap your meshes quickly. Instead of manually exporting files and running commands, it handles everything with one click – it exports your mesh, runs MOF’s unwrapping tools, and brings the new UVs back into Blender. Your original UVs stay untouched as backups, and the new MOF-generated UVs get added as a separate layer. It also copies over sharp edges and materials and can optionally replace your original mesh with the MOF-processed version (while keeping its position/rotation). Requires MOF installed separately. Useful for game assets, architectural models, or any project where you need clean, automated UV unwrapping.

![blender_QfP0Nr2MY8](https://github.com/user-attachments/assets/f22fe1d6-4d5c-44cf-9252-135656626c29)

## Features

- 🎛️ Single-click UV unwrapping utilizing MOF engine  
- 🚀 Batch Processing: Process multiple meshes in one go with a progress bar update  
- 📏 Resolution presets from 32 to 4096 for island spacing control
- 🔄 Aspect ratio control for non-square textures  
- 🗺️ World-space scaling and texture density settings
- ⚙️ Advanced settings for mesh replacement, UV transfers, and edge sharpness preservation

## Installation

1. **Download** [Ministry of Flat](https://www.quelsolaar.com/ministry_of_flat/) executables
2. **Download** the [latest release ZIP](https://github.com/dudebroSW/AutoUVMOF/releases/) from this GitHub page
3. **Install in Blender**:
   - Edit > Preferences > Add-ons > Install
   - Select downloaded ZIP file
   - Enable the add-on
4. **Configure MOF Path**:
   - Open add-on preferences
   - Set path to Ministry of Flat (MOF) directory containing executable files

## Usage

1. Select **one or more** mesh objects (all selected objects must be meshes).
2. Open the "AutoUV MOF Bridge" panel (N-panel > AutoUV MOF Bridge).
3. Adjust parameters (optional):
   - **Core Settings:** Resolution, Separate Hard Edges, etc.
   - **Advanced:** Toggle options for mesh replacement, UV transfers, and more.
4. Click the operator button:
   - When a single mesh is selected, the button reads **"Auto UV Unwrap"**.
   - When multiple meshes are selected, the button reads **"Auto UV Unwrap (Batch)"**.
5. During batch processing, a progress bar in Blender’s status bar will indicate how far along the process is.

### Core Parameters

| Parameter              | Description                                                                         | Default |
|------------------------|-------------------------------------------------------------------------------------|---------|
| Resolution             | Texture resolution (determines island spacing)                                      | 1024    |
| Aspect Ratio           | Width/height ratio for non-square textures                                          | 1.0     |
| Separate Hard Edges    | Guarantees hard edges are separated for baking; useful for light/normal mapping     | False   |
| Use Normals            | Use mesh normals for polygon classification                                         | False   |
| Overlap Identical Parts| Overlap identical geometry in UV space                                              | False   |
| Overlap Mirrored Parts | Overlap mirrored geometry in UV space                                               | False   |
| UDIM Tiles             | Number of UDIM tiles for texture splitting                                          | 1       |
| World Scale            | Scale UVs to real-world dimensions                                                  | False   |
| Texture Density        | Pixels per unit in world scale mode                                                 | 1024    |

### Advanced Settings

| Parameter                  | Description                                                                                   | Default |
|----------------------------|-----------------------------------------------------------------------------------------------|---------|
| Replace Original Mesh      | Replace original geometry with processed version (preserving transform and materials)         | False   |
| Sanitize Original Mesh     | Clean up selected mesh (remove loose geometry, merge doubles, recalc normals, auto-smooth)       | False   |
| Sanitize Processed Mesh    | Clean up the MOF-processed mesh (remove custom split normals, disable sharp edges)              | False   |
| Copy Source UVs            | Copy existing UV layers from the source mesh onto the processed MOF mesh                        | False   |
| Copy Processed UVs         | Copy processed MOF UV layers back onto the source mesh (ignored if mesh replacement is enabled)  | False   |
| Copy Processed Edge Sharps | Copy sharp edge markings from the processed MOF mesh back to the original mesh                   | False   |

## Key Functionality

### Batch Processing
- **Batch Processing:** The add-on now supports unwrapping multiple meshes simultaneously. When more than one mesh is selected, the operator processes each mesh sequentially.

### Mesh Replacement
When enabled:
- Preserves materials and transforms  
- Applies automatic rotation correction  
- Maintains object relationships  
- Cleans up temporary data automatically  

## Troubleshooting

**Common Issues:**  
- **"Operation not available":**  
  → Ensure that all selected objects are meshes  
- **Rotation mismatch:**  
  → Enable mesh replacement for auto-correction  
- **Missing MOF executable:**  
  → Verify the MOF directory path in add-on preferences  
- **Batch Process Freezes/No Feedback:**  
  → Check that your system meets the minimum Blender version requirements (3.6.4+)

## Support

[📚 Ministry of Flat Documentation](https://www.quelsolaar.com/ministry_of_flat/)  
[🐛 Report Issues](https://github.com/dudebroSW/AutoUVMOF/issues)

## License

This project is licensed under the MIT License – See [LICENSE](LICENSE) for details
