import maya.cmds as cmds

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtCore
else:
    from PySide2 import QtCore


def alignButtons(buttons   : 'list[PickerButton]', 
                 parentPos : QtCore.QPointF, 
                 sceneScale: float, 
                 alignType : str = 'horizontal or vertical') -> None:
                    
    if not buttons or len(buttons) < 2:
        return

    startButton = buttons[0]; endButton = buttons[-1]
    
    if alignType == 'horizontal':
        firstCenter   = startButton.pos().y() + startButton.scaleY * sceneScale / 2
        lastCenter    = endButton.pos().y() + endButton.scaleY * sceneScale / 2
        averageCenter = (firstCenter + lastCenter) / 2

        for button in buttons:
            globalPos = QtCore.QPointF(button.pos().x(), averageCenter - button.scaleY * sceneScale / 2)
            button.move(globalPos.toPoint())
            button.updateLocalPos(globalPos, parentPos, sceneScale)
            
    elif alignType == 'vertical':
        firstCenter   = startButton.pos().x() + startButton.scaleX * sceneScale / 2
        lastCenter    = endButton.pos().x() + endButton.scaleX * sceneScale / 2
        averageCenter = (firstCenter + lastCenter) / 2

        for button in buttons:
            globalPos = QtCore.QPointF(averageCenter - button.scaleX * sceneScale / 2, button.pos().y())
            button.move(globalPos.toPoint())
            button.updateLocalPos(globalPos, parentPos, sceneScale)
            

def distributeButtonsEvenly(selectedButtons : 'list[PickerButton]',
                            buttonsParentPos: QtCore.QPointF,
                            sceneScale      : float) -> None:
                                
    startX = selectedButtons[0].pos().x() + selectedButtons[0].scaleX * sceneScale / 2
    startY = selectedButtons[0].pos().y() + selectedButtons[0].scaleY * sceneScale / 2
    
    endX = selectedButtons[-1].pos().x() + selectedButtons[-1].scaleX * sceneScale / 2
    endY = selectedButtons[-1].pos().y() + selectedButtons[-1].scaleY * sceneScale / 2
                                                  
    count = len(selectedButtons)
    for i, button in enumerate(selectedButtons[1:-1], start=1):
        t = i / (count - 1) if count > 1 else 0 
        x = (1 - t) * startX + t * endX
        y = (1 - t) * startY + t * endY

        globalPos = QtCore.QPointF(x - button.scaleX * sceneScale / 2,  y - button.scaleY * sceneScale / 2)
        button.move(globalPos.toPoint())
        button.updateLocalPos(globalPos, buttonsParentPos, sceneScale)
        
        
def updateButtonsDuringDrag(buttons         : 'list[PickerButton]', 
                            startPos        : QtCore.QPointF, 
                            endPos          : QtCore.QPointF,
                            buttonsParentPos: QtCore.QPointF,
                            sceneScale      : float) -> None:
    count = len(buttons)
    for i, button in enumerate(buttons):
        t = i / (count - 1) if count > 1 else 0  
        x = (1 - t) * startPos.x() + t * endPos.x()
        y = (1 - t) * startPos.y() + t * endPos.y()

        globalPos = QtCore.QPointF(x - (button.scaleX / 2) * sceneScale, 
                                   y - (button.scaleY / 2) * sceneScale)
        button.move(globalPos.toPoint())
        button.updateLocalPos(globalPos, buttonsParentPos, sceneScale)  