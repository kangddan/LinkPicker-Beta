import json
import maya.cmds as cmds


class PickerDataNode(object):
    
    def __repr__(self):
        return f'< PickerDataNode at {hex(id(self))}: {self.node} >'
        
        
    def __str__(self):
        return self.node
        
        
    def __init__(self, node:str):
        self.node = node
    
    
    def unlock(self):
        if cmds.lockNode(self.node, q=True):
            cmds.lockNode(self.node, lock=False)
    
    
    def lockAttr(self, state=True):
        self.unlock()
        cmds.setAttr(f'{self.node}.linkPickerData', lock=state)

 
    def set(self, data: list):
        self.lockAttr(False)
        cmds.setAttr(f'{self.node}.linkPickerData', json.dumps(data), type='string')
        self.lockAttr(True)
        
 
    def get(self) -> list:
        return json.loads(cmds.getAttr(f'{self.node}.linkPickerData'))
        
        
    def delete(self):
        self.unlock()
        cmds.delete(self.node)
    
    
    @property
    def isTagReference(self) -> bool:
        return cmds.getAttr(f'{self.node}.isReferenced')
        
        
    def tagReference(self):
        cmds.setAttr(f'{self.node}.isReferenced', True)
        
    @property    
    def isReferenced(self) -> bool:
        return cmds.referenceQuery(self.node, isNodeReferenced=True)

    
def getPickerDataNode() -> 'list[PickerDataNode]':
    pickerDataNodes = []
    for node in cmds.ls(typ='network'):
        if cmds.objExists(f'{node}.isLinkPicker') and cmds.getAttr(f'{node}.isLinkPicker') and not cmds.getAttr(f'{node}.isReferenced'):
            pickerDataNodes.append(PickerDataNode(node))
             
    return pickerDataNodes or [createPickerDataNode()]
    
    
def createPickerDataNode() -> PickerDataNode:
    metaNode = cmds.createNode('network', name='Link_Picker_Meta', ss=True)
    cmds.addAttr(metaNode, ln='isLinkPicker', at='bool', dv=True)
    cmds.addAttr(metaNode, ln='isReferenced', at='bool', dv=False)
    cmds.addAttr(metaNode, ln='linkPickerData', dt='string')
    cmds.setAttr(f'{metaNode}.linkPickerData', '[]', type='string')
    
    cmds.setAttr(f'{metaNode}.isLinkPicker', lock=True)
    cmds.setAttr(f'{metaNode}.linkPickerData', lock=True)
    
    return PickerDataNode(metaNode)


def getReferenceNodeData() -> list:
    refNodeDatas = []
    for node in cmds.ls(typ='network'):
        if not (cmds.objExists(f'{node}.isLinkPicker') and cmds.getAttr(f'{node}.isLinkPicker') and not cmds.getAttr(f'{node}.isReferenced')):
            continue
        if cmds.referenceQuery(node, isNodeReferenced=True):
            refNodeDatas.extend(json.loads(cmds.getAttr(f'{node}.linkPickerData'))) 
                         
    return refNodeDatas
    
    
def mergeNodes() -> PickerDataNode:
    metaNodes = getPickerDataNode()
    
    noRefTagMetaNodes = [metaNode for metaNode in metaNodes if not metaNode.isTagReference]
    noRefMetaNodes    = [metaNode for metaNode in metaNodes if (not metaNode.isTagReference and not metaNode.isReferenced)]

    if len(noRefMetaNodes) == len(noRefTagMetaNodes) == 1:
        return noRefMetaNodes[0]
        
    newData = []
    for metaNode in metaNodes:
        data = metaNode.get()
        if not isinstance(data, list):
            raise TypeError(f'Expected data to be of type list, but got {type(data).__name__} for node {metaNode.node}')
        newData.extend(data)
        if metaNode.isReferenced:
            metaNode.tagReference()
            continue
        metaNode.delete()
        
    newNode = createPickerDataNode()
    newNode.set(newData)
    return newNode
        