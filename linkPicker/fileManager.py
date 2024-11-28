import os
import sys
import json
from PySide2 import QtWidgets
from maya.api import OpenMaya as om2 


class FileManager(object):
    
    BASE_FILE_PATH = _BASE_FILE_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    def __init__(self, parent=None):
        self.parent = parent
        
    
    def checkPath(self, filePath):
        directory = os.path.dirname(filePath)
        return os.path.exists(directory)
    
    
    def getDatas(self, undoToFile):
        if self.parent.tabWidget.count() == 1:
            return None, None
        pickerView = self.parent.tabWidget.currentWidget()
        if not hasattr(pickerView, 'getAllPickerButtons'):
            return None, None  
        data = pickerView.get(undoToFile)
        return pickerView, data
        
        
    def showFileWindow(self, pickerView, data, path=''):
        newFilePath, _ = QtWidgets.QFileDialog.getSaveFileName(self.parent, 'Save File', path, 'Link Picker Files (*.lpk)')
        if sys.version_info[0] == 2:
            newFilePath = str(newFilePath)
        if not newFilePath:
            return
        pickerView.cacheSavePath = newFilePath
        data['cacheSavePath'] = newFilePath
        self._saveToFile(data, newFilePath)
        
        self.parent.updateTabToolTip(pickerView)
        
    def save(self, undoToFile):
        pickerView, data = self.getDatas(undoToFile)
        if pickerView is None:
            return
        filePath = data['cacheSavePath']
        
        if self.checkPath(filePath):
            self._saveToFile(data, filePath)
        else:
            self.showFileWindow(pickerView, data, self._BASE_FILE_PATH)
            
    
    def saveAs(self):
        pickerView, data = self.getDatas()
        if pickerView is None:
            return
        filePath = data['cacheSavePath']
        basefilePath =  os.path.dirname(filePath) if self.checkPath(filePath) else self._BASE_FILE_PATH
        self.showFileWindow(pickerView, data, basefilePath)
        
                  
    def open(self):
        filePaths, _ = QtWidgets.QFileDialog.getOpenFileNames(self.parent, 'Select Pickers', self.BASE_FILE_PATH, 'Link Picker Files (*.lpk)')
        if sys.version_info[0] == 2:
            filePaths = [str(path) for path in filePaths]
        if not filePaths:
            return
        self.BASE_FILE_PATH = os.path.dirname(filePaths[0])
        
        datas = []
        for pickerPath in filePaths:
            with open(pickerPath, 'rb' if sys.version_info[0] == 2 else 'r') as f:
                datas.append(json.load(f))
        self.parent.set(datas)

        
    def _saveToFile(self, data, filePath):
        try:
            with open(filePath, 'wb' if sys.version_info[0] == 2 else 'w') as f:
                json.dump(data, f, indent=4)
            om2.MGlobal.displayInfo('File saved successfully to: {}'.format(filePath))
        except IOError as e:
            om2.MGlobal.displayError('Error occurred while saving the file: {}. Error: {}'.format(filePath, e))
