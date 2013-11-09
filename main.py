#!/usr/bin/python3.2
# -*- coding: utf-8 -*-

"""
Created on Fri Sep 20 22:14:26 2013

@author: snoozerworks
"""
import sys

from ConnectorBase import ConnectorBase 
from ComponentBase import ComponentBase
from ComponentRect import ComponentRect
from PyQt4 import QtGui 
from PyQt4.QtCore import QUrl
from SVGCompCreator import Ui_MainWindow
from HelpDialog import Ui_Dialog
from ConnectorListModel import ConnectorListModel 
import pickle


class StartQT4(QtGui.QMainWindow):
  
  def __init__(self, parent=None):
    QtGui.QWidget.__init__(self, parent)
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)
    
    # Create datamodel for the QT table views
    self.mdl = ConnectorListModel()
    self.mdl.set_col_mapping(ConnectorListModel.schematic_col_map)
    # Add a fritzing component to it
    self.mdl.set_component(ComponentRect())
    # Connect model signals
    self.mdl.dataChanged.connect(self.refresh_svg_canvas)
    self.mdl.modelReset.connect(self.on_model_reset)

    # Set a component to draw
    self.ui.svg_canvas.set_component(self.mdl.cmp)

    # Create schematic table view.
    self.ui.tbl_schematic.setModel(self.mdl)
    self.ui.tbl_schematic.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
    self.ui.tbl_schematic.show()
    # Create pcb table view.
    self.ui.tbl_pcb.setItemDelegateForColumn(2, ComboDelegate(self))
    self.ui.tbl_pcb.setModel(self.mdl)
    self.ui.tbl_pcb.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
    self.ui.tbl_pcb.show()
    
    # Setup the silkscreen line editor    
    self.ui.txt_silkscreen.set_component(self.mdl.cmp)
    self.ui.txt_silkscreen.set_list(self.ui.list_path_cmds)
    
    # Set text validators
    self.ui.txt_label.setText(self.mdl.cmp.part_name)
    self.ui.txt_spacing_h.setText("%0.3f" % self.mdl.cmp.p_spacing_h)
    self.ui.txt_spacing_v.setText("%0.3f" % self.mdl.cmp.p_spacing_v)
    self.ui.txt_spacing_h.setValidator(QtGui.QDoubleValidator(0, 50, 3))
    self.ui.txt_spacing_v.setValidator(QtGui.QDoubleValidator(0, 50, 3))
    
    # Connect ui signals (schematics tab)
    self.ui.spnbox_pincount.valueChanged.connect(self.on_pincount_change)
    self.ui.spn_add_height.valueChanged.connect(self.on_body_height_add)
    self.ui.spn_add_width.valueChanged.connect(self.on_body_width_add)
    self.ui.txt_label.textEdited.connect(self.on_name_change)
    
    # Connect ui signals (pcb tab)
    self.ui.txt_spacing_v.textEdited.connect(self.on_pcb_v_spacing_changed)
    self.ui.txt_spacing_h.textEdited.connect(self.on_pcb_h_spacing_changed)
    self.ui.radio_smd.clicked.connect(self.on_mount_changed)
    self.ui.radio_tht.clicked.connect(self.on_mount_changed)
    
    # Connect ui signals (silkscreen tab)
    self.ui.txt_silkscreen.segmentsChanged.connect(self.refresh_svg_canvas)
    
    # Connect other signals
    self.ui.actionSave.triggered.connect(self.on_save)
    self.ui.actionLoad.triggered.connect(self.on_load)
    self.ui.actionExport.triggered.connect(self.ui.svg_canvas.export_svg)
    self.ui.actionHelp.triggered.connect(self.on_help)
    self.ui.tabWidget.currentChanged.connect(self.on_change_tab)

    
    self.refresh_svg_canvas()

  
  def refresh_svg_canvas(self):
    """ Build and display svg view for current tab. """
    if self.ui.tabWidget.currentIndex() == 0:
      self.ui.svg_canvas.build_schematic()
      self.ui.svg_canvas.viewport().update()
    elif self.ui.tabWidget.currentIndex() in (1,2):
      self.ui.svg_canvas.build_pcb()
      self.ui.svg_canvas.viewport().update()
    else:
      raise Exception("Unknown view to draw")


  def on_model_reset(self):
    """ Reload all valus from model to show in UI elements. """
    cmp = self.mdl.cmp
    ui  = self.ui

    cmp.pcb_layers["silkscreen"].attribs["stroke-width"] = "0.5"
    # Set values on schematic tab
    ui.txt_label.setText(cmp.part_name)
    ui.spnbox_pincount.setValue(len(cmp.connectors))
    ui.spn_add_width.setValue(cmp.s_add_width)
    ui.spn_add_height.setValue(cmp.s_add_height)

    # Set values on pcb tab
    ui.txt_spacing_h.setText(str(cmp.p_spacing_h))
    ui.txt_spacing_v.setText(str(cmp.p_spacing_v))
    ui.radio_smd.setChecked(ComponentBase.MOUNT_SMD == cmp.mount)
    ui.radio_tht.setChecked(ComponentBase.MOUNT_THT == cmp.mount)

    # Set values on silkscreen tab
    self.ui.txt_silkscreen.set_component(cmp)
    
    # Refresh canvas
    self.ui.svg_canvas.set_component(cmp)
    self.refresh_svg_canvas()
    # Just to update table... ugly way but...
    self.ui.tabWidget.setCurrentIndex(1)
    self.ui.tabWidget.setCurrentIndex(0)



  def on_mount_changed(self, btn):
    """ Change mount. Only smd and tht supported by Friting. """
    sender = self.sender()
    if sender == self.ui.radio_smd:
      self.mdl.cmp.mount = ComponentBase.MOUNT_SMD
    elif sender == self.ui.radio_tht:
      self.mdl.cmp.mount = ComponentBase.MOUNT_THT
    self.refresh_svg_canvas()  
    
    
  def on_pincount_change(self, val):
    """ Add or remove component connectors. """
    if val<0:
      return
      
    rows = self.mdl.rowCount()
    if rows<val:  # Add rows
      for i in range(rows, val):
        self.mdl.insertRow(i)  
    elif rows>val:  # Remove rows
      for i in range(rows, val, -1):
        self.mdl.removeRow(i-1)
    self.refresh_svg_canvas()
      

  def on_change_tab(self, tab_no):
    """ Change tab. """
    self.refresh_svg_canvas()
    if tab_no == 0:
      self.mdl.set_col_mapping(ConnectorListModel.schematic_col_map)
    elif tab_no == 1:
      self.mdl.set_col_mapping(ConnectorListModel.pcb_col_map)

    
  def on_name_change(self, txt):
    """ Change name on component. """
    self.mdl.cmp.part_name = txt    
    self.refresh_svg_canvas()
    
   
  def on_pcb_v_spacing_changed(self, txt):
    """ Adds extra vertical spacing between schematic pins. """
    if self.ui.txt_spacing_v.hasAcceptableInput():
      self.mdl.cmp.p_spacing_v = float(txt.replace(",", "."))
      self.refresh_svg_canvas()
    else:
      self.ui.txt_spacing_v.setText("%0.3f" % self.mdl.cmp.p_spacing_v)
      

  def on_pcb_h_spacing_changed(self, txt):
    """ Adds extra horisontal spacing between schematic pins. """
    if self.ui.txt_spacing_h.hasAcceptableInput():
      self.mdl.cmp.p_spacing_h = float(txt.replace(",", "."))
      self.refresh_svg_canvas()
    else:
      self.ui.txt_spacing_h.setText("%0.3f" % self.mdl.cmp.p_spacing_h)


  def on_body_height_add(self, val):
    """ Adds extra height to schematic body """
    val = max(0, int(val))
    self.mdl.cmp.s_add_height = val
    self.refresh_svg_canvas()


  def on_body_width_add(self, val):
    """ Adds extra width to schematic body """
    val = max(0, int(val))
    self.mdl.cmp.s_add_width = val
    self.refresh_svg_canvas()
    
    
  def on_help(self):
    """ Display the online documentation in a help window. """
    d = QtGui.QDialog(parent=self)
    dialog = Ui_Dialog()
    dialog.setupUi(d)
    dialog.webView.setUrl(QUrl("http://code.google.com/p/svg-component-creator/wiki/UserDocumentation"))
    d.show()


  def on_save(self):
    """ Show a file dialogue and save componet to a file. """
    filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", "", "*.scc")
    if filename == "":
      return
    print("Save file ", filename)
    f = open(filename, mode="wb")
    state = self.mdl.cmp.get_state()
    pickle.dump(state, f, pickle.HIGHEST_PROTOCOL)
    f.close()    


  def on_load(self):
    """ Show a file dialoge and load saved componet. """
    filename = QtGui.QFileDialog.getOpenFileName(self, "Open file", "", "*.scc")
    print("Load file ", filename)
    if filename == "":
      return
    f   = open(filename, mode="rb")
    state = pickle.load(f)
    f.close()    
    cmp = ComponentRect()
    cmp.set_state(state)
    self.mdl.set_component(cmp)


class ComboDelegate(QtGui.QItemDelegate):
  """
  A delegate that places a QComboBox in every cell of the column to which 
  it's applied.
  """
  def __init__(self, parent):
    self._main_win = parent
    QtGui.QItemDelegate.__init__(self, parent)
      
      
  def createEditor(self, parent, option, index):
    combo = QtGui.QComboBox(parent)
    # List different shape depending on mount
    if self._main_win.mdl.cmp.mount == ComponentBase.MOUNT_THT:
      combo.addItem(ConnectorBase.SHAPE_HOLE)
      combo.addItem(ConnectorBase.SHAPE_RHOLE)
    else:
      combo.addItem(ConnectorBase.SHAPE_PAD)
    combo.currentIndexChanged.connect(self.currentIndexChanged)
    return combo
    
      
  def setEditorData(self, editor, index):
    editor.blockSignals(True)
    i = ConnectorBase._shapes.index(index.data())
    editor.setCurrentIndex(i)
    editor.blockSignals(False)

      
  def setModelData(self, editor, model, index):
    if editor.currentIndex() < 0:
      return
    model.setData(index, editor.currentText())

      
  def currentIndexChanged(self):
    self.commitData.emit(self.sender())
    

    
if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = StartQT4()
  myapp.show()
  sys.exit(app.exec_())