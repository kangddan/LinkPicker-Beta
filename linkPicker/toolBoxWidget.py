import maya.cmds as cmds
if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui

from linkPicker import colorWidget, widgets


class ToolBoxWidget(QtWidgets.QWidget):
    
    buttonColorLabelSelected = QtCore.Signal(QtGui.QColor)
    labelTextColorSelected   = QtCore.Signal(QtGui.QColor)
    textUpdate               = QtCore.Signal(str)
    
    scaleXUpdate = QtCore.Signal(int)
    scaleYUpdate = QtCore.Signal(int)
    
    scaleXUndo = QtCore.Signal(int)
    scaleYUndo = QtCore.Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        self.updateLayout = True
       # self.setFocusPolicy(QtCore.Qt.StrongFocus)#; self.setFocus()

        
    def _createWidgets(self):
        self.colorLabel           = QtWidgets.QLabel('<span style="font-size: 15px; font-weight: 400;">Color:</span>')
        self.buttonColorLabel     = colorWidget.ColorWidget(34, 24, QtGui.QColor(QtGui.QColor(214, 208, 0)))
        self.widthLabel           = QtWidgets.QLabel('<span style="font-size: 15px; font-weight: 400;">Width:</span>')
        self.widthNumberLineEdit  = widgets.NumberLineEdit('int', 40, 1, 10, 400)
        self.widthNumberLineEdit.setFixedHeight(30)

        self.heightLabel          = QtWidgets.QLabel('<span style="font-size: 15px; font-weight: 400;">Height:</span>')
        self.heightNumberLineEdit = widgets.NumberLineEdit('int', 40, 1, 10, 400)
        self.heightNumberLineEdit.setFixedHeight(30)

        self.buttonLabel         = QtWidgets.QLabel('<span style="font-size: 15px; font-weight: 400;">Label:</span>')
        self.labelTextColor      = colorWidget.ColorWidget(34, 24, QtGui.QColor(QtCore.Qt.black))
        self.labelLineEdit       = QtWidgets.QLineEdit()
        self.labelLineEdit.setPlaceholderText('name...')
        self.labelLineEdit.setFixedHeight(30)
        
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(4, 0, 4, 0)
        mainLayout.setSpacing(4)
        
        self.toolBoxLayout1 = QtWidgets.QHBoxLayout()
        self.toolBoxLayout1.setContentsMargins(0, 0, 0, 0)
        
        self.toolBoxLayout2 = QtWidgets.QHBoxLayout()
        self.toolBoxLayout2.setContentsMargins(0, 0, 0, 0)
        
        self.toolBoxLayout1.addWidget(self.colorLabel)
        self.toolBoxLayout1.addWidget(self.buttonColorLabel)
        self.toolBoxLayout1.addWidget(self.widthLabel)
        self.toolBoxLayout1.addWidget(self.widthNumberLineEdit)
        self.toolBoxLayout1.addWidget(self.heightLabel)
        self.toolBoxLayout1.addWidget(self.heightNumberLineEdit)
        
        self.toolBoxLayout1.addWidget(self.buttonLabel)
        self.toolBoxLayout1.addWidget(self.labelTextColor)
        self.toolBoxLayout1.addWidget(self.labelLineEdit)

        mainLayout.addLayout(self.toolBoxLayout1)
        mainLayout.addLayout(self.toolBoxLayout2)
        
    def _createConnections(self):
        self.buttonColorLabel.colorSelected.connect(self.buttonColorLabelSelected.emit)
        self.labelTextColor.colorSelected.connect(self.labelTextColorSelected.emit)
        self.labelLineEdit.editingFinished.connect(lambda: self.textUpdate.emit(self.labelLineEdit.text()))
        
        self.widthNumberLineEdit.editingFinished.connect(lambda: self.scaleXUpdate.emit(self.widthNumberLineEdit.get()))
        self.heightNumberLineEdit.editingFinished.connect(lambda: self.scaleYUpdate.emit(self.heightNumberLineEdit.get()))
        
        '''
        Ensure that the signal defined inside focusOutEvent triggers after the editingFinished signal 
        to guarantee correct data retrieval and facilitate the undo operation.
        '''
        self.widthNumberLineEdit.oldAndNewNumber.connect(self.scaleXUndo.emit)
        self.heightNumberLineEdit.oldAndNewNumber.connect(self.scaleYUndo.emit)
        
        
        
        
    def _moveWidgets(self, fromLayout, toLayout, widgets):
        for widget in widgets:
            if fromLayout.indexOf(widget) != -1:
                fromLayout.removeWidget(widget) 
                toLayout.addWidget(widget) 
 
    def resizeEvent(self, event):
        width = self.width()
        if width < 450 and self.updateLayout:
            self.updateLayout = False
            self._moveWidgets(self.toolBoxLayout1, self.toolBoxLayout2, [self.buttonLabel, self.labelTextColor, self.labelLineEdit])

        elif width > 450 and not self.updateLayout:
            self.updateLayout = True
            self._moveWidgets(self.toolBoxLayout2, self.toolBoxLayout1, [self.buttonLabel, self.labelTextColor, self.labelLineEdit])

        super().resizeEvent(event)
        
        
    # -----------------------------------------------------
    def set(self, data: dict):
        color     = data['color']
        scaleX    = data['scaleX']
        scaleY    = data['scaleY'] 
        text      = data['labelText']
        textColor = data['textColor']
        
        self.buttonColorLabel.setColor(color)
        self.buttonColorLabel.updateCmdsColorLabel(color)
        
        self.widthNumberLineEdit.set(scaleX)
        self.heightNumberLineEdit.set(scaleY)
        
        self.labelTextColor.setColor(textColor)
        self.labelTextColor.updateCmdsColorLabel(textColor)
        self.labelLineEdit.setText(text)
        
        
    def get(self) -> dict:
        data = {'color':self.buttonColorLabel.getColor(),
                'scaleX':self.widthNumberLineEdit.get(),
                'scaleY':self.heightNumberLineEdit.get(),
                'labelText':self.labelLineEdit.text(),
                'textColor':self.labelTextColor.getColor()
                }  
        return data
