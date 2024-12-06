import uuid
import maya.cmds as cmds

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
    UndoStack   = QtGui.QUndoStack
    UndoCommand = QtGui.QUndoCommand
else:
    from PySide2 import QtWidgets, QtCore, QtGui
    UndoStack   = QtWidgets.QUndoStack
    UndoCommand = QtWidgets.QUndoCommand

from . import align, pickerUtils, mirror, zorder


class PickerViewUndoStackBase(UndoStack):
    def __init__(self, parent=None, 
                       enableUndo: 'undo switch'=True, 
                       queue:      'undo depth' =20):
        super().__init__(parent)
        self.enableUndo   = enableUndo
        
        self.oldUndoQueue = queue # undo length
        
        self.picker = parent
        self.cacheAllCmd = {'index'    : -1, 
                            'undoDatas': []}
                            
        self.setUndoLimit(queue)
           
           
    def push(self, command):
        if self.enableUndo:
            super().push(command)  
        else:
            command.redo() 
            
            
    def setUndoLimit(self, undoQueue):
        if self.oldUndoQueue != undoQueue:
            self.oldUndoQueue = undoQueue
            self._getAllCmdData()
            self.clear()
            
        super().setUndoLimit(undoQueue)
        
        self._setCmdData()

        
    def _getAllCmdData(self):
        self._resetCache()
        self.cacheAllCmd['index'] = self.index()
        for index in range(self.count()):
            self.cacheAllCmd['undoDatas'].append(self.command(index).get())
            

    def _setCmdData(self):
        if not self.cacheAllCmd['undoDatas']:
            return

        cacheCmdCount = len(self.cacheAllCmd['undoDatas'])
        oldIndex      = self.cacheAllCmd['index']
        
        newCmd = []
        if cacheCmdCount < self.oldUndoQueue:
            newCmd   = self.cacheAllCmd['undoDatas']
            newIndex = oldIndex
        else:
            '''
            Currently, only the case where the new undo length is less than the previous undo index has been handled!!
            '''
            if oldIndex > self.oldUndoQueue:
                newCmd = self.cacheAllCmd['undoDatas'][self.oldUndoQueue : oldIndex]
                newIndex = oldIndex
            # elif ...:
            #     pass
                
        if newCmd:
            for undoData in newCmd:
                undoCls = globals().get(undoData['undoClassName'])
                undoInstance = undoCls(self.picker, True)
                undoInstance.set(undoData)
                self.push(undoInstance) 
            self.setIndex(newIndex)
 
        self._resetCache()

            
    def _resetCache(self):
        self.cacheAllCmd['index'] = -1
        self.cacheAllCmd['undoDatas'].clear()
        

        
class PickerViewUndoBase(UndoCommand):
    
    def __init__(self, skipRedo: bool = False):
        super().__init__()
        self.skipRedo = skipRedo
        
    def initialize(self):
        pass
        
    def undo(self):
        pass
        
    def redo(self):
        if self.skipRedo:
            self.skipRedo = False
            return False
        return True
        
    def get(self):
        pass
        
    def set(self, data=None):
        pass
        

class BaseAlignCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.pickerView = pickerView
        
    
    def initialize(self):
        self.buttonIds     = [button.buttonId for button in self.pickerView.selectedButtons]
        self.buttonsPosMap = {}
        for button in self.pickerView.selectedButtons:
            localPos = button.localPos
            self.buttonsPosMap[button.buttonId] = [localPos.x(), localPos.y()]        
        return self

    def undo(self):
        buttonsParentPos = self.pickerView.buttonsParentPos
        sceneScale       = self.pickerView.sceneScale
        
        buttons = getButtonsByCacheButtonsID(self.buttonIds, self.pickerView)
        
        for button in buttons:
            cachePos = self.buttonsPosMap[button.buttonId]
            localPos = QtCore.QPointF(cachePos[0], cachePos[1])
            globalPos = pickerUtils.localToGlobal(localPos, buttonsParentPos, sceneScale)
            button.move(globalPos.toPoint())
            button.localPos = localPos
 
            
    def redo(self):
        if not super().redo():
            return
        selectedButtons = getButtonsByCacheButtonsID(self.buttonIds, self.pickerView)
        self.run(selectedButtons, self.pickerView.buttonsParentPos, self.pickerView.sceneScale)
        
    def run(self, selectedButtons, buttonsParentPos, sceneScale):
        pass
            
    def get(self):
        return {'undoClassName' : self.__class__.__name__,
                'buttonIds'     : self.buttonIds,
                'buttonsPosMap' : self.buttonsPosMap}
    
    def set(self, data):
        self.buttonIds      = data['buttonIds']
        self.buttonsPosMap  = data['buttonsPosMap']
  
  
class AlignHorizontalCmd(BaseAlignCmd):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Align Horizontally')


    def run(self, selectedButtons, buttonsParentPos, sceneScale):
        align.alignButtons(selectedButtons, buttonsParentPos, sceneScale, 'horizontal')


class AlignVerticalCmd(BaseAlignCmd):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Align Vertically')


    def run(self, selectedButtons, buttonsParentPos, sceneScale):
        align.alignButtons(selectedButtons, buttonsParentPos, sceneScale, 'vertical')


class DistributeEvenlyCmd(BaseAlignCmd):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Distribute Evenly')


    def run(self, selectedButtons, buttonsParentPos, sceneScale):
        align.distributeButtonsEvenly(selectedButtons, buttonsParentPos, sceneScale)
        

class ReverseSelectionCmd(BaseAlignCmd):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Reverse Selection')


    def run(self, selectedButtons, buttonsParentPos, sceneScale):
        mirror.reversePosition(selectedButtons, buttonsParentPos, sceneScale)
       
       
       

class CreateButtonsCmd(PickerViewUndoBase):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.pickerView = pickerView


    def initialize(self):
        self.buttonIds   = []
        self.buttonDatas = []
        return self


    def undo(self):
        for buttonId in self.buttonIds:
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.deleteLater()
                self.pickerView._updateButtonsCache(button) # update cache
            
      
    def redo(self):
        if not super().redo():
            return

        if not self.buttonDatas:
            self.buttonDatas = getSelectedButtonsInfo(self.pickerView, self.buttonIds) 
        else:
            buttons = [createButtonByInfo(buttonData, self.pickerView) for buttonData in self.buttonDatas]
            self.pickerView.updateButtonsPos(True, buttons) # update button pos
            
    def get(self):
        return {'undoClassName' : self.__class__.__name__,
                'buttonIds'     : self.buttonIds,
                'buttonDatas'   : self.buttonDatas}
    
    def set(self, data):
        self.buttonIds    = data['buttonIds']
        self.buttonDatas  = data['buttonDatas']



class CreateMultipleButtonsCmd(CreateButtonsCmd):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Create Multipl Buttons')
    
    def initialize(self):
        self.buttonIds   = [button.buttonId for button in self.pickerView.trackedButtons]
        self.buttonDatas = []
        return self
        
    def undo(self):
        super().undo()
        
    def redo(self):
        super().redo()            
            
            
class MriiroButtonsCmd(CreateButtonsCmd):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Mirror Buttons')
        
    def initialize(self):
        self.buttonIds   = [button.buttonId for button in self.pickerView.mirrorCacheButtons.keys()]
        self.buttonDatas = []
        return self
        
    def undo(self):
        super().undo()
        
    def redo(self):
        super().redo()
        

class MoveButtonCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Move Button(s)')
        self.pickerView = pickerView
            
    def initialize(self):
        self.MoveButtonsPosMap = self.pickerView.undoMoveButtonsPosMap
        self.initUndo          = True
        return self
           
    def _moveButtons(self, typ=''):
        newMoveButtonsMap = {}
        for button in self.pickerView.allPickerButtons:
            if button.buttonId in self.MoveButtonsPosMap:
                newMoveButtonsMap[button] = self.MoveButtonsPosMap[button.buttonId]
                
        buttonsParentPos = self.pickerView.buttonsParentPos
        sceneScale       = self.pickerView.sceneScale
        for button, pos in newMoveButtonsMap.items():
            _pos = pos[typ]
            globalPos = pickerUtils.localToGlobal(QtCore.QPointF(*_pos), buttonsParentPos, sceneScale)
            button.move(globalPos.toPoint())
            button.updateLocalPos(globalPos, buttonsParentPos, sceneScale)
            
    def undo(self):
        self._moveButtons('old')
                
    def redo(self):
        if not super().redo():
            return
        if self.initUndo:
            self.initUndo = False
            return  
        self._moveButtons('new')
        
    def get(self):
        return {'undoClassName'     : self.__class__.__name__,
                'MoveButtonsPosMap' : self.MoveButtonsPosMap,
                'initUndo'          : self.initUndo}
    
    def set(self, data):
        self.MoveButtonsPosMap = data['MoveButtonsPosMap']
        self.initUndo          = data['initUndo']
        
         
        
class UpdateButtonCmd(PickerViewUndoBase):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update Button')
        self.pickerView = pickerView
        
    def initialize(self):
        self.buttonId       = self.pickerView.clickedButton.buttonId
        self.buttonNodes    = self.pickerView.clickedButton.nodes
        self.buttonOldNodes = self.pickerView.clickedButton.oldNodes
        self.nweNodes       = self.pickerView.newNodes # maya nodes by menu
        return self
    
    def _update(self, nodes, oldNodes=None):
        if self.buttonId in self.pickerView.allPickerButtonsIdMap:
            updateButton = self.pickerView.allPickerButtonsIdMap[self.buttonId]
            updateButton.updateButton(nodes, oldNodes)
            self.pickerView.updateButtonList(updateButton)
            updateButton.update()
    
    def undo(self):
        self._update(self.buttonNodes, self.buttonOldNodes)
      
    def redo(self):
        if not super().redo():
            return
        self._update(self.nweNodes, None)
        
    def get(self):
        return {'undoClassName'  : self.__class__.__name__,
                'buttonId'       : self.buttonId,
                'buttonNodes'    : self.buttonNodes,
                'buttonOldNodes' : self.buttonOldNodes,
                'nweNodes'       : self.nweNodes}
    
    def set(self, data):
        self.buttonId       = data['buttonId']
        self.buttonNodes    = data['buttonNodes']
        self.buttonOldNodes = data['buttonOldNodes']
        self.nweNodes       = data['nweNodes']
        
        
# ---------------------------------------------------------------------------
def getButtonData(button):
    localPos  = button.localPos
    color     = button.color
    textColor = button.textColor
    buttonData = {'localPos'    : [localPos.x(), localPos.y()],
                  'color'       : [color.red(), color.green(), color.blue()],
                  'scaleX'      : button.scaleX,
                  'scaleY'      : button.scaleY,
                  'textColor'   : [textColor.red(), textColor.green(), textColor.blue()],
                  'labelText'   : button.labelText,
                  'oldNodes'    : button.oldNodes,
                  'nodes'       : button.nodes,
                  'buttonId'    : button.buttonId,
                  'code'        : button.code}
    return buttonData
    
    
def getSelectedButtonsInfo(pickerView, buttonsIds):
    
    buttonsData = []
    for buttonId in buttonsIds:
        if buttonId in pickerView.allPickerButtonsIdMap:
            button     = pickerView.allPickerButtonsIdMap[buttonId]
            buttonData = getButtonData(button)
            buttonsData.append(buttonData)
    return buttonsData
    
    
def createButtonByInfo(buttonData, pickerView):
    localPos  = QtCore.QPointF(*buttonData['localPos'])
    globalPos = pickerUtils.localToGlobal(localPos, pickerView.buttonsParentPos, pickerView.sceneScale)
    cenrerPos = globalPos + QtCore.QPointF(buttonData['scaleX'] * pickerView.sceneScale / 2, buttonData['scaleY'] * pickerView.sceneScale / 2)  

    pickerView.buttonGlobalPos = cenrerPos
    _data = {'color'     : QtGui.QColor(*buttonData['color']),
             'scaleX'    : buttonData['scaleX'],
             'scaleY'    : buttonData['scaleY'],
             'textColor' : QtGui.QColor(*buttonData['textColor']),
             'labelText' : buttonData['labelText']} 

    button = pickerView.createButton(buttonData['oldNodes'], _data, buttonData['buttonId'], buttonData['code'])
    button.updateButton(buttonData['nodes'], buttonData['oldNodes'])
    
    '''
    Due to the conversion from local coordinates to world coordinates and the subsequent calculation of the button's center point
    floating-point precision errors are inevitable. To ensure accuracy
    we update the button's previous local coordinates to guarantee correctness. 
    Although the code is far from elegant, it perfectly restores the button to its previous position
    '''
    button.localPos = localPos # update localPos
    return button
    
def updateButtonsZorder(buttonIds, buttonsMap):
    for buttonId in buttonIds:
        if buttonId in buttonsMap:
            button = buttonsMap[buttonId]
            button.raise_()


def getButtonsByCacheButtonsID(buttonsId, pickerView):
    buttons = [pickerView.allPickerButtonsIdMap[buttonId] 
               for buttonId in buttonsId
               if buttonId in pickerView.allPickerButtonsIdMap]
    return buttons

        

class DeleteButtonCmd(PickerViewUndoBase):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Delete Button(s)')
        self.pickerView  = pickerView      
  
    
    def initialize(self):
        self.buttonsId   = [button.buttonId for button in self.pickerView.selectedButtons]
        self.buttonDatas = []
        # cache Z Order
        self.AllButtonZOrder = [button.buttonId for button in self.pickerView.allPickerButtons]
        return self
        
        
    def undo(self):
        
        buttons = [createButtonByInfo(buttonData, self.pickerView) for buttonData in self.buttonDatas]
        self.pickerView.updateButtonsPos(True, buttons) # update button pos
            
        # update z orde !!    
        updateButtonsZorder(self.AllButtonZOrder, self.pickerView.allPickerButtonsIdMap)   
        # update cache buttons zorder
        self.pickerView.allPickerButtons = self.pickerView.getAllPickerButtons() 
        
         
    def redo(self):
        if not super().redo():
            return
        if not self.buttonDatas: 
            self.buttonDatas = getSelectedButtonsInfo(self.pickerView, self.buttonsId) 
        for buttonId in self.buttonsId:
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.deleteLater()
                self.pickerView._updateButtonsCache(button) # update cache
                
        
    def get(self):
        return {'undoClassName'  : self.__class__.__name__,
                'buttonsId'      : self.buttonsId,
                'buttonDatas'    : self.buttonDatas,
                'AllButtonZOrder': self.AllButtonZOrder}
    
    def set(self, data):
        self.buttonsId       = data['buttonsId']
        self.buttonDatas     = data['buttonDatas']
        self.AllButtonZOrder = data['AllButtonZOrder']



class CreateSingleButtonCmd(PickerViewUndoBase):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Create Single Button')
        self.pickerView = pickerView

    def initialize(self):
        self.buttonData = {}
        return self

    def undo(self):
        buttonId = self.buttonData['buttonId']
        if buttonId in self.pickerView.allPickerButtonsIdMap:
            button = self.pickerView.allPickerButtonsIdMap[buttonId]
            
            button.deleteLater()
            self.pickerView._updateButtonsCache(button) # update cache
     
    def redo(self):
        if not super().redo():
            return
            
        if not self.buttonData:
            nodeList  = self.pickerView.pickerViewMenu.getSelectedNodes()
            newButton = self.pickerView.createButton(nodeList)
            newButton.setSelected(True)
            self.pickerView.selectedButtons.append(newButton) 

            self.buttonData = getButtonData(newButton)
        else:
            button = createButtonByInfo(self.buttonData, self.pickerView)       
            self.pickerView.updateButtonsPos(True, [button])    
            
    def get(self):
        return {'undoClassName': self.__class__.__name__,
                'buttonData'    : self.buttonData}
    
    def set(self, data):
        self.buttonData = data['buttonData']
        
       
   
class ZOrderBaseCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.pickerView = pickerView      
        
    def initialize(self):
        self.buttonsId       = [button.buttonId for button in self.pickerView.selectedButtons]
        self.allButtonsId    = [button.buttonId for button in self.pickerView.allPickerButtons]
        # cache Z Order
        self.AllButtonZOrder = [button.buttonId for button in self.pickerView.allPickerButtons]  
        return self
          
    def undo(self):
        # update z orde !!    
        updateButtonsZorder(self.AllButtonZOrder, self.pickerView.allPickerButtonsIdMap)   
        self.pickerView.pickerBackground.lower()
        # update buttons zorder
        self.pickerView.allPickerButtons = self.pickerView.getAllPickerButtons() 
        
        
    def redo(self):
        if not super().redo():
            return
        buttons = getButtonsByCacheButtonsID(self.buttonsId, self.pickerView)

        self.run(buttons)
        self.pickerView.pickerBackground.lower()
        self.pickerView.allPickerButtons = self.pickerView.getAllPickerButtons()  # update buttons zorder
        
    def run(self, buttons):
        pass
        
    def get(self):
        return {'undoClassName'   : self.__class__.__name__,
                'buttonsId'       : self.buttonsId,
                'allButtonsId'    : self.allButtonsId,
                'AllButtonZOrder' : self.AllButtonZOrder}
    
    def set(self, data):
        self.buttonsId       = data['buttonsId']
        self.allButtonsId    = data['allButtonsId']
        self.AllButtonZOrder = data['AllButtonZOrder']


class RaiseCmd(ZOrderBaseCmd):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Raise Selected Buttons')


    def run(self, buttons):
        zorder.raiseSelectedButtons(buttons)
        

class LowerCmd(ZOrderBaseCmd):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Lower Selected Buttons')


    def run(self, buttons):
        zorder.lowerSelectedButtons(buttons)
        
        
class UpCmd(ZOrderBaseCmd):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Move Selected Buttons Up')
        
    def run(self, buttons):
        allButton = getButtonsByCacheButtonsID(self.allButtonsId, self.pickerView)
        zorder.moveSelectedButtonsUp(buttons, allButton)
        

class DownCmd(ZOrderBaseCmd):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(pickerView, skipRedo)
        self.setText('Move Selected Buttons Down')
 
    def run(self, buttons):
        allButton = getButtonsByCacheButtonsID(self.allButtonsId, self.pickerView)
        zorder.moveSelectedButtonsDown(buttons, allButton)
        
        
  
class UpdateButtonsColorCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update Color')
        self.pickerView = pickerView      
        
    def initialize(self, newColor):
        self.newColor = [newColor.red(), newColor.green(), newColor.blue()]
        self.oldSelectedButtonsColor = {}
        for button in self.pickerView.selectedButtons:
            color = button.color
            self.oldSelectedButtonsColor[button.buttonId] = [color.red(), color.green(), color.blue()]
        
        return self
          
    def undo(self):
        for buttonId, color in self.oldSelectedButtonsColor.items():
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.updateColor(QtGui.QColor(*color))
        
    def redo(self):
        if not super().redo():
            return

        buttons = getButtonsByCacheButtonsID(list(self.oldSelectedButtonsColor.keys()), self.pickerView)
        for button in buttons:
            button.updateColor(QtGui.QColor(*self.newColor))
            

    def get(self):
        return {'undoClassName'          : self.__class__.__name__,
                'newColor'               : self.newColor,
                'oldSelectedButtonsColor': self.oldSelectedButtonsColor}
    
    def set(self, data):
        self.oldSelectedButtonsColor = data['oldSelectedButtonsColor']
        self.newColor                = data['newColor']
        

class UpdateButtonsTextColorCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update Text Color')
        self.pickerView = pickerView      
        
    def initialize(self, newColor):
        self.newColor = [newColor.red(), newColor.green(), newColor.blue()]
        self.oldSelectedButtonsTextColor = {}
        for button in self.pickerView.selectedButtons:
            color = button.textColor
            self.oldSelectedButtonsTextColor[button.buttonId] = [color.red(), color.green(), color.blue()]
        
        return self
          
    def undo(self):
        for buttonId, color in self.oldSelectedButtonsTextColor.items():
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.updateLabelColor(QtGui.QColor(*color))
        
    def redo(self):
        if not super().redo():
            return

        buttons = getButtonsByCacheButtonsID(list(self.oldSelectedButtonsTextColor.keys()), self.pickerView)
        for button in buttons:
            button.updateLabelColor(QtGui.QColor(*self.newColor))
            

    def get(self):
        return {'undoClassName'              : self.__class__.__name__,
                'newColor'                   : self.newColor,
                'oldSelectedButtonsTextColor': self.oldSelectedButtonsTextColor}
    
    def set(self, data):
        self.oldSelectedButtonsTextColor = data['oldSelectedButtonsTextColor']
        self.newColor                    = data['newColor']
        
     
class UpdateButtonsTextCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update Text')
        self.pickerView = pickerView      
        
    def initialize(self, newText):
        self.newText = newText
        self.oldSelectedButtonsText = {}
        for button in self.pickerView.selectedButtons:
            self.oldSelectedButtonsText[button.buttonId] = button.labelText
        
        return self
          
    def undo(self):
        for buttonId, oldText in self.oldSelectedButtonsText.items():
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.updateLabelText(oldText, self.pickerView.sceneScale)
        
    def redo(self):
        if not super().redo():
            return

        buttons = getButtonsByCacheButtonsID(list(self.oldSelectedButtonsText.keys()), self.pickerView)
        for button in buttons:
            button.updateLabelText(self.newText, self.pickerView.sceneScale)
            

    def get(self):
        return {'undoClassName'         : self.__class__.__name__,
                'newText'               : self.newText,
                'oldSelectedButtonsText': self.oldSelectedButtonsText}
    
    def set(self, data):
        self.oldSelectedButtonsText = data['oldSelectedButtonsText']
        self.newText                = data['newText']
            
        
class UpdateSelectedButtonsScaleCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update Scale')
        self.pickerView = pickerView      
        
    def initialize(self, scaleValue):
        self.scaleValue              = scaleValue
        self.oldSelectedButtonsScale = {}
        for button in self.pickerView.selectedButtons:
            self.oldSelectedButtonsScale[button.buttonId] = button.scaleX
        
        return self
          
    def undo(self):
        for buttonId, oldScale in self.oldSelectedButtonsScale.items():
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.updateScaleX(oldScale, self.pickerView.sceneScale, self.pickerView.buttonsParentPos)
                button.updateScaleY(oldScale, self.pickerView.sceneScale, self.pickerView.buttonsParentPos)
                button.scaleText(self.pickerView.sceneScale)
        
    def redo(self):
        if not super().redo():
            return

        buttons = getButtonsByCacheButtonsID(list(self.oldSelectedButtonsScale.keys()), self.pickerView)
        for button in buttons:
            button.updateScaleX(button.scaleX + self.scaleValue, self.pickerView.sceneScale, self.pickerView.buttonsParentPos)
            button.updateScaleY(button.scaleY + self.scaleValue, self.pickerView.sceneScale, self.pickerView.buttonsParentPos)
            button.scaleText(self.pickerView.sceneScale)
            

    def get(self):
        return {'undoClassName'          : self.__class__.__name__,
                'scaleValue'             : self.scaleValue,
                'oldSelectedButtonsScale': self.oldSelectedButtonsScale}
    
    def set(self, data):
        self.oldSelectedButtonsScale   = data['oldSelectedButtonsScale']
        self.scaleValue                = data['scaleValue']
        
        
        

class UpdateButtonsScaleXCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update ScaleX')
        self.pickerView = pickerView  
           
    def initialize(self, newScaleValue):
        self.cacheOldButtonsScaleX = dict(self.pickerView.cacheOldButtonsScaleX)
        self.newScaleValue         = newScaleValue
        self.initUndo              = True  
        return self
          
    def undo(self):

        for buttonId, oldScaleX in self.cacheOldButtonsScaleX.items():
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.updateScaleX(oldScaleX[0], self.pickerView.sceneScale, self.pickerView.buttonsParentPos)
                button.localPos = QtCore.QPointF(*oldScaleX[1])
        if self.pickerView.selectedButtons:
            self.pickerView.buttonManager.updateToolBoxWidget(self.pickerView.selectedButtons[-1])
                
    def redo(self):
        if not super().redo():
            return

        if self.initUndo:
            self.initUndo = False
            return  

        for buttonId, oldScaleX in self.cacheOldButtonsScaleX.items():
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.updateScaleX(self.newScaleValue, self.pickerView.sceneScale, self.pickerView.buttonsParentPos)
                button.localPos = QtCore.QPointF(*oldScaleX[2])
            
            
        if self.pickerView.selectedButtons:
            self.pickerView.buttonManager.updateToolBoxWidget(self.pickerView.selectedButtons[-1])
            

    def get(self):
        return {'undoClassName'          : self.__class__.__name__,
                'cacheOldButtonsScaleX'  : self.cacheOldButtonsScaleX,
                'newScaleValue'          : self.newScaleValue,
                'initUndo'               : self.initUndo}
    
    def set(self, data):
        self.cacheOldButtonsScaleX = data['cacheOldButtonsScaleX']
        self.newScaleValue         = data['newScaleValue']
        self.initUndo              = data['initUndo']



class UpdateButtonsScaleYCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update ScaleY')
        self.pickerView = pickerView  
           
    def initialize(self, newScaleValue):
        self.cacheOldButtonsScaleY = dict(self.pickerView.cacheOldButtonsScaleY)
        self.newScaleValue         = newScaleValue
        self.initUndo              = True  
        return self
          
    def undo(self):

        for buttonId, oldScaleY in self.cacheOldButtonsScaleY.items():
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.updateScaleY(oldScaleY[0], self.pickerView.sceneScale, self.pickerView.buttonsParentPos)
                button.localPos = QtCore.QPointF(*oldScaleY[1])
                button.scaleText(self.pickerView.sceneScale)
        if self.pickerView.selectedButtons:
            self.pickerView.buttonManager.updateToolBoxWidget(self.pickerView.selectedButtons[-1])
                
    def redo(self):
        if not super().redo():
            return

        if self.initUndo:
            self.initUndo = False
            return  

        for buttonId, oldScaleY in self.cacheOldButtonsScaleY.items():
            if buttonId in self.pickerView.allPickerButtonsIdMap:
                button = self.pickerView.allPickerButtonsIdMap[buttonId]
                button.updateScaleY(self.newScaleValue, self.pickerView.sceneScale, self.pickerView.buttonsParentPos)
                button.localPos = QtCore.QPointF(*oldScaleY[2])
                button.scaleText(self.pickerView.sceneScale)
            
        if self.pickerView.selectedButtons:
            self.pickerView.buttonManager.updateToolBoxWidget(self.pickerView.selectedButtons[-1])



    def get(self):
        return {'undoClassName'          : self.__class__.__name__,
                'cacheOldButtonsScaleY'  : self.cacheOldButtonsScaleY,
                'newScaleValue'          : self.newScaleValue,
                'initUndo'               : self.initUndo}
    
    def set(self, data):
        self.cacheOldButtonsScaleY = data['cacheOldButtonsScaleY']
        self.newScaleValue         = data['newScaleValue']
        self.initUndo              = data['initUndo']
        
        

class UpdateButtonsNamespaceCmd(PickerViewUndoBase):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update Namespace')
        self.pickerView = pickerView
        
        
    def initialize(self, NewNamespace):
        self.initUndo           = True
        self.pickerOldNamespace = self.pickerView.namespace
        self.pickerNewNamespace = NewNamespace
        
        self.buttonsInfo = {}
        for button in self.pickerView.allPickerButtons:
            nodesData = {'oldNodes':button.oldNodes,
                         'nodes'   :button.nodes}
            self.buttonsInfo[button.buttonId] = nodesData   
        return self
    

    
    def undo(self):
        self.pickerView.namespace = self.pickerOldNamespace

        for buttonId, info in self.buttonsInfo.items():
            if buttonId not in self.pickerView.allPickerButtonsIdMap:
                continue
            button = self.pickerView.allPickerButtonsIdMap[buttonId]
            button.updateButton(info['nodes'], info['oldNodes'])
        # update namespace widget
        self.pickerView.mainUI._selectNamespace(self.pickerOldNamespace)
      
    def redo(self):
        if not super().redo():
            return
        
        self.pickerView.namespace = self.pickerNewNamespace
        buttons = getButtonsByCacheButtonsID(list(self.buttonsInfo.keys()), self.pickerView)
        for button in buttons:
            button.updateNamespace(self.pickerNewNamespace)
        
        '''
        The namespaceItem has already been manually selected during the first namespace switch; it should only be invoked on the next redo
        '''
        if self.initUndo:
            self.initUndo = False
            return 
        self.pickerView.mainUI._selectNamespace(self.pickerNewNamespace)
        
        
    def get(self):
        return {'undoClassName'     : self.__class__.__name__,
                'pickerOldNamespace': self.pickerOldNamespace,
                'pickerNewNamespace': self.pickerNewNamespace,
                'buttonsInfo'       : self.buttonsInfo,
                'initUndo'          : self.initUndo}
    
    
    def set(self, data):
        self.pickerOldNamespace = data['pickerOldNamespace']
        self.pickerNewNamespace = data['pickerNewNamespace']
        self.buttonsInfo        = data['buttonsInfo']
        self.initUndo           = data['initUndo']



class ImageUpdateCmd(PickerViewUndoBase):
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Set Background')
        self.pickerView = pickerView      
        
    def initialize(self, data):
        self.oldData  = data['old']
        self.nweData  = data['new']
        self.initUndo = True
        return self
          
    def undo(self):
        self.pickerView.pickerBackground.set(self.oldData)
        
    def redo(self):
        if not super().redo():
            return
        if self.initUndo:
            self.initUndo = False
            return  
        self.pickerView.pickerBackground.set(self.nweData)
        
        
    def get(self):
        return {'undoClassName' : self.__class__.__name__,
                'old'           : self.oldData,
                'new'           : self.nweData,
                'initUndo'      : self.initUndo}
    
    def set(self, data):
        self.oldData  = data['old']
        self.nweData  = data['new']
        self.initUndo = data['initUndo']


class CreateCommandButtonCmd(PickerViewUndoBase):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Create Command Button')
        self.pickerView = pickerView

    def initialize(self, codeData: dict):
        self.codeData   = codeData
        self.buttonData = {}
        return self

    def undo(self):
        buttonId = self.buttonData['buttonId']
        if buttonId in self.pickerView.allPickerButtonsIdMap:
            button = self.pickerView.allPickerButtonsIdMap[buttonId]
            
            button.deleteLater()
            self.pickerView._updateButtonsCache(button) # update cache
     
    def redo(self):
        if not super().redo():
            return
            
        if not self.buttonData:
            cmdButton = self.pickerView.createButton(nodeList=[str(uuid.uuid4())], code=dict(self.codeData))
            cmdButton.updateLabelText(self.codeData['name'], self.pickerView.sceneScale)
            self.buttonData = getButtonData(cmdButton)
        else:
            button = createButtonByInfo(self.buttonData, self.pickerView)       
            self.pickerView.updateButtonsPos(True, [button])    
            
    def get(self):
        return {'undoClassName': self.__class__.__name__,
                'buttonData'    : self.buttonData}
    
    def set(self, data):
        self.buttonData = data['buttonData']
        
     
class UpdateCommandButtonCmd(PickerViewUndoBase):
    
    def __init__(self, pickerView, skipRedo=False):
        super().__init__(skipRedo=skipRedo)
        self.setText('Update CommandButton')
        self.pickerView = pickerView
        
    def initialize(self, codeData: dict):
        self.buttonId    = self.pickerView.clickedButton.buttonId
        self.oldCodeData = self.pickerView.clickedButton.code
        self.newCodeData = codeData
        return self
    
    def _update(self, codeData: dict):
        if self.buttonId in self.pickerView.allPickerButtonsIdMap:
            updateButton = self.pickerView.allPickerButtonsIdMap[self.buttonId]
            updateButton.updateCode(codeData)
    
    def undo(self):
        self._update(self.oldCodeData)
      
    def redo(self):
        if not super().redo():
            return
        self._update(self.newCodeData)
        
    def get(self):
        return {'undoClassName' : self.__class__.__name__,
                'buttonId'      : self.buttonId,
                'oldCodeData'   : self.oldCodeData,
                'newCodeData'   : self.newCodeData}
    
    def set(self, data):
        self.buttonId    = data['buttonId']
        self.oldCodeData = data['oldCodeData']
        self.newCodeData = data['newCodeData']