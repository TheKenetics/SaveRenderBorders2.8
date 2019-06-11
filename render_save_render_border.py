bl_info = {
	"name": "Save Render Borders",
	"author": "Kenetics",
	"version": (0, 1),
	"blender": (2, 80, 0),
	"location": "Properties window > Output tab > Saved Render Borders",
	"description": "Tool to save/set render borders.",
	"warning": "",
	"wiki_url": "",
	"category": "Render"
}

import bpy
from bpy.props import EnumProperty, IntProperty, FloatVectorProperty, BoolProperty, FloatProperty, StringProperty, CollectionProperty
from bpy.types import PropertyGroup, UIList


class SRB_saved_render_border(PropertyGroup):
	"""Property Group to store render border information"""
	name : StringProperty(
		name="Saved Render Border Name",
		default="Render Border"
	)
	
	x_min_max : FloatVectorProperty(
		name="X Min Max",
		size=2,
		default=(0.0, 1.0),
		min=0.0,
		max=1.0
	)
	
	y_min_max : FloatVectorProperty(
		name="Y Min Max",
		size=2,
		default=(0.0, 1.0),
		min=0.0,
		max=1.0
	)


class SRB_OT_save_render_border(bpy.types.Operator):
	"""Saves current render border"""
	bl_idname = "render.srb_ot_save_render_border"
	bl_label = "Save Current Render Border"
	bl_options = {'REGISTER','UNDO'}
	
	# Properties
	name : StringProperty(
		name="Render Border Name",
		default="Render Border"
	)
	
	@classmethod
	def poll(cls, context):
		return context.scene.render.use_border
	
	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		render = context.scene.render
		
		# Create new saved render border
		saved_render_border = context.scene.saved_render_borders.add()
		
		saved_render_border.name = self.name
		saved_render_border.x_min_max = (
			render.border_min_x,
			render.border_max_x
		)
		saved_render_border.y_min_max = (
			render.border_min_y,
			render.border_max_y
		)
		
		return {'FINISHED'}


class SRB_OT_set_render_border(bpy.types.Operator):
	"""Sets render border from a saved render border."""
	bl_idname = "render.srb_ot_set_render_border"
	bl_label = "Set Render Border"
	bl_options = {'REGISTER','UNDO', 'INTERNAL'}
	
	# Properties
	index : IntProperty(
		name="Render Border Index",
		description="Index of a saved render border"
	)
	
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		saved_render_border = context.scene.saved_render_borders[self.index]
		render = context.scene.render
		
		render.use_border = True
		render.border_min_x = saved_render_border.x_min_max[0]
		render.border_max_x = saved_render_border.x_min_max[1]
		render.border_min_y = saved_render_border.y_min_max[0]
		render.border_max_y = saved_render_border.y_min_max[1]
		
		return {'FINISHED'}


class SRB_OT_delete_saved_render_border(bpy.types.Operator):
	"""Deletes saved render border"""
	bl_idname = "render.srb_ot_delete_saved_render_border"
	bl_label = "Delete Render Border"
	bl_options = {'REGISTER','UNDO', 'INTERNAL'}
	
	# Properties
	index : IntProperty(
		name="Saved Render Border Index"
	)
	
	@classmethod
	def poll(cls, context):
		return context.scene.saved_render_borders

	def execute(self, context):
		context.scene.saved_render_borders.remove(self.index)
		context.scene.saved_render_borders_index = min(max(0, self.index - 1), len(context.scene.saved_render_borders) - 1)
		
		return {'FINISHED'}


class SRB_UL_saved_render_borders_list(UIList):
	"""List to show all saved render borders."""
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
		if self.layout_type in {"DEFAULT", "COMPACT"}:
			layout.label(text=item.name, icon="SELECT_SET")
			
		elif self.layout_type == "GRID":
			layout.alignment = "CENTER"
			layout.label(label="", icon="SELECT_SET")


class SRB_PT_saved_render_borders_panel(bpy.types.Panel):
	"""Creates a Panel in the Render properties window that lists saved render borders"""
	bl_label = "Saved Render Borders"
	bl_idname = "RENDER_PT_saved_render_borders"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "output"

	def draw(self, context):
		layout = self.layout

		#obj = context.object
		
		# Saved Render Border List
		row = layout.row()
		row.template_list("SRB_UL_saved_render_borders_list", "", context.scene, "saved_render_borders", context.scene, "saved_render_borders_index")
		
		# Operator to save render border
		row = layout.row()
		row.operator(SRB_OT_save_render_border.bl_idname, text="Save", icon='ADD')
		# Operator to set render border as active
		row.operator(SRB_OT_set_render_border.bl_idname, text="Set", icon='IMPORT').index = context.scene.saved_render_borders_index
		# Operator to delete Render Border
		row.operator(SRB_OT_delete_saved_render_border.bl_idname, text="Remove", icon='REMOVE').index = context.scene.saved_render_borders_index


classes = (
	SRB_saved_render_border,
	SRB_OT_save_render_border,
	SRB_OT_set_render_border,
	SRB_OT_delete_saved_render_border,
	SRB_UL_saved_render_borders_list,
	SRB_PT_saved_render_borders_panel
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	bpy.types.Scene.saved_render_borders = CollectionProperty(type = SRB_saved_render_border)
	bpy.types.Scene.saved_render_borders_index = IntProperty(name = "Index for saved_render_borders", default = 0)

def unregister():
	del bpy.types.Scene.saved_render_borders
	del bpy.types.Scene.saved_render_borders_index
	
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()
