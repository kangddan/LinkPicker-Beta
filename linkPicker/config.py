import os
import sys
import json


ICONS_PATH  = os.path.join(os.path.dirname(__file__), 'icons')


alignHorizontallyIcon = os.path.join(ICONS_PATH, 'alignHorizontallyIcon.png')
alignVerticallyIcon   = os.path.join(ICONS_PATH, 'alignVerticallyIcon.png')
pythonLogo            = os.path.join(ICONS_PATH, 'pythonLogo2.png')
mirrorIcon            = os.path.join(ICONS_PATH, 'mirrorIcon.png')
blackCursorIcon       = os.path.join(ICONS_PATH, 'blackCursor.png')
greenCursorIcon       = os.path.join(ICONS_PATH, 'greenCursor.png')
backgroundIcon        = os.path.join(ICONS_PATH, 'backgroundLogo.png')


class ConfigManager(object):
    DEFAULT_CONFIG = {'general': {
                                  'showNamespaceCheckBox': True,
                                  'autoSelectedCheckBox' : True,
                                  'closeTabCheckBox'     : True,
                                  'showTabBarCheckBox'   : True,
                                  'toolBoxCheckBox'      : True,

                                  'viewModeComboBox'     : 2,
                                  'ZoomSlider'           : 25},
                                  
                     'settings': {'queue'     : 20, 
                                  'undo'      : True,    
                                  'undoToFile': False}}
    
    CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
    
    _INSTANCE = None
    
    def __new__(cls, *args, **kwargs):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(ConfigManager, cls).__new__(cls)
        return cls._INSTANCE
        
        
    def set(self, data):
        with open(ConfigManager.CONFIG_PATH, 'w') as f:
            json.dump(data, f, indent=4)
        
        
    def get(self):
        if not os.path.exists(ConfigManager.CONFIG_PATH):
            self.set(ConfigManager.DEFAULT_CONFIG) 
            return ConfigManager.DEFAULT_CONFIG
            
        with open(ConfigManager.CONFIG_PATH, 'r') as f:
            return json.load(f)        
    