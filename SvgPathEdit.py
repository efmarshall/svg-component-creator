# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 23:44:13 2013

@author: snoozerworks
"""

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QLineEdit, QListWidget, QListWidgetItem
import ComponentBase as Cmp

class SvgPathEdit(QLineEdit):
  """
  This is an extionsion to a QLineEdit. It checks for inputs that can be used 
  as values for the d attribute of a svg path element. 
  By Calling setup() a QListWidget is supplied to list the path segments. 
  """
  segmentsChanged = pyqtSignal() # When a path segment is added, updated or removed
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._cmp  = None 
    self._list = None
    
  
  def set_component(self, component):
    """ Assign a ComponentBase object at which to set the silkscreen. """
    assert isinstance(component, Cmp.ComponentBase)
    self._cmp  = component 
    self.sync_list()
    

  def set_list(self, qlistwidget):
    """ Provide the qlistwidget (QListWidget) to list the path segments. """
    assert isinstance(qlistwidget, QListWidget)
    self._list = qlistwidget
    self._list.itemDoubleClicked.connect(self.on_remove)
    self._list.itemSelectionChanged.connect(self.on_select)
    
    
  def sync_list(self):
    """ Re-populate the QListWidget with path segments from component. """
    if self._list==None or self._cmp==None:
      return
    self._list.clear()
    cmds = self._cmp.silkscreen_commands
    for i in range(1,len(cmds)):
      QListWidgetItem(cmds[i], self._list)
  
    
  def keyPressEvent(self, event):
    """ 
    Validate path shape text when pressing Enter or Ctrl+Enter. If valid, add 
    shape to QListWidget and emit the addedSegment() signal. The segments may 
    be added, updated (Ctrl+Enter) or removed (Ctrl+Enter with empty input) 
    from the path.
    Up and Down key presses are passed on to the supplied QListWidget in order
    to select path segments.
    """
    row = self._list.currentRow()
    txt = self.text()
    if event.key()==Qt.Key_Enter:  
      event.accept()
      if (event.modifiers()==(Qt.ControlModifier|Qt.KeypadModifier) and
            row>=0): 
        
        if txt=="":
          # Remove selected segment
          self.on_remove(self._list.currentItem())
        elif self._cmp.set_silkscreen_segment(txt, row+1):
          # Update selected segment
          self._list.item(row).setText(txt)
          self.segmentsChanged.emit()
        
      elif self._cmp.set_silkscreen_segment(txt):
        # Add new segment
        QListWidgetItem(txt, self._list)
        self.segmentsChanged.emit()
      
    elif event.key() in (Qt.Key_Up, Qt.Key_Down):  
      self._list.keyPressEvent(event)
    
    return super().keyPressEvent(event)

    
  def on_select(self):
    """ Copy selected text to the line edit field. """
    try:
      item = self._list.selectedItems()[0]
    except IndexError:
      return
    else:
      self.setText(item.text())
      self.selectAll()
    

  def on_remove(self, item):
    """
    Remove the path segment which was double clicked and emit the 
    removedSegment() signal.
    """
    row = self._list.row(item)
    if self._cmp.set_silkscreen_segment("", row+1):
      x = self._list.takeItem(row)
      del x
      self.segmentsChanged.emit()

