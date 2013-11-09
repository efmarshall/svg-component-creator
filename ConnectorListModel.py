# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 22:06:30 2013

@author: snoozerworks
"""

from PyQt4 import QtCore
from PyQt4.QtCore import Qt, QAbstractTableModel
#from ConnectorBase import ConnectorBase as Con
from ComponentBase import ComponentBase as Cmp


class ConnectorListModel(QAbstractTableModel):
  #  schematic_col_map = {0:"s_pin", 1:"s_lbl", 2:"s_dir", 3:"s_before", 4:"s_after"}
  #  pcb_col_map       = {0:"p_pin", 1:"s_lbl", 2:"p_dir", 3:"p_shape",  4:"p_dx", 5:"p_dy", 6:"p_dim1", 7:"p_dim2"}
  schematic_col_map = {0:"s_label", 1:"s_dir", 2:"s_before", 3:"s_after"}
  pcb_col_map       = {0:"s_label", 1:"p_dir", 2:"p_shape",  3:"p_dx", 4:"p_dy", 5:"p_dim1", 6:"p_dim2"}
  
  headings = {"s_pin"   : "Pin", 
              "s_label" : "Label", 
              "s_dir"   : "Dir",
              "s_before": "Bef.",
              "s_after" : "Aft.",
              "p_pin"   : "Pin",
              "p_dir"   : "Dir",
              "p_shape" : "Shape",
              "p_dx"    : " dx",
              "p_dy"    : " dy",
              "p_dim1"  : " d1",
              "p_dim2"  : " d2"}
              
              
  def __init__(self):
    super().__init__()
    self.cmp      = None
    self._col_map = {}
    

  def set_col_mapping(self, mapping):
    """ 
    Set connector columns to show. 
    The mapping is a dict key/value as column number/component attribute name.
    """
    l1 = len(self._col_map)
    l2 = len(mapping)
    if l1>l2:
      # Remove from column l2 to l1-1
      self.beginRemoveColumns(QtCore.QModelIndex(), l2, l1-1)
      self._col_map = mapping
      self.endRemoveColumns()
    elif l1<l2:
      # Add from column l1 to l2-1
      self.beginInsertColumns(QtCore.QModelIndex(), l1, l2-1)
      self._col_map = mapping
      self.endInsertColumns()
    else:
      pass


  def set_component(self, cmp):
    """ Assign the fritzing component to the model. """
    assert isinstance(cmp, Cmp)
    self.beginResetModel()
    self.cmp = cmp
    self.endResetModel()


  # Overloaded abstract methods
  def rowCount(self, parent=QtCore.QModelIndex()):
    return len(self.cmp.connectors)
  
  
  def columnCount(self, parent=QtCore.QModelIndex()):
    return len(self._col_map)

  
  def data(self, index, role = Qt.DisplayRole):
    if role not in (Qt.DisplayRole, Qt.EditRole):
      return None
      
    if not index.isValid():
      print("data() - invalid index given")
      return None

    r     = index.row()
    c     = self._col_map[index.column()]
    conn  = self.cmp.connectors[r]
    
    if c=="p_dim1":
      return float(conn.p_elm.dim[0])
    elif c=="p_dim2":
      return float(conn.p_elm.dim[1])      
    elif c=="p_dx":
      return float(conn.p_elm.pos[0])      
    elif c=="p_dy" :
      return float(conn.p_elm.pos[1])      
    elif c=="p_dir" :
      return conn.p_elm.rot

    else:
      return getattr(conn, c)

    
  def headerData(self, section, orientation, role):
    if (role !=  Qt.DisplayRole):
      return None

    if (orientation != Qt.Horizontal):
      return "%d" % section
    
    c = self._col_map[section]
    return ConnectorListModel.headings[c]
 

  
  # To enabling model editing...
  
  def setData(self, index, val, role=Qt.EditRole):
    if index.isValid()==False or role!=Qt.EditRole:
      return False
    
    r   = index.row()
    c   = self._col_map[index.column()]
    con = self.cmp.connectors[r]
    if c == "p_dim1":
      con.p_elm.dim = (val, con.p_elm.dim[1])
    elif c == "p_dim2":
      con.p_elm.dim = (con.p_elm.dim[0], val)
    elif c == "p_dx":
      con.p_elm.pos = (val, con.p_elm.pos[1])
    elif c == "p_dy":
      con.p_elm.pos = (con.p_elm.pos[0], val)
    elif c == "p_dir":
      con.p_elm.rot = val
    elif c == "s_dir":
      con.s_dir = val
      self.cmp.body_resize()
    else:
      setattr(con, c, val)

    index_last = self.index(r,self.columnCount()-1)
    self.dataChanged.emit(index, index_last)
    return True   
  
  
  def flags(self, index):
    return  Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
  
  
  def insertRow(self, row, parent=QtCore.QModelIndex()):    
    self.beginInsertRows(parent, row, row)
    self.cmp.add_connector()   
    self.endInsertRows()
    return True
  
  
  def removeRow(self, pos, parent=QtCore.QModelIndex()):
    self.beginRemoveRows(parent, pos, pos)
    self.cmp.remove_connector(pos)
    self.endRemoveRows()
    return True

