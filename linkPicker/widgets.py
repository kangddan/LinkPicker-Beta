# -*- coding: utf-8 -*-
import maya.api.OpenMaya as om2
import maya.cmds as cmds
from functools import partial

if int(cmds.about(version=True)) >= 2025:
    from PySide6 import QtWidgets, QtCore, QtGui
    Action = QtGui.QAction
else:
    from PySide2 import QtWidgets, QtCore, QtGui
    Action = QtWidgets.QAction


class NullWidget(QtWidgets.QWidget):
    createClicked = QtCore.Signal()
    openClicked   = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True) 
        self.setObjectName('nullWidget')
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        self.setStyleSheet('''
                            QPushButton#createBut {background: #346788; border-radius: 3px;}
                            QPushButton:hover#createBut {background: #2A5D7E;}
                            QPushButton:pressed#createBut {background: #205374;}
                            
                            QWidget#nullWidget {background-color: #333333;}
                            
                            QPushButton#openBut {background: #282828; border-radius: 3px;}
                            QPushButton:hover#openBut {background: #232323;}
                            QPushButton:pressed#openBut {background: #191919;}
                        ''')

    def _createWidgets(self):
        self.iconLabel = QtWidgets.QLabel()
        self.iconLabel.setAlignment(QtCore.Qt.AlignCenter) 
        self.iconLabel.setWordWrap(True)
        self.iconLabel.setText("<img src=':np-head.png'><h4>Create a new picker tab to get started</h4>")
        
        self.createBut = QtWidgets.QPushButton('New Picker')
        self.createBut.setFixedSize(140, 40)
        self.createBut.setObjectName('createBut')
        self.openBut = QtWidgets.QPushButton('Open Picker')
        self.openBut.setFixedSize(140, 40)
        self.openBut.setObjectName('openBut')
    
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(30)
        
        mainLayout.addStretch()
        mainLayout.addWidget(self.iconLabel)

        buttonLayout = QtWidgets.QHBoxLayout() 
        buttonLayout.setSpacing(5)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.createBut)
        buttonLayout.addWidget(self.openBut)
        buttonLayout.addStretch()

        mainLayout.addLayout(buttonLayout)
        mainLayout.addStretch()
        
    def _createConnections(self):
        self.createBut.clicked.connect(self.createClicked.emit)
        self.openBut.clicked.connect(self.openClicked.emit)
       
        
class MyTabBar(QtWidgets.QTabBar):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        
class TabNameDialog(QtWidgets.QInputDialog):
    def __init__(self, parent=None, currentName=''):
        super().__init__(parent)

        self.setWindowTitle('Tab Name')
        self.setLabelText('New Name')
        self.setTextValue(currentName)
        self.setInputMode(QtWidgets.QInputDialog.TextInput)
        self.setTextEchoMode(QtWidgets.QLineEdit.Normal)

        self.lineEdit = self.findChild(QtWidgets.QLineEdit)
        if self.lineEdit:
            self.lineEdit.textChanged.connect(self.validateInput)

    def validateInput(self, text):
        if '*' in text:
            cursorPos = self.lineEdit.cursorPosition()
            text = text.replace('*', '')
            self.lineEdit.setText(text)
            self.lineEdit.setCursorPosition(cursorPos - 1)
        
    
class MyTabWidget(QtWidgets.QTabWidget):
    newTab     = QtCore.Signal()
    tabCount   = QtCore.Signal(int)
    
    duplicateTriggered = QtCore.Signal(int)
    openClicked   = QtCore.Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMovable(True)
        self.setTabsClosable(True)
        self.tabBar = self.tabBar()
        self.tabBar.installEventFilter(self)
        # ------------------------------------------------
        self.isMovingTab      = False 
        self.hasMoved         = False 
        self.MouseRightandMid = False
        self._createMenu()
        self._createWidgets()
        self._createConnections()
        
        self.showTabClosewarning = True

    
    def _createWidgets(self):
        self.nullWidget = NullWidget()
     
        self.iconLabel = QtWidgets.QLabel('+')
        self.iconLabel.setFont(QtGui.QFont('Arial', 8, QtGui.QFont.Bold) )
        self.tabBar.setTabButton(self.addTab(self.nullWidget, ''), QtWidgets.QTabBar.RightSide, self.iconLabel)
        #self.iconLabel.installEventFilter(self)
        #self.tabBar.setTabButton(self.addTab(self.nullWidget, '+'), QtWidgets.QTabBar.RightSide, None) # add base tab

        
    def _createMenu(self):
        self.addTableMenu = QtWidgets.QMenu(self)
        self.createAction = Action('New Tab', self.addTableMenu)
        self.addTableMenu.addAction(self.createAction) 
        # ---------------------------------------------------
        self.TableMenu = QtWidgets.QMenu(self)
        self.duplicateAction   = Action('Duplicate Tab',  self.TableMenu)
        self.closeAllAction    = Action('Close All Tabs', self.TableMenu)
        self.closeOthersAction = Action('Close Others',   self.TableMenu)
        self.TableMenu.addAction(self.duplicateAction)
        self.TableMenu.addSeparator()
        self.TableMenu.addAction(self.closeAllAction)
        self.TableMenu.addAction(self.closeOthersAction)
    
        
    def _createConnections(self):
        self.nullWidget.createClicked.connect(self.newTab.emit)
        self.nullWidget.openClicked.connect(self.openClicked.emit)
        self.createAction.triggered.connect(self.newTab.emit)
        self.tabCloseRequested.connect(self._closeTab)
        self.tabBarDoubleClicked.connect(self._renameTab)
        
        self.duplicateAction.triggered.connect(lambda: self.duplicateTriggered.emit(self.duplicateAction.data()))
        self.closeAllAction.triggered.connect(partial(self._closeAllTab, showWarning=True))
        self.closeOthersAction.triggered.connect(self._closeOthers)
        
        # ----------------------------------------
        self.showTabTimer = QtCore.QTimer(self)
        self.showTabTimer.setSingleShot(True)
        self.showTabTimer.timeout.connect(self._showAddTab)


    def eventFilter(self, obj, event):
        if obj == self.tabBar:
            if event.type() == QtCore.QEvent.Wheel:
                '''
                Skip switching to the last tab (e.g., the "add tab" button)
                '''
                currentIndex = self.currentIndex()
                index = currentIndex - 1 if event.angleDelta().y() > 0 else currentIndex + 1
                if index == self.count() - 1:
                    return True
                return False
                       
            if event.type() in [QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick]:
                button = event.button()

                if button in [QtCore.Qt.LeftButton, QtCore.Qt.MiddleButton, QtCore.Qt.RightButton]:
                    '''
                    All three types of mouse buttons can trigger the addTableMenu
                    '''
                    if self.tabBar.tabAt(event.pos()) == self.count() - 1:
                        self.addTableMenu.exec_(event.globalPos())
                        return True
                        
                    elif event.buttons() in [QtCore.Qt.RightButton, QtCore.Qt.MiddleButton]:
                        self.MouseRightandMid  = True
                        index = self.tabBar.tabAt(event.pos()) # get tag index
                        self.closeOthersAction.setData(index) 
                        self.duplicateAction.setData(index) 
                        self.TableMenu.exec_(event.globalPos())
                        return True
                    
                    
                    elif button == QtCore.Qt.RightButton:
                   
                        '''
                        Ignore to prevent middle/right mouse button from triggering tabBarDoubleClicked
                        Track middle/right button state and reset movement flags
                        '''
                        self.MouseRightandMid  = True
                        self.isMovingTab       = False
                        self.hasMoved          = False
                        return True              
                    
                if button == QtCore.Qt.LeftButton:
                    self.MouseRightandMid  = True
                    self.isMovingTab = True
                    self.hasMoved    = False
                    return False 

            elif event.type() == QtCore.QEvent.MouseMove and self.MouseRightandMid  and not self.hasMoved:
                # vis end tab
                self.setTabVisible(self.count() - 1, False)
                self.hasMoved = True
                return False

            elif event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
                if self.hasMoved or self.MouseRightandMid:
                    #vis end tab
                    #If the interval is too slow, quickly dragging the tab may cause 'New Tab' to appear in the wrong position ����
                    self.showTabTimer.start(250)
                
                if not isinstance(self.widget(self.count() - 1), NullWidget):
                    nullWidgetIndex = self.indexOf(self.nullWidget)
                    self.tabBar.moveTab(nullWidgetIndex, self.count() - 1)
                # ----------------------------------------------------------------------------
                
                self.isMovingTab      = False
                self.MouseRightandMid = False
                self.hasMoved         = False
                return False
            return False
            
        elif isinstance(obj, QtWidgets.QAbstractButton):
            if event.type() == QtCore.QEvent.Enter:
                obj.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                return False
            elif event.type() == QtCore.QEvent.Leave:
                obj.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
                return False
            return False
            
        else:
            return super().eventFilter(obj, event)


    def _showAddTab(self):
        self.showTabTimer.stop()
        self.setTabVisible(self.count() - 1, True) 


    def addNewTab(self, widget, name=None) -> int:
        count = self.count()
        tabName: str = name or self._getNextName()
        index:   int = self.insertTab(count - 1, widget, tabName)
        
        # get close button
        closeButton = self.tabBar.tabButton(index, QtWidgets.QTabBar.RightSide)
        if isinstance(closeButton, QtWidgets.QAbstractButton):
            closeButton.installEventFilter(self)
        
        self.tabCount.emit(count+1)
        return index
        
        
    def getWidget(self) -> 'list[PickerView]':
        pickerViewWidgets = []
        for i in  range(self.count()):
            widget = self.widget(i)
            if isinstance(widget,  NullWidget):
                continue
            if hasattr(widget, 'getAllPickerButtons'):
                pickerViewWidgets.append(widget)
        return pickerViewWidgets
        #return [widget for i in range(self.count()) if not isinstance((widget := self.widget(i)), NullWidget)]

    
    def _closeTab(self, index, showWarning=True):
        count = self.count()
        
        if count == 1:
            return
                 
        if showWarning and self.showTabClosewarning:
            tabName = self.tabText(index)
            reply = QtWidgets.QMessageBox.warning(self, 'Close Tab', 
                    "Are you sure you want to close the tab '{}'? \nAll changes will be lost.".format(tabName), 
                    QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes)
            
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                return 
 
        widget = self.widget(index)  
        self.removeTab(index)
        widget.setParent(None)
        widget.deleteLater()

        if index == count - 2:
            newIndex = index - 1 if index > 0 else 0
            self.setCurrentIndex(newIndex)
        self.tabCount.emit(count-1) # hide namespaceWidget
        
        
    def _closeAllTab(self, showWarning=True):
        count = self.count() - 1
        for i in reversed(range(count)):
            try:
                self._closeTab(i, showWarning)
            except Exception as e:
                import traceback
                traceback.print_exc() 
                om2.MGlobal.displayWarning(f'Incorrect tab. \n{str(e)}')
                continue
            
            
    def _closeOthers(self):
        index = self.closeOthersAction.data()
        count = self.count() - 1
        for i in reversed(range(count)):
            if i == index:
                continue
            self._closeTab(i)

    
    def _renameTab(self, index):
        if self.count() == 1:
            return
        currentName = self.tabText(index)
        if currentName[-1] == '*':
            currentName = currentName[:-1]
            
        # newName, isOk = QtWidgets.QInputDialog.getText(self, 'Tab Name', 'New Name', QtWidgets.QLineEdit.Normal, currentName)
        # if isOk and newName and newName != currentName:
        #     self.setTabText(index, f'{newName}*')
        nameDialog = TabNameDialog(self, currentName)
        if nameDialog.exec() == QtWidgets.QDialog.Accepted:
            newName = nameDialog.textValue()
            self.setTabText(index, f'{newName}*')
            
            
    def _duplicateTab(self):
        pass
        

    def _getNextName(self) -> str:
        prefix = 'Untitled '
        items = [name[:-1] if name and name[-1] == '*' else name for name in [self.tabText(i) for i in range(self.count())]]
        
        suffixNumbers = []
        
        for item in items:
            if not item.startswith(prefix):
                continue
            suffix = item[len(prefix):] 
            if suffix.isdigit():
                suffixNumbers.append(int(suffix))  
 
        maxSuffix = max(suffixNumbers) if suffixNumbers else 0
        return f'{prefix}{maxSuffix + 1}'
        
        
        
class ZoomHintWidget(QtWidgets.QWidget):
    pass
    
    
class NumberLineEdit(QtWidgets.QLineEdit):
    
    oldAndNewNumber = QtCore.Signal(int)
    def __repr__(self):
        return f"< {self.__class__.__name__} '{self.get()}'>"
    
    def __init__(self, dataType: str ='int', 
                       defaultValue=0, 
                       step=1, 
                       minimum=-100, 
                       maximum=100, 
                       parent=None):
                        
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self._dataType    = dataType
        self._step        = step
        self._minimum     = minimum
        self._maximum     = maximum
    
        self._storedValue = self._valueCheck(defaultValue)
        self._cacheNumber = self._formatDisplayValue(self._storedValue)
        self.setText(self._cacheNumber)
        
        self.dragging   = False 
        self.lastMouseX = 0
        
        self.moveTag = False


    @staticmethod
    def isNumber(value):
        # from re import match
        # pattern = r'^[+-]?(\d+(\.\d*)?|\.\d+)$'
        # return bool(match(pattern, value))
        try:
            float(value)
            return True
        except ValueError:
            return False
    

    
    def focusInEvent(self, event):
        self._cacheNumber = self.text()
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        value = self.text()
        if not self.isNumber(value):
            self.setText(self._cacheNumber)
        else:
            value = self._valueCheck(value)
            # ---------------------------------
            if value != self._storedValue:
                '''
                Make the editingFinished signal trigger earlier than our custom-defined oldAndNewNumber signal. 
                This is primarily used for button scaling undo functionality, 
                ensuring the correct retrieval of the button's historical scaling values and incorporating them into the undo operation
                '''
                QtCore.QTimer.singleShot(0, lambda: self.oldAndNewNumber.emit(int(value)))
            self._storedValue = value
            self.setText(self._formatDisplayValue(value))
  
        super().focusOutEvent(event)
        
    # -----------------------------------------
    def _valueCheck(self, value):
        value = int(float(value)) if self._dataType == 'int' else float(value)
        value = max(self._minimum, min(self._maximum, value))
        return value
        
    def _formatDisplayValue(self, value):
        if self._dataType == 'float':
            return f'{value:.3f}'
        return str(value)
        
    def mousePressEvent(self, event):
        if (event.buttons() == QtCore.Qt.MiddleButton and 
           QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier):
            
            self.dragging = True
            self.lastMouseX = event.x()
            self.clearFocus() 
            self.setCursor(QtCore.Qt.SizeHorCursor)
        else:
            '''
            If any other mouse button is clicked during the middle-button dragging process
            immediately stop the dragging logic
            '''
            if self.dragging:
                self.dragging = False 
                self.setCursor(QtCore.Qt.IBeamCursor)
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.x() - self.lastMouseX
            if delta != 0:
                adjustment = (delta / (1000.0 if self._dataType == 'float' else 2)) * self._step 
                
                value = self._valueCheck(self._storedValue + adjustment)
                self._storedValue = value
                self.setText(self._formatDisplayValue(value))
                self.lastMouseX = event.x()
                
                self.editingFinished.emit() # update signal emit
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self.dragging = False
            
            #print(type(self._cacheNumber), type(self._storedValue))
            if abs(float(self._cacheNumber) - float(self._storedValue)) > 1e-6:
                self.oldAndNewNumber.emit(int(self._storedValue))

            self.setCursor(QtCore.Qt.IBeamCursor)
        else:
            super().mouseReleaseEvent(event)
            
    def get(self):
        return self._storedValue
        
    def set(self, value):
        if not isinstance(value, (int, float)):
            self.setText(self._cacheNumber)
            return
            
        self._storedValue = self._valueCheck(value)
        self.setText(self._formatDisplayValue(self._storedValue))
        
        
class SelectionBox(QtWidgets.QRubberBand):
    def __init__(self, parent=None, shape=QtWidgets.QRubberBand.Line):
        super().__init__(shape, parent)
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtGui.QColor(150, 150, 150), 4, QtCore.Qt.SolidLine))
        painter.setBrush(QtGui.QColor(100, 100, 100, 50))
        painter.drawRect(self.rect())
        
        
class AxisWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(100, 100)
        self.createWidgets()
        
    def createWidgets(self):
        self.axisLabel = QtWidgets.QLabel(self)
        self.axisLabel.setText('(0.000, 0.000)')
        self.axisLabel.move(10, 10)
        
    def reset(self):
        self.move(QtCore.QPoint(0, 0))
        self.resize(100, 100)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)  
        painter.setPen(QtGui.QPen(QtCore.Qt.red, self.width() / 20))
        painter.drawLine(0, 0, self.width(), 0)
        painter.setPen(QtGui.QPen(QtCore.Qt.green, self.height() / 20))
        painter.drawLine(0, 0, 0, self.height())
        painter.end()
  
        self.axisLabel.setText(f'({self.pos().x()}, {self.pos().y()})')


class CustomItemDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        if option.state & QtWidgets.QStyle.State_HasFocus:
            option.state &= ~QtWidgets.QStyle.State_HasFocus  # remove focus
        super().paint(painter, option, index)
           
                
class CustomDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None, itemHeight=30):
        super().__init__(parent)
        self.itemHeight = itemHeight

    def sizeHint(self, option, index):
        if index.data() == 'separator':
            return QtCore.QSize(option.rect.width(), 7)
        size = super().sizeHint(option, index)
        size.setHeight(self.itemHeight)
        return size    
        
    def paint(self, painter, option, index):
        painter.fillRect(option.rect, QtGui.QColor(82, 82, 82)) 
        if index.data() == 'separator': 
            painter.save()
            pen = QtGui.QPen(QtGui.QColor(105, 105, 105)); pen.setWidth(1)
            painter.setPen(pen)
            painter.drawLine(option.rect.left(), option.rect.center().y(),
                             option.rect.right(), option.rect.center().y())
            painter.restore()
        else:
            super().paint(painter, option, index)
        

def toParentMidPos(_self, parent):
    if parent is None:
        return
    mainRect = parent.geometry()
    selfRect = _self.geometry() 
    
    x = mainRect.x() + (mainRect.width() - selfRect.width()) / 2
    y = mainRect.y() + (mainRect.height() - selfRect.height()) / 2
    _self.move(QtCore.QPoint(round(x), round(y)))
        

class NamespaceEditWidget(QtWidgets.QDialog):
    
    selectedNamespace = QtCore.Signal(str)
    
    def __init__(self, parent=None, tabWidget=None):
        super().__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus); self.setFocus()
        self.setWindowTitle('Select Namespace')
        self.resize(300, 90)

        
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        toParentMidPos(self, parent)
        
    def _createWidgets(self):
        self.namespaceComboBox = QtWidgets.QComboBox()
        self.namespaceComboBox.setItemDelegate(CustomDelegate(self, 25))
        self.namespaceComboBox.setEditable(True)
        self.namespaceComboBox.lineEdit().setPlaceholderText('Clear Namespace')

        self.namespaceComboBox.addItems([':'] + cmds.namespaceInfo(lon=True, recurse=True))
        
        self.okBut = QtWidgets.QPushButton('Apply')
        self.closeBut = QtWidgets.QPushButton('Cancel')
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addWidget(self.namespaceComboBox)
        
        butsLayout = QtWidgets.QHBoxLayout()
        butsLayout.setSpacing(5)
        butsLayout.addWidget(self.okBut)
        butsLayout.addWidget(self.closeBut)
        mainLayout.addLayout(butsLayout)
        
        mainLayout.addStretch()
        
        
    def _createConnections(self):
        self.closeBut.clicked.connect(self.close)
        self.okBut.clicked.connect(self._getNamespace)
        
        
    def _getNamespace(self):
        text = self.namespaceComboBox.currentText()
        self.selectedNamespace.emit(text)
        self.close()
        

    
        
class NamespaceWidget(QtWidgets.QWidget):
    
    namespaceClicked = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._createWidgets()
        self._createLayouts()
        self._createConnections()
        
        self.showNamespaceTag = True
        
    def _createWidgets(self):
        self.namespaceLabel    = QtWidgets.QLabel('Namespace:')
        self.namespaceComboBox = QtWidgets.QComboBox()
        higth = self.namespaceComboBox.sizeHint().height()
        self.namespaceComboBox.setItemDelegate(CustomDelegate(self, 25))
        self.namespaceComboBox.setFixedWidth(120)
        self.updateNamespace()
        
        self.updateBut = QtWidgets.QPushButton()
        self.updateBut.setToolTip('Update Namespace')
        self.updateBut.setFixedSize(higth-1, higth-1)
        self.updateBut.setIcon(QtGui.QIcon(':refresh.png'))
        
    def _createLayouts(self):
        mainLayout = QtWidgets.QHBoxLayout(self)
        mainLayout.setSpacing(2)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.namespaceLabel)
        mainLayout.addWidget(self.namespaceComboBox)
        mainLayout.addWidget(self.updateBut)
        mainLayout.addWidget(QtWidgets.QLabel(' '))
        
    def _createConnections(self):
        self.updateBut.clicked.connect(self.updateNamespace)
        self.namespaceComboBox.currentIndexChanged.connect(lambda i: self.namespaceClicked.emit(self.namespaceComboBox.itemText(i)))
        #self.namespaceComboBox.currentIndexChanged.connect(lambda i: print(self.namespaceComboBox.itemText(i)))
    
    def namespaceText(self):
        return [self.namespaceComboBox.itemText(i) for i in range(self.namespaceComboBox.count())]
        
    def selectItem(self, namespace):
        index = self.namespaceComboBox.findText(namespace)
        if index != -1:
            self.namespaceComboBox.setCurrentIndex(index)
        
    def updateNamespace(self):
        currentNamespace = self.namespaceComboBox.currentText()
        
        '''
        Temporarily block the currentIndexChanged signal 
        Avoid triggering multiple times when the update button is clicked!
        '''
        self.namespaceComboBox.blockSignals(True)
        self.namespaceComboBox.clear()

        namespaces = [':', 'separator'] + cmds.namespaceInfo(lon=True, recurse=True)
        self.namespaceComboBox.addItems(namespaces)
        
        '''
        https://stackoverflow.com/questions/38915001/disable-specific-items-in-qcombobox
        '''
        model = self.namespaceComboBox.model()
        item = model.item(1) # get separator item
        if item: item.setFlags(QtCore.Qt.NoItemFlags)
            
        # for i in range(model.rowCount()):
        #     item = model.item(i)
        #     if item.text() == 'separator':
        #         item.setFlags(QtCore.Qt.NoItemFlags)
        
        for i in range(self.namespaceComboBox.count()):
            itemText = self.namespaceComboBox.itemText(i)
            if itemText == 'separator':
                continue
            self.namespaceComboBox.setItemData(i, itemText, QtCore.Qt.ToolTipRole)
            
            #elidedText = self.namespaceComboBox.fontMetrics().elidedText(itemText, QtCore.Qt.ElideRight, 80)
            #self.namespaceComboBox.setItemData(i, elidedText, QtCore.Qt.DisplayRole)
        '''
        Unblock the signals
        '''    
        self.namespaceComboBox.blockSignals(False) 
 
        index = self.namespaceComboBox.findText(currentNamespace if currentNamespace in namespaces else ':')
        if index != -1:
            self.namespaceComboBox.setCurrentIndex(index)
            
    def hideNamespace(self, count):
        if count > 1 and self.showNamespaceTag:
            self.show()
        else:
            self.hide()
            
    