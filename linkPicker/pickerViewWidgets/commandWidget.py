import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om2

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui

from .. import widgets


class CommandWidget(QtWidgets.QDialog):
    
    runCommandData = QtCore.Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus); self.setFocus()
        self.setWindowTitle('Edit Command')
        self.resize(400, 500)
        
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        widgets.toParentMidPos(self, parent)
        
        
    def _createWidgets(self):
        self.cmdNameLineEdit = QtWidgets.QLineEdit()
        
        self.buttonGroup = QtWidgets.QButtonGroup(self)
        self.buttonGroup.setExclusive(True)
        self.pythonButton = QtWidgets.QRadioButton('Python')
        self.melButton    = QtWidgets.QRadioButton('Mel')
        
        self.pythonButton.setChecked(True)
        self.buttonGroup.addButton(self.pythonButton, 0)
        self.buttonGroup.addButton(self.melButton, 1)
        
        self.codeTextEdit = QtWidgets.QPlainTextEdit()
        
        self.testButton = QtWidgets.QPushButton('Test')
        self.applyButton  = QtWidgets.QPushButton('Apply')
        self.CancelButton = QtWidgets.QPushButton('Cancel')
        self.testButton.setFixedHeight(32)
        self.applyButton.setFixedHeight(32)
        self.CancelButton.setFixedHeight(32)
 
 
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(7, 7, 7, 7)
        
        subLayout = QtWidgets.QGridLayout(self)
        subLayout.addWidget(QtWidgets.QLabel('Name :'), 0, 0)
        subLayout.addWidget(self.cmdNameLineEdit, 0, 1)
        
        subLayout.addWidget(QtWidgets.QLabel('Type   :'), 1, 0)
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.pythonButton); buttonLayout.addWidget(self.melButton)
        subLayout.addLayout(buttonLayout, 1, 1)
        
        subLayout.addWidget(QtWidgets.QLabel('Code  :'), 2, 0, QtCore.Qt.AlignTop)
        subLayout.addWidget(self.codeTextEdit, 2, 1)
        
        buttonLayout2 = QtWidgets.QHBoxLayout()
        buttonLayout2.setSpacing(3)
        buttonLayout2.addWidget(self.testButton)
        buttonLayout2.addWidget(self.applyButton)
        buttonLayout2.addWidget(self.CancelButton)
        
        mainLayout.addLayout(subLayout)
        mainLayout.addLayout(buttonLayout2)
        
        
    def _createConnections(self):
        self.CancelButton.clicked.connect(self.close)
        self.applyButton.clicked.connect(self.runCommand)
        self.testButton.clicked.connect(self.testCode)
        
        
    def runCommand(self):
        self.runCommandData.emit(self.get())
        self.close()
        
        
    def testCode(self):
        code = self.codeTextEdit.toPlainText()
        try:
            #exec(code) if self.isPython else cmds.evalDeferred(mel.eval(code))
            cmds.evalDeferred(code) if self.isPython else mel.eval(code)
        except Exception as e:
            om2.MGlobal.displayError(f'An error occurred while executing the code:\n{str(e)}')        
    
    
    @property    
    def isPython(self) -> bool:
        return self.pythonButton.isChecked()
        
        
    def get(self) -> dict:
        return {'name': self.cmdNameLineEdit.text(),
                'type': 'Python' if self.isPython else 'Mel',
                'code': self.codeTextEdit.toPlainText()}
                
                
    def set(self, data: dict):
        self.cmdNameLineEdit.setText(data['name'])
        self.pythonButton.setChecked(True) if data['type'] == 'Python' else self.melButton.setChecked(True)
        self.codeTextEdit.setPlainText(data['code'])
        