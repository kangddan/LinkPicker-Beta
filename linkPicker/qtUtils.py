import sys
import maya.OpenMayaUI as omui
import maya.cmds as cmds
from shiboken2 import wrapInstance, getCppPointer

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore


def getMayaMainWindow():
    if sys.version_info.major >= 3:
        return wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QMainWindow)
    return wrapInstance(long(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)




    
