import maya.cmds as cmds
if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui


class PickerBackground(QtWidgets.QWidget):
    
    def __init__(self, globalPos : QtCore.QPointF, # top left or mid pos
                       parentPos : QtCore.QPointF, 
                       sceneScale: float = 1.0, 
                       parent    : QtWidgets.QWidget = None):
                        
        ...
        
    