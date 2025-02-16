# AutoUV MOF Bridge (for Blender)

[![Blender Version](https://img.shields.io/badge/Blender-3.6.4+-orange)](https://www.blender.org/)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

Professional UV unwrapping integration between Blender and Ministry of Flat (MOF). This add-on lets you use MOF directly in Blender to unwrap your meshes quickly. Instead of manually exporting files and running commands, it handles everything with one click – it exports your mesh, runs MOF’s unwrapping tools, and brings the new UVs back into Blender. Your original UVs stay untouched as backups, and the new MOF-generated UVs get added as a separate layer. It also copies over sharp edges and materials, and can optionally replace your original mesh with the MOF-processed version (while keeping its position/rotation). Requires MOF installed separately. Useful for game assets, architectural models, or any project where you need clean, automated UV unwrapping.

![blender_S7KDdavQSz](https://github.com/user-attachments/assets/3b5824f8-ffc4-47bf-9412-03f5afc14a6f)

## Features

- 🎛️ Single-click UV unwrapping utilizing MOF engine
- 📏 Resolution presets from 32 to 4096
- 🔄 Aspect ratio control for non-square textures
- 🗺️ World-space scaling and texture density
- ⚙️ Single advanced setting for mesh replacement

## Installation

1. **Download** [Ministry of Flat](https://www.quelsolaar.com/ministry_of_flat/) executables
2. **Download** the latest release ZIP from this GitHub page
3. **Install in Blender**:
   - Edit > Preferences > Add-ons > Install
   - Select downloaded ZIP file
   - Enable the add-on
4. **Configure MOF Path**:
   - Open add-on preferences
   - Set path to Ministry of Flat (MOF) directory containing executable files

## Usage

1. Select **exactly one** mesh object
2. Open "AutoUV MOF Bridge" panel (N-panel > AutoUV MOF Bridge)
3. Adjust parameters (optional):
   - **Core Settings**: Resolution, Aspect Ratio, etc.
   - **Advanced**: Toggle mesh replacement
4. Click "Auto UV Unwrap"

### Core Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| Resolution | Texture resolution (determines island spacing) | 1024 |
| Aspect Ratio | Width/height ratio for non-square textures | 1.0 |
| Separate Hard Edges | Guarantees hard edges are separated for baking | False |
| Use Normals | Use mesh normals for polygon classification | False |
| Overlap Identical Parts | Overlap identical geometry in UV space | False |
| Overlap Mirrored Parts | Overlap mirrored geometry in UV space | False |
| UDIM Tiles | Number of UDIM tiles for texture splitting | 1 |
| World Scale | Scale UVs to real-world dimensions | False |
| Texture Density | Pixels per unit in world scale mode | 1024 |

### Advanced Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| Replace Original Mesh | Replace original geometry with processed version | False |

## Key Functionality

### Mesh Replacement
When enabled:
- Preserves materials and transforms
- Applies automatic rotation correction
- Maintains object relationships
- Cleans up temporary data automatically

⚠️ **Note:** Original UV maps are preserved in replacement mesh.

## Troubleshooting

**Common Issues:**  
- "Operation not available"  
  → Select exactly one mesh object  
- Rotation mismatch  
  → Enable mesh replacement for auto-correction  
- Missing MOF executable  
  → Verify path in add-on preferences  

## Support

[📚 Ministry of Flat Documentation](https://www.quelsolaar.com/ministry_of_flat/)  
[🐛 Report Issues](https://github.com/dudebroSW/AutoUVMOF/issues)

## License

This project is licensed under the MIT License - See [LICENSE](LICENSE) for details