import maya.api.OpenMaya as om2
from importlib import reload
    

modulesToReload = [
    'linkPicker.colorWidget', 'linkPicker.config', 'linkPicker.fileManager', 'linkPicker.mainUI', 'linkPicker.mainUIMenu', 
    'linkPicker.mayaUtils', 'linkPicker.metaNode', 'linkPicker.path', 'linkPicker.preferencesWidget', 
    'linkPicker.qtUtils', 'linkPicker.toolBoxWidget', 'linkPicker.widgets',
    'linkPicker.pickerViewWidgets.align', 'linkPicker.pickerViewWidgets.buttonManager', 'linkPicker.pickerViewWidgets.mirror',
    'linkPicker.pickerViewWidgets.pickerBackground', 'linkPicker.pickerViewWidgets.pickerButton', 'linkPicker.pickerViewWidgets.pickerMenu',
    'linkPicker.pickerViewWidgets.pickerStates', 'linkPicker.pickerViewWidgets.pickerUtils', 'linkPicker.pickerViewWidgets.pickerView',
    'linkPicker.pickerViewWidgets.selection', 'linkPicker.pickerViewWidgets.undo', 'linkPicker.pickerViewWidgets.view', 
    'linkPicker.pickerViewWidgets.zorder', 'linkPicker.imageWidget'
]

def reloadIt():
    for moduleName in modulesToReload:
        try:
            module = __import__(moduleName, fromlist=[''])
            reload(module)
            print('{} reloaded successfully'.format(moduleName))
        except Exception as e:
            print('Error reloading {}: {}'.format(moduleName, e))

    print('-------------------- ALL RELOAD : OK')
    om2.MGlobal.displayInfo('-------------------- ALL RELOAD : OK')

if __name__ == '__main__':
    reloadIt()
    

    

    