"""
AutoUV MOF Bridge for Blender
-----------------------------
A Blender add-on that integrates Ministry of Flat's UV unwrapping capabilities directly into Blender's workflow.
Provides professional-grade UV unwrapping with configurable parameters and advanced features.
"""

# Add-on metadata shown in Blender's preferences
bl_info = {
    "name": "AutoUV MOF Bridge (for Blender)",
    "description": "Automate professional UV unwrapping with Ministry of Flat’s engine, directly in Blender",
    "blender": (3, 6, 4),  # Minimum Blender version requirement
    "category": "UV",
    "location": "View Editor > N-Panel > AutoUV MOF Bridge",
    "version": (0, 0, 1),
    "author": "dudebroSW",
    "doc_url": "https://www.quelsolaar.com/ministry_of_flat/",
    "tracker_url": "https://github.com/dudebroSW/AutoUVMOF/",
}

from . import autouvmof, properties, panels, preferences

def register():
    # Registration order matters!
    preferences.register()
    properties.register()
    panels.register()
    autouvmof.register()

def unregister():
    # Reverse order for unregister
    autouvmof.unregister()
    panels.unregister()
    properties.unregister()
    preferences.unregister()

if __name__ == "__main__":
    register()