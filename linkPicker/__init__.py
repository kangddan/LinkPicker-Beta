import os
import maya.cmds as cmds

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtCore
else:
    from PySide2 import QtCore
    

ICONS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'linkPickerIcons')
QtCore.QDir.addSearchPath('linkPickerIcons', ICONS_PATH)
