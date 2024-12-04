import maya.cmds as cmds
if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui

from . import widgets, config


class ImageWindow(QtWidgets.QDialog):
    imagePathSet = QtCore.Signal(str)
    resizeImage  = QtCore.Signal(int, int)
    setOpacity   = QtCore.Signal(int)
    
    canceClicked = QtCore.Signal(dict)
    addUndo      = QtCore.Signal(dict)
    
    FILE_FTLTERS    = 'PNG (*.png);;JPG (*.jpg *.jpeg);;BMP (*.bmp);;Images (*.png *.jpg *.bmp *.jpeg);;All Files (*.*)'
    SELECTED_FILTER = 'PNG (*.png)'
    
    
    def closeEvent(self, event):
        if not self.applyTag:
            self.canceClicked.emit(self.oldImageData)
        self.applyTag = False
        super().closeEvent(event)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus); self.setFocus()
        self.setWindowTitle('Image Window')
        self.resize(330, 165)
        self.mainUI = parent
 
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        widgets.toParentMidPos(self, parent)
        
        self.setStyleSheet('''
        QSlider#opacitySlider::groove:horizontal {border: none; height: 5px; background-color: #2B2B2B; }
        QSlider#opacitySlider::handle:horizontal {background-color: #E6E6E6; 
                                               width: 10px; 
                                               margin: -5px 0 -5px 0;
                                               border-radius: 2px;}
        QSlider#opacitySlider::sub-page:horizontal {background-color: #A5A5A5;}
        ''')
        
        self.oldImageData = {}
        self.applyTag = False
        
    def _createWidgets(self):
        self.pathLineEdit = QtWidgets.QLineEdit()
        self.pathLineEdit.setFixedHeight(32)
        self.pathLineEdit.setPlaceholderText('Image Path...')
        
        self.pathLineEditAction = self.pathLineEdit.addAction(QtGui.QIcon(config.closeIcon), QtWidgets.QLineEdit.TrailingPosition)
        
        self.pathButton = QtWidgets.QPushButton('')
        self.pathButton.setIcon(QtGui.QIcon(':fileOpen.png'))
        self.pathButton.setFixedSize(35, 30)
        
        self.widthLineEdit  = widgets.NumberLineEdit('int', 0, 1, 1, 99999)
        self.widthLineEdit.setFixedHeight(32)
        self.heightLineEdit = widgets.NumberLineEdit('int', 0, 1, 1, 99999)
        self.heightLineEdit.setFixedHeight(32)
        
        self.opacitySlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacitySlider.setObjectName('opacitySlider')
        self.opacitySlider.setRange(1, 100)
        self.opacitySlider.setValue(100)
        
        self.ApplyButton  = QtWidgets.QPushButton('Apply')
        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.ApplyButton.setFixedHeight(32)
        self.cancelButton.setFixedHeight(32)
        
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(7, 7, 7, 7)
        
        pathLayout = QtWidgets.QHBoxLayout()
        pathLayout.setSpacing(3)
        pathLayout.addWidget(self.pathLineEdit)
        pathLayout.addWidget(self.pathButton)
        
        sizeLayout = QtWidgets.QHBoxLayout()
        sizeLayout.addWidget(QtWidgets.QLabel('Width:  '))
        sizeLayout.addWidget(self.widthLineEdit)
        sizeLayout.addWidget(QtWidgets.QLabel('Height:  '))
        sizeLayout.addWidget(self.heightLineEdit)
        
        opacityLayout = QtWidgets.QHBoxLayout()
        opacityLayout.addWidget(QtWidgets.QLabel('Opacity:'))
        opacityLayout.addWidget(self.opacitySlider)
        
        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.setSpacing(3)
        buttonsLayout.addWidget(self.ApplyButton)
        buttonsLayout.addWidget(self.cancelButton)
        
        mainLayout.addLayout(pathLayout)
        mainLayout.addLayout(sizeLayout)
        mainLayout.addLayout(opacityLayout)
        mainLayout.addStretch()
        mainLayout.addLayout(buttonsLayout)
        
        
    def _createConnections(self):
        self.pathButton.clicked.connect(self._showFileSelectDialog)
        self.widthLineEdit.editingFinished.connect(lambda: self.resizeImage.emit(self.widthLineEdit.get(), self.heightLineEdit.get()))
        self.heightLineEdit.editingFinished.connect(lambda: self.resizeImage.emit(self.widthLineEdit.get(), self.heightLineEdit.get()))
        
        self.opacitySlider.valueChanged.connect(self.setOpacity.emit)
        
        self.cancelButton.clicked.connect(self.close)
        self.ApplyButton.clicked.connect(self.applyClose)
        
        self.pathLineEdit.editingFinished.connect(self.updateUI)
        self.pathLineEditAction.triggered.connect(self.clearPath)
        
    def clearPath(self):
        self.pathLineEdit.clear()
        self.updateUI()
        #self.setFocus()
        
    def updateUI(self, path=''):
        imagePath = path or self.pathLineEdit.text()
        image = QtGui.QPixmap(imagePath)
        if image.isNull():
            self.imagePathSet.emit('') 
            return
        imageSize = image.size()
        self.pathLineEdit.setText(imagePath)
        self.widthLineEdit.set(imageSize.width())
        self.heightLineEdit.set(imageSize.height())
        self.imagePathSet.emit(imagePath)    
        
        
    def applyClose(self):
        self.applyTag = True
        
        # get oldData and newData 
        oldData = self.oldImageData
        newData = self.get()
        if oldData != newData:# and not QtGui.QPixmap(newData['imagePath']).isNull():
            data = {'old' : oldData,
                    'new' : newData}
            self.addUndo.emit(data)
        self.close()
        
        
    def _showFileSelectDialog(self):
        imagePath, self.SELECTED_FILTER = QtWidgets.QFileDialog.getOpenFileName(self, 'Select Image', '', self.FILE_FTLTERS, self.SELECTED_FILTER)
        self.updateUI(imagePath)
            
            
    def get(self) -> dict:
        return {'imagePath'  : self.pathLineEdit.text(),
                'ImageWidth' : self.widthLineEdit.get(),
                'ImageHeight': self.heightLineEdit.get(),
                'opacity'    : self.opacitySlider.value() / 100.0,}
            
            
    def set(self, data):
        self.oldImageData = data
        self.pathLineEdit.setText(data['imagePath'])
        self.widthLineEdit.set(data['ImageWidth'])
        self.heightLineEdit.set(data['ImageHeight'])
        self.opacitySlider.setValue(data['opacity'] * 100)