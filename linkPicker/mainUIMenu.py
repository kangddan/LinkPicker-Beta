import maya.cmds as cmds

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
    Action = QtGui.QAction
else:
    from PySide2 import QtWidgets, QtCore, QtGui
    Action  = QtWidgets.QAction

from . import config

class MainMenu(QtWidgets.QMenuBar):
    
    newTriggered       = QtCore.Signal()
    openTriggered      = QtCore.Signal()
    saveTriggered      = QtCore.Signal()
    saveAsTriggered    = QtCore.Signal()
    renameTabTriggered = QtCore.Signal()
    closeTriggered     = QtCore.Signal()
    #closeAllTriggered  = QtCore.Signal()
    quatTriggered      = QtCore.Signal()
    
    undoTriggered  = QtCore.Signal()
    redoTriggered  = QtCore.Signal()
    #cutTriggered   = QtCore.Signal()
    #copyTriggered  = QtCore.Signal()
    #pasteTriggered = QtCore.Signal()
    changeBackgroundTriggered = QtCore.Signal()
    resizeBackgroundTriggered = QtCore.Signal()
    changeNamespaceTriggered  = QtCore.Signal()
    #showToolBoxTriggered = QtCore.Signal(bool)
    preferencesTriggered = QtCore.Signal()
    
    aboutTriggered       = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainUI = parent
        self._createActions()
        self._createConnections()
        
        
    def _createActions(self):
        self.fileMenu = QtWidgets.QMenu('File', self) 
        self.editMenu = QtWidgets.QMenu('Edit', self)
        self.helpMenu = QtWidgets.QMenu('Help', self)
        
        #self.fileMenu.setTearOffEnabled(True)
        #self.editMenu.setTearOffEnabled(True)
        #self.helpMenu.setTearOffEnabled(True)
        self.addMenu(self.fileMenu)
        self.addMenu(self.editMenu)
        self.addMenu(self.helpMenu)
        
        self.newAction        = Action(QtGui.QIcon(':fileNew.png'), 'New...',   self.fileMenu, shortcut='Ctrl+N')
        self.openAction       = Action(QtGui.QIcon(':fileOpen.png'), 'Open...', self.fileMenu, shortcut='Ctrl+O')
        self.saveAction       = Action(QtGui.QIcon(':fileSave.png'), 'Save',    self.fileMenu, shortcut='Ctrl+S')
        self.saveAsAction     = Action('Save as...', self.fileMenu, shortcut='Ctrl+Shift+S')
        self.renameTabAction  = Action(QtGui.QIcon(':renamePreset.png'), 'Rename Tab',    self.fileMenu)
        self.closeAction      = Action(QtGui.QIcon(':nodeGrapherClose.png'), 'Close Tab', self.fileMenu)
        #self.closeAllAction   = Action('Close All Tab', self.fileMenu)
        self.quatPickerAction = Action(QtGui.QIcon(':enabled.png'), 'Quit Picker', self.fileMenu, shortcut='Alt+F4')

        self.undoAction   = Action(QtGui.QIcon(':undo_s.png'), 'Undo ', self.editMenu, shortcut='Ctrl+Z')
        self.redoAction   = Action(QtGui.QIcon(':redo_s.png'), 'Redo ', self.editMenu, shortcut='Ctrl+Y')
        #self.cutAction    = Action('Cut', self.editMenu, shortcut='Ctrl+X')
        #self.copyAction   = Action(QtGui.QIcon(':polyCopyUV.png'), 'Copy',   self.editMenu, shortcut='Ctrl+C')
        #self.pasteAction  = Action(QtGui.QIcon(':polyPasteUV.png'), 'Paste', self.editMenu, shortcut='Ctrl+V')
        self.changeBackgroundAction = Action(QtGui.QIcon(config.backgroundIcon), 'Change Background', self.editMenu)
        self.resizeBackgroundAction = Action('Resize Background', self.editMenu)
        self.changeNamespaceAction  = Action('Change Namespace',  self.editMenu)
        # self.ToolAction = Action('Show ToolBox', self.editMenu)
        # self.ToolAction.setCheckable(True)
        # self.ToolAction.setChecked(True)
        self.preferencesAction = Action(QtGui.QIcon(':advancedSettings.png'),'Preferences...',  self.editMenu, shortcut='Ctrl+E')
        
        self.aboutAction = Action(QtGui.QIcon(':help.png'), 'About Link Picker', self.helpMenu)

        self.fileMenu.addAction(self.newAction)
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.renameTabAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)
        #self.fileMenu.addAction(self.closeAllAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quatPickerAction)
            
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)
        self.editMenu.addSeparator()
        #self.editMenu.addAction(self.cutAction)
        #self.editMenu.addAction(self.copyAction)
        #self.editMenu.addAction(self.pasteAction)
        #self.editMenu.addSeparator()
        self.editMenu.addAction(self.changeBackgroundAction)
        self.editMenu.addAction(self.resizeBackgroundAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.changeNamespaceAction)
        #self.editMenu.addSeparator()
        #self.editMenu.addAction(self.ToolAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.preferencesAction)

        self.helpMenu.addAction(self.aboutAction)
        
        
    def _createConnections(self):
        self.fileMenu.aboutToShow.connect(self._updateFileMenuActions)
        self.editMenu.aboutToShow.connect(self._updateEditMenuActions)
        
        self.newAction.triggered.connect(self.newTriggered.emit)
        self.openAction.triggered.connect(self.openTriggered.emit)
        self.saveAction.triggered.connect(self.saveTriggered.emit)
        self.saveAsAction.triggered.connect(self.saveAsTriggered.emit)
        self.renameTabAction.triggered.connect(self.renameTabTriggered.emit)
        self.closeAction.triggered.connect(self.closeTriggered.emit)
        #self.closeAllAction.triggered.connect(self.closeAllTriggered.emit)
        self.quatPickerAction.triggered.connect(self.quatTriggered.emit)
        
        self.undoAction.triggered.connect(self.undoTriggered.emit)
        self.redoAction.triggered.connect(self.redoTriggered.emit)
        #self.cutAction.triggered.connect(self.cutTriggered.emit)
        #self.copyAction.triggered.connect(self.copyTriggered.emit)
        #self.pasteAction.triggered.connect(self.pasteTriggered.emit)
        self.changeBackgroundAction.triggered.connect(self.changeBackgroundTriggered.emit)
        self.resizeBackgroundAction.triggered.connect(self.resizeBackgroundTriggered.emit)
        self.changeNamespaceAction.triggered.connect(self.changeNamespaceTriggered.emit)
        
        #self.ToolAction.triggered.connect(lambda _bool: self.showToolBoxTriggered.emit(_bool))
        self.preferencesAction.triggered.connect(self.preferencesTriggered.emit)
        self.aboutAction.triggered.connect(self.aboutTriggered.emit)  
        
    def _updateFileMenuActions(self):
        _ = self.mainUI.tabWidget.count() >= 2
        self.saveAction.setEnabled(_)
        self.saveAsAction.setEnabled(_) 
        self.renameTabAction.setEnabled(_)
        self.closeAction.setEnabled(_)
        #self.closeAllAction.setEnabled(_)

    def _updateEditMenuActions(self):
        _ = self.mainUI.tabWidget.count() >= 2
        #self.cutAction.setEnabled(False)
        #self.copyAction.setEnabled(False)
        #self.pasteAction.setEnabled(False)
        #self.preferencesAction.setEnabled(True)
        
        self.changeBackgroundAction.setEnabled(_)
        self.resizeBackgroundAction.setEnabled(_)
        self.changeNamespaceAction.setEnabled(_)
        
        # undo / redo
        if _:
            currentPicker = self.mainUI.tabWidget.currentWidget()
            if hasattr(currentPicker, 'undoStack'):
                self.undoAction.setEnabled(currentPicker.undoStack.canUndo())
                self.setUndoType(currentPicker.undoStack.undoText())
                self.redoAction.setEnabled(currentPicker.undoStack.canRedo()) 
                self.setRedoType(currentPicker.undoStack.redoText())
        else:
            self.undoAction.setEnabled(False)
            self.redoAction.setEnabled(False) 
            self.setUndoType()
            self.setRedoType()
        
    def setUndoType(self, typ=''):
        self.undoAction.setText('Undo ' + typ)
        
    def setRedoType(self, typ=''):
        self.redoAction.setText('Redo ' + typ)
        
    def updateMenuAboutToShow(self):
        self.fileMenu.aboutToShow.emit()
        self.editMenu.aboutToShow.emit()
        

        

              