# Custom properties on objects

Zip the contents of this folder from within the parent directory:

```bash
zip -r custom_properties_on_objects.zip custom_properties_on_objects/
```

In Blender 2.79, navigate to `File > User Preferences... > Add-ons > Install Add-on from file...` and select `custom_properties_on_objects.zip`

Next, open Blender's scripting view, and select an object in the scene. Paste the following into the script terminal:

```python
# this will print False
print(bpy.context.active_object.my_custom_property_group.skip_export)

bpy.context.active_object.my_custom_property_group.skip_export = True

# this will print True
print(bpy.context.active_object.my_custom_property_group.skip_export)
```