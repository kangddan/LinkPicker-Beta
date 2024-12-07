import maya.cmds as cmds
if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui



class PickerBackground(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.picker = parent
        
        self.imagePath       = ''
        self.backgroundImage = None
        self.scaledImage     = None
        
        self.ImageWidth  = 1
        self.ImageHeight = 1
        self.opacity = 1
        
    def get(self) -> dict:
        return {'imagePath'  : self.imagePath,
                'ImageWidth' : self.ImageWidth,
                'ImageHeight': self.ImageHeight,
                'opacity'    : self.opacity,}
                
    def set(self, data):
        self.imagePath   = data['imagePath']
        self.ImageWidth  = data['ImageWidth']
        self.ImageHeight = data['ImageHeight']
        self.opacity     = data['opacity']
        
        self.setBackgroundImage(data['imagePath'], data['ImageWidth'], data['ImageHeight'])
        

    def setBackgroundImage(self, imagePath, width=None, height=None):
        self.imagePath = imagePath
        self.backgroundImage = QtGui.QPixmap(imagePath)
        if not self.backgroundImage.isNull():
            imageSize = self.backgroundImage.size()
            self.resizeBackground(width or imageSize.width(),
                                  height or imageSize.height())   
        self.update()
            
            
    def resizeBackground(self, newWidth, newHeight):
        self.ImageWidth, self.ImageHeight = newWidth, newHeight
        self.updateScale()
        self.updatePos()
        self.update()
        
    
    def updateScale(self):
        self.resize(round(self.ImageWidth * self.picker.sceneScale), round(self.ImageHeight * self.picker.sceneScale))
        
        
    def updatePos(self):
        globalPos = self.picker.buttonsParentPos
        if self.picker.midView:
            globalPos = globalPos - QtCore.QPointF(self.ImageWidth / 2 * self.picker.sceneScale, self.ImageHeight / 2 * self.picker.sceneScale)
        self.move(globalPos.toPoint())
        
        
    def updateOpacity(self, value: float):
        self.opacity = value / 100.0
        self.update()
        
    
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.backgroundImage and not self.backgroundImage.isNull():
            painter = QtGui.QPainter(self)
            painter.setOpacity(self.opacity)
            painter.drawPixmap(self.rect(), self.backgroundImage)
    
    



    
    
    