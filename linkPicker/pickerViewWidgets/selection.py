import maya.cmds as cmds


def releaseAddSelection(allPickerButtons, 
                        nonMaxPickerButtons, 
                        MaxPickerButtons, 
                        selectedButtons):
    
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
        for selectedButton in selectedButtons:
            if not selectedButton.isMaxButton:
                continue
            for button in allPickerButtons:
                if not (button in selectedButton and not button.selected):
                    continue
                nodes = [node for node in button if cmds.objExists(node)]
                if not nodes:
                    continue
                button.setSelected(True)
                
                # to maya node list
                for node in nodes:
                    if node not in selectedNodes:
                        selectedNodes.append(node)
                
                if button not in selectedButtons:
                    selectedButtons.append(button)
                    
            # check max button
            if not all(cmds.objExists(node) for node in selectedButton):
                if selectedButton in selectedButtons:
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
                 

        cmds.select(selectedNodes, ne=True, replace=True)

def releaseSubSelection(clickedButton,
                        selectedButtons):
                            
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
                    
                    
