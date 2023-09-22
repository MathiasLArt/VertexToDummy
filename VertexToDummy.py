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

    def calculate_vertex_normal(self, obj, vertex):
        # Store the original vertex selection and deselect all
        original_selection = [v.select for v in obj.data.vertices]
        for v in obj.data.vertices:
            v.select = False

        # Select the current vertex
        vertex.select = True

        # Get the normal of the selected vertex
        vertex_normal = vertex.normal

        # Restore the original vertex selection
        for v, selected in zip(obj.data.vertices, original_selection):
            v.select = selected

        return vertex_normal

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

            # Calculate vertex normal for the current vertex
            vertex_normal = self.calculate_vertex_normal(obj, vert)

            # Calculate the rotation matrix to align the empty with the vertex normal
            align_matrix = vertex_normal.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            new_empty.matrix_world = align_matrix @ new_empty.matrix_world

        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

def register():
    bpy.utils.register_class(AddEmptyToVerticesOperator)

def unregister():
    bpy.utils.unregister_class(AddEmptyToVerticesOperator)

#if __name__ == "__main__":
register()

# Execute the operator directly
bpy.ops.object.add_empty_to_vertices()
