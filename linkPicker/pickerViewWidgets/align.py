from __future__ import division
from PySide2 import QtCore


def alignButtons(buttons, 
                 parentPos, 
                 sceneScale, 
                 alignType='horizontal'):
                    
    if not buttons or len(buttons) < 2:
        return

    startButton = buttons[0]; endButton = buttons[-1]
    
    if alignType == 'horizontal':
        firstCenter   = startButton.pos().y() + startButton.scaleY * sceneScale / 2.0
        lastCenter    = endButton.pos().y() + endButton.scaleY * sceneScale / 2.0
        averageCenter = (firstCenter + lastCenter) / 2.0

        for button in buttons:
            globalPos = QtCore.QPointF(button.pos().x(), averageCenter - button.scaleY * sceneScale / 2.0)
            button.move(globalPos.toPoint())
            button.updateLocalPos(globalPos, parentPos, sceneScale)
            
    elif alignType == 'vertical':
        firstCenter   = startButton.pos().x() + startButton.scaleX * sceneScale / 2.0
        lastCenter    = endButton.pos().x() + endButton.scaleX * sceneScale / 2.0
        averageCenter = (firstCenter + lastCenter) / 2.0

        for button in buttons:
            globalPos = QtCore.QPointF(averageCenter - button.scaleX * sceneScale / 2.0, button.pos().y())
            button.move(globalPos.toPoint())
            button.updateLocalPos(globalPos, parentPos, sceneScale)
            

def distributeButtonsEvenly(selectedButtons,
                            buttonsParentPos,
                            sceneScale):
                                
    startX = selectedButtons[0].pos().x() + selectedButtons[0].scaleX * sceneScale / 2.0
    startY = selectedButtons[0].pos().y() + selectedButtons[0].scaleY * sceneScale / 2.0
    
    endX = selectedButtons[-1].pos().x() + selectedButtons[-1].scaleX * sceneScale / 2.0
    endY = selectedButtons[-1].pos().y() + selectedButtons[-1].scaleY * sceneScale / 2.0
                                                  
    count = len(selectedButtons)
    for i, button in enumerate(selectedButtons[1:-1], start=1):
        t = i / (count - 1) if count > 1 else 0 
        x = (1 - t) * startX + t * endX
        y = (1 - t) * startY + t * endY

        globalPos = QtCore.QPointF(x - button.scaleX * sceneScale / 2.0,  y - button.scaleY * sceneScale / 2.0)
        button.move(globalPos.toPoint())
        button.updateLocalPos(globalPos, buttonsParentPos, sceneScale)

  
        
def updateButtonsDuringDrag(buttons , 
                            startPos, 
                            endPos,
                            buttonsParentPos,
                            sceneScale):
    count = len(buttons)
    for i, button in enumerate(buttons):
        t = i / float(count - 1) if count > 1 else 0  
        x = (1 - t) * startPos.x() + t * endPos.x()
        y = (1 - t) * startPos.y() + t * endPos.y()

        globalPos = QtCore.QPointF(x - (button.scaleX / 2.0) * sceneScale, 
                                   y - (button.scaleY / 2.0) * sceneScale)
        button.move(globalPos.toPoint())
        button.updateLocalPos(globalPos, buttonsParentPos, sceneScale)  