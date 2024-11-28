import uuid
from linkPicker.pickerViewWidgets import pickerButton
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui


class ButtonManager(object):
    
    def __init__(self, toolBoxWidget=None):
        self.toolBoxWidget = toolBoxWidget
        
    
    def getToolBoxInfo(self):
        if self.toolBoxWidget is None:
            return {'color'    :QtGui.QColor(QtCore.Qt.yellow),
                    'scaleX'   :40,
                    'scaleY'   :40,
                    'textColor':QtGui.QColor(QtCore.Qt.black),
                    'labelText':''} 
                                 
        data = self.toolBoxWidget.get()
        return data
        
        
    def create(self, buttonGlobalPos, 
                     buttonsParentPos, 
                     sceneScale,
                     nodeList,
                     parent = None,
                     data = None ,
                     buttonId = None):
                        
        data           = data or self.getToolBoxInfo()
        buttonColor    = data['color']
        buttonScaleX   = data['scaleX']
        buttonscaleY   = data['scaleY']
        labelTextColor = data['textColor']
        labelText      = data['labelText']
        button = pickerButton.PickerButton(globalPos  = buttonGlobalPos, 
                                           parentPos  = buttonsParentPos,
                                           color      = buttonColor,
                                           sceneScale = sceneScale,
                                           scaleX     = buttonScaleX, 
                                           scaleY     = buttonscaleY,
                                           textColor  = labelTextColor,
                                           labelText  = labelText,
                                           parent     = parent,
                                           nodes      = nodeList,
                                           buttonId   = str(uuid.uuid4()) if buttonId is None else buttonId)
        return button
        
        
    def updateToolBoxWidget(self, selectedButton):
        if self.toolBoxWidget is None:
            return
        self.toolBoxWidget.set(selectedButton.get())
            
        