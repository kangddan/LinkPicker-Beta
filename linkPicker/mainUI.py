# -*- coding: utf-8 -*-
from __future__ import division
import sys
import importlib
import maya.cmds as cmds
import maya.api.OpenMaya as om2

import json

from functools  import partial
from PySide2    import QtWidgets, QtGui, QtCore
from linkPicker import qtUtils, widgets, colorWidget, toolBoxWidget, config, metaNode, fileManager, mainUIMenu, preferencesWidget
from linkPicker.pickerViewWidgets import buttonManager, pickerView



class MainUI(QtWidgets.QWidget):
    GEOMETRY            = None
    _INSTANCE           = None
    _SCRIPT_JOB_NUMBERS = []
    

    # -----------------------------------------------------------------------------------
    def currentTabUpdateCallback(self):
        self.updateButtonsSelection(None, autoSwitchTab=False)
        
    
    def updateButtonsSelection(self, _, autoSwitchTab=True):
        
        if pickerView.PickerView.isSelectionviaUiActive():
           return
  
        allPickerViews = self.tabWidget.getWidget()
        if not allPickerViews:
            return
            
        selectedNodes  = set(cmds.ls(sl=True, fl=True))     
        if not selectedNodes:
            for picker in allPickerViews:
                picker.clearSelectedButtons()
            return

        # ----------------------------
        allButtonsInfo = {picker: {button: set(button.nodes) for button in picker.allPickerButtons}
                          for picker in allPickerViews}
            
        cacheSelectedButtons = []
        for picker, buttons in allButtonsInfo.items():
            selButtons = [button for button, nodes in buttons.items() if nodes <= selectedNodes]
 
            picker.clearSelectedButtons() 
            
            if selButtons:
                for button in selButtons:
                    button.setSelected(True)
                    if button not in picker.selectedButtons:
                        picker.selectedButtons.append(button)
                    cacheSelectedButtons.append(button)
        
        # to tab
        if not autoSwitchTab:
            return
        if not self.autoSwitchTab:
            return
        currentPicker = self.tabWidget.currentWidget()  
        if not isinstance(currentPicker, pickerView.PickerView):
            return
 
        currentAllNodes = {tuple(button.nodes) for button in currentPicker.allPickerButtons}
    
        for button in cacheSelectedButtons:
            if tuple(button.nodes) in currentAllNodes:
                continue
            else:
                for picker, buttons in allButtonsInfo.items():
                    if button not in buttons:
                        continue
                    self.tabWidget.setCurrentWidget(picker)
                    return 
                    

    def updateOpenScene(self, _):
        # metaNode.mergeNodes().set(self.get())
        self.deleteAllTab(None)
        data = metaNode.mergeNodes().get()
        if data:
            self.set(data)

    
    def setScriptJobEnabled(self, enabled):
        if enabled and not MainUI._SCRIPT_JOB_NUMBERS:
            jobMap = {'SelectionChanged': self.updateButtonsSelection,
                      'NewSceneOpened'  : self.deleteAllTab,
                      'SceneOpened'     : self.updateOpenScene}
            for key, value in jobMap.items():
                jobIndex = om2.MEventMessage.addEventCallback(key, value)
                MainUI._SCRIPT_JOB_NUMBERS.append(jobIndex)
            
        elif not enabled and MainUI._SCRIPT_JOB_NUMBERS:
            try:
                for scriptIndex in MainUI._SCRIPT_JOB_NUMBERS:
                    om2.MMessage.removeCallback(scriptIndex)
            except Exception as e:
                om2.MGlobal.displayWarning('Error removing callback: {}'.format(e))
            MainUI._SCRIPT_JOB_NUMBERS = []
            
            
    def showEvent(self, event):
        if self.isMinimized(): 
            event.ignore() 
            return
        
        self.namespaceWidget.updateNamespace() # update namespace
        
        if self.GEOMETRY is not None:
            self.restoreGeometry(self.GEOMETRY) 
            
        super(MainUI, self).showEvent(event)
        self.setScriptJobEnabled(True)
        self.currentTabUpdateCallback()
        
        # --------------------------------------
        data = metaNode.mergeNodes().get()
        if data:
            self.set(data)
            self.restoreSavedTabIndex()
        
        
    def closeEvent(self, event):
        self.saveCurrentTabIndex()
        
        self.GEOMETRY = self.saveGeometry()
        if isinstance(self, MainUI):
            super(MainUI, self).closeEvent(event)
            self.setScriptJobEnabled(False)
        '''
        If a file is referenced while the picker is open, and the reference file contains pickerNode data,
        the tabs will not refresh automatically (since no callback for references has been identified yet).
        Therefore, when closing the UI, it is necessary to check for any referenced pickerNode data again.
        If such data exists, synchronize it with the current pickerNode to ensure data consistency.
        '''
        refData    = metaNode.getReferenceNodeData() 
        pickerData = self.get()
        if refData:
            pickerData.extend(refData)
        
        metaNode.mergeNodes().set(pickerData)
        self.deleteAllTab(None)
        
        
    def saveCurrentTabIndex(self):
        self.savedTabIndex = -1 if self.tabWidget.count() <= 1 else self.tabWidget.currentIndex()
        
    def restoreSavedTabIndex(self):
        if self.savedTabIndex < 0:
            return
        self.tabWidget.setCurrentIndex(self.savedTabIndex)
        
        
        
    def resizeEvent(self, event):
        width = self.width()
        if self.showNamespaceTag:
            self.namespaceWidget.show() if width > 400 and self.tabWidget.count() >= 2 else self.namespaceWidget.hide()
        else:
            self.namespaceWidget.hide()
        super(MainUI, self).resizeEvent(event)    
   
    
    def __new__(cls, *args, **kwargs):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(MainUI, cls).__new__(cls)
        return cls._INSTANCE

        
    def __repr__(self):
        return '< PickerWindow{} Tab -> {} >'.format(self.__class__.__name__, self.tabWidget.count())
        
    def leaveEvent(self, event):
        super(MainUI, self).leaveEvent(event)
        self.mainWindow.activateWindow()
        
    '''
    def enterEvent(self, event):
        super().enterEvent(event)
        currentPicker = self.tabWidget.currentWidget()  
        if isinstance(currentPicker, pickerView.PickerView):
            currentPicker.activateWindow()
    '''

    def dragEnterEvent(self, event):
        if not event.mimeData().hasUrls():
            return

        fileUrls = event.mimeData().urls()
        self.pickerPaths = []
        for fileUrl in fileUrls:
            #filePath = fileUrl.toLocalFile()
            filePath = str(fileUrl.toLocalFile())
            if not filePath.endswith('.lpk'):
                continue
            self.pickerPaths.append(filePath)
        if not self.pickerPaths:
            return
 
        event.acceptProposedAction()


    def dropEvent(self, event):
        if self.pickerPaths:
            datas = []
            for pickerPath in self.pickerPaths:
                with open(pickerPath, 'r', encoding='utf-8') as f:
                    datas.append(json.load(f))
            self.set(datas)
            
   
    def __init__(self, parent=qtUtils.getMayaMainWindow()):
        if hasattr(self, '_init') and self._init:
            return
        self._init = True
        super(MainUI, self).__init__(parent)
        self.mainWindow = parent
        self.setAcceptDrops(True)
        self.setObjectName('PickerWindow')
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowTitle('Link Picker v0.1.0-beta')
        self.resize(600, 750)
        
        self._createMenu()
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        self.pickerPaths = None
        self.buttonManager = buttonManager.ButtonManager(self.toolBoxWidget)
        self.fileManager   = fileManager.FileManager(self)
        
        self.configManager = config.ConfigManager()
        self.updateTags()
        
        self.savedTabIndex = -1
        
    
    def keyPressEvent(self, event): 
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.key() == QtCore.Qt.Key_Z:
                self.undo()   
            elif event.key() == QtCore.Qt.Key_Y:
                self.redo()
        else:
            super(MainUI, self).keyPressEvent(event)
        
        
    def _createMenu(self):
        self.mainMenuBar = mainUIMenu.MainMenu(self) 
     

    def _createWidgets(self):
        self.namespaceWidget = widgets.NamespaceWidget()
        self.namespaceWidget.hide()
        # -----------------------------------------------------
        self.tabWidget     = widgets.MyTabWidget(parent = self)
        self.toolBoxWidget = toolBoxWidget.ToolBoxWidget()
        

    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(4)
        mainLayout.setContentsMargins(1, 1, 1, 6)
        
        mainLayout.setMenuBar(self.mainMenuBar)
        self.mainMenuBar.setCornerWidget(self.namespaceWidget, QtCore.Qt.TopRightCorner)
        
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(self.toolBoxWidget)
 
    def _createConnections(self):
        self.tabWidget.duplicateTriggered[int].connect(self.duplicateActiveTab)
        self.tabWidget.openClicked.connect(lambda: self.fileManager.open())
        self.tabWidget.newTab.connect(self._createNewTab)
        self.tabWidget.tabCount[int].connect(self.updateNamespaceWidgetTag) # hide namespaceWidget
        self.tabWidget.currentChanged.connect(self._updateNamespaceItem)
        self.tabWidget.currentChanged.connect(self.currentTabUpdateCallback) # update callback
        
        
        self.mainMenuBar.newTriggered.connect(self.tabWidget.newTab.emit)
        self.mainMenuBar.openTriggered.connect(lambda: self.fileManager.open())
        self.mainMenuBar.saveTriggered.connect(lambda: self.fileManager.save(self.undoToFile))
        self.mainMenuBar.saveAsTriggered.connect(lambda: self.fileManager.saveAs())
        self.mainMenuBar.renameTabTriggered.connect(lambda: self.tabWidget._renameTab(self.tabWidget.currentIndex()))
        self.mainMenuBar.closeTriggered.connect(lambda: self.tabWidget._closeTab(self.tabWidget.currentIndex()))
        #self.mainMenuBar.closeAllTriggered.connect(partial(self.tabWidget._closeAllTab, showWarning=True))
        self.mainMenuBar.quatTriggered.connect(self.close)

        self.mainMenuBar.undoTriggered.connect(self.undo)
        self.mainMenuBar.redoTriggered.connect(self.redo)
        
        #self.mainMenuBar.showToolBoxTriggered[bool].connect(lambda _bool: self.toolBoxWidget.show() if _bool else self.toolBoxWidget.hide())
        self.mainMenuBar.changeNamespaceTriggered.connect(self._showNamespaceEdit)
        self.mainMenuBar.preferencesTriggered.connect(self._showPreferences)
        
    # ---------------------------------------------------------------------------------------------------    
    def undo(self):
        currentPicker = self.tabWidget.currentWidget()
        if not isinstance(currentPicker, pickerView.PickerView):
            return
        self.mainMenuBar.setUndoType(currentPicker.undoStack.undoText())
        currentPicker.undo()

        
        
    def redo(self):
        currentPicker = self.tabWidget.currentWidget()
        if not isinstance(currentPicker, pickerView.PickerView):
            return
        self.mainMenuBar.setRedoType(currentPicker.undoStack.redoText())
        currentPicker.redo()
        
    # ----------------------------------------------------------------------------------------------------
    def _showPreferences(self):
        preferences = preferencesWidget.PreferencesWidget(self, self.configManager)
        preferences.preferencesUpdated.connect(self.updateTags)
        preferences.exec_()
        
    def updateTags(self):
        data = self.configManager.get()
        self.midView          = True if data['general']['viewModeComboBox'] == 0 else False
        self.autoSwitchTab    = data['general']['autoSelectedCheckBox']
        self.showToolBox      = data['general']['toolBoxCheckBox']
        self.showNamespaceTag = data['general']['showNamespaceCheckBox']
        
        self.showTabClosewarning = data['general']['closeTabCheckBox']

            
        
        
        self.ZoomDrag      = data['general']['ZoomSlider']
        self.undoQueue     = data['settings']['queue']
        self.enableUndo    = data['settings']['undo']
        self.undoToFile    = data['settings']['undoToFile']
        

        self.updatePickerTags()
        self.showToolBoxWidget(self.showToolBox)
        self.updateNamespaceWidgetTag(self.tabWidget.count())
        self.setTabWidgetShowCloseWarningTag()

        
    def updatePickerTags(self):
        allPickerViews = self.tabWidget.getWidget()
        if not allPickerViews: return
        for picker in allPickerViews:
            picker['ZoomDrag']   = self.ZoomDrag
            picker['undoQueue']  = self.undoQueue
            picker['enableUndo'] = self.enableUndo
            picker.setUndoMode(self.enableUndo, self.undoQueue)
            
    def showToolBoxWidget(self, _):
        self.toolBoxWidget.show() if _ else self.toolBoxWidget.hide()
        
    def updateNamespaceWidgetTag(self, index):
        self.namespaceWidget.showNamespaceTag = self.showNamespaceTag
        if self.width() > 400:
            self.namespaceWidget.hideNamespace(index)
            
    def setTabWidgetShowCloseWarningTag(self):
        self.tabWidget.showTabClosewarning = self.showTabClosewarning
        
    # ----------------------------------------------------------------------------------------------------
    def _selectNamespace(self, namespace):
        '''
        If the namespaceEditWidget returns an empty string
        meaning the namespace is cleared via the clear button, then attempt to select ':'!!
        '''
        if namespace in self.namespaceWidget.namespaceText() + ['']:
            self.namespaceWidget.blockSignals(True) 
            self.namespaceWidget.selectItem(namespace or ':')
            self.namespaceWidget.blockSignals(False)
 
          
    def _showNamespaceEdit(self):
        namespaceEdit = widgets.NamespaceEditWidget(self)
        currentPicker = self.tabWidget.currentWidget()  
        
        namespaceEdit.selectedNamespace[str].connect(currentPicker.updateButtonsNamespace)
        namespaceEdit.exec_()
        
        self._selectNamespace(currentPicker.namespace)


    def _updateNamespaceItem(self, index):
        picker = self.tabWidget.widget(index)
        if not isinstance(picker, pickerView.PickerView):
            return

        self._selectNamespace(picker.namespace)

        
    def _createNewTab(self, name=None, data=None):
        pickerViewInstance = pickerView.PickerView(parent = self, 
                                                  buttonManager = self.buttonManager, 
                                                  midView       = self.midView,
                                                  ZoomDrag      = self.ZoomDrag,
                                                  undoQueue     = self.undoQueue,
                                                  enableUndo    = self.enableUndo)
        
        self.toolBoxWidget.buttonColorLabelSelected.connect(pickerViewInstance.updateButtonsColor)
        self.toolBoxWidget.scaleXUndo[int].connect(pickerViewInstance.undoButtonsScaleX) # 
        
        self.toolBoxWidget.scaleXUpdate.connect(pickerViewInstance.updateButtonsScaleX)
        self.toolBoxWidget.scaleYUndo[int].connect(pickerViewInstance.undoButtonsScaleY) #
        self.toolBoxWidget.scaleYUpdate.connect(pickerViewInstance.updateButtonsScaleY)
        
        
        self.toolBoxWidget.labelTextColorSelected.connect(pickerViewInstance.updateButtonsTextColor)
        self.toolBoxWidget.textUpdate.connect(pickerViewInstance.updateButtonsText)
        self.namespaceWidget.namespaceClicked.connect(pickerViewInstance.updateButtonsNamespace)

        index = self.tabWidget.addNewTab(pickerViewInstance, name=name)
        self.tabWidget.setCurrentIndex(index)

        if data is not None:
            pickerViewInstance.set(data)
            self._updateNamespaceItem(index)
        self.updateTabToolTip(pickerViewInstance)
        
    def updateTabToolTip(self, picker):
        index = self.tabWidget.indexOf(picker)
        self.tabWidget.setTabToolTip(index, picker.cacheSavePath or 'Link Picker')
        
        
    def duplicateActiveTab(self, index):
        pickerView = self.tabWidget.widget(index) 
        data = pickerView.get()
        
        data['cacheSavePath'] = '' # update cacheSavePath
        self._createNewTab("{} (copy)".format(data['tabName']), data)
        self.currentTabUpdateCallback()
        
        
    def deleteAllTab(self, _):
        pickerViews = self.tabWidget.getWidget()
        if not pickerViews:
            return
            
        self.tabWidget._closeAllTab(showWarning=False)
            
    
    def get(self):
        pickerViewsData = []  
        pickerViews = self.tabWidget.getWidget()
        if not pickerViews:
            return pickerViewsData
            
        for pickerView in pickerViews:
            pickerViewsData.append(pickerView.get())
        return pickerViewsData
        
        
    def set(self, data):
        if not data:
            return
        for pickerData in data:
            self._createNewTab(pickerData['tabName'], pickerData)
        self.currentTabUpdateCallback()

if __name__ == '__main__':
    MainUI().show()
