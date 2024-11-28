from __future__ import division
import uuid

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

from linkPicker import path
from linkPicker.pickerViewWidgets import pickerUtils


class PickerButton(QtWidgets.QWidget):
    SELECTED_COLOR = QtGui.QColor(225, 225, 225)
    
    def __repr__(self):
        globaPos = self.pos()
        localPos = self.localPos
        return '<{} at {}: G->({}, {}), L->({}, {})>'.format(self.__class__.__name__, hex(id(self)), globaPos.x(), globaPos.y(), localPos.x(), localPos.y())


    def __str__(self):
        return str(self.nodes)
    
    
    def __contains__(self, other):
        if isinstance(other, self.__class__):
            return all(node in self.nodes for node in other.nodes)
        elif isinstance(other, str):
            return other in self.nodes
        return False
        
        
    def __iter__(self):
        return (node for node in self.nodes)
    
    
    def __len__(self):
        return len(self.nodes)
        
        
    def __getitem__(self, index):
        if isinstance(index, int):
            return self.nodes[index]
        elif isinstance(index, str):
            if index in self.__dict__:
                return self.__dict__[index]
            raise KeyError("Key '{}' not found in object attributes.".format(index, ))
        else:
            raise TypeError("Index must be an int or str, got {}.".format(type(index).__name__))

        

    
    def __init__(self, globalPos, 
                       parentPos, 
                       color = QtGui.QColor(100, 100, 100),
                       sceneScale = 1.0, 
                       scaleX = 40,
                       scaleY = 40,
                       textColor = QtGui.QColor(10, 10, 10),
                       labelText = '',
                       parent = None,
                       nodes  = None,
                       buttonId = None):  
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
        super(PickerButton, self).__init__(parent)

        self.scaleX     = scaleX
        self.scaleY     = scaleY
        self.color      = color
        self.sceneScale = sceneScale
        
        _width  = round(scaleX * sceneScale)
        _height = round(scaleY * sceneScale)
        
        globalTopLeftPos = QtCore.QPointF(globalPos.toPoint().x() - _width / 2.0, globalPos.toPoint().y() - _height / 2.0) # get button top left Pos
        
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
        tooltipText = '<br>'.join('-> {}'.format(node) for node in self.nodes)
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
        
        
    def updateNamespace(self, namespace):
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
        
        
    def updateLabelText(self, text, sceneScale):
        self.labelText = text
        self.scaleText(sceneScale)
        
    def scaleText(self, sceneScale):
        font = QtGui.QFont('Verdana', round(self.scaleY * sceneScale * 0.15))
    
        self.textLabel.setFont(font)
        self.textLabel.setText(self.labelText)
        
        
    def updateLabelColor(self, color):
        self.textColor = color
        palette = self.textLabel.palette()
        palette.setColor(QtGui.QPalette.WindowText, self.textColor) 
        self.textLabel.setPalette(palette)
    

    def setSelected(self, selected):
        self.selected    = selected
        self.buttonColor = PickerButton.SELECTED_COLOR if self.selected else self.color
        self.update()
        
    
    def resetPos(self, buttonsParentPos=QtCore.QPointF()):
        self.resize(self.scaleX, self.scaleY)
        self.move(self.localPos.toPoint() + buttonsParentPos.toPoint())
    
    
    def updateLocalPos(self, globalPos, 
                             parentPos, 
                             sceneScale):
        self.localPos = pickerUtils.globalToLocal(globalPos, parentPos, sceneScale)
        
         
    def updateColor(self, color):
        if color == self.color:
            return
        self.color = self.buttonColor = color
        self.update()
    
    
    def cenrerPos2(self, globalPos, sceneScale):
        '''
        Use internal floating-point values to calculate the center position for higher precision
        '''
        return globalPos + QtCore.QPointF(self.scaleX * sceneScale / 2.0, self.scaleY * sceneScale / 2.0)    
  
  
    def cenrerPos(self, globalPos):
        return globalPos + QtCore.QPointF(self.width() / 2.0, self.height() / 2.0)

    
    def updateScaleX(self, scaleX, sceneScale, parentPos) :  
        if scaleX == self.scaleX:
            return
            
        self.scaleX = max(10, min(scaleX, 400))
        self._scale(sceneScale, parentPos)
        

    def updateScaleY(self, scaleY, sceneScale, parentPos):
        if scaleY == self.scaleY:
            return
 
        self.scaleY = max(10, min(scaleY, 400))
        self._scale(sceneScale, parentPos)
    
    
    def _scale(self, sceneScale, parentPos):
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
        
        
    def get(self):
        return {'color'    :self.color,
                'scaleX'   :self.scaleX,
                'scaleY'   :self.scaleY,
                'textColor':self.textColor,
                'labelText':self.labelText
                }  
                
                
    def set(self):
        pass
   