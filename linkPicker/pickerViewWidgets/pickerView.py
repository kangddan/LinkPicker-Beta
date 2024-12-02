import maya.cmds as cmds
import maya.api.OpenMaya as om2
import enum

from functools import partial

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
else:
    from PySide2 import QtWidgets, QtCore, QtGui


from linkPicker import (
    qtUtils, config, widgets
    )
from linkPicker.pickerViewWidgets import (
    pickerButton, pickerMenu, pickerUtils, pickerStates,  
    zorder, align, selection, mirror, view, buttonManager, pickerBackground, undo
    ) 


class PickerEnum(enum.Enum):
    NONE = enum.auto()  
      
    MIRROR_BUTTONS = enum.auto()
    ADDING_BUTTONS = enum.auto()  
      
    MOVE_VIEW        = enum.auto() 
    SCALE_VIEW       = enum.auto() 
    SELECTED_BUTTONS = enum.auto()  
    MOVE_BUTTONS     = enum.auto()
    
    
   
class PickerView(QtWidgets.QWidget):
    
    def signalEmitter(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.updateTab.emit() 
            return result
        return wrapper
        
    updateTab = QtCore.Signal()
    
    _IS_SELECTION_VIA_UI = True
    
    @classmethod
    def setSelectionViaUi(cls, status):
        cls._IS_SELECTION_VIA_UI = status

    @classmethod
    def isSelectionviaUiActive(cls):
        return cls._IS_SELECTION_VIA_UI
        
    
    def __init__(self, parent        = None, 
                       buttonManager = None,
                       midView       = False,
                       ZoomDrag      = 50,
                       undoQueue     = 20,
                       enableUndo    = True):
                        
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) 
        self.setObjectName('PickerView')
        self.setStyleSheet('#PickerView { background-color: #333333;}')
        self.setMouseTracking(True)
        self.buttonManager = buttonManager
        
        # tags
        self.midView    = midView
        self.ZoomDrag   = ZoomDrag
        self.undoQueue  = undoQueue
        self.enableUndo = enableUndo
        
        
        self.viewOffset = QtCore.QPointF(0, 0) 
        
        
        self._createMenu()
        self._createWidgets()
        self._createConnections()
        
        self.pickerState    = None
        self.pickerViewEnum = PickerEnum.NONE

        self.clickedButton = None
        
        self.sceneScale = 1.0
        self.origScale  = 1.0
        
        self.frameMoveTag = True

        self.clickedParentPos = QtCore.QPointF()
        self.buttonsParentPos = QtCore.QPointF()
        self.clickedPos       = QtCore.QPointF()

        self.buttonGlobalPos  = QtCore.QPointF() # set button global pos by menu

        '''
        This variable might cause confusion.
        It is only set to True when holding down the left mouse button to perform a box selection. 
        It takes effect when holding down Ctrl to deselect through the selectionBox,
        performing a second check on the buttons. 
        If a button is inside or intersects with the box, it will be deselected
        '''
        self.clearMoveTag     = False
        
        self.startPos         = QtCore.QPoint() # selectionBox start pos
        self.endtPos          = QtCore.QPoint() # selectionBox end pos
        self.selectionBoxRect = QtCore.QRect()  # selectionBox Rect
        
        self.allPickerButtons    = []
        self.nonMaxPickerButtons = []
        self.MaxPickerButtons    = []
        
        self.selectedButtons = []
        self.shiftAddButtons = []
        
        self.buttonsTranslateOffset = {}
        
        # create buttons
        self.trackedButtons = []
        
        # mirror buttons
        self.mirrorCacheButtons = {}

        self.namespace = ':'
        self.cacheSavePath = ''
        self.mainUI = parent
        
        self.allPickerButtonsIdMap = {}    
        self.undoStack = undo.PickerViewUndoStackBase(self, self.enableUndo, self.undoQueue)    
        #self.undoStack = QtWidgets.QUndoStack()
        self.undoCacheButtons = {}
        self.newNodes = [] # maya nodes by menu
        
        self.cacheOldButtonsScaleX = {}
        self.cacheOldButtonsScaleY = {}
    
    
    def setUndoMode(self, enableUndo, undoQueue):
        self.undoStack.enableUndo = enableUndo
        if not enableUndo:
            self.undoStack.clear()
            return
        
        self.undoStack.setUndoLimit(undoQueue)
    

    def __getitem__(self, attr):
        if isinstance(attr, str):
            if attr in self.__dict__:
                return self.__dict__[attr]
            raise KeyError(f"Key '{attr}' not found in object attributes.")
            
    def __setitem__(self, attr, value):
        self.__setattr__(attr, value)


    def _createMenu(self):
        self.pickerViewMenu = pickerMenu.PickerMenu(self)
        #self.pickerViewMenu.setViewMode(self.midView)


    def _createWidgets(self):
        self.parentAxis   = widgets.AxisWidget(self); self.parentAxis.hide()
        self.selectionBox = widgets.SelectionBox(parent=self)
        
        # -----------------------------------------------------
        # self.undoButton = QtWidgets.QPushButton(self)
        # self.redoButton = QtWidgets.QPushButton(self)
        # self.undoButton.move(200, 0)
        # self.redoButton.move(250, 0)
        
        # self.undoButton.setIcon(QtGui.QIcon(':undo_s.png'))
        # self.redoButton.setIcon(QtGui.QIcon(':redo_s.png'))
        
        # self.undoButton.clicked.connect(self.undo)
        # self.redoButton.clicked.connect(self.redo)
        
    
        
    @signalEmitter    
    def undo(self):
        if self.undoStack.canUndo():
            self.undoStack.undo()
        else:
            om2.MGlobal.displayWarning('There are no more commands to undo.')
            
    @signalEmitter
    def redo(self):
        if self.undoStack.canRedo():
            self.undoStack.redo()
        else:
            om2.MGlobal.displayWarning('There are no more commands to redo.')
        
        
    def _createConnections(self):
        #self.updateTab.connect(lambda instance: print(instance))
        #self.pickerViewMenu.viewModeTriggered[bool].connect(self.autoCenterView)
        
        self.pickerViewMenu.addSingleButtonTriggered.connect(self.createSingleButton)
        self.pickerViewMenu.addMultipleButtonsTriggered.connect(self.updateAddingButtons)
        self.pickerViewMenu.updateButtonTriggered.connect(self._updateSelectedButton)
        self.pickerViewMenu.deleteButtonTriggered.connect(self._deleteSelectedButton)
        
        self.pickerViewMenu.alignHorizontallyTriggered.connect(self._alignButtonsHorizontally)
        self.pickerViewMenu.alignVerticallyTriggered.connect(self._alignButtonsVertically)
        self.pickerViewMenu.distributeButtonsTriggered.connect(self._distributeButtonsEvenly)
            
        self.pickerViewMenu.mirrorTriggered.connect(self.updateMirrorButtons)
        self.pickerViewMenu.reverseTriggered.connect(self._reverseSelection)
        
        self.pickerViewMenu.raiseButtonTriggered.connect(self._raiseSelectedButtons)
        self.pickerViewMenu.lowerButtonTriggered.connect(self._lowerSelectedButtons)
        self.pickerViewMenu.moveForwardTriggered.connect(self._moveSelectedButtonsUp)
        self.pickerViewMenu.moveBackwardTriggered.connect(self._moveSelectedButtonsDown)
        
        self.pickerViewMenu.increaseSizeTriggered.connect(partial(self._adjustSelectionScale, 1))
        self.pickerViewMenu.decreaseSizeTriggered.connect(partial(self._adjustSelectionScale, -1))
        
        self.pickerViewMenu.frameDefaultTriggered.connect(self._frameDefault)
        self.pickerViewMenu.frameSelectionTriggered.connect(self._frameSelection)
        
        
    def keyPressEvent(self, event): 
        if event.key() == QtCore.Qt.Key_F: 
            self._frameSelection()
        elif event.key() == QtCore.Qt.Key_Up: 
            self._moveSelectedButtonsUp()
        elif event.key() == QtCore.Qt.Key_Down: 
            self._moveSelectedButtonsDown()
        elif event.key() in [QtCore.Qt.Key_Equal, QtCore.Qt.Key_Plus]: 
            self._adjustSelectionScale(1)
        elif event.key() == QtCore.Qt.Key_Minus: 
            self._adjustSelectionScale(-1)
        elif event.key() in [QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete]:
            self._deleteSelectedButton()
        else:
            super().keyPressEvent(event)
         
    @signalEmitter
    def _adjustSelectionScale(self, adjustment: int):
        self.undoStack.push(undo.UpdateSelectedButtonsScaleCmd(self).initialize(adjustment))
        self.buttonManager.updateToolBoxWidget(self.selectedButtons[-1]) # update toolbox   
    
    # update button -------------------------------------------------------------------
    
    def updateButtonList(self, button):
        if button.isMaxButton:
            if button not in self.MaxPickerButtons:
                self.MaxPickerButtons.append(button)
            if button in self.nonMaxPickerButtons:
                self.nonMaxPickerButtons.remove(button)
        else:
            if button in self.MaxPickerButtons:
                self.MaxPickerButtons.remove(button)
            if button not in self.nonMaxPickerButtons:
                self.nonMaxPickerButtons.append(button)
  
    @signalEmitter
    def _updateSelectedButton(self):
        if self.clickedButton is None:
            return
            
        self.newNodes = self.pickerViewMenu.getSelectedNodes()
        self.undoStack.push(undo.UpdateButtonCmd(self).initialize())

        
    # update button ------------------------------------------------------------------- 
    def updateButtonsNamespace(self, namespace: str):
        if self.isActiveTab: 
            self.undoStack.push(undo.UpdateButtonsNamespaceCmd(self).initialize(namespace))
            self.updateTab.emit()
            # self.namespace = namespace
            # for button in self.allPickerButtons:
            #     button.updateNamespace(namespace)
    
    
    # delete button -------------------------------------------------------------------  
    def _updateButtonsCache(self, button):
        if button in self.selectedButtons:
            self.selectedButtons.remove(button)
        if button in self.allPickerButtons:
            self.allPickerButtons.remove(button)
        if button in self.MaxPickerButtons:
            self.MaxPickerButtons.remove(button)
        if button in self.nonMaxPickerButtons:
            self.nonMaxPickerButtons.remove(button)
        if button.buttonId in self.allPickerButtonsIdMap:
            del self.allPickerButtonsIdMap[button.buttonId]
    
    @signalEmitter
    def _deleteSelectedButton(self):
        self.undoStack.push(undo.DeleteButtonCmd(self).initialize())
        
    # delete button -------------------------------------------------------------------        
        
        
    # zoreder ----------------------------------------------------------    
    @signalEmitter
    def _raiseSelectedButtons(self):
        self.undoStack.push(undo.RaiseCmd(self).initialize())
    @signalEmitter
    def _lowerSelectedButtons(self):
        self.undoStack.push(undo.LowerCmd(self).initialize())
    @signalEmitter
    def _moveSelectedButtonsUp(self):
        self.undoStack.push(undo.UpCmd(self).initialize())
    @signalEmitter
    def _moveSelectedButtonsDown(self):
        self.undoStack.push(undo.DownCmd(self).initialize())
            
    # ------------------------------------------------------------------
    def getAllPickerButtons(self) -> 'list[pickerButton.PickerButton]':
        return self.findChildren(pickerButton.PickerButton) 
        
        
    def getMaxPickerButtons(self) -> 'list[pickerButton.PickerButton]':
        return [button for button in self.getAllPickerButtons() if button.isMaxButton]
        
        
    def getNonMaxPickerButtons(self) -> 'list[pickerButton.PickerButton]':
        return [button for button in self.getAllPickerButtons() if not button.isMaxButton]
        
        
    def clearSelectedButtons(self):
        for button in self.selectedButtons:
            button.setSelected(False)
        self.selectedButtons.clear()  
    
    # ------------------------------------------------------------------
    @property
    def isActiveTab(self) -> bool:
        return self.mainUI.tabWidget.currentWidget() == self
        #return self.parent().currentWidget() == self
        

    def updateButtonsColor(self, color: QtGui.QColor):
        if self.isActiveTab and self.selectedButtons:  
            self.undoStack.push(undo.UpdateButtonsColorCmd(self).initialize(color))
            self.updateTab.emit()
            

    def updateButtonsTextColor(self, color: QtGui.QColor):
        if self.isActiveTab and self.selectedButtons:
            self.undoStack.push(undo.UpdateButtonsTextColorCmd(self).initialize(color))
            self.updateTab.emit()
            
    def updateButtonsText(self, text: str):
        if self.isActiveTab and self.selectedButtons:
            self.undoStack.push(undo.UpdateButtonsTextCmd(self).initialize(text))
            self.updateTab.emit()
    
    
    # ---------------------------------------------------------------------------------------   
    @staticmethod
    def getBUttonsScaleInfo(buttons, buttonsMap, typ='scaleX'):
        for button in buttons:
            localPos = button.localPos
            buttonsMap[button.buttonId] = [button[typ], [localPos.x(), localPos.y()]]
        
        
    @staticmethod        
    def updateButtonsScaleInfo(buttons, buttonsMap, allButtonsMap):
        for buttonId in buttonsMap:
            button = allButtonsMap[buttonId]
            newLocalPos = button.localPos
            buttonsMap[buttonId].append([newLocalPos.x(), newLocalPos.y()])
        

    def updateButtonsScaleX(self, value: int):
        if not (self.isActiveTab and self.selectedButtons):
            return
        # 1 get buttons old localPos and old scaleX
        if not self.cacheOldButtonsScaleX:
            self.getBUttonsScaleInfo(self.selectedButtons, self.cacheOldButtonsScaleX, 'scaleX')
        
        for but in self.selectedButtons:
            but.updateScaleX(value, self.sceneScale, self.buttonsParentPos)

 
    def undoButtonsScaleX(self, value):
        if not (self.isActiveTab and self.cacheOldButtonsScaleX):
            return
            
        # 2 update button new localPos
        self.updateButtonsScaleInfo(self.selectedButtons, self.cacheOldButtonsScaleX, self.allPickerButtonsIdMap)

 
        self.undoStack.push(undo.UpdateButtonsScaleXCmd(self).initialize(value))
        self.cacheOldButtonsScaleX.clear()
        self.updateTab.emit()

    # ---------------------------------------------------------------------------------------    

    def updateButtonsScaleY(self, value: int):
        if not (self.isActiveTab and self.selectedButtons):
            return
        # 1 get buttons old localPos and old scaleY
        if not self.cacheOldButtonsScaleY:
            self.getBUttonsScaleInfo(self.selectedButtons, self.cacheOldButtonsScaleY, 'scaleY')
                
        for but in self.selectedButtons:
            but.updateScaleY(value, self.sceneScale, self.buttonsParentPos)
            but.scaleText(self.sceneScale)
    

    def undoButtonsScaleY(self, value):
        if not (self.isActiveTab and self.cacheOldButtonsScaleY):
            return
            
        # 2 update button new localPos
        self.updateButtonsScaleInfo(self.selectedButtons, self.cacheOldButtonsScaleY, self.allPickerButtonsIdMap)

        self.undoStack.push(undo.UpdateButtonsScaleYCmd(self).initialize(value))
        self.cacheOldButtonsScaleY.clear()
        self.updateTab.emit()
        
    # ---------------------------------------------------------------------------------------    
    
    def createButton(self, nodeList:list, data: dict=None, buttonId: str=None):
        button = self.buttonManager.create(self.buttonGlobalPos, 
                                           self.buttonsParentPos, 
                                           self.sceneScale, 
                                           nodeList, 
                                           self, 
                                           data = data,
                                           buttonId = buttonId)
        button.show()
        # to cache list
        if button.isMaxButton:
            self.MaxPickerButtons.append(button)
        else:
            self.nonMaxPickerButtons.append(button)
        self.allPickerButtons.append(button)
        self.allPickerButtonsIdMap[button.buttonId] = button
        return button

    @signalEmitter
    def createSingleButton(self): 
        self.undoStack.push(undo.CreateSingleButtonCmd(self).initialize())     


    def updateAddingButtons(self):
        self.setCursor(QtGui.QCursor(QtGui.QPixmap(':leftArrowPlus.png')))
        self.pickerViewEnum = PickerEnum.ADDING_BUTTONS
        
    @signalEmitter
    def createMultipleButtons(self):
        nodeList:'list[MayaNodeName]' = self.pickerViewMenu.getSelectedNodes()
        self.trackedButtons = [self.createButton([node]) for node in nodeList]
            
         
    def _updateButtonsDuringDrag(self, startPos, endPos):
        align.updateButtonsDuringDrag(self.trackedButtons, 
                                      startPos, 
                                      endPos, 
                                      self.buttonsParentPos, 
                                      self.sceneScale)
   
    @signalEmitter
    def _alignButtonsHorizontally(self):
        self.undoStack.push(undo.AlignHorizontalCmd(self).initialize())
    @signalEmitter
    def _alignButtonsVertically(self):
        self.undoStack.push(undo.AlignVerticalCmd(self).initialize())
    @signalEmitter    
    def _distributeButtonsEvenly(self):
        self.undoStack.push(undo.DistributeEvenlyCmd(self).initialize())
        
        
    def _frameDefault(self):
        self.sceneScale = 1.0
        self.origScale  = 1.0
        self.clickedParentPos = QtCore.QPointF()
        self.buttonsParentPos = QtCore.QPointF() if not self.midView else QtCore.QPointF(self.width() / 2, self.height() / 2)
        
        self.parentAxis.move(self.buttonsParentPos.toPoint())
        self.parentAxis.resize(100, 100) 
        
        if self.midView:
            self.updateMidViewOffset()
            
        for but in self.allPickerButtons:
            but.resetPos(self.buttonsParentPos)
            but.scaleText(self.sceneScale)
            
    @signalEmitter
    def mirrorButtons(self, clickedPosX):
        for mirrorButton in self.selectedButtons:
            mirrorButtonData = mirrorButton.get()
            mirrorNodes      = mirror.getMirrorObjs(mirrorButton.nodes)
            newButton        = self.createButton(mirrorNodes, mirrorButtonData) 
            
            oldGlobalPos = pickerUtils.localToGlobal(mirrorButton.localPos, self.buttonsParentPos, self.sceneScale)     
            topRightPosX = clickedPosX - oldGlobalPos.x() - (mirrorButton.scaleX * self.sceneScale)

            self.mirrorCacheButtons[newButton] = [topRightPosX, oldGlobalPos.y(), clickedPosX]
            
            x = clickedPosX + topRightPosX
            newPos = QtCore.QPointF(x, oldGlobalPos.y())
            
            newButton.move(newPos.toPoint())
            newButton.updateLocalPos(newPos, self.buttonsParentPos, self.sceneScale)
    
    
    def updateButtonsPos(self, updateScale=True, buttons=None):
        _buttons = buttons or self.allPickerButtons
        for button in _buttons:
            globalPos = pickerUtils.localToGlobal(button.localPos, self.buttonsParentPos, self.sceneScale)
            button.move(globalPos.toPoint())
            if updateScale:
                button.resize(round(button.scaleX * self.sceneScale), round(button.scaleY * self.sceneScale))
                button.scaleText(self.sceneScale)
            
    
    def setPickerState(self, stateClass, event):
        self.pickerState = stateClass()
        self.pickerState.handlePressEvent(event, self)
        
    def resetPickerState(self, resetCursor=True):
        self.pickerState = None
        if resetCursor:
            self.setCursor(QtCore.Qt.ArrowCursor)
    
    
    def mousePressEvent(self, event): 
        
        # mirro selected buttons
        if self.pickerViewEnum == PickerEnum.MIRROR_BUTTONS:
            if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
                self.setPickerState(pickerStates.MriiroButtonsState, event)
            else:
                self.resetPickerState(True)
        
        # create buttons
        elif self.pickerViewEnum == PickerEnum.ADDING_BUTTONS:
            if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
                self.setPickerState(pickerStates.CreateButtonsState, event)
            else:
                self.resetPickerState(True)
                
        # show menu
        elif event.buttons() == QtCore.Qt.MouseButton.RightButton and event.modifiers() == QtCore.Qt.NoModifier:
            self.setPickerState(pickerStates.ShowMenuState, event); self.activateWindow() # set focus
  
            
        # move view
        elif event.buttons() == QtCore.Qt.MouseButton.MiddleButton:
            self.setPickerState(pickerStates.MoveViewState, event)

        # scale view
        elif event.modifiers() == QtCore.Qt.AltModifier and event.buttons() == QtCore.Qt.MouseButton.RightButton:
            self.setPickerState(pickerStates.ScaleViewState, event)
            
        # selected buttons and update Selection Box
        elif event.buttons() == QtCore.Qt.MouseButton.LeftButton and event.modifiers() != QtCore.Qt.ControlModifier:
            self.setPickerState(pickerStates.SelectedState, event)
            
        # move buttons
        elif event.modifiers() == QtCore.Qt.ControlModifier and event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.setPickerState(pickerStates.MoveButtonsState, event)
            
        else:
            super().mousePressEvent(event)
        
        
    def mouseMoveEvent(self, event):
        if self.pickerState is not None:
            self.update() 
            self.pickerState.handleMoveEvent(event, self)           
        else:     
            super().mouseMoveEvent(event)
            
 
    def mouseReleaseEvent(self, event):
        if self.midView:
            self.updateMidViewOffset()
            
        if self.pickerState is not None:
            self.pickerState.handleReleaseEvent(event, self)
            # updateTab emit! 
            if isinstance(self.pickerState, pickerStates.MoveButtonsState) and self.undoMoveButtonsPosMap:
                self.updateTab.emit()
            
            self.resetPickerState(False)
            
        '''
        Avoid triggering callbacks in a loop after selecting buttons within the UI
        '''  
        PickerView.setSelectionViaUi(True)
        if self.selectedButtons:
            self.buttonManager.updateToolBoxWidget(self.selectedButtons[-1]) # update toolbox
            if event.button() not in (QtCore.Qt.RightButton, QtCore.Qt.MiddleButton):
                selection.releaseAddSelection(self.allPickerButtons,
                                              self.nonMaxPickerButtons,
                                              self.MaxPickerButtons,
                                              self.selectedButtons)        
        else:
            cmds.select(cl=True)
        '''
        Permit callbacks when selecting nodes in Maya
        '''     
        PickerView.setSelectionViaUi(False) 
        
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.pickerViewEnum = PickerEnum.NONE
        
        # update sub menu
        self.pickerViewMenu._updateZOrder()
        super().mouseReleaseEvent(event)
    
        
    def resizeEvent(self, event):
        if not self.frameMoveTag:
            self.frameMoveTag = True
        super().resizeEvent(event)
        if self.midView:
            try:
                newOrigPos = QtCore.QPointF(self.width() / 2, self.height() / 2)
                self.buttonsParentPos = newOrigPos + self.viewOffset

                self.parentAxis.move(self.buttonsParentPos.toPoint())
        
                self.updateMidViewOffset()
                self.updateButtonsPos(updateScale=False)
            except Exception as e:
                om2.MGlobal.displayWarning(f'Error during resize: {e}')
 
 
    def wheelEvent(self, event):  
        offset = self.sceneScale * (0.2 if (
                                            event.angleDelta().x() if event.modifiers() & QtCore.Qt.AltModifier else event.angleDelta().y()
                                            ) > 0 else -0.2)

        self.frameMoveTag = True
        self.sceneScale = max(0.20, min(self.origScale + offset, 10.0))
        
        _scale = self.sceneScale / self.origScale
        
        pos = event.position() if int(cmds.about(version=True)) >= 2025 else event.pos()
        cx, cy = pos.x(), pos.y()
        
        self.buttonsParentPos = QtCore.QPointF(cx + _scale * (self.buttonsParentPos.x() - cx), 
                                               cy + _scale * (self.buttonsParentPos.y() - cy))
                                               
        self.parentAxis.move(self.buttonsParentPos.toPoint())
        self.parentAxis.resize(round(100 * self.sceneScale), round(100 * self.sceneScale)) 
        
        # move buttons
        self.updateButtonsPos(updateScale=True)
        if self.midView:
            self.updateMidViewOffset()
        self.origScale = self.sceneScale
      
        
    def _frameSelection(self):
        view.FrameSelectorHelper(self).frameSelection()
        
        '''
        There is a serious logical error in the view module
        when buttons are sufficiently small, they still appear maximized, causing them to fill the entire view area
        
        This is a relatively low-cost solution; although it is far from elegant, it can effectively resolve the issue
        '''
        if self.frameMoveTag:
            return
            
        mouseEvent = QtGui.QMouseEvent(
            QtCore.QEvent.MouseMove, 
            QtCore.QPointF(self.width() / 2, self.height() / 2), 
            QtCore.Qt.NoButton, 
            QtCore.Qt.NoButton, 
            QtCore.Qt.NoModifier  
        )
        # mousePressEvent
        self.setPickerState(pickerStates.ScaleViewState, mouseEvent)
        # mouseMoveEvent
        self.pickerState.handleMoveEvent(mouseEvent, self)
        # mouseReleaseEvent
        if self.midView:
            self.updateMidViewOffset()
        self.pickerState.handleReleaseEvent(mouseEvent, self)
        self.resetPickerState(True)

          
    def updateMirrorButtons(self):
        self.setCursor(QtGui.QCursor(QtGui.QPixmap(':cursor_trim.png')))      
        self.pickerViewEnum = PickerEnum.MIRROR_BUTTONS
        
    @signalEmitter    
    def _reverseSelection(self):
        self.undoStack.push(undo.ReverseSelectionCmd(self).initialize())
        
    
    # ------------------------------------------------------------------------------------------
    def updateMidViewOffset(self):
        self.viewOffset = self.buttonsParentPos - QtCore.QPointF(self.width() / 2, self.height() / 2)
        
        
    def autoCenterView(self, midMode=False):
        self.midView = midMode
        
        buttonGlobalPos = [pickerUtils.localToGlobal(button.localPos, self.buttonsParentPos, self.sceneScale) 
                           for button in self.allPickerButtons]          
        self.buttonsParentPos = QtCore.QPointF(self.width() / 2, self.height() / 2) if self.midView else QtCore.QPointF()
        self.parentAxis.move(self.buttonsParentPos.toPoint())
        for button, globalPos in zip(self.allPickerButtons, buttonGlobalPos):
            button.updateLocalPos(globalPos, self.buttonsParentPos, self.sceneScale)

        self.updateMidViewOffset()
        
    #------------------------------------------------------------------
    def toMaxView(self):     
        self.toOrigView(10.0)
        
        
    def toOrigView(self, sceneScale):
        self.sceneScale = self.origScale = sceneScale
        self.updateButtonsPos(updateScale=True)
        
    def getTabName(self) -> str:
        stackedWidget = self.parent()
        if not isinstance(stackedWidget, QtWidgets.QStackedWidget):
            return 'Null'
            
        index     = stackedWidget.indexOf(self)
        tabWidget = stackedWidget.parent()
        return tabWidget.tabText(index)
    
    # ------------------------------------------------------
    @staticmethod    
    def toUndoClass(className, pickerView, data):
        undoCls = getattr(undo, className, None)
        if undoCls is None:
            raise NameError(
                f"Class '{className}' not found in module '{undo.__name__}'. "
                "Please ensure the class name is correct and the module is properly imported.")
        undoInstance = undoCls(pickerView, True)
        undoInstance.set(data)
        return undoInstance
        
    def getUndoData(self, undoToFile=True):
        undoData = {'index'     : self.undoStack.index(),
                    'undoDatas' : []}
        if undoToFile:
            for index in range(self.undoStack.count()):
                undoCmd = self.undoStack.command(index)
                undoCmdData = undoCmd.get()
                undoData['undoDatas'].append(undoCmdData)
        return undoData
        
    
    def setUndoData(self, data):
        for undoData in data['undos']['undoDatas']:
            cmd = self.toUndoClass(undoData['undoClassName'], self, undoData)
            self.undoStack.push(cmd) 
        if data['undos']['undoDatas']:
            self.undoStack.setIndex(data['undos']['index'])

    # ------------------------------------------------------
    def get(self, undoToFile=True) -> dict:
        
        origSceneScale = self.sceneScale
        '''
        Maximizing the view to retrieve button data helps avoid precision loss
        While this may not be the most elegant approach
        it effectively resolves the issue of precision loss :)
        '''
        #self.toMaxView() 
        data = {'tabName'         : self.getTabName(),
                'origSceneScale'  : origSceneScale,
                'sceneScale'      : self.sceneScale,
                'buttonsParentPos': [self.buttonsParentPos.x(), self.buttonsParentPos.y()],
                'midView'         : self.midView,
                'viewOffset'      : [self.viewOffset.x(), self.viewOffset.y()],
                'namespace'       : self.namespace,
                'cacheSavePath'   : self.cacheSavePath}
              
        buttonsData = []
        for button in self.getAllPickerButtons():
            localPos  = button.localPos
            globalPos = pickerUtils.localToGlobal(localPos, self.buttonsParentPos, self.sceneScale)
            '''
            globalPos represents the button's center. Internally
            it's converted to the top-left corner position for proper alignment
            '''
            cenrerPos = button.cenrerPos2(globalPos, self.sceneScale)
            
            color     = button.color
            textColor = button.textColor
            
            buttonData= {'globalPos' : [cenrerPos.x(), cenrerPos.y()],
                         'localPos'  : [localPos.x(), localPos.y()],
                         'color'     : [color.red(), color.green(), color.blue()],
                         'scaleX'    : button.scaleX,
                         'scaleY'    : button.scaleY,
                         'textColor' : [textColor.red(), textColor.green(), textColor.blue()],
                         'labelText' : button.labelText,
                         'oldNodes'  : button.oldNodes,
                         'nodes'     : button.nodes,
                         'buttonId'  : button.buttonId}
            buttonsData.append(buttonData)
            
        data['buttons'] = buttonsData
        '''
        Revert to the view before zooming
        mainly to keep the original tab's view unchanged when duplicating a tab
        '''
        #self.toOrigView(origSceneScale)
        # get undo data
        data['undos'] = self.getUndoData(undoToFile)
        return data
    
        
    def set(self, data: dict):
        try:
            self.namespace = data['namespace']
            self.cacheSavePath = data['cacheSavePath']
            
            self.sceneScale = self.origScale = data['sceneScale']
            self.buttonsParentPos = QtCore.QPointF(*data['buttonsParentPos'])

            for buttonData in data['buttons']:
                '''
                Please refactor the logic for creating buttons!! 
                It no longer relies on buttonGlobalPos !!
                because the button's position will always be updated to the correct coordinates from the local position after creation!!!
                '''
                self.buttonGlobalPos = QtCore.QPointF(*buttonData['globalPos']) 
                
                _data = {'color'     : QtGui.QColor(*buttonData['color']),
                         'scaleX'    : buttonData['scaleX'],
                         'scaleY'    : buttonData['scaleY'],
                         'textColor' : QtGui.QColor(*buttonData['textColor']),
                         'labelText' : buttonData['labelText']} 
        
                button = self.createButton(buttonData['oldNodes'], _data, buttonData['buttonId'])
                button.updateButton(buttonData['nodes'], buttonData['oldNodes'])
                
                '''
                Due to the conversion from local coordinates to world coordinates and the subsequent calculation of the button's center point
                floating-point precision errors are inevitable. To ensure accuracy
                we update the button's previous local coordinates to guarantee correctness. 
                Although the code is far from elegant, it perfectly restores the button to its previous position
                '''
                button.localPos = QtCore.QPointF(*buttonData['localPos']) # update Local Pos
                
            self.viewOffset = QtCore.QPointF(*data['viewOffset'])
            self.midView    = data['midView']
            #self.pickerViewMenu.setViewMode(self.midView)
            if self.midView:
                self.resizeEvent(QtGui.QResizeEvent(self.size(), self.size()))
            
            # Restore to the original scale !!!
            #self.toOrigView(data['origSceneScale'])
            
            # set undo
            self.setUndoData(data)
            
        except Exception as e:
            raise ValueError(f'Error processing button data: {e}')
        self.updateButtonsPos(True)   