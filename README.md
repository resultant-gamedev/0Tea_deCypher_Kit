# 0Tea_deCypher_Kit
Blender, access to module command with ease.

UPDATE v1.3:

  Added multi-word filter popup for modules with high number of attributes.
  Filter popup can be forced by holding down Shift key when clicking on a menu item.
  It can also be skipped by holding down Alt or OS-key.


UPDATE v1.2:

  Made sure it will not map each letter in a string into a new menu.
  Added bpy_extra module into the default.  Turn it on or off in the addon preference panel.


UPDATE v1.1:

  Most of the items in the modules will now display proper name/text instead of a string of unreadable code.


Easy access for additional modules.  Mathutils and Bmesh module support is included.  Instructions on how to add support for any modules are commented along side an example of Numpy module.

This menu is accessible from all windows in Blender.

bpy.context is respected.
Though, any command manually entered from the console will limit the context to the console itself.
Context sensitive commands to be converted into actual executeble commands inside the console is on the todo list.

Default short-cut/hotkey:  Ctrl + W.

Happy Blending.
