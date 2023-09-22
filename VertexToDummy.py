import bpy
import math

class AddEmptyToVerticesOperator(bpy.types.Operator):
    bl_idname = "object.add_empty_to_vertices"
    bl_label = "Add Empty to Selected Vertices"

    empty_type: bpy.props.EnumProperty(
        items=[
            ('PLAIN_AXES', 'Plain Axes', 'Plain Axes'),
            ('SINGLE_ARROW', 'Single Arrow', 'Single Arrow'),
            ('CUBE', 'Cube', 'Cube'),
            ('CIRCLE', 'Circle', 'Circle'),
        ],
        name="Empty Type",
        description="Choose the type of empty object to create",
        default='CUBE'
    )

    object_scale: bpy.props.FloatProperty(
        name="Object Scale",
        description="Scale factor for the empty object",
        default=0.5,
        min=0.01,
        max=2.0
    )

    empty_name_prefix: bpy.props.StringProperty(
        name="Empty Name Prefix",
        description="Prefix for the empty object names",
        default="Empty_"
    )

    align_with_normal: bpy.props.BoolProperty(
        name="Align with Vertex Normal",
        description="Align the empty with the vertex normal",
        default=False
    )

    def calculate_vertex_normal(self, obj, vertex):
        # Get the normalized normal of the vertex
        return vertex.normal.normalized()

    def execute(self, context):
        # Get the active object (assumes it's a mesh)
        obj = context.active_object
        if obj is None or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object first.")
            return {'CANCELLED'}

        # Store the current mode (Object or Edit)
        current_mode = context.mode

        # Switch to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Get the selected vertices
        selected_verts = [v for v in obj.data.vertices if v.select]

        # Counter for naming convention
        empty_counter = 1

        # Create a new empty (dummy) for each selected vertex
        for vert in selected_verts:
            empty_name = f"{self.empty_name_prefix}{empty_counter}"
            bpy.ops.object.empty_add(type=self.empty_type, location=obj.matrix_world @ vert.co)
            new_empty = context.active_object
            new_empty.scale = (self.object_scale, self.object_scale, self.object_scale)
            new_empty.name = empty_name
            empty_counter += 1

            if self.align_with_normal:
                # Calculate vertex normal for the current vertex
                vertex_normal = self.calculate_vertex_normal(obj, vert)

                # Calculate the rotation quaternion to align the empty with the vertex normal
                rot_quaternion = vertex_normal.to_track_quat('Z', 'Y')

                # Apply the rotation to the empty object
                new_empty.rotation_euler = rot_quaternion.to_euler()

        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(AddEmptyToVerticesOperator)

def unregister():
    bpy.utils.unregister_class(AddEmptyToVerticesOperator)

# Register the operator
register()

# Execute the operator with default values
bpy.ops.object.add_empty_to_vertices('INVOKE_DEFAULT')
