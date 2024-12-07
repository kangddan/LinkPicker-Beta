import os   
import maya.api.OpenMaya as om2
from importlib import reload
 
def findPythonModules(directory):
    moduleNames = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and file != '__init__.py': 
                relativePath = os.path.relpath(os.path.join(root, file), start=os.path.dirname(directory))
                modulePath = relativePath.replace(os.sep, '.').rsplit('.', 1)[0]
                moduleNames.append(modulePath)
    return moduleNames


def reloadIt():
    modulesToReload = findPythonModules(os.path.dirname(os.path.abspath(__file__)))
    for moduleName in modulesToReload:
        try:
            module = __import__(moduleName, fromlist=[''])
            reload(module)
            print('{} reloaded successfully'.format(moduleName))
        except Exception as e:
            print('Error reloading {}: {}'.format(moduleName, e))
    om2.MGlobal.displayInfo('-------------------- ALL RELOAD : OK')

if __name__ == '__main__':
    reloadIt()
