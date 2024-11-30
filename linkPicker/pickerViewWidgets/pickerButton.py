import uuid
import maya.cmds as cmds
if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui

from .. import path
from . import pickerUtils


class PickerButton(QtWidgets.QWidget):
    SELECTED_COLOR = QtGui.QColor(225, 225, 225)
    
    def __repr__(self) -> str:
        globaPos = self.pos()
        localPos = self.localPos
        return f'<{self.__class__.__name__} at {hex(id(self))}: G->({globaPos.x()}, {globaPos.y()}), L->({localPos.x()}, {localPos.y()})>'


    def __str__(self) -> str:
        return str(self.nodes)
    
    
    def __contains__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return all(node in self.nodes for node in other.nodes)
        elif isinstance(other, str):
            return other in self.nodes
        return False
        
        
    def __iter__(self):
        return (node for node in self.nodes)
    
    
    def __len__(self) -> int:
        return len(self.nodes)
        
        
    def __getitem__(self, index):
        if isinstance(index, int):
            return self.nodes[index]
        elif isinstance(index, str):
            if index in self.__dict__:
                return self.__dict__[index]
            raise KeyError(f"Key '{index}' not found in object attributes.")
        else:
            raise TypeError(f"Index must be an int or str, got {type(index).__name__}.")

    
    def __init__(self, globalPos : QtCore.QPointF, 
                       parentPos : QtCore.QPointF, 
                       color     : QtGui.QColor = QtGui.QColor(100, 100, 100),
                       sceneScale: float = 1.0, 
                       scaleX    : int = 40,
                       scaleY    : int = 40,
                       textColor : QtGui.QColor = QtGui.QColor(10, 10, 10),
                       labelText : str = '',
                       parent    : QtWidgets.QWidget = None,
                       nodes     : list = None,
                       buttonId  : str = None):  
        '''
        Args:
            globalPos (QPointF): Initial global position of the button when created.
            parentPos (QPointF): Virtual position relative to the picker, used to calculate the button's position relative to it.
            color (QColor)     : Button background color.
            sceneScale (float) : Scale factor of the scene.
            scaleX (int)       : Button width.
            scaleY (int)       : Button height.
            textColor (QColor) : Button text color.
            labelText (str)    : Button text.
            parent (QWidget)   : Parent widget.
            nodes (str)        : Maya node names
            buttonId (int)     : uuid
        '''
        super().__init__(parent)

        self.scaleX     = scaleX
        self.scaleY     = scaleY
        self.color      = color
        self.sceneScale = sceneScale
        
        _width  = round(scaleX * sceneScale)
        _height = round(scaleY * sceneScale)
        
        globalTopLeftPos = QtCore.QPointF(globalPos.toPoint().x() - _width / 2, globalPos.toPoint().y() - _height / 2) # get button top left Pos
        
        self.resize(_width, _height)
        self.move(globalTopLeftPos.toPoint())
        
        '''
        Initialize the local position relative to the virtual axis based on the global position at the time of button creation.
        '''
        self.updateLocalPos(globalTopLeftPos, parentPos, sceneScale)
        
        self.buttonColor = color
        self.selected    = False

        self.labelText = labelText
        self.textColor = textColor
        self._createWidgets()
        self._createLayouts()
        self.updateLabelText(self.labelText, sceneScale)
        self.updateLabelColor(self.textColor)
        
        self.updateButton(nodes)
        
        self.buttonId = buttonId
        

    def _setToolTop(self):
        tooltipText = '<br>'.join(f'-> {node}' for node in self.nodes)
        self.setToolTip(tooltipText)
        
        
    def updateButton(self, nodes, oldNodes=None):
        '''
        Usually, updating a button only requires passing the nodes parameter
        The lodNodes parameter is only used in conjunction with undo functionality and is not mandatory
        '''
        self.oldNodes    = oldNodes or nodes
        self.nodes       = nodes
        self.isCircle    = len(nodes) > 1
        self.isMaxButton = self.isCircle 
        self._setToolTop()
        
        
    def updateNamespace(self, namespace: str):
        self.nodes = self.oldNodes if namespace == ':' else path.updateNamespaceWithOptional(self.nodes, namespace)
        
        # clear namespace and update oldNodes
        if namespace == '':
            self.oldNodes = self.nodes
        self._setToolTop()


    def _createWidgets(self):
        self.textLabel = QtWidgets.QLabel('', self)
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)
        
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.textLabel)
        
        
    def updateLabelText(self, text: str, sceneScale: float):
        self.labelText = text
        self.scaleText(sceneScale)
        
    def scaleText(self, sceneScale: float):
        font = QtGui.QFont('Verdana', round(self.scaleY * sceneScale * 0.15))
    
        self.textLabel.setFont(font)
        self.textLabel.setText(self.labelText)
        
        
    def updateLabelColor(self, color: QtGui.QColor):
        self.textColor = color
        palette = self.textLabel.palette()
        palette.setColor(QtGui.QPalette.WindowText, self.textColor) 
        self.textLabel.setPalette(palette)
    

    def setSelected(self, selected: bool) -> None:
        self.selected    = selected
        self.buttonColor = PickerButton.SELECTED_COLOR if self.selected else self.color
        self.update()
        
    
    def resetPos(self, buttonsParentPos=QtCore.QPointF()) -> None:
        self.resize(self.scaleX, self.scaleY)
        self.move(self.localPos.toPoint() + buttonsParentPos.toPoint())
    
    
    def updateLocalPos(self, globalPos: QtCore.QPointF, 
                             parentPos: QtCore.QPointF, 
                             sceneScale: float) -> None:
        self.localPos = pickerUtils.globalToLocal(globalPos, parentPos, sceneScale)
        
         
    def updateColor(self, color: QtGui.QColor) -> None:
        if color == self.color:
            return
        self.color = self.buttonColor = color
        self.update()
    
    
    def cenrerPos2(self, globalPos:QtCore.QPointF, sceneScale: float) -> QtCore.QPointF:
        '''
        Use internal floating-point values to calculate the center position for higher precision
        '''
        return globalPos + QtCore.QPointF(self.scaleX * sceneScale / 2, self.scaleY * sceneScale / 2)    
  
  
    def cenrerPos(self, globalPos:QtCore.QPointF) -> QtCore.QPointF:
        return globalPos + QtCore.QPointF(self.width() / 2, self.height() / 2)

    
    def updateScaleX(self, scaleX: int, sceneScale: float, parentPos: QtCore.QPointF) -> None:  
        if scaleX == self.scaleX:
            return
            
        self.scaleX = max(10, min(scaleX, 400))
        self._scale(sceneScale, parentPos)
        

    def updateScaleY(self, scaleY: int, sceneScale: float, parentPos: QtCore.QPointF) -> None:
        if scaleY == self.scaleY:
            return
 
        self.scaleY = max(10, min(scaleY, 400))
        self._scale(sceneScale, parentPos)
    
    
    def _scale(self, sceneScale: float, parentPos: QtCore.QPointF) -> None:
        newWidth  = round(self.scaleX * sceneScale)
        newHeight = round(self.scaleY * sceneScale)
        
        globalPos = pickerUtils.localToGlobal(self.localPos, parentPos, sceneScale)
        

        oldCenter = self.cenrerPos(globalPos)
        self.resize(newWidth, newHeight)
        newCenter = self.cenrerPos(globalPos)

        
        newPosition = globalPos + (oldCenter - newCenter)
        self.move(newPosition.toPoint())
        self.updateLocalPos(newPosition, parentPos, sceneScale)

        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setBrush(self.buttonColor)
        painter.setPen(QtCore.Qt.NoPen)

        rect = QtCore.QRect(0, 0, self.width(), self.height())
        
        if self.isCircle:
            painter.drawEllipse(rect)
        else:
            painter.drawRect(rect)
        
        
    def enterEvent(self, event):
        self.buttonColor = PickerButton.SELECTED_COLOR if self.selected else QtGui.QColor(180, 180, 180)
        self.update()
        
        
    def leaveEvent(self, event):
        self.buttonColor = PickerButton.SELECTED_COLOR if self.selected else self.color
        self.update()
        
        
    def get(self) -> dict:
        return {'color'    :self.color,
                'scaleX'   :self.scaleX,
                'scaleY'   :self.scaleY,
                'textColor':self.textColor,
                'labelText':self.labelText
                }  
                
                
    def set(self):
        pass
   