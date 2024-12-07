import maya.cmds as cmds
if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui

from . import widgets


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
        self.resize(350, 180)
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
        
        self.origImagePath = ''
        
        # CACHE UNDO DATA
        self.undoWidth  = 0
        self.undoheight = 0
        
        
    def _createWidgets(self):
        self.pathLineEdit = QtWidgets.QLineEdit()
        self.pathLineEdit.setFixedHeight(32)
        self.pathLineEdit.setPlaceholderText('Image Path...')
        
        self.pathLineEditAction = self.pathLineEdit.addAction(QtGui.QIcon('linkPickerIcons:close.png'), QtWidgets.QLineEdit.TrailingPosition)
        
        self.pathButton = QtWidgets.QPushButton('')
        self.pathButton.setIcon(QtGui.QIcon(':fileOpen.png'))
        self.pathButton.setToolTip('Select Image')
        self.pathButton.setToolTipDuration(2000)
        self.pathButton.setFixedSize(35, 30)
        
        
        self.widthLineEdit  = widgets.NumberLineEdit('int', 0, 1, 1, 99999)
        self.widthLineEdit.setFixedHeight(32)
        self.heightLineEdit = widgets.NumberLineEdit('int', 0, 1, 1, 99999)
        self.heightLineEdit.setFixedHeight(32)
        self.resizeButton = QtWidgets.QPushButton('')
        self.resizeButton.setIcon(QtGui.QIcon(':refresh.png'))
        self.resizeButton.setToolTip('Reset to original resolution')
        self.resizeButton.setToolTipDuration(2000)
        self.resizeButton.setFixedSize(35, 30)
            
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
        sizeLayout.setSpacing(3)
        sizeLayout.addWidget(QtWidgets.QLabel('Width:  '))
        sizeLayout.addWidget(self.widthLineEdit)
        sizeLayout.addWidget(QtWidgets.QLabel('Height:  '))
        sizeLayout.addWidget(self.heightLineEdit)
        sizeLayout.addWidget(self.resizeButton)
        
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
        self.widthLineEdit.editingFinished.connect(self.runResizeImageSignal)
        self.heightLineEdit.editingFinished.connect(self.runResizeImageSignal)
        
        self.opacitySlider.valueChanged.connect(self.setOpacity.emit)
        
        self.cancelButton.clicked.connect(self.close)
        self.ApplyButton.clicked.connect(self.applyClose)
        
        self.pathLineEdit.editingFinished.connect(self.updateUI)
        self.pathLineEditAction.triggered.connect(self.clearPath)
        
        self.resizeButton.clicked.connect(self.getOriginalResolution)
    
    
    def updateCacheData(self):
        self.undoWidth  = self.widthLineEdit.get()
        self.undoheight = self.heightLineEdit.get()
        
        
    def runResizeImageSignal(self):
        self.resizeImage.emit(self.widthLineEdit.get(), self.heightLineEdit.get())
        self.updateCacheData()
        
        
        
    def getOriginalResolution(self):
        imagePath = self.pathLineEdit.text()
        image = QtGui.QPixmap(imagePath)
        if image.isNull():
            return 
        imageSize = image.size()
        self.widthLineEdit.set(imageSize.width())
        self.heightLineEdit.set(imageSize.height())
        self.updateCacheData()
        self.runResizeImageSignal()

           
    def clearPath(self):
        self.pathLineEdit.clear()
        self.origImagePath = ''
        self.updateUI()


    def updateUI(self, path=''):
        imagePath = path or self.pathLineEdit.text()
        image = QtGui.QPixmap(imagePath)
        
        if image.isNull():
            self.imagePathSet.emit('') 
            self.origImagePath = ''
            return   
        if imagePath == self.origImagePath:
            return
            
        self.origImagePath = imagePath
        
        self.pathLineEdit.setText(imagePath)
        imageSize = image.size()    
        
        w = self.undoWidth if self.undoWidth != 1 else imageSize.width()
        h = self.undoheight if self.undoheight != 1 else imageSize.height()
        
        self.widthLineEdit.set(w)
        self.heightLineEdit.set(h)
        self.imagePathSet.emit(imagePath)  
        self.resizeImage.emit(self.widthLineEdit.get(), self.heightLineEdit.get())
   
        
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
        if imagePath:
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
        
        self.origImagePath = data['imagePath']
        self.updateCacheData()
