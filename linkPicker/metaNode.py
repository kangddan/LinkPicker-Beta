from __future__ import unicode_literals
import os
import sys
import json
import maya.cmds as cmds


class PickerDataNode(object):
    
    def __repr__(self):
        return u'< PickerDataNode at {}: {} >'.format(hex(id(self)), self.node)
        
        
    def __str__(self):
        return unicode(self.node) if sys.version_info[0] == 2 else str(self.node)
        
        
    def __init__(self, node):
        self.node = node
    
    
    def unlock(self):
        if cmds.lockNode(self.node, q=True):
            cmds.lockNode(self.node, lock=False)
    
    
    def lockAttr(self, state=True):
        self.unlock()
        cmds.setAttr('{}.linkPickerData'.format(self.node), lock=state)

 
    def set(self, data):
        self.lockAttr(False)
        cmds.setAttr('{}.linkPickerData'.format(self.node), json.dumps(data, ensure_ascii=False), type='string')
        self.lockAttr(True)
        
 
    def get(self):
        return json.loads(cmds.getAttr('{}.linkPickerData'.format(self.node)))
        
        
    def delete(self):
        self.unlock()
        cmds.delete(self.node)
    
    
    @property
    def isTagReference(self):
        return cmds.getAttr('{}.isReferenced'.format(self.node))
        
        
    def tagReference(self):
        cmds.setAttr('{}.isReferenced'.format(self.node), True)
        
    @property    
    def isReferenced(self):
        return cmds.referenceQuery(self.node, isNodeReferenced=True)

    
def getPickerDataNode():
    pickerDataNodes = []
    for node in cmds.ls(typ='network'):
        if cmds.objExists('{}.isLinkPicker'.format(node)) and cmds.getAttr('{}.isLinkPicker'.format(node)) and not cmds.getAttr('{}.isReferenced'.format(node)):
            pickerDataNodes.append(PickerDataNode(node))
             
    return pickerDataNodes or [createPickerDataNode()]
    
    
def createPickerDataNode():
    metaNode = cmds.createNode('network', name='Link_Picker_Meta', ss=True)
    cmds.addAttr(metaNode, ln='isLinkPicker', at='bool', dv=True)
    cmds.addAttr(metaNode, ln='isReferenced', at='bool', dv=False)
    cmds.addAttr(metaNode, ln='linkPickerData', dt='string')
    cmds.setAttr('{}.linkPickerData'.format(metaNode), '[]', type='string')
    
    cmds.setAttr('{}.isLinkPicker'.format(metaNode), lock=True)
    cmds.setAttr('{}.linkPickerData'.format(metaNode), lock=True)
    
    return PickerDataNode(metaNode)


def getReferenceNodeData():
    refNodeDatas = []
    for node in cmds.ls(typ='network'):
        if not (cmds.objExists('{}.isLinkPicker'.format(node)) and cmds.getAttr('{}.isLinkPicker'.format(node)) and not cmds.getAttr('{}.isReferenced'.format(node))):
            continue
        if cmds.referenceQuery(node, isNodeReferenced=True):
            refNodeDatas.extend(json.loads(cmds.getAttr('{}.linkPickerData'.format(node)))) 
                         
    return refNodeDatas
    
    
def mergeNodes():
    metaNodes = getPickerDataNode()
    
    noRefTagMetaNodes = [metaNode for metaNode in metaNodes if not metaNode.isTagReference]
    noRefMetaNodes    = [metaNode for metaNode in metaNodes if (not metaNode.isTagReference and not metaNode.isReferenced)]

    if len(noRefMetaNodes) == len(noRefTagMetaNodes) == 1:
        return noRefMetaNodes[0]
        
    newData = []
    for metaNode in metaNodes:
        data = metaNode.get()
        if not isinstance(data, list):
            raise TypeError(u'Expected data to be of type list, but got {} for node {}'.format(type(data).__name__, metaNode.node))
        newData.extend(data)
        if metaNode.isReferenced:
            metaNode.tagReference()
            continue
        metaNode.delete()
        
    newNode = createPickerDataNode()
    newNode.set(newData)
    return newNode
