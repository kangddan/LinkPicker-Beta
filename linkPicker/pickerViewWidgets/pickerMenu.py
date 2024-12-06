import maya.cmds as cmds

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
    Action      = QtGui.QAction
    ActionGroup = QtGui.QActionGroup 
else:
    from PySide2 import QtWidgets, QtCore, QtGui
    Action      = QtWidgets.QAction
    ActionGroup = QtWidgets.QActionGroup


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
        super().__init__(parent)
        self.pickerView = parent
        self.selectedNodes: 'list[selectedNodeNames]' = []
        self._createActions()
        self._createConnections()
        
        
    def setViewMode(self, enabled ):
        self.viewModeAction.setChecked(enabled)
        
        
    def _createActions(self):
        self.addSingleButtonAction    = Action(QtGui.QIcon(':addClip.png'), 'Add Single Button', self)
        self.addMultipleButtonsAction = Action('Add Multiple Buttons',  self)
        self.updateButtonAction       = Action(QtGui.QIcon(':refresh.png'), 'Update Button', self)
        self.deleteButtonAction       = Action(QtGui.QIcon(':delete.png'), 'Delete Selected Button(s)',  self, shortcut='Delete')
        
        self.addCommandButtonAction  = Action(QtGui.QIcon('icons:pythonLogo2.png'), 'Add Command Button (Beta)',  self)
        self.alignHorizontallyAction = Action(QtGui.QIcon('icons:alignHorizontallyIcon.png'), 'Align Buttons Horizontally', self)
        self.alignVerticallyAction   = Action(QtGui.QIcon('icons:alignVerticallyIcon.png'), 'Align Buttons Vertically',  self)
        self.distributeButtonsAction = Action('Distribute Buttons Evenly', self)
        
        self.mirrorAction  = Action(QtGui.QIcon(':teLoopTool.png'), 'Mirror', self)
        self.reverseAction = Action(QtGui.QIcon(':reverseOrder.png'), 'Reverse', self)
            
        self.raiseButtonAction  = Action(QtGui.QIcon(':nodeGrapherArrowUp.png'), 'Bring to Front', self)
        self.lowerButtonAction  = Action(QtGui.QIcon(':nodeGrapherArrowDown.png'), 'Send to Back', self)
        self.moveForwardAction  = Action(QtGui.QIcon(':moveUVUp.png'), 'Move Forward', self, shortcut='Up')
        self.moveBackwardAction = Action(QtGui.QIcon(':moveUVDown.png'), 'Move Backward', self, shortcut='Down')
        
        self.increaseSizeAction = Action(QtGui.QIcon(':moveUVUpd.png'), 'Increase Size', self, shortcut='+')
        self.decreaseSizeAction = Action(QtGui.QIcon(':moveUVDownd.png'), 'Decrease Size', self, shortcut='-')
        
        #self.viewModeAction = Action('Auto-Center (Beta)', self)
        #self.viewModeAction.setCheckable(True)
        
        self.frameDefaultAction   = Action(QtGui.QIcon(':home.png'), 'Frame Default', self)
        self.frameSelectionAction = Action(QtGui.QIcon(':visible.png'), 'Frame Selection', self, shortcut='F')

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
        selectedNodes  : 'list[selectedNodeNames]' = cmds.ls(sl=True, fl=True)
        selectedButtons: 'list[PickerButton]'      = self.pickerView.selectedButtons
        clickedButton  : 'PickerButton'            = self.pickerView.clickedButton
        
        isMayaNodeSelected = bool(selectedNodes)
        isButtonSelected   = bool(selectedButtons)
        hasMultipleNodes   = len(selectedNodes) > 1
        
        hasMoreThanOneButton  = len(selectedButtons) > 1
        hasMoreThanTwoButtons = len(selectedButtons) > 2
        
        self.addSingleButtonAction.setEnabled(isMayaNodeSelected)
        self.addMultipleButtonsAction.setEnabled(hasMultipleNodes)
        
        # update cmd button action text
        if clickedButton is not None and clickedButton.isCmdButton:
            self.addCommandButtonAction.setText('Edit Command Button (Beta)')
        else:
            self.addCommandButtonAction.setText('Add Command Button (Beta)')
        
        self.updateButtonAction.setEnabled(clickedButton is not None and not clickedButton.isCmdButton and isMayaNodeSelected)
        self.deleteButtonAction.setEnabled(isButtonSelected)
        
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
        
        
    def getSelectedNodes(self) -> 'list[selectedNodeNames]':
        return self.selectedNodes
              