import sys
import maya.OpenMayaUI as omui
import maya.cmds as cmds


if int(cmds.about(version=True)) >= 2025:
    from shiboken6 import wrapInstance
    from PySide6   import QtWidgets, QtCore, QtGui
else:
    from shiboken2 import wrapInstance
    from PySide2   import QtWidgets, QtCore, QtGui


def addUndo(func):
    def undo(*args, **kwargs):
        cmds.undoInfo(openChunk=True)
        func(*args, **kwargs)
        cmds.undoInfo(closeChunk=True)
    return undo  

def getMayaMainWindow() -> QtWidgets.QMainWindow:
    if sys.version_info.major >= 3:
        return wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QMainWindow)
    return wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)





    
