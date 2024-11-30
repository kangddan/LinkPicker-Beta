import maya.cmds         as cmds
import maya.api.OpenMaya as om2
import maya.OpenMayaUI   as omui

from functools import partial

if int(cmds.about(version=True)) >= 2025:
    from shiboken6 import wrapInstance
    from PySide6   import QtWidgets, QtCore, QtGui
    Action      = QtGui.QAction
    ActionGroup = QtGui.QActionGroup 
else:
    from shiboken2 import wrapInstance
    from PySide2   import QtWidgets, QtCore, QtGui
    Action      = QtWidgets.QAction
    ActionGroup = QtWidgets.QActionGroup


class _IndexColorPicker(QtWidgets.QDialog):
    mayaIndexColor      = QtCore.Signal(int)
    mayaIndextoRGBColor = QtCore.Signal(list)
    
    mayaIndexToQtColor  = QtCore.Signal(QtGui.QColor)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('indexColorPicker')
        
        self.index = 16
        self.setFixedSize(400, 240)
        self.setWindowFlags(QtCore.Qt.Popup)
        
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        self.setMouseTracking(True)
        self.extendedRect = self.rect().adjusted(-60, -60, 60, 60)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) 
        self.setStyleSheet('QDialog#indexColorPicker {border: 1px solid #292929;}')
        
        
    def _createWidgets(self):
        colors = [QtGui.QColor(119, 119, 119)] + [self.indexToQtColor(i) for i in range(1, 32)]
        self.buttonGroup = QtWidgets.QButtonGroup(self)

        self.buttons = []
        for index, color in enumerate(colors):
            button = QtWidgets.QPushButton(f'{index}' if index != 0 else 'RST')
            button.setFixedSize(45, 45)
            self._setButColor(button, color)
            self.buttonGroup.addButton(button, index)
            self.buttons.append(button)
            
            
    def _createLayouts(self):
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.setVerticalSpacing(0) 
        gridLayout.setSpacing(0)
        
        maxWidth = self.width()
        buttonWidth = 45 + gridLayout.spacing() 
        buttonsPerRow = maxWidth // buttonWidth
        
        for index, button in enumerate(self.buttons):
            row = index // buttonsPerRow
            col = index % buttonsPerRow
            gridLayout.addWidget(button, row, col)
            
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        gridLayout.addItem(spacer, row + 1, 0, 1, buttonsPerRow)
        # ------------------------------------
        mainLayout = QtWidgets.QVBoxLayout(self)  
        mainLayout.setContentsMargins(5, 5, 5, 5) 
        groupBox   = QtWidgets.QGroupBox('Color Index')
        groupBox.setLayout(gridLayout)
        mainLayout.addWidget(groupBox)
        
        
    def _createConnections(self):
        self.buttonGroup.buttonClicked.connect(self._getColor)
        
        
    def _getColor(self, button):
        index = self.buttonGroup.id(button) 
        if index == 0:
            return
        self.index = index
        self.mayaIndexColor.emit(self.index)
        self.mayaIndextoRGBColor.emit(cmds.colorIndex(self.index, q=True))
        self.mayaIndexToQtColor.emit(self.indexToQtColor(self.index))
    
    # --------------------------------------------------------------------------------    
    @staticmethod
    def indexToQtColor(index) -> QtGui.QColor:
        rgb = [int(channel * 255) for channel in cmds.colorIndex(index, q=True)]
        return QtGui.QColor(*rgb)
        
        
    def _textColor(self, BGColor) -> QtGui.QColor:
        value = (BGColor.red() * 299 + BGColor.green() * 587 + BGColor.blue() * 114) / 1000
        return QtGui.QColor(QtCore.Qt.black) if value > 128 else QtGui.QColor(QtCore.Qt.white)
        
        
    def _setButColor(self, button, color):
        textColor = self._textColor(color)
        palette = button.palette()
        palette.setColor(QtGui.QPalette.ButtonText, textColor)
        palette.setColor(QtGui.QPalette.Button,     color)
        button.setAutoFillBackground(True)
        button.setPalette(palette)
        
        
    def mouseMoveEvent(self, mouseEvent):
        super().mouseMoveEvent(mouseEvent)
        globalPos = self.mapToGlobal(mouseEvent.pos())
        localPos  = self.mapFromGlobal(globalPos)
        if not self.extendedRect.contains(localPos):
            self.hide()
            
            
    def hideEvent(self, event):
        self.mayaIndexColor.emit(self.index)
        self.mayaIndextoRGBColor.emit(cmds.colorIndex(self.index, q=True))
        #self.mayaIndexToQtColor.emit(self.indexToQtColor(self.index))
        
        super().hideEvent(event)


class _GetCmdsRGBColorPicker(QtCore.QObject):
    mayaRGBColor       = QtCore.Signal(list)
    mayaRGBToQtColor   = QtCore.Signal(QtGui.QColor)
    mayaRGBToQtColor2  = QtCore.Signal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.baseColor = [1.0, 1.0, 1.0] 
        self.colorLabel  = None
        
        self.parenLayout = QtWidgets.QHBoxLayout(parent)
        self._getMayaColorLabel()


    def _getMayaColorLabel(self):
        window = cmds.window()
        self.colorSliderObject = omui.MQtUtil.findControl(cmds.colorSliderGrp())
        
        if self.colorSliderObject is not None:
            self.colorSliderWidget = wrapInstance(int(self.colorSliderObject), QtWidgets.QWidget) 
            self.colorSliderWidget.hide()
            self.parenLayout.addWidget(self.colorSliderWidget)                                  
            self.colorLabel = self.colorSliderWidget.findChild(QtWidgets.QLabel, 'port')   
            cmds.colorSliderGrp(self._colorSliderFullPathName(), e=True, cc=partial(self._getColor))
        cmds.deleteUI(window, window=True)
        
        
    def _colorSliderFullPathName(self):
        return omui.MQtUtil.fullName(int(self.colorSliderObject))
    
    @staticmethod
    def mayaRGBColorToQtColor(color):
        return QtGui.QColor(color[0] * 255, color[1] * 255, color[2] * 255)
        
    @staticmethod
    def mayaRGBColorToQtColor2(color):
        newColor = cmds.colorManagementConvert(toDisplaySpace=color) 
        return QtGui.QColor(newColor[0] * 255, newColor[1] * 255, newColor[2] * 255)
        
        
    def _getColor(self, *args):
        color: list = self.get()
        self.mayaRGBColor.emit(color)
        self.mayaRGBToQtColor.emit(self.mayaRGBColorToQtColor(color))
        self.mayaRGBToQtColor2.emit(self.mayaRGBColorToQtColor2(color))
        
    # ---------------------------------------------------------
    def set(self, color: list):
        cmds.colorSliderGrp(self._colorSliderFullPathName(), e=True, rgbValue=(color)) # set picker color
        
        
    def get(self) -> list:
        return cmds.colorSliderGrp(self._colorSliderFullPathName(), q=True, rgb=True)
        

class ColorWidget(QtWidgets.QLabel):
    colorSelected = QtCore.Signal(QtGui.QColor)
    
    def __init__(self, x=100, y=30, color=QtGui.QColor(), parent=None):
        super().__init__(parent)
        
        self.setFixedSize(x, y)
        self._pixmap  = QtGui.QPixmap(self.size()) 
        self.tabColor = color # baseColor
        self.setColor(self.tabColor)
        
        self.isRGB = True
        
        self._createActions()
        self._createMenu()
        self._createWidgets()
        self._createConnections()
        self.updateCmdsColorLabel(self.tabColor)
        
        self.oldColor = None

    
    def _createWidgets(self):
        self.indexColorPicker = _IndexColorPicker()
        self.cmdsColorUI      = _GetCmdsRGBColorPicker(self)
        self.cmdsColorUILabel = self.cmdsColorUI.colorLabel
        
        
    def _createConnections(self):
        self.RGBAction.triggered.connect(partial(self._setColorMode, True))
        self.indexAction.triggered.connect(partial(self._setColorMode, False))
        
        self.cmdsColorUI.mayaRGBToQtColor2.connect(self.updateColor)
        self.indexColorPicker.mayaIndexToQtColor.connect(self.updateColor)
        self.indexColorPicker.mayaIndextoRGBColor.connect(self.cmdsColorUI.set) # update cmdsUI color
        
    
    
    def _createActions(self):
        self.RGBAction    = Action('RGB   Color Picker')
        self.indexAction  = Action('Index Color Picker')
        
        self.RGBAction.setCheckable(True)
        self.indexAction.setCheckable(True)
        self.RGBAction.setChecked(True)
        
        actionGroup = ActionGroup(self)
        actionGroup.setExclusive(True)
        actionGroup.addAction(self.RGBAction)
        actionGroup.addAction(self.indexAction)
        
        
    def _createMenu(self):
        self.colorWidgetMenu = QtWidgets.QMenu(self)
        self.colorWidgetMenu.addAction(self.RGBAction)
        self.colorWidgetMenu.addAction(self.indexAction)
        
        
    def _setColorMode(self, isRGB: bool):
        self.isRGB = isRGB
     
    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.RightButton and event.modifiers() == QtCore.Qt.NoModifier:
            self.colorWidgetMenu.exec_(event.globalPos())
        else:
            super().mousePressEvent(event)
        
        
    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.isRGB:
                # show rgb ColorPicker
                self._showCmdsRGBColorPicker()
            else:
                # show index ColorPicker
                pos = self.mapToGlobal(event.pos())
                x = pos.x() - (self.indexColorPicker.width() // 2)
                y = pos.y() - (self.indexColorPicker.height() // 2)
                self.indexColorPicker.move(x, y)
                self.indexColorPicker.show()
        else:
            super().mouseReleaseEvent(event)
                
                
    def _showCmdsRGBColorPicker(self):
        event = QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
                                 self.cmdsColorUILabel.rect().center(),
                                 QtCore.Qt.LeftButton,
                                 QtCore.Qt.LeftButton,
                                 QtCore.Qt.NoModifier)
        QtWidgets.QApplication.postEvent(self.cmdsColorUILabel, event)
        
    # ---------------------------------------------------------------
    def updateCmdsColorLabel(self, color):
        color = [color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0]
        self.cmdsColorUI.set(color)
        
    def getColor(self) -> QtGui.QColor:
        return self.tabColor
        
    def updateColor(self, color: QtGui.QColor):

        if self.oldColor is None:
            self.oldColor = color
        elif self.oldColor == color:
            return
            
        self.setColor(color)
        self.colorSelected.emit(color)
        self.oldColor = color
        
        
    def setColor(self, color: QtGui.QColor):
        self.tabColor  = color
        self._pixmap.fill(self.tabColor)
        self.setPixmap(self._pixmap) 
        