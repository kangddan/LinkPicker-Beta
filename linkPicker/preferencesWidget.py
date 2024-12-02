import maya.cmds as cmds

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
    Action = QtGui.QAction 
else:
    from PySide2 import QtWidgets, QtCore, QtGui
    Action = QtWidgets.QAction

from . import widgets


class NullWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignCenter) 
        self.setWordWrap(True)
        self.setText('<img src=":info.png"><h4>No item selected. Click on an item to view details</h4>')
        

def createGroupbox(title, layout):
    groupbox = QtWidgets.QGroupBox(title)
    groupbox.setLayout(layout)
    groupbox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
    return groupbox

        
class GeneralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.showViewModeWarningTag = False
        
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        self.setStyleSheet('''QScrollArea {border: none;}
        QSlider#ZoomSlider::groove:horizontal {border: none; height: 5px; background-color: #2B2B2B; }
        QSlider#ZoomSlider::handle:horizontal {background-color: #E6E6E6; 
                                               width: 10px; 
                                               margin: -5px 0 -5px 0;
                                               border-radius: 2px;}
        QSlider#ZoomSlider::sub-page:horizontal {background-color: #A5A5A5;}
        ''')
        
    def _createLayouts(self):
        # main Window
        mainWindowLayout = QtWidgets.QVBoxLayout()
        mainWindowLayout.addWidget(self.showNamespaceCheckBox)
        mainWindowLayout.addWidget(self.showTabBarCheckBox)
        mainWindowLayout.addWidget(self.autoSelectedCheckBox)
        mainWindowLayout.addWidget(self.closeTabCheckBox)
        mainWindowLayout.addWidget(self.toolBoxCheckBox)
        
        mainWindowGroupBox = createGroupbox('Main Window', mainWindowLayout)
        
        # picker mode
        pickerLayout = QtWidgets.QGridLayout()
        pickerLayout.addWidget(self.viewModeComboBoxLabel, 0, 0)
        pickerLayout.addWidget(self.viewModeComboBox, 0, 1)
        pickerLayout.addWidget(self.ZoomSliderLabel, 1, 0)
        pickerLayout.addWidget(self.ZoomSlider, 1, 1)
        
        pickerGroupBox = createGroupbox('Picker', pickerLayout)
        
        # scrollWidget
        scrollWidget = QtWidgets.QWidget()
        subLayout = QtWidgets.QVBoxLayout(scrollWidget)
        subLayout.setSpacing(0)
        subLayout.setContentsMargins(0, 0, 0, 0)
        subLayout.addWidget(mainWindowGroupBox)
        subLayout.addWidget(pickerGroupBox)
        subLayout.addStretch() 

        # ------------------------------------------------------
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollArea.setWidget(scrollWidget)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addWidget(scrollArea)
        mainLayout.addStretch()
        

    def _createWidgets(self):
        # main Window
        self.showNamespaceCheckBox = QtWidgets.QCheckBox('Display namespace in the toolbar')
        self.showTabBarCheckBox    = QtWidgets.QCheckBox('Show Tab Bar')
        self.autoSelectedCheckBox  = QtWidgets.QCheckBox('Auto-switch tabs by selected node')
        self.closeTabCheckBox      = QtWidgets.QCheckBox('Show a warning when closing a tab')
        self.toolBoxCheckBox       = QtWidgets.QCheckBox('Show Tool Box')
        
        
        # picker 
        self.viewModeComboBoxLabel = QtWidgets.QLabel('Viewport Mode:')
        self.viewModeComboBoxLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        
        self.viewModeComboBox = QtWidgets.QComboBox()
        self.viewModeComboBox.setItemDelegate(widgets.CustomDelegate(itemHeight=25))
        self.viewModeComboBox.addItems(['Auto-Centered (Beta)', 'separator', 'Fixed'])
        self.viewModeComboBox.model().item(1).setFlags(QtCore.Qt.NoItemFlags) # lock separator
        
        self.ZoomSliderLabel = QtWidgets.QLabel('Zoom Sensitivity:')
        self.ZoomSliderLabel.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)
        
        self.ZoomSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.ZoomSlider.setObjectName('ZoomSlider')
        self.ZoomSlider.setRange(1, 100)
        self.ZoomSlider.setValue(1)


    def _createConnections(self):
        self.viewModeComboBox.currentIndexChanged.connect(self.showViewModeTip)
        
        
    def showViewModeTip(self, *args):
        if not self.showViewModeWarningTag:
            self.showViewModeWarningTag = True
            QtWidgets.QMessageBox.information(self, 'View Mode', 'Takes effect on next tab.')
            
            
    def get(self):
        return {'showNamespaceCheckBox': self.showNamespaceCheckBox.isChecked(),
                'autoSelectedCheckBox' : self.autoSelectedCheckBox.isChecked(),
                'closeTabCheckBox'     : self.closeTabCheckBox.isChecked(),
                'showTabBarCheckBox'   : self.showTabBarCheckBox.isChecked(),
                'toolBoxCheckBox'      : self.toolBoxCheckBox.isChecked(),

                
                'viewModeComboBox'     : self.viewModeComboBox.currentIndex(),
                'ZoomSlider'           : self.ZoomSlider.value()}
        
    def set(self, data):
        self.showNamespaceCheckBox.setChecked(data['showNamespaceCheckBox'])
        self.showTabBarCheckBox.setChecked(data['showTabBarCheckBox'])
        self.autoSelectedCheckBox.setChecked(data['autoSelectedCheckBox'])
        self.closeTabCheckBox.setChecked(data['closeTabCheckBox'])
        self.toolBoxCheckBox.setChecked(data['toolBoxCheckBox'])
        

        
        self.viewModeComboBox.blockSignals(True)
        self.viewModeComboBox.setCurrentIndex(data['viewModeComboBox'])
        self.viewModeComboBox.blockSignals(False)
        self.ZoomSlider.setValue(data['ZoomSlider'])


class SettingsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.showUndoWarningTag = False
        
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        self.setStyleSheet('''QScrollArea {border: none;}''')
        
    def _createLayouts(self):
        # undo
        
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.addWidget(self.undoLabel, 0, 0)
        gridLayout.addWidget(self.onBut, 0, 1)
        gridLayout.addWidget(self.offBut, 0, 2)
        
        gridLayout.addWidget(self.queueLabel, 1, 0)
        gridLayout.addWidget(self.infiniteBut, 1, 1)
        gridLayout.addWidget(self.finiteBut, 1, 2)
        gridLayout.addWidget(self.queueSizeLabel, 2, 0)
        gridLayout.addWidget(self.undoLenEdit, 2, 1)

        undoGroupBox = createGroupbox('Undo', gridLayout)
        
        # view mode
        fileLayout = QtWidgets.QHBoxLayout()
        fileLayout.addWidget(self.includeUndoDataCheckBox)

        fileGroupBox = createGroupbox('File', fileLayout)

        subLayout = QtWidgets.QVBoxLayout()
        subLayout.setSpacing(0)
        subLayout.setContentsMargins(0, 0, 0, 0)
        subLayout.addWidget(undoGroupBox)
        subLayout.addWidget(fileGroupBox)
        subLayout.addStretch() 
        
        # -------------------------------------
        scrollWidget = QtWidgets.QWidget()
        scrollWidget.setLayout(subLayout)
        
        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollArea.setWidget(scrollWidget)  

        mainLayout = QtWidgets.QVBoxLayout(self)  
        mainLayout.addWidget(scrollArea)
        mainLayout.addStretch()
        

    def _createWidgets(self):
        # undo
        self.undoLabel = QtWidgets.QLabel('Undo:')
        self.undoLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.queueLabel = QtWidgets.QLabel('Queue:')
        self.queueLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self.queueSizeLabel = QtWidgets.QLabel('Queue size:')
        self.queueSizeLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        
        self.undoGroup = QtWidgets.QButtonGroup(self)
        self.undoGroup.setExclusive(True)
        self.onBut   = QtWidgets.QRadioButton('On')
        self.offBut = QtWidgets.QRadioButton('Off')

        self.onBut.setChecked(True)
        self.undoGroup.addButton(self.onBut, 0)
        self.undoGroup.addButton(self.offBut, 1)
        
        self.queueGroup = QtWidgets.QButtonGroup(self)
        self.queueGroup.setExclusive(True)
        self.infiniteBut = QtWidgets.QRadioButton('Infinite')
        self.finiteBut   = QtWidgets.QRadioButton('Finite')

        self.finiteBut.setChecked(True)
        self.queueGroup.addButton(self.infiniteBut, 0)
        self.queueGroup.addButton(self.finiteBut, 1)
        
        self.undoLenEdit = widgets.NumberLineEdit('int', 20, 1, 1, 9999)
        self.undoLenEdit.setFixedWidth(100)
        # file
        self.includeUndoDataCheckBox = QtWidgets.QCheckBox('Carry undo data when saving the file')
        self.includeUndoDataCheckBox.setChecked(True)

        
    def _createConnections(self):
        self.queueGroup.buttonClicked.connect(self.lockQueueAttr)
        self.undoGroup.buttonClicked.connect(self.showUndoWarning)
    
    
    def showUndoWarning(self, index):
        if index and not self.showUndoWarningTag:
            self.showUndoWarningTag = True
            reply = QtWidgets.QMessageBox.warning(self, 'Undo Warning', 
                    'This will clear undo data for current tabs', 
                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                self.onBut.setChecked(True)

        
    def lockQueueAttr(self, index):
        self.undoLenEdit.setEnabled(bool(index))
        self.queueSizeLabel.setEnabled(bool(index))
    
    
    def get(self):
        return {'undo'      : self.onBut.isChecked(),
                'queue'     : self.undoLenEdit.get() if self.finiteBut.isChecked() else 0,
                'undoToFile': self.includeUndoDataCheckBox.isChecked()}
        
    def set(self, data):
        self.onBut.setChecked(True) if data['undo'] else self.offBut.setChecked(True)
        
        queue = data['queue']
        if 0 < queue:
            self.finiteBut.setChecked(True)
            self.undoLenEdit.set(queue)
            self.lockQueueAttr(True)
        else:
            self.infiniteBut.setChecked(True)
            self.lockQueueAttr(False)

        self.includeUndoDataCheckBox.setChecked(data['undoToFile'])
 
 
class ListWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)                               
        self.setFixedWidth(110)
        self.setItemDelegate(widgets.CustomItemDelegate())
        self.setStyleSheet('''
                           QListWidget::item:alternate { background-color: #373737; }
                           QListWidget::item:alternate:selected { background-color: #5285A6; } 
                           ''')  
        
    
    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if not item:
            self.clearSelection() 
        super().mousePressEvent(event) 


class PreferencesWidget(QtWidgets.QDialog):
    
    preferencesUpdated = QtCore.Signal()
    
    def __init__(self, parent=None, configManager=None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowTitle('Preferences')
        self.resize(510, 450)
        self.mainUI = parent
        self.configManager = configManager
    
        self._createMenu()
        self._createStackedWidget()
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        widgets.toParentMidPos(self, parent)
        
        self.set(self.configManager.get())
        self.cacheData = self.get()
        
        
    def _createWidgets(self):
        self.listWidget = ListWidget(); self._addItems()
        
    
        self.ApplyButton  = QtWidgets.QPushButton('Apply')
        self.cancelButton = QtWidgets.QPushButton('Cancel')
        self.ApplyButton.setFixedHeight(32)
        self.cancelButton.setFixedHeight(32)
        
        
    def _addItems(self):
        itemMap = {'General'  : self.generalWidget,
                   'Settings' : self.settingsWidget}
                   
        for itemName, widget in itemMap.items():
            newItem = QtWidgets.QListWidgetItem(itemName)
            newItem.setData(QtCore.Qt.UserRole, widget)
            self.listWidget.addItem(newItem)
            
        self.listWidget.setCurrentRow(0)
        QtCore.QTimer.singleShot(0, self.listWidget.setFocus) # focus to listWidget
        
          
    def _createMenu(self):
        self.menuBar = QtWidgets.QMenuBar(self) 
        self.editMenu = QtWidgets.QMenu('Edit', self)
        self.helpMenu = QtWidgets.QMenu('Help', self)
        
        self.revertToSavedAction  = Action('Revert to Saved', self)  
        self.restoreDefaultAction = Action('Restore Default Settings', self)
        
        self.editMenu.addAction(self.revertToSavedAction)
        self.editMenu.addAction(self.restoreDefaultAction)
        
        self.aboutHelpAction = Action('Help on Preferences...', self)
        self.helpMenu.addAction(self.aboutHelpAction)

        self.menuBar.addMenu(self.editMenu)
        self.menuBar.addMenu(self.helpMenu)
        
          
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.setContentsMargins(7, 7, 7, 7)
        subLayout = QtWidgets.QHBoxLayout()
        subLayout.addWidget(self.listWidget)
        subLayout.addWidget(self.stackedWidget)
        
        buttonsLayout = QtWidgets.QHBoxLayout()
        buttonsLayout.setSpacing(3)
        buttonsLayout.addWidget(self.ApplyButton)
        buttonsLayout.addWidget(self.cancelButton)
        
        mainLayout.addLayout(subLayout)
        mainLayout.addLayout(buttonsLayout)
        

    def _createConnections(self):
        self.cancelButton.clicked.connect(self.close)
        self.ApplyButton.clicked.connect(self.updateConfig)
        
        self.revertToSavedAction.triggered.connect(self.resetToSaved)
        self.restoreDefaultAction.triggered.connect(self.resetToDefault)
        
        self.aboutHelpAction.triggered.connect(self.openHelp)
        
        self.listWidget.itemSelectionChanged.connect(self.showSelectedWidget)
        
     
    def _createStackedWidget(self):
        self.stackedWidget  = QtWidgets.QStackedWidget()
        self.generalWidget  = GeneralWidget()
        self.settingsWidget = SettingsWidget()
        self.nullLabel      = NullWidget()
        self.stackedWidget.addWidget(self.generalWidget)
        self.stackedWidget.addWidget(self.settingsWidget)
        self.stackedWidget.addWidget(self.nullLabel)
        
        
    def openHelp(self):
        url = "https://github.com/kangddan/LinkPicker-Beta" 
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
            
            
    def showSelectedWidget(self):
        selItems = self.listWidget.selectedItems()
        self.stackedWidget.setCurrentWidget(self.nullLabel if not selItems else selItems[-1].data(QtCore.Qt.UserRole))
         
            
    def get(self):
        return {'general' : self.generalWidget.get(),
                'settings': self.settingsWidget.get()}
                
    def set(self, data):
        self.generalWidget.set(data['general'])
        self.settingsWidget.set(data['settings'])
        
        
    def updateConfig(self):
        self.cacheData = self.get() # update cacheData
        
        self.configManager.set(self.cacheData)
        self.preferencesUpdated.emit()
        self.close()
        
    def resetToDefault(self):
        self.set(self.configManager.DEFAULT_CONFIG) 
        
    def resetToSaved(self):
        self.set(self.cacheData) 
        
 