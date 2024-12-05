import uuid
import maya.cmds as cmds

from . import pickerButton

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui


class ButtonManager(object):
    
    def __init__(self, toolBoxWidget:'ToolBoxWidget' = None):
        self.toolBoxWidget = toolBoxWidget
        
    
    def getToolBoxInfo(self) -> dict:
        if self.toolBoxWidget is None:
            return {'color'    :QtGui.QColor(QtCore.Qt.yellow),
                    'scaleX'   :40,
                    'scaleY'   :40,
                    'textColor':QtGui.QColor(QtCore.Qt.black),
                    'labelText':''} 
                                 
        data = self.toolBoxWidget.get()
        return data
        
        
    def create(self, buttonGlobalPos : QtCore.QPointF, 
                     buttonsParentPos: QtCore.QPointF, 
                     sceneScale      : float,
                     nodeList        : 'list[MayaNodeName]',
                     parent          : 'PickerView' = None,
                     data            : dict = None,
                     buttonId        : str  = None,
                     code            : dict = None) -> pickerButton.PickerButton:
                        
        data           = data or self.getToolBoxInfo()
        buttonColor    = data['color']
        buttonScaleX   = data['scaleX']
        buttonscaleY   = data['scaleY']
        labelTextColor = data['textColor']
        labelText      = data['labelText']
        button = pickerButton.PickerButton(globalPos   = buttonGlobalPos, 
                                           parentPos   = buttonsParentPos,
                                           color       = buttonColor,
                                           sceneScale  = sceneScale,
                                           scaleX      = buttonScaleX, 
                                           scaleY      = buttonscaleY,
                                           textColor   = labelTextColor,
                                           labelText   = labelText,
                                           parent      = parent,
                                           nodes       = nodeList,
                                           buttonId    = str(uuid.uuid4()) if buttonId is None else buttonId,
                                           code        = code)
        return button
        
        
    def updateToolBoxWidget(self, selectedButton):
        if self.toolBoxWidget is None:
            return
        self.toolBoxWidget.set(selectedButton.get())
                