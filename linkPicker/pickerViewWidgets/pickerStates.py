import math
import maya.cmds as cmds

from abc import ABC, abstractmethod

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtCore
else:
    from PySide2 import QtCore

from . import pickerUtils, selection, undo


class MouseState(ABC):
    @abstractmethod
    def handlePressEvent(self, event, picker):
        pass
    @abstractmethod
    def handleMoveEvent(self, event, picker):
        pass
    @abstractmethod
    def handleReleaseEvent(self, event, picker):
        pass


class MriiroButtonsState(MouseState):
    
    def handlePressEvent(self, event, picker):
        picker.mirrorButtons(event.localPos().x())

    def handleMoveEvent(self, event, picker):     
        for button, pos in picker.mirrorCacheButtons.items():
            x = event.localPos().x() + pos[0] + (event.localPos().x() - pos[2])
            newPos = QtCore.QPointF(x, pos[1])
            
            button.move(newPos.toPoint())
            button.updateLocalPos(newPos, picker.buttonsParentPos, picker.sceneScale)

    def handleReleaseEvent(self, event, picker):
        mirrorButtons = picker.mirrorCacheButtons.keys()
        # add undo
        picker.undoStack.push(undo.MriiroButtonsCmd(picker).initialize())
        
        picker.selectedButtons.extend(mirrorButtons)
        picker.mirrorCacheButtons.clear()
        for button in picker.selectedButtons:
            button.setSelected(True)
            
            
class CreateButtonsState(MouseState):
    
    def handlePressEvent(self, event, picker):
        picker.buttonGlobalPos = event.localPos() # update button global pos
        picker.createMultipleButtons()
        picker.clearSelectedButtons()

    def handleMoveEvent(self, event, picker):     
        picker._updateButtonsDuringDrag(picker.buttonGlobalPos, event.localPos())

    def handleReleaseEvent(self, event, picker):
        # add undo
        picker.undoStack.push(undo.CreateMultipleButtonsCmd(picker).initialize())
        
        picker.selectedButtons.extend(picker.trackedButtons)
        picker.trackedButtons.clear()
        for button in picker.selectedButtons:
            button.setSelected(True)
            
            
class ShowMenuState(MouseState):
    def handlePressEvent(self, event, picker):
        picker.clickedButton = None
        for button in picker.allPickerButtons:
            if button.geometry().contains(event.pos()):
                picker.clickedButton = button
                
        if picker.clickedButton is not None and not picker.clickedButton.selected:
            picker.clearSelectedButtons()
            '''
            The purpose of adding to the button list is to treat right-clicking a button as an active state 
            This is particularly useful for buttons containing multiple nodes
            as it allows for adjusting the button's properties after being activated by a right-click
            '''
            picker.selectedButtons = [picker.clickedButton]
            picker.clickedButton.setSelected(True)
            picker.buttonManager.updateToolBoxWidget(picker.clickedButton) # update toolBox

        picker.buttonGlobalPos = event.localPos() # update button global pos
        picker.pickerViewMenu.exec_(event.globalPos())

    def handleMoveEvent(self, event, picker):     
        pass

    def handleReleaseEvent(self, event, picker):
        pass
            

class MoveViewState(MouseState):
    
    def handlePressEvent(self, event, picker):
        picker.setCursor(QtCore.Qt.SizeAllCursor)
        picker.clickedPos       = event.localPos()
        picker.clickedParentPos = picker.buttonsParentPos

    def handleMoveEvent(self, event, picker):     
        picker.frameMoveTag = True # update frameSelection
        picker.buttonsParentPos = picker.clickedParentPos + (event.localPos() - picker.clickedPos)
        picker.pickerBackground.updatePos()
        
        # move buttons
        picker.updateButtonsPos(updateScale=False)

    def handleReleaseEvent(self, event, picker):
        pass  
        
        
class ScaleViewState(MouseState):
    
    def handlePressEvent(self, event, picker):
        picker.setCursor(QtCore.Qt.SizeHorCursor)        
        picker.clickedPos       = event.localPos()
        picker.clickedParentPos = picker.buttonsParentPos

    def handleMoveEvent(self, event, picker):     
        picker.frameMoveTag = True # update frameSelection
        offset = event.localPos() - picker.clickedPos
        #picker.sceneScale = max(0.20, min(picker.origScale + (offset.x() + offset.y())  * (picker.ZoomDrag * 0.0003), 10.0)) # update scale
        picker.sceneScale = max(0.20, 
                            min(picker.origScale + (offset.x() + offset.y())  
                            * (picker.ZoomDrag / 200) ** math.e, 10.0)) # update scale
        
        _scale = picker.sceneScale / picker.origScale
        cx, cy = picker.clickedPos.x(), picker.clickedPos.y()
        picker.buttonsParentPos = QtCore.QPointF(cx + _scale * (picker.clickedParentPos.x() - cx), 
                                                 cy + _scale * (picker.clickedParentPos.y() - cy))
                                                   
        picker.pickerBackground.updatePos()
        picker.pickerBackground.updateScale()
        
        # move buttons
        picker.updateButtonsPos(updateScale=True)

    def handleReleaseEvent(self, event, picker):
        picker.origScale = picker.sceneScale
        

class SelectedState(MouseState):
    
    def handlePressEvent(self, event, picker):
        picker.startPos = event.pos()
        picker.selectionBox.setGeometry(QtCore.QRect(picker.startPos, QtCore.QSize())); picker.selectionBox.show() # show selectionBox
        
        picker.clickedButton = None
        for button in reversed(picker.allPickerButtons):
            if button.geometry().contains(picker.startPos):
                picker.clickedButton = button
                break
        
        if picker.clickedButton is not None:
            if picker.clickedButton.isCmdButton:
                picker.resetPickerState(False)
                '''
                If the script button is clicked, do not deselect on mouse release, as this is more user-friendly
                '''
                picker.clearSelectedNodes = True 
                return
                
            if event.modifiers() == QtCore.Qt.ShiftModifier:
                if picker.clickedButton not in picker.selectedButtons:
                    picker.selectedButtons.append(picker.clickedButton)
                    picker.clickedButton.setSelected(True)
                              
            elif event.modifiers() != QtCore.Qt.AltModifier:
                picker.clearSelectedButtons()
                picker.selectedButtons = [picker.clickedButton]
                picker.clickedButton.setSelected(True)
                
        else: 
            if not (event.modifiers() & (QtCore.Qt.ShiftModifier | QtCore.Qt.AltModifier)):
                picker.clearSelectedButtons()
                
        
    def handleMoveEvent(self, event, picker):  
        picker.endPos = event.pos()
        picker.clearMoveTag = True # update cleat tag
            
        picker.selectionBox.setGeometry(QtCore.QRect(picker.startPos, picker.endPos).normalized()) # update selectionBox
        picker.selectionBoxRect = QtCore.QRect(picker.startPos, picker.endPos)

        if not (event.modifiers() & QtCore.Qt.AltModifier):
            for button in picker.allPickerButtons:
                inSelection = picker.selectionBoxRect.intersects(button.geometry())

                if event.modifiers() == QtCore.Qt.ShiftModifier:
                    if inSelection and button not in picker.selectedButtons:
                        button.setSelected(True)
                        picker.selectedButtons.append(button)
                        picker.shiftAddButtons.append(button)
                    elif not inSelection and button in picker.shiftAddButtons:
                        button.setSelected(False)
                        picker.selectedButtons.remove(button)
                        picker.shiftAddButtons.remove(button)
                elif inSelection:
                    '''
                    If the mouse click position is on a button
                    check the Z-order of the clicked button and all selected buttons within the selection box to prevent selection from passing through
                    '''
                    if picker.clickedButton is not None and picker.clickedButton.geometry().contains(picker.selectionBoxRect) and (
                        picker.allPickerButtons.index(picker.clickedButton) > picker.allPickerButtons.index(button)):

                        picker.clearSelectedButtons()
                        picker.clickedButton.setSelected(True)
                        picker.selectedButtons.append(picker.clickedButton)      
                        
                    elif button not in picker.selectedButtons:
                        button.setSelected(True)
                        picker.selectedButtons.append(button)
    
                else:
                    button.setSelected(False)
                    if button in picker.selectedButtons:
                        picker.selectedButtons.remove(button)
                        
  

    def handleReleaseEvent(self, event, picker):
        picker.shiftAddButtons.clear()
        picker.selectionBox.hide() # hide selectionBox
        
        # clear selected button
        if picker.clickedButton is not None:
            if event.modifiers() == QtCore.Qt.AltModifier and event.button() != QtCore.Qt.MouseButton.RightButton:
                picker.clickedButton.setSelected(False)
                if picker.clickedButton in picker.selectedButtons:
                    picker.selectedButtons.remove(picker.clickedButton)
                    
                selection.releaseSubSelection(picker.clickedButton, picker.selectedButtons)

                  
        if picker.clearMoveTag:
            '''
            Perform a second check. If the button is inside or intersects with the box, it will be deselected!!
            '''  
            if event.modifiers() == QtCore.Qt.AltModifier:
                for button in picker.allPickerButtons:
                    if not picker.selectionBoxRect.intersects(button.geometry()):# and button in picker.selectedButtons:
                        continue
                    button.setSelected(False)
                    if button in picker.selectedButtons:
                        picker.selectedButtons.remove(button)
                        
                    selection.releaseSubSelection(button, picker.selectedButtons)

            picker.clearMoveTag = False
            
            
class MoveButtonsState(MouseState):

    def handlePressEvent(self, event, picker):
        localPos = event.localPos()       
        '''
        Get the last button that contains the mouse position.
        This ensures that when multiple buttons overlap, the topmost button is selected
        instead of always selecting the bottommost button
        # oneButton = next((but for but in picker.allPickerButtons if but.geometry().contains(localPos.toPoint())), None)
        ''' 
        _oneButton = [button for button in picker.allPickerButtons if button.geometry().contains(localPos.toPoint())]
        picker.clickedButton  = _oneButton[-1] if _oneButton else None
        
        # undo cache list
        picker.undoMoveButtonsPosMap = {}
        
        if picker.clickedButton is not None and picker.clickedButton not in picker.selectedButtons:
            picker.clickedButton.setSelected(True)
            '''
            Convert from the button's local position to world position to avoid errors caused by floating-point precision
            '''
            globalPos = pickerUtils.localToGlobal(picker.clickedButton.localPos, picker.buttonsParentPos, picker.sceneScale)
            picker.buttonsTranslateOffset[picker.clickedButton] = globalPos - localPos
            
            # to undo cache list
            _localPos = picker.clickedButton.localPos
            picker.undoMoveButtonsPosMap[picker.clickedButton.buttonId] = {'old':[_localPos.x(), _localPos.y()]}
            
        elif picker.selectedButtons and any(button.geometry().contains(localPos.toPoint()) for button in picker.selectedButtons):
            for button in picker.selectedButtons:
                '''
                Convert from the button's local position to world position to avoid errors caused by floating-point precision
                '''
                globalPos = pickerUtils.localToGlobal(button.localPos, picker.buttonsParentPos, picker.sceneScale)
                picker.buttonsTranslateOffset[button] = globalPos - localPos
                
                # to undo cache list
                _localPos = button.localPos
                picker.undoMoveButtonsPosMap[button.buttonId] = {'old':[_localPos.x(), _localPos.y()]}
        else:
            picker.clearSelectedButtons()


    def handleMoveEvent(self, event, picker):
        for button, offset in picker.buttonsTranslateOffset.items():
            globalPos = event.localPos() + offset
            button.move(globalPos.toPoint())
            button.updateLocalPos(globalPos, picker.buttonsParentPos, picker.sceneScale)
            
            
    def handleReleaseEvent(self, event, picker):
        # to undo cache list
        for button in picker.buttonsTranslateOffset:
            _localPos = button.localPos
            picker.undoMoveButtonsPosMap[button.buttonId]['new'] = [_localPos.x(), _localPos.y()]
        
        picker.buttonsTranslateOffset.clear()
            
        if picker.clickedButton is not None and picker.clickedButton not in picker.selectedButtons:
            picker.clickedButton.setSelected(False)
        
        # add undo
        if picker.undoMoveButtonsPosMap:
            picker.undoStack.push(undo.MoveButtonCmd(picker).initialize())


