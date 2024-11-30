
def raiseSelectedButtons(selectedButtons: 'list[PickerButton]') -> None:                    
    for button in selectedButtons:
        button.raise_()
             
        
def lowerSelectedButtons(selectedButtons: 'list[PickerButton]') -> None:

    for button in selectedButtons:
        button.lower()
        
        
def __raiseButtons(selectedButtons: 'list[PickerButton]') -> None:
    for button in selectedButtons:
        button.raise_()
      
        
def moveSelectedButtonsUp(selectedButtons: 'list[PickerButton]', 
                          allButtons     : 'list[PickerButton]') -> None:
    if len(allButtons) <= 1 or not selectedButtons:
        return
    for button in reversed(selectedButtons):
        index = allButtons.index(button) 
        if index == len(allButtons) - 1: 
            continue 
        allButtons[index], allButtons[index + 1] = allButtons[index + 1], allButtons[index]
    __raiseButtons(allButtons)


def moveSelectedButtonsDown(selectedButtons: 'list[PickerButton]', 
                            allButtons     : 'list[PickerButton]') -> None:
    if len(allButtons) <= 1 or not selectedButtons:
        return
    for button in selectedButtons:
        index = allButtons.index(button)
        if index == 0: 
            continue
        allButtons[index], allButtons[index - 1] = allButtons[index - 1], allButtons[index]
    __raiseButtons(allButtons)
    
