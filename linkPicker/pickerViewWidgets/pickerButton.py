import enum
import uuid
import maya.cmds as cmds
import maya.mel as mel

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui

from .. import path, qtUtils
from . import pickerUtils


class PickerButtonEnum(enum.Enum):
    NONE = enum.auto()  
      
    LEFT_CLICKE = enum.auto()


class PickerButton(QtWidgets.QWidget):
    SELECTED_COLOR = QtGui.QColor(225, 225, 225)
    STATE_COLOR    = QtGui.QColor(170, 170, 170)
    
    def __repr__(self) -> str:
        #globaPos = self.pos()
        #localPos = self.localPos
        #return f'<{self.__class__.__name__} at {hex(id(self))}: G->({globaPos.x()}, {globaPos.y()}), L->({localPos.x()}, {localPos.y()})>'
        return f'<{self.__class__.__name__} at {hex(id(self))} max={self.isMaxButton}>'


    def __str__(self) -> str:
        #return str(self.nodes)
        return f'<{self.__class__.__name__} at {hex(id(self))} max={self.isMaxButton}>'
    
    
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

    
    def __init__(self, globalPos   : QtCore.QPointF, 
                       parentPos   : QtCore.QPointF, 
                       color       : QtGui.QColor = QtGui.QColor(100, 100, 100),
                       sceneScale  : float = 1.0, 
                       scaleX      : int = 40,
                       scaleY      : int = 40,
                       textColor   : QtGui.QColor = QtGui.QColor(10, 10, 10),
                       labelText   : str = '',
                       parent      : QtWidgets.QWidget = None,
                       nodes       : list = None,
                       buttonId    : str = None,
                       code        : dict = None):  
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
        
        self.code = code

        self.labelText = labelText
        self.textColor = textColor
        self._createWidgets()
        self._createLayouts()
        self.updateLabelText(self.labelText, sceneScale)
        self.updateLabelColor(self.textColor)
        
        
        
        self.buttonId = buttonId
        self.picker = parent
        
        self.updateButton(nodes)
        
        self.buttonEnum = PickerButtonEnum.NONE
        '''
        self.maxState = False
        
        
    def updateMaxButtonState(self, maxState):
        if not self.isMaxButton:
            return
        self.maxState = maxState
        self.buttonColor = PickerButton.STATE_COLOR if self.maxState else self.color
        self.update()'''
    
    @property    
    def isCmdButton(self) -> bool:
        return self.code and isinstance(self.code, dict)
        
    def updateCode(self, codeData: dict):
        self.code = codeData
        self._setToolTop()
        self.updateLabelText(self.code['name'], self.picker.sceneScale)
        self.setSelected(False)
           

    def _setToolTop(self):
        if self.isCmdButton:
            self.setToolTip(self.code['code'] or 'Null')
        else:
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
        
        # update code data
        if self.isCmdButton:
            self.code['name'] = text
        
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
        elif self.isCmdButton:
            radius = min(self.width(), self.height()) * 0.2
            painter.drawRoundedRect(rect, radius, radius) 
        else:
            painter.drawRect(rect)
        
        
    def enterEvent(self, event):
        if self.isCmdButton:
            return
        self.buttonColor = PickerButton.SELECTED_COLOR if self.selected else PickerButton.STATE_COLOR
        self.update()
        
        
    def leaveEvent(self, event):
        if self.isCmdButton:
            return
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
        
    def clickeMove(self, value):
        pos = self.pos()
        self.move(round(pos.x() + value * self.picker.sceneScale), round(pos.y() + value * self.picker.sceneScale))
        
    def mousePressEvent(self, event): 
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton and event.modifiers() == QtCore.Qt.NoModifier and self.isCmdButton:
            self.setSelected(True)
            self.buttonEnum = PickerButtonEnum.LEFT_CLICKE
            self.clickeMove(1)
            
        super().mouseReleaseEvent(event)
        
        
    def mouseReleaseEvent(self, event):
        if self.buttonEnum == PickerButtonEnum.LEFT_CLICKE:
            self.setSelected(False)
            self.buttonEnum = PickerButtonEnum.NONE
            self.clickeMove(-1)  
            if self.rect().contains(qtUtils.getLocalPos(event).toPoint()):
                cmds.evalDeferred(self.code['code']) if self.code['type'] == 'Python' else mel.eval(self.code['code'])
   
        super().mouseReleaseEvent(event)




