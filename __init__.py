# Copyright (C) 2016  Yuanqing(Brent) Liu

# ### BEGIN GPL LICENSE BLOCK ###
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ### END GPL LICENSE BLOCK ###

'''

Generates a nested menu for all attributes available under the selected module.
Selecting an attribute in the menu will automatically generate a console command and copied to the clipboard.
The list of "bpy.context" varies in different area/space.  Some of the context command generated outside of 3D view and console may yield error when copied to the console.

Adding more modules are easy tasks.  See comment.

IMPORTANT:  bpy.types has 5000+ entries, it will freeze for a blink.  It's not very useful having 5000 items in the menu I know.  Working on a special menu for submodule that contains large amount of entries.

'''

bl_info = {
    "name": "Tea's deCypher Kit [TCK] 1.3",
    "author": "TeaCrab",
    "blender": (2, 7, 8),
    "description": "Generate menus for all available attributes from selected modules.",
    "location": "<Ctrl + W>, accessible in all windows.",
    "category": "Development"
    }

import bpy
from mathutils import Color, Euler, Vector, Matrix, Quaternion

### Import modules here if you don't wish the ON/OFF toggle.

# Example:
# import {module}
# OR
numpy = None
bpy_extras = None
bmesh = None
mathutils = None

modules = []
command = ''

subject = None
count = 0

class TCK_Pref(bpy.types.AddonPreferences):
    bl_idname = __name__

    hide_generic = bpy.props.BoolProperty(
        name = "Hide Attribute Names That Starts With Underscore",
        default = True)

    filter_threshold = bpy.props.IntProperty(
        name = "Filter Activation Threshold",
        description = "Threshold amount of elements in the about-to-be-generated menu.\nIf greater than the value, a filter prompt will show before running the menu generator.",
        min = 64,
        max = 1024,
        default = 150)

    filter_resets = bpy.props.BoolProperty(
        name = "Resets",
        description = "Determines whether to reset the filter conditions every time it is activated.",
        default = True)

    filter_target = bpy.props.StringProperty(default = '')

    filter_mode = bpy.props.EnumProperty(
        items = (
            ('N', 'None', ""),
            ('S', 'Starts with', ""),
            ('E', 'Ends with', ""),),
        default = 'N')

    access_bpy = bpy.props.BoolProperty(
        name = "Bpy",
        default = True)

    access_bpy_extras = bpy.props.BoolProperty(
        name = "Bpy_Extras",
        default = False)

    access_bmesh = bpy.props.BoolProperty(
        name = "Bmesh",
        default = False)

    access_mathutils = bpy.props.BoolProperty(
        name = "Mathutils",
        default = False)

    access_numpy = bpy.props.BoolProperty(
        name = "Numpy",
        default = False)

    # access_{module} = bpy.props.BoolProperty(
    #     name = "{module}",
    #     default = False)

    def draw(self, context):
        layout = self.layout
        row = layout.split(1/2)

        b1 = row.box()
        b2 = row.box()

        opt_col = b1.column(True)
        opt_col.label("Use 'bpy.context' when no modules are enabled.")
        opt_col.separator()
        opt_col.prop(self, "hide_generic", toggle = True)
        opt_row = opt_col.split(4/5, True)
        opt_row.prop(self, "filter_threshold")
        opt_row.prop(self, "filter_resets", toggle = True)

        mod_col = b2.column(True)
        mod_col.label("Module Access:")
        mod_col.separator()
        mod_row = mod_col.row(True)
        mod_row.prop(self, "access_bpy", toggle = True)
        mod_row.prop(self, "access_bpy_extras", toggle = True)
        mod_row.prop(self, "access_bmesh", toggle = True)
        mod_row = mod_col.row(True)
        mod_row.prop(self, "access_mathutils", toggle = True)
        mod_row.prop(self, "access_numpy", toggle = True)

def pref():
    return bpy.context.user_preferences.addons[__name__].preferences

def aDir(subject):
    return [i for i in dir(subject) if not (pref().hide_generic and i.startswith('_'))]

def print_info(self, obj):
    self.report({'INFO'}, '{}'.format(str(obj)))

def overmass(obj):
    if obj in getModules():
        amount = len(aDir(obj))
    elif hasattr(obj, '__iter__') and obj not in iter_exceptions:
        amount = len(obj)
    else:
        amount = len(aDir(obj))
    return amount > pref().filter_threshold

def getColumn():
    return 4 if overmass(subject) else 3

def check_name(string):
    mode = pref().filter_mode
    target = pref().filter_target.lower().split()
    string = string.lower()
    if target == []:
        return True
    else:
        if mode == 'S':
            return any(string.startswith(i) for i in target)
        elif mode == 'E':
            return any(string.endswith(i) for i in target)
        else:
            return all(i in string for i in target)



def check_modules():
    global bpy_extras, bmesh, mathutils, numpy

    if pref().access_bpy_extras: import bpy_extras
    else: bpy_extras = None

    if pref().access_bmesh: import bmesh
    else: bmesh = None

    if pref().access_mathutils: import mathutils
    else: mathutils = None

    if pref().access_numpy: import numpy
    else: numpy = None

### if pref().access_{module}: import {module}
### else: {module} = None
#   This is to achieve on/off toggle function for the new module .


def getModules():
    global modules
    modules = [bpy, bpy_extras, bmesh, mathutils, numpy] # Add numpy here.
    modules = [m for m in modules if m != None]
    if not pref().access_bpy:
        modules.remove(bpy)
    return modules # If {module} != 'None', it means it's imported, which will show up in the initial menu.

def command_extract(module_name = ''):
    global command
    if module_name == '':
        i = command.rfind('  ')
        if i == -1:
            return ''
        else:
            return command[(i+2):]
    else:
        i = command.rfind(module_name)
        return command[i:]

# This function hasn't being used.
def command_last_access():
    access_sequence = command.split('.')
    return '.'.join(access_sequence[-2:])

def is_basetype(obj):
    basetypes = [str, bool, int, float, complex, Color, Euler, Vector, Matrix, Quaternion]
    if '__class__' in dir(obj):
        return obj.__class__ in basetypes
    else:
        return type(obj) in basetypes

def get_name(candidate, deep = False):
    if candidate in getModules():
        return candidate.__name__
    elif deep:
        dirs = dir(candidate)
        if __name__ in dirs:
            return str(candidate.__name__)
        if 'module' in dirs:
            return str(candidate.module)
        elif 'name' in dirs:
            return str(candidate.name)
        elif 'type' in dirs:
            return str(candidate.type)
        elif 'bl_rna' in dirs and 'name' in dir(candidate.bl_rna):
            return str(candidate.bl_rna.name)
        else:
            return str(candidate)
    else:
        return str(candidate)


class TCK_generate(bpy.types.Operator):
    bl_idname = "tck.generate"
    bl_label = "TCK_generate"

    attribute = bpy.props.StringProperty(options = {'HIDDEN'}, default = '')
    mode = bpy.props.StringProperty(options = {'HIDDEN'}, default = '')

    def invoke(self, context, event):
        self.mode = ''
        if event.shift:
            self.mode = 'FILTER'
        elif event.oskey or event.alt:
            self.mode = 'BYPASS'
        if pref().filter_resets:
            pref().filter_target = ''
            pref().filter_mode = 'N'
        return self.execute(context)

    def execute(self, context):
        if self.attribute == '':
            return {'CANCELLED'}

        global subject, command, count
        obj = getattr(subject, self.attribute)

        command = command + '.' + self.attribute
        context.window_manager.clipboard = command_extract()
        print_info(self, obj)

        if is_basetype(obj) or callable(obj):
            return {'FINISHED'}
        elif self.mode == 'BYPASS':
            subject = obj
            bpy.ops.wm.call_menu(name = TCK_MT_Menu.bl_idname)
            count += 1
            return {'FINISHED'}
        elif self.mode == 'FILTER' or overmass(obj):
            subject = obj
            bpy.ops.tck.filter("INVOKE_DEFAULT")
            count += 1
            return {'FINISHED'}
        else:
            subject = obj
            bpy.ops.wm.call_menu(name = TCK_MT_Menu.bl_idname)
            count += 1
            return {'FINISHED'}


class TCK_iterate(bpy.types.Operator):
    bl_idname = "tck.iterate"
    bl_label = "TCK_iterate"

    index = bpy.props.IntProperty(default = -1)
    mode = bpy.props.StringProperty(options = {'HIDDEN'}, default = '')

    def invoke(self, context, event):
        self.mode = ''
        if event.shift:
            self.mode = 'FILTER'
        elif event.oskey or event.alt:
            self.mode = 'BYPASS'
        if pref().filter_resets:
            pref().filter_target = ''
            pref().filter_mode = 'N'
        return self.execute(context)

    def execute(self, context):
        if self.index < 0:
            return {'CANCELLED'}

        global subject, command, count
        obj = subject[self.index]
        if obj in modules:
            command = command + '  ' + get_name(obj)
        else:
            command = command + "[{0}]".format(str(self.index))

        context.window_manager.clipboard = command_extract()
        print_info(self, obj)

        if is_basetype(obj) or callable(obj):
            return {'FINISHED'}
        elif self.mode == 'BYPASS':
            subject = obj
            bpy.ops.wm.call_menu(name = TCK_MT_Menu.bl_idname)
            count += 1
            return {'FINISHED'}
        elif self.mode == 'FILTER' or overmass(obj):
            subject = obj
            bpy.ops.tck.filter("INVOKE_DEFAULT")
            count += 1
            return {'FINISHED'}
        else:
            subject = obj
            bpy.ops.wm.call_menu(name = TCK_MT_Menu.bl_idname)
            count += 1
            return {'FINISHED'}




class TCK_filter(bpy.types.Operator):
    bl_idname = "tck.filter"
    bl_label = "deCypher"
    bl_descrption = "If left empty, next menu will display everything"

    def invoke(self, context, event):
        if pref().filter_resets:
            pref().filter_target = ''
            pref().filter_mode = 'N'
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width = 500)

    def draw(self, context):
        layout = self.layout
        row = layout.split(1/7)
        col = row.column(True)
        col.label("Filter:")
        col = row.column(True)
        col.prop(pref(), "filter_target", text = '')
        row = col.row(True)
        row.prop(pref(), "filter_mode", expand = True)

    def execute(self, context):
        bpy.ops.wm.call_menu(name = TCK_MT_Submenu.bl_idname)
        return {'FINISHED'}


iter_exceptions = [bpy.app]
special_names = ['name', 'type', 'mode', 'color', 'draw_type']
special_access = ['tna.outerp', 'tna.prefix', 'tna.core', 'tna.suffix']

class TCK_menu_call(bpy.types.Operator):
    bl_idname = "tck.menu_call"
    bl_label = "deCypher"

    def execute(self, context):
        global subject, command, count
        count = 0
        check_modules()
        modules = getModules()
        if len(modules) == 0:
            subject = bpy.context
            command = command + '  ' + "bpy.context"
        elif len(modules) == 1:
            subject = modules[0]
            command = command + '  ' + get_name(subject)
        else:
            subject = modules
        bpy.ops.wm.call_menu(name = TCK_MT_Menu.bl_idname)
        return {'FINISHED'}


class TCK_MT_Submenu(bpy.types.Menu):
    bl_idname = "TCK_MT_Submenu"
    bl_label = "deCypher"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        col = layout.column_flow(columns = getColumn(), align = True) # Change the column number for a wider menu.
        if subject in getModules():
            for i in aDir(subject):
                if check_name(i):
                    col.operator("tck.generate", text = i).attribute = i
        elif hasattr(subject, '__iter__') and subject not in iter_exceptions:
            for index, i in enumerate(subject):
                if check_name(get_name(i)):
                    col.operator("tck.iterate", text = get_name(i, deep = True)).index = index
        else:
            for i in aDir(subject):
                if check_name(i):
                    col.operator("tck.generate", text = i).attribute = i


class TCK_MT_Menu(bpy.types.Menu):
    bl_idname = "TCK_MT_Menu"
    bl_label = "deCypher"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        col = layout.column_flow(columns = getColumn(), align = True) # Change the column number for a wider menu.
        if subject in getModules():
            for i in aDir(subject):
                col.operator("tck.generate", text = i).attribute = i
        elif hasattr(subject, '__iter__') and subject not in iter_exceptions:
            for index, i in enumerate(subject):
                col.operator("tck.iterate", text = get_name(i, deep = True)).index = index
        else:
            for i in aDir(subject):
                col.operator("tck.generate", text = i).attribute = i

# Registration

addon_keymaps = []

def register_keymaps():
    wm = bpy.context.window_manager

    km = wm.keyconfigs.addon.keymaps.new(name = 'Window', space_type = 'EMPTY')
    kmi = km.keymap_items.new('tck.menu_call', 'W', 'PRESS', ctrl = True)
    addon_keymaps.append((km, kmi))

def unregister_keymaps():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

def register():
    bpy.utils.register_module(__name__)

    register_keymaps()

def unregister():
    unregister_keymaps()

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
