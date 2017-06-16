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


'''

bl_info = {
    "name": "Tea's deCypher Kit [TCK] 1.1",
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

    # Properties to access mathutils module.
    access_mu = bpy.props.BoolProperty(
        name = "Access Mathutils",
        default = False)

    # Properties to access bmesh module.
    access_bm = bpy.props.BoolProperty(
        name = "Access Bmesh",
        default = False)

    # access_numpy = bpy.props.BoolProperty(
    #     name = "Access Numpy",
    #     default = False)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column()
        row = col.split(1/2, True)
        row.prop(self, "hide_generic", toggle = True)
        sub = row.split(1/2, True) # Change this to 1/3 so the numpy button can fit in the row.
        sub.prop(self, "access_mu", toggle = True)
        sub.prop(self, "access_bm", toggle = True)
        # sub.prop(self, "access_numpy", toggle = True)


def pref():
    return bpy.context.user_preferences.addons[__name__].preferences

### Here is a good place to import modules.
### If you don't wish the ON/OFF toggle, you can import it along side the 'bpy' module at the top of this file.

# Example:
# import numpy
# OR
# numpy = None      if you wish to turn it on or off.

mathutils = None
bmesh = None
modules = []

command = ''
subject = None

def check_modules():
    global modules, mathutils, bmesh
    if pref().access_mu and mathutils == None:
        import mathutils
    if pref().access_bm and bmesh == None:
        import bmesh
#   Adds on/off function for the numpy module.
### if pref().access_numpy and numpy == None:
###     import numpy


def getModules():
    global modules
    modules = [bpy, mathutils, bmesh] # Add numpy here.
    return [m for m in modules if m != None] # If numpy is still 'None', it means it hasn't been imported, which means it's turned off in the preferences, which will be excluded from the targets.

def aDir(subject):
    return [i for i in dir(subject) if not (pref().hide_generic and i.startswith('_'))]

def extract_last_command(module_name = ''):
    global command
    if module_name == '':
        j = command.rfind('  ')
        return command[(j+2):]
    else:
        i = command.rfind(module_name)
        return command[i:]

def get_module_name(module):
    modules = {
        bpy         :   "bpy",
        mathutils   :   "mathutils",
        bmesh       :   "bmesh",
        # numpy       :   "numpy",
        ### So that the UI knows what name to give all the modules when the menu tries to generate a list for them.  Modules do not have name properties.  Or I wasn't able to find it.
    }
    return modules.get(module, None)

def get_name(subject):
    dirs = dir(subject)
    if subject in modules:
        return get_module_name(subject)
    elif 'module' in dirs:
        return subject.module
    elif 'name' in dirs:
        return subject.name
    elif 'bl_rna' in dirs and 'name' in dir(subject.bl_rna):
        return subject.bl_rna.name
    else:
        return str(subject)


class TCK_generate(bpy.types.Operator):
    bl_idname = "tck.generate"
    bl_label = "TCK_generate"

    attribute = bpy.props.StringProperty(default = '')

    def execute(self, context):
        if self.attribute == '':
            return {'CANCELLED'}

        global subject, command
        obj = getattr(subject, self.attribute)

        command = command + '.' + self.attribute
        context.window_manager.clipboard = extract_last_command()
        self.report({'OPERATOR'}, '{}'.format(str(obj)))

        if self.attribute in special_attributes:
            return {'FINISHED'}
        subject = obj
        bpy.ops.wm.call_menu(name = TCK_menu.bl_idname)
        return {'FINISHED'}


class TCK_iterate(bpy.types.Operator):
    bl_idname = "tck.iterate"
    bl_label = "TCK_iterate"

    index = bpy.props.IntProperty(default = -1)

    def execute(self, context):
        if self.index < 0:
            return {'CANCELLED'}

        global subject, command
        obj = subject[self.index]
        if obj in modules:
            command = command + '  ' + get_module_name(obj)
        else:
            command = command + "[{}]".format(self.index)

        context.window_manager.clipboard = extract_last_command()
        self.report({'OPERATOR'}, '{}'.format(str(obj)))

        subject = obj
        bpy.ops.wm.call_menu(name = TCK_menu.bl_idname)
        return {'FINISHED'}

exceptions = [bpy.app]
special_attributes = ['name',]


class TCK_menu_call(bpy.types.Operator):
    bl_idname = "tck.menu_call"
    bl_label = "deCypher"

    def execute(self, context):
        global subject, command
        check_modules()
        if len(getModules()) < 2:
            subject = modules[0]
            # Skips the first menu when there are only 1 option to choose.  This defaults to the 'bpy' module.
            command = command + '  ' + get_module_name(subject)
        else:
            subject = getModules()
        bpy.ops.wm.call_menu(name = TCK_menu.bl_idname)
        return {'FINISHED'}


class TCK_menu(bpy.types.Menu):
    bl_idname = "tca.menu"
    bl_label = "deCypher"

    def draw(self, context):
        layout = self.layout
        col = layout.column_flow(columns = 4, align = True) # Change the column number for a wider menu.
        if subject in modules:
            for i in aDir(subject):
                col.operator("tck.generate", text = i).attribute = i
        elif hasattr(subject, '__iter__') and subject not in exceptions:
            for index, i in enumerate(subject):
                col.operator("tck.iterate", text = get_name(i)).index = index
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
