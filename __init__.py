# Tea's deCypher Kit, get into the API in no time.
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
    "name": "Tea's deCypher Kit [TCK] 1.2",
    "author": "TeaCrab",
    "blender": (2, 7, 8),
    "description": "Generate a nested menu for any available attributes from available modules.",
    "location": "<Ctrl + W>, accessible in all windows.",
    "category": "Development"
    }

import bpy

class TCK_Pref(bpy.types.AddonPreferences):
    bl_idname = __name__

    hide_generic = bpy.props.BoolProperty(
        name = "Hide Attribute Names That Starts With Underscore",
        default = True)

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

    # access_numpy = bpy.props.BoolProperty(
    #     name = "Access Numpy",
    #     default = False)

    def draw(self, context):
        layout = self.layout
        row = layout.split(1/2)

        b1 = row.box()
        b2 = row.box()

        opt_col = b1.column(True)
        opt_col.label("Defaults to 'bpy' if all modules turned off.")
        opt_col.separator()
        opt_col.prop(self, "hide_generic", toggle = True)

        mod_col = b2.column(True)
        mod_col.label("Module Access:")
        mod_col.separator()
        mod_row = mod_col.row(True)
        mod_row.prop(self, "access_bpy", toggle = True)
        mod_row.prop(self, "access_bpy_extras", toggle = True)
        mod_row.prop(self, "access_bmesh", toggle = True)
        mod_row.prop(self, "access_mathutils", toggle = True)
        # sub.prop(self, "access_numpy", toggle = True)

def pref():
    return bpy.context.user_preferences.addons[__name__].preferences

def aDir(subject):
    return [i for i in dir(subject) if not (pref().hide_generic and i.startswith('_'))]

def print_info(self):
    # self.report({'INFO'}, '{}'.format(str(subject)))
    return
### Here is a good place to import modules.
### If you don't wish the ON/OFF toggle, you can import it along side the 'bpy' module at the top of this file.

# Example:
# import numpy
# OR
# numpy = None      if you wish to turn it on or off.
bpy_extras = None
bmesh = None
mathutils = None

modules = []
command = ''

subject = None
count = 0

def check_modules():
    global bpy_extras, bmesh, mathutils

    if pref().access_bpy_extras: import bpy_extras
    else: bpy_extras = None

    if pref().access_bmesh: import bmesh
    else: bmesh = None

    if pref().access_mathutils: import mathutils
    else: mathutils = None

#   Adds on/off function for the numpy module.
### if pref().access_mathutils: import numpy
### else: numpy = None

def getModules():
    global modules
    modules = [bpy, bpy_extras, bmesh, mathutils] # Add numpy here.
    modules = [m for m in modules if m != None]
    if not pref().access_bpy and len(modules) != 1:
        modules.remove(bpy)
    return modules # If numpy is still 'None', it means it hasn't been imported, which means it's turned off in the preferences, which will be excluded from the targets.

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

def command_last_access():
    access_sequence = access.split('.')
    return '.'.join(access_sequence[-2:])

def print_info(self, obj):
    self.report({'INFO'}, '{}'.format(str(obj)))

def is_basetype(obj):
    basetype = [str, bool, int, float]
    return type(obj) in basetype

def get_name(candidate):
    if candidate in getModules():
        modules_dict = {
            bpy             :   "bpy",
            bpy_extras      :   "bpy_extras",
            bmesh           :   "bmesh",
            mathutils       :   "mathutils",
            # numpy       :   "numpy",
            ### So that the UI knows what name to give all the modules when the menu tries to generate a list for them.  Modules do not have name properties.  Or I wasn't able to find it.
        }
        return modules_dict.get(candidate, None)
    else:
        dirs = dir(candidate)
        if 'module' in dirs:
            return candidate.module
        elif 'name' in dirs:
            return candidate.name
        elif 'type' in dirs:
            return candidate.type
        elif 'bl_rna' in dirs and 'name' in dir(candidate.bl_rna):
            return candidate.bl_rna.name
        else:
            return str(candidate)


class TCK_generate(bpy.types.Operator):
    bl_idname = "tck.generate"
    bl_label = "TCK_generate"

    attribute = bpy.props.StringProperty(default = '')

    def execute(self, context):
        if self.attribute == '':
            return {'CANCELLED'}

        global subject, command, count
        obj = getattr(subject, self.attribute)

        command = command + '.' + self.attribute
        context.window_manager.clipboard = command_extract()
        print_info(self, obj)

        if is_basetype(obj):
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

    def execute(self, context):
        if self.index < 0:
            return {'CANCELLED'}

        global subject, command, count
        obj = subject[self.index]
        if obj in modules:
            command = command + '  ' + get_name(obj)
        else:
            command = command + "[{}]".format(self.index)

        context.window_manager.clipboard = command_extract()
        print_info(self, obj)

        if is_basetype(obj):
            return {'FINISHED'}
        else:
            subject = obj
            bpy.ops.wm.call_menu(name = TCK_MT_Menu.bl_idname)
            count += 1
            return {'FINISHED'}


iter_exceptions = [bpy.app]
special_names = ['name', 'type', 'mode', 'color', 'draw_type']
special_access = ['tna.outerp', 'tna.prefix', 'tna.core', 'tna.suffix']


class TCK_MT_Menu(bpy.types.Menu):
    bl_idname = "TCK_MT_Menu"
    bl_label = "deCypher"

    def draw(self, context):
        global count
        layout = self.layout
        col = layout.column_flow(columns = 3, align = True) # Change the column number for a wider menu.
        if subject in getModules():
            for i in aDir(subject):
                col.operator("tck.generate", text = i).attribute = i
        elif hasattr(subject, '__iter__') and subject not in iter_exceptions:
            for index, i in enumerate(subject):
                col.operator("tck.iterate", text = get_name(i)).index = index
            
        else:
            for i in aDir(subject):
                col.operator("tck.generate", text = i).attribute = i


class TCK_menu_call(bpy.types.Operator):
    bl_idname = "tck.menu_call"
    bl_label = "deCypher"

    def execute(self, context):
        print("\nStarting deCypher...")
        global subject, command, count
        count = 0
        check_modules()
        if len(getModules()) == 1:
            subject = modules[0]
            command = command + '  ' + get_name(subject)
        else:
            subject = getModules()
        bpy.ops.wm.call_menu(name = TCK_MT_Menu.bl_idname)
        return {'FINISHED'}


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
