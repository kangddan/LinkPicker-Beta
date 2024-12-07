import maya.cmds as cmds


def releaseAddSelection(allPickerButtons   : 'list[PickerButton]', 
                        nonMaxPickerButtons: 'list[PickerButton]', 
                        MaxPickerButtons   : 'list[PickerButton]', 
                        selectedButtons    : 'list[PickerButton]') -> list:
    
    selectedNodes = []

    for button in list(selectedButtons):
        nodes = [node for node in button
                 if cmds.objExists(node) and len(cmds.ls(node, long=True)) == 1]
        if nodes:
            selectedNodes.extend(nodes)
        else:
            button.setSelected(False)
            selectedButtons.remove(button)
    
    if selectedNodes:
        # maxButton to button
        cacheSelectedButtons = list(selectedButtons)
        
        for selectedButton in cacheSelectedButtons:
            if not selectedButton.isMaxButton:
                continue
            
            for button in nonMaxPickerButtons:
                if not (button in selectedButton and not button.selected):
                    continue
                
                mayaNode = button.nodes[0]
                if not cmds.objExists(mayaNode):
                    continue
                    
                button.setSelected(True)
                if mayaNode not in selectedNodes:
                    selectedNodes.append(node)
                    
                if button not in selectedButtons:
                    selectedButtons.append(button)

            # check max button
            if not all(cmds.objExists(node) for node in selectedButton):
                if selectedButton in cacheSelectedButtons:
                    selectedButtons.remove(selectedButton)
                selectedButton.setSelected(False)
        
        # update nonButton         
        for button in nonMaxPickerButtons:
            if button[0] in selectedNodes and not button.selected:
                button.setSelected(True)
                if button not in selectedButtons:
                    selectedButtons.append(button)        
          
        # button to maxButton
        for maxButton in MaxPickerButtons:
            if maxButton.selected:
                continue
            if all(node in selectedNodes for node in maxButton):
                maxButton.setSelected(True)
                if maxButton not in selectedButtons:
                    selectedButtons.append(maxButton)
                 
        #cmds.select(selectedNodes, ne=True, replace=True)
        return selectedNodes
    return []


def releaseSubSelection(clickedButton  : 'PickerButton',
                        selectedButtons: 'list[PickerButton]') -> None:
                            
    if not clickedButton.isMaxButton:
        clickedNonButtons = [button 
                            for button in selectedButtons 
                            if not button.isMaxButton and clickedButton in button and button.selected]
                             
        for selectedButton in list(selectedButtons):
            if selectedButton.isMaxButton:
                if selectedButton.selected and clickedButton in selectedButton:
                    selectedButton.setSelected(False)
                    selectedButtons.remove(selectedButton)
            else:
                # update nonButton              
                for button in clickedNonButtons:
                    button.setSelected(False)
                    if button in selectedButtons:
                        selectedButtons.remove(button)
    else:
        # max button
        for selectedButton in list(selectedButtons):
            if selectedButton.isMaxButton:
                if (clickedButton in selectedButton) or (selectedButton in clickedButton):
                    selectedButton.setSelected(False)
                    selectedButtons.remove(selectedButton)

            else:
                if selectedButton in clickedButton:
                    selectedButton.setSelected(False)
                    selectedButtons.remove(selectedButton)





def clearMaxButtonsState(MaxPickerButtons):
    for maxButton in MaxPickerButtons:
        maxButton.updateMaxButtonState(False)
    
            
def updateMaxButtonState(clickedButton, 
                         allPickerButtons : 'list[PickerButton]',
                         MaxPickerButtons : 'list[PickerButton]', 
                         selectedButtons  : 'list[PickerButton]',):
                            
    clearMaxButtonsState(MaxPickerButtons)                          
    if not selectedButtons:
        return   
    
    maxStateButtons = []
    cacheButtons = []
    if clickedButton is not None and clickedButton.isMaxButton:
        for button in allPickerButtons:
            if button in clickedButton:
                cacheButtons.append(button)
        
        for cacheButton in cacheButtons:
            for maxButton in MaxPickerButtons:
                if cacheButton in maxButton:
                    maxStateButtons.append(maxButton)
          
        for maxButton in maxStateButtons:
            maxButton.updateMaxButtonState(True)
        
        return
  
    for selectedButton in selectedButtons:
        for maxButton in MaxPickerButtons:
            if selectedButton in maxButton and not maxButton.selected:
                maxButton.updateMaxButtonState(True)

                
                
