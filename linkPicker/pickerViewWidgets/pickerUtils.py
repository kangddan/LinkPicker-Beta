from __future__ import division
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

def buttonsBoundingBox(selectedButtons, 
                       pickerButtons):
    buttons = selectedButtons or pickerButtons
    if not buttons:
        return None

    boundingBox = QtCore.QRectF()
    for button in buttons:
        '''
        https://doc.qt.io/qtforpython-5/PySide2/QtCore/QRectF.html#PySide2.QtCore.PySide2.QtCore.QRectF.united
        '''
        buttonRect = QtCore.QRectF(button.pos(), button.size())
        boundingBox = boundingBox.united(buttonRect)

    return boundingBox
    

def localToGlobal(localPos, 
                  parentPos, 
                  sceneScale): 
    return (localPos * sceneScale) + parentPos
    
def globalToLocal(globalPos, 
                  parentPos, 
                  sceneScale):  
    return (globalPos - parentPos) * 1.0 / sceneScale 
    

        