# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 12:29:06 2013

@author: snoozerworks
"""

from PyQt4.QtGui import QGraphicsView 
from PyQt4 import QtCore, QtGui, QtSvg 

from ComponentBase import ComponentBase
import svgwrite


#from pympler import tracker
#tr = tracker.SummaryTracker()

class SvgView(QGraphicsView):
  schematic_width   = 200
  schematic_height  = 200
  pcb_width         = 50
  pcb_height        = 50
  schematic_fname   = "schematic.svg"
  pcb_fname         = "pcb.svg"
  
  def __init__(self, parent):
    super(SvgView, self).__init__(parent)
    self._cmp       = None # The component to draw
    self._renderer  = None
    self._bounds    = None
    
    # Create background grid
    self.s_bg = self._init_schema_bg()
    self.p_bg = self._init_pcb_bg()


  def _init_schema_bg(self):
    """ Create schematics background. """
    h = SvgView.schematic_height
    w = SvgView.schematic_width

    g = svgwrite.container.Group(stroke="#BBBBBB", stroke_width="0.2mm") 
    s = round(w / 2.0 / 7.5)
    for i in range(-s,s):
      x = i * 7.5 + 7.5/2
      g.add(svgwrite.shapes.Line((x,"-100%"), (x, "100%"))) 
      
    s = round(h / 2.0 / 7.5)
    for i in range(-s,s):
      x = i * 7.5 + 7.5/2
      g.add(svgwrite.shapes.Line(("-100%", x), ("100%", x))) 
    return g
    

  def _init_pcb_bg(self):
    """ Create pcb background. """
    g = svgwrite.container.Group(stroke="#BBBBBB", stroke_width="0.1mm") 
    g.add(svgwrite.shapes.Line((0,"-100%"), (0,"100%"))) 
    g.add(svgwrite.shapes.Line(("-100%",0), ("100%",0))) 
    return g
    

  def set_component(self, cmp):
    """ Set a component to render on the viewport. """
    assert isinstance(cmp, ComponentBase)
    self._cmp = cmp
    

  def build_schematic(self, background=True):
    if background:
      self._cmp.build_schematic(self.s_bg)
    else:
      self._cmp.build_schematic()
    self._set_bounds("schematic")
#    tr.print_diff()
    

  def build_pcb(self, background=True):
    if background:
      self._cmp.build_pcb(self.p_bg)
    else:
      self._cmp.build_pcb()
    self._set_bounds("pcb")


  def paintEvent(self, e):
    """ Overloads the QGraphicsView method. Makes the svg appear. """
    # Draw component on the SvgView  
    
    painter   = QtGui.QPainter()   
    painter.begin(self.viewport())

    # Scale viewport to fit contents of the svg 
    bs  = self._bounds.size()
    vps = painter.viewport().size()
    
    bs.scale(vps.width()*0.9, vps.height()*0.9, QtCore.Qt.KeepAspectRatio)    
    x   = (vps.width()-bs.width()) / 2
    y   = (vps.height()-bs.height()) / 2
    
    painter.setViewport(QtCore.QRect(QtCore.QPoint(x,y), bs.toSize()))
    
    self._renderer.render(painter)
    painter.end()

    
  def _set_bounds(self, bound_elem=""):
    """
    An ugly way to set the svg bounds by using QSvgRenderer.boundsOnElement().
    """
    if bound_elem == "schematic":
      dwg = self._cmp.drw_sch
    elif bound_elem == "pcb":
      dwg = self._cmp.drw_pcb
    else:
      raise Exception("Unknown drawing bound")
    
    xml       = bytearray(dwg.tostring().encode('utf-8'))  # The svg as a xml string
    renderer  = QtSvg.QSvgRenderer(xml)                         # Create svg renderer
    assert renderer.isValid()
    
    bounds  = renderer.boundsOnElement(bound_elem)
    renderer.setViewBox(bounds)
    x       = round(bounds.x(), 4)
    y       = round(bounds.y(), 4)
    h       = round(bounds.height(), 4)
    w       = round(bounds.width(), 4)
    
    dwg.attribs["height"] = "%0.4fmm" % h
    dwg.attribs["width"]  = "%0.4fmm" % w
    dwg.viewbox(x,y,w,h)
    
    self._renderer  = renderer
    self._bounds    = bounds
    

  def export_svg(self):
    """ 
    Export pcb and schematic to svg to a files.
    """    
    directory = QtGui.QFileDialog.getExistingDirectory(self, "Directory for svg export")
    if directory == "":
      return
    
    print("Export schematic to " + directory + "\\" + SvgView.schematic_fname)
    print("Export pcb to " + directory + "\\" + SvgView.pcb_fname)

    self.build_schematic(False)
    self._cmp.drw_sch.saveas(directory + "\\" + SvgView.schematic_fname)
    
    self.build_pcb(False)
    self._cmp.drw_pcb.saveas(directory + "\\" + SvgView.pcb_fname)
