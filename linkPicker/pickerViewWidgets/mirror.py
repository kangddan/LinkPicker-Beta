import maya.cmds as cmds

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtCore
else:
    from PySide2 import QtCore

from . import pickerUtils


def reversePosition(selectedButtons : 'list[PickerButton]', 
                    buttonsParentPos: QtCore.QPointF, 
                    sceneScale      : float):
    
    reverseCenterPos = [button.cenrerPos(
                        pickerUtils.localToGlobal(button.localPos, buttonsParentPos, sceneScale)) 
                        for button in reversed(selectedButtons)]
                        
    for button, pos in zip(selectedButtons, reverseCenterPos):
        globalTopLeftPos = QtCore.QPointF(pos.toPoint().x() - round(button.scaleX * sceneScale) / 2.0, 
                                          pos.toPoint().y() - round(button.scaleY * sceneScale) / 2.0) 
        button.move(globalTopLeftPos.toPoint())
        button.updateLocalPos(globalTopLeftPos, buttonsParentPos, sceneScale)
        

def findMirrorObjName(origName: str) -> str:
    leftMarkers  = ['L_', '_L', 'left', 'Left', 'lt_', '_lt']
    rightMarkers = ['R_', '_R', 'right', 'Right', 'rt_', '_rt']
    
    newName = None
    for left, right in zip(leftMarkers, rightMarkers):
        if left in origName:
            newName = origName.replace(left, right)
            break
        elif right in origName:
            newName = origName.replace(right, left)
            break
            
    return newName if newName and cmds.objExists(newName) else origName
        
  
def getMirrorObjs(nodeList: 'list[MayaNodeName]') -> 'list[MayaNodeName]':
    return [findMirrorObjName(node) for node in nodeList]
    


