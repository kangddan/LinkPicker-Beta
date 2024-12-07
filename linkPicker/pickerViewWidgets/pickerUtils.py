import maya.cmds as cmds

if int(cmds.about(version=True)) >= 2025:
    from PySide6   import QtWidgets, QtCore, QtGui
else:
    from PySide2   import QtWidgets, QtCore, QtGui

def buttonsBoundingBox(selectedButtons: 'list[PickerButton]', 
                       pickerButtons  : 'list[PickerButton]') -> QtCore.QRectF:
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
    

def localToGlobal(localPos  : QtCore.QPointF, 
                  parentPos : QtCore.QPointF, 
                  sceneScale: float) -> QtCore.QPointF: 
    return (localPos * sceneScale) + parentPos
    
def globalToLocal(globalPos : QtCore.QPointF, 
                  parentPos : QtCore.QPointF, 
                  sceneScale: float) -> QtCore.QPointF:  
    return (globalPos - parentPos) * 1.0 / sceneScale 
    

        