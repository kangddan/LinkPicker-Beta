import maya.cmds as cmds
if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtCore
else:
    from PySide2 import QtCore


from . import pickerUtils


class FrameSelectorHelper(object):
  
    def __init__(self, pivkerViewInstance: 'PickerView'):
        self.pivkerView = pivkerViewInstance
        
 
    def _buttonsBoundingBox(self) -> QtCore.QRectF:
        buttons = self.pivkerView.selectedButtons or self.pivkerView.allPickerButtons
        if not buttons:
            return None
        
        boundingBox = QtCore.QRectF()
        for button in buttons:
            '''
            https://doc.qt.io/qtforpython-5/PySide2/QtCore/QRectF.html#PySide2.QtCore.PySide2.QtCore.QRectF.united
            '''
            #buttonRect = QtCore.QRectF(button.pos(), button.size())
            buttonRect = QtCore.QRectF(pickerUtils.localToGlobal(button.localPos, self.pivkerView.buttonsParentPos, self.pivkerView.sceneScale), 
                                       QtCore.QSizeF(button.scaleX * self.pivkerView.sceneScale, button.scaleY * self.pivkerView.sceneScale))
            boundingBox = boundingBox.united(buttonRect)

        return boundingBox
        
        
    def frameSelection(self):
        if not self.pivkerView.frameMoveTag:
            return 
            
        boundingBox = self._buttonsBoundingBox()
        if boundingBox is None:
            self.pivkerView._frameDefault()
            return 
            
        viewRect   = self.pivkerView.geometry()
        viewWidth  = viewRect.width()
        viewHeight = viewRect.height()

        # get scale
        scale = min(viewWidth / boundingBox.width(), viewHeight / boundingBox.height())

        self.pivkerView.sceneScale = self.pivkerView.origScale * scale

        # move to view center
        boundingBoxCenter = boundingBox.center()
        viewCenter = QtCore.QPointF(viewWidth / 2.0, viewHeight / 2.0)
        
        localPos = (self.pivkerView.buttonsParentPos + (viewCenter - boundingBoxCenter) - viewCenter) * scale
        newButtonsParentPos = viewCenter + localPos

        self.pivkerView.buttonsParentPos = newButtonsParentPos
    
        self.pivkerView.parentAxis.move(self.pivkerView.buttonsParentPos.toPoint())
        self.pivkerView.parentAxis.resize(round(100 * self.pivkerView.sceneScale), round(100 * self.pivkerView.sceneScale))

        # update buttons pos and scale
        self.pivkerView.updateButtonsPos(updateScale=True)

        self.pivkerView.origScale = self.pivkerView.sceneScale
        self.pivkerView.frameMoveTag = False
        if self.pivkerView.midView:
            self.pivkerView.updateMidViewOffset()
        return 
        


        

            
            