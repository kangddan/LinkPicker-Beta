import maya.cmds as cmds

from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore

from linkPicker import config


class PickerMenu(QtWidgets.QMenu):
    
    addSingleButtonTriggered    = QtCore.Signal()
    addMultipleButtonsTriggered = QtCore.Signal()
    updateButtonTriggered       = QtCore.Signal()
    deleteButtonTriggered       = QtCore.Signal()
    
    addCommandButtonTriggered  = QtCore.Signal()
    alignHorizontallyTriggered = QtCore.Signal()
    alignVerticallyTriggered   = QtCore.Signal()
    distributeButtonsTriggered = QtCore.Signal()
    
    mirrorTriggered  = QtCore.Signal()
    reverseTriggered = QtCore.Signal()

    raiseButtonTriggered  = QtCore.Signal()
    lowerButtonTriggered  = QtCore.Signal()
    moveForwardTriggered  = QtCore.Signal()
    moveBackwardTriggered = QtCore.Signal()
    
    increaseSizeTriggered = QtCore.Signal()
    decreaseSizeTriggered = QtCore.Signal()
    
    #viewModeTriggered = QtCore.Signal(bool)
    
    frameDefaultTriggered   = QtCore.Signal()
    frameSelectionTriggered = QtCore.Signal()
    
    def __init__(self, parent=None):
        super(PickerMenu, self).__init__(parent)
        self.pickerView = parent
        self.selectedNodes = [] # List of selected Maya node names
        self._createActions()
        self._createConnections()
        
        
    def setViewMode(self, enabled ):
        self.viewModeAction.setChecked(enabled)
        
        
    def _createActions(self):
        self.addSingleButtonAction    = QtWidgets.QAction(QtGui.QIcon(':addClip.png'), 'Add Single Button', self)
        self.addMultipleButtonsAction = QtWidgets.QAction('Add Multiple Buttons',  self)
        self.updateButtonAction       = QtWidgets.QAction(QtGui.QIcon(':refresh.png'), 'Update Button', self)
        self.deleteButtonAction       = QtWidgets.QAction(QtGui.QIcon(':delete.png'), 'Delete Selected Button(s)',  self, shortcut='Delete')
        
        self.addCommandButtonAction  = QtWidgets.QAction(QtGui.QIcon(config.pythonLogo), 'Add Command Button',  self)
        self.alignHorizontallyAction = QtWidgets.QAction(QtGui.QIcon(config.alignHorizontallyIcon), 'Align Buttons Horizontally', self)
        self.alignVerticallyAction   = QtWidgets.QAction(QtGui.QIcon(config.alignVerticallyIcon), 'Align Buttons Vertically',  self)
        self.distributeButtonsAction = QtWidgets.QAction('Distribute Buttons Evenly', self)
        
        self.mirrorAction  = QtWidgets.QAction(QtGui.QIcon(':teLoopTool.png'), 'Mirror', self)
        self.reverseAction = QtWidgets.QAction(QtGui.QIcon(':reverseOrder.png'), 'Reverse', self)
            
        self.raiseButtonAction  = QtWidgets.QAction(QtGui.QIcon(':nodeGrapherArrowUp.png'), 'Bring to Front', self)
        self.lowerButtonAction  = QtWidgets.QAction(QtGui.QIcon(':nodeGrapherArrowDown.png'), 'Send to Back', self)
        self.moveForwardAction  = QtWidgets.QAction(QtGui.QIcon(':moveUVUp.png'), 'Move Forward', self, shortcut='Up')
        self.moveBackwardAction = QtWidgets.QAction(QtGui.QIcon(':moveUVDown.png'), 'Move Backward', self, shortcut='Down')
        
        self.increaseSizeAction = QtWidgets.QAction(QtGui.QIcon(':moveUVUpd.png'), 'Increase Size', self, shortcut='+')
        self.decreaseSizeAction = QtWidgets.QAction(QtGui.QIcon(':moveUVDownd.png'), 'Decrease Size', self, shortcut='-')
        
        #self.viewModeAction = QtWidgets.QAction('Auto-Center (Beta)', self)
        #self.viewModeAction.setCheckable(True)
        
        self.frameDefaultAction   = QtWidgets.QAction(QtGui.QIcon(':home.png'), 'Frame Default', self)
        self.frameSelectionAction = QtWidgets.QAction(QtGui.QIcon(':visible.png'), 'Frame Selection', self, shortcut='F')

        self.addAction(self.addSingleButtonAction)
        self.addAction(self.addMultipleButtonsAction)
        self.addAction(self.updateButtonAction)
        self.addAction(self.deleteButtonAction)
        
        self.addSeparator()
        self.addAction(self.addCommandButtonAction)
        
        self.addSeparator()
        self.addAction(self.alignHorizontallyAction)
        self.addAction(self.alignVerticallyAction)
        self.addAction(self.distributeButtonsAction)
        
        self.addSeparator()
        self.addAction(self.mirrorAction)
        self.addAction(self.reverseAction)
        
        self.addSeparator()
        self.zOrderMenu = self.addMenu(QtGui.QIcon(':out_displayLayer.png'), 'Z-Order')
        self.zOrderMenu.setTearOffEnabled(True)
        self.zOrderMenu.addAction(self.raiseButtonAction)
        self.zOrderMenu.addAction(self.moveForwardAction)
        self.zOrderMenu.addAction(self.moveBackwardAction)
        self.zOrderMenu.addAction(self.lowerButtonAction)
        
        self.addSeparator()
        self.addAction(self.increaseSizeAction)
        self.addAction(self.decreaseSizeAction)
        
        #self.addSeparator()
        #self.addAction(self.viewModeAction)
        
        self.addSeparator()
        self.addAction(self.frameDefaultAction)
        self.addAction(self.frameSelectionAction)
        
        
    def _createConnections(self):
        self.aboutToShow.connect(self._updateActionsState) 
        self.aboutToShow.connect(self._updateZOrder) 
        
        self.addSingleButtonAction.triggered.connect(self.addSingleButtonTriggered.emit)
        self.addMultipleButtonsAction.triggered.connect(self.addMultipleButtonsTriggered.emit)
        self.updateButtonAction.triggered.connect(self.updateButtonTriggered.emit)
        self.deleteButtonAction.triggered.connect(self.deleteButtonTriggered.emit)
        
        self.addCommandButtonAction.triggered.connect(self.addCommandButtonTriggered.emit)
        
        self.alignHorizontallyAction.triggered.connect(self.alignHorizontallyTriggered.emit)
        self.alignVerticallyAction.triggered.connect(self.alignVerticallyTriggered.emit)
        self.distributeButtonsAction.triggered.connect(self.distributeButtonsTriggered.emit)
        
        self.mirrorAction.triggered.connect(self.mirrorTriggered.emit)
        self.reverseAction.triggered.connect(self.reverseTriggered.emit)
        
        self.raiseButtonAction.triggered.connect(self.raiseButtonTriggered.emit)
        self.lowerButtonAction.triggered.connect(self.lowerButtonTriggered.emit)
        self.moveForwardAction.triggered.connect(self.moveForwardTriggered.emit)
        self.moveBackwardAction.triggered.connect(self.moveBackwardTriggered.emit)
        
        self.increaseSizeAction.triggered.connect(self.increaseSizeTriggered.emit)
        self.decreaseSizeAction.triggered.connect(self.decreaseSizeTriggered.emit)
        
        #self.viewModeAction.triggered.connect(lambda _bool:self.viewModeTriggered.emit(_bool))
        
        self.frameDefaultAction.triggered.connect(self.frameDefaultTriggered.emit)
        self.frameSelectionAction.triggered.connect(self.frameSelectionTriggered.emit) 
        
        
    def _updateActionsState(self):
        selectedNodes   = cmds.ls(sl=True, fl=True)
        selectedButtons = self.pickerView.selectedButtons
        clickedButton   = self.pickerView.clickedButton
        
        isMayaNodeSelected = bool(selectedNodes)
        isButtonSelected   = bool(selectedButtons)
        hasMultipleNodes   = len(selectedNodes) > 1
        
        hasMoreThanOneButton  = len(selectedButtons) > 1
        hasMoreThanTwoButtons = len(selectedButtons) > 2
        
        self.addSingleButtonAction.setEnabled(isMayaNodeSelected)
        self.addMultipleButtonsAction.setEnabled(hasMultipleNodes)

        self.updateButtonAction.setEnabled(clickedButton is not None and isMayaNodeSelected)
        self.deleteButtonAction.setEnabled(isButtonSelected)
        
        self.addCommandButtonAction.setEnabled(False)
        
        self.mirrorAction.setEnabled(isButtonSelected)
        self.reverseAction.setEnabled(hasMoreThanOneButton)
  
        self.alignHorizontallyAction.setEnabled(hasMoreThanOneButton)
        self.alignVerticallyAction.setEnabled(hasMoreThanOneButton)
        self.distributeButtonsAction.setEnabled(hasMoreThanTwoButtons)


        self.increaseSizeAction.setEnabled(isButtonSelected)
        self.decreaseSizeAction.setEnabled(isButtonSelected)
        
        self.selectedNodes = selectedNodes
        
    def _updateZOrder(self):
        isButtonSelected   = bool(self.pickerView.selectedButtons)
        self.raiseButtonAction.setEnabled(isButtonSelected)
        self.lowerButtonAction.setEnabled(isButtonSelected)
        self.moveForwardAction.setEnabled(isButtonSelected)
        self.moveBackwardAction.setEnabled(isButtonSelected)
        
        
    def getSelectedNodes(self):
        return self.selectedNodes
              