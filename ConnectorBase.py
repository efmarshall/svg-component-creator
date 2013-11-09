# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 12:47:52 2013

@author: snoozerworks
"""

import abc
import svgwrite as SW
import math

class ConnectorBase:
  """ This is the base class for all connectors (male, female and pads.) """
  font_family     = "OCRA"
  font_size_label = 3.5     # 3,5mm
  font_size_chr   = 2.5     # 2,5mm
  
  SHAPE_HOLE  = "THT hole"  
  SHAPE_RHOLE = "THT square"
  SHAPE_PAD   = "SMD pad"
  DIR_E   = "E"
  DIR_N   = "N"
  DIR_W   = "W"
  DIR_S   = "S"

  
  _shapes = (SHAPE_HOLE, SHAPE_RHOLE, SHAPE_PAD)  # PCB shapes
  _dirs   = (DIR_E, DIR_S, DIR_W, DIR_N)          # Connector directions
  _rot    = {DIR_E: 0,
             DIR_N: -90,
             DIR_W: -180,
             DIR_S: -270}    

  
  def __init__(self):
    self.no       = -99      # Connector number

    self.s_svg    = SW.container.Group()
    self._init_svg()
    self.p_svg    = SW.container.Group()
    self._p_elm   = None

    # Set default shape    
    self.p_shape  = ConnectorBase.SHAPE_HOLE
    self.s_pin    = -99 # Connector position on schematic
    self.s_label  = "C" # Connector label
    self.s_before = 1   # Space before connector
    self.s_after  = 0   # Space after connector
    self.s_dir    = "E" # Connector direction
    
    

  @property
  def p_elm(self):
    return self._p_elm
     


  @property
  def p_pin(self):
    return self._p_elm.num

  @p_pin.setter
  def p_pin(self, value):
    self._p_elm.num = value


  
  @property
  def p_shape(self):
    return self._p_shape
  
  @p_shape.setter
  def p_shape(self, value):
    del self.p_svg.elements[:]
    
    if value == self.SHAPE_PAD: # Rectangular smd pad 
      self._p_elm = self.p_svg.add(ConnSvgPad(self._p_elm))
    elif value == self.SHAPE_HOLE: # Round tht hole
      self._p_elm = self.p_svg.add(ConnSvgHole(self._p_elm))
    elif value == self.SHAPE_RHOLE: # Rectangular tht hole
      self._p_elm = self.p_svg.add(ConnSvgRhole(self._p_elm))
    else:
      raise Exception("Unsupported pcb connector shape ", str(value))    
    self._p_shape = value  



  @property 
  def s_dir(self):
    return self._s_dir
    
  @s_dir.setter
  def s_dir(self, value):
    value = value.upper()  
    if value not in ConnectorBase._dirs:
      return
    self._s_dir = value



  @property
  def s_label(self):
    return self._s_label
    
  @s_label.setter
  def s_label(self, value):
    self._s_label = value
    if len(value) > 0 and value[0] == "*":
      self.s_svg.elements[1].text = ""
    else:
      self.s_svg.elements[1].text = value
    
    
    
  @property
  def s_pin(self):
    return self._s_pin
    

  @s_pin.setter
  def s_pin(self, value):
    self._s_pin = value
    self.s_svg.elements[0].elements[0].attribs["id"] = "connector%dterminal" % value
    self.s_svg.elements[0].elements[1].attribs["id"] = "connector%dpin" % value
    self.s_svg.elements[1].text = "C%d" % int(value)



  def _init_svg(self):
    """ Initiate svg elements """
    length      = 7.5

    # Create pin and terminal elements
    g = self.s_svg.add(SW.container.Group())
    g.add(SW.shapes.Circle(center = (length, 0), 
                           r      = 0.4235, 
                           id     = "def_terminal",
                           fill   = "none",
                           stroke = "none" ))
    g.add(SW.shapes.Line(start = (0, 0),
                         end   = (length, 0),
                         id     = "def_pin"))

    # Add text label 
    t = self.s_svg.add(SW.text.Text("lbl", 
                                    stroke      = "none", 
                                    fill        = "#000000", 
                                    font_size   = ConnectorBase.font_size_label )) 
    t.attribs["y"] = 1.25
    
    
    
  def set_pcb_pos(self, x=0, y=0):
    try:
      del self.p_svg.attribs["transform"]
    except KeyError:
      pass
    self.p_svg.translate(round(x, 4), round(-y, 4))
    

      
  def set_schematic_pos(self, dx=0, dy=0):
    """ Get the svg for the connector """
    rot     = {"E":0, "N":-90, "W":-180, "S":-270}
    
    pin = self.s_svg.elements[0]  # pin element
    matrix  = _TransformMatrix(dx, -dy)
    if rot[self.s_dir] != 0:
      matrix.rot = rot[self.s_dir]
      
    pin.update({ "transform": matrix.tostring() })

    t       = self.s_svg.elements[1]  # text element
    matrix  = _TransformMatrix(dx, -dy)
    if self.s_dir == "E":     # East
      t.update({"text-anchor" : "end", "x" : -2})
    elif self.s_dir == "N":   # North
      t.update({"text-anchor" : "start", "x" : 2})
      matrix.rot = 90
    elif self.s_dir == "W":   # West
      t.update({"text-anchor" : "start", "x" : 2})
    elif self.s_dir == "S":   # South
      t.update({"text-anchor" : "end", "x" : -2})
      matrix.rot = 90
    
    t.update({ "transform": matrix.tostring() })


  def get_state(self):
    """
    Return a dict describing the state of the component. Useful for saving 
    object data to a file.
    The state can be reloaded using set_state().    
    """
    #print("ConnectorBase.get_state")   
    state = {"no"       : self.no,
             "s_after"  : self.s_after,
             "s_before" : self.s_before,
             "s_dir"    : self.s_dir,
             "s_label"  : self.s_label,
             "s_pin"    : self.s_pin,
             "p_pin"    : self.p_pin,
             "p_shape"  : self.p_shape
             }
    return state
             
             
  def set_state(self, state):
    """ Set state as returned by get_state(). """
    #print("ConnectorBase.set_state")   
    for k,v in state.items():
      #print("  Set {:10s} to {:s}".format(k,str(v)))
      setattr(self, k, v)


    
class _TransformMatrix:
  """ Class representing a svg transformation. """
  def __init__(self, dx=0, dy=0, rot=0):
    self._matrix = [0, 0, 0, 0, 0, 0] # matrix(a,b,c,d,e,f)
    self.dx      = dx
    self.dy      = dy
    self.rot     = rot
    
  @property
  def rot(self):
    return self._r
    
  @rot.setter
  def rot(self, val):
    self._r = val % 360
    self._matrix[0] =  math.cos(val*math.pi/180.0)
    self._matrix[1] =  math.sin(val*math.pi/180.0)
    self._matrix[2] = -self._matrix[1]
    self._matrix[3] =  self._matrix[0]

  @property
  def dx(self):
    return self._matrix[4]
  @dx.setter
  def dx(self, val):
    self._matrix[4] = val

  @property
  def dy(self):
    return self._matrix[5]
  @dx.setter
  def dy(self, val):
    self._matrix[5] = val
    
  def tostring(self):
    matrix = [str(round(v,4)) for v in self._matrix]
    return "matrix(" + ", ".join(matrix) + ")"
      

    
  
class ConnSvgBase:
  def __init__(self, source=None):
    """ 
    Base class for svg connector element. 
    Copies attributes from instance source of ConnSvgBase if present.
    """
    self._num = 0
    self._dim = (0, 0)
    self._pos = (0, 0)  # Translate (dx, dy)
    self._rot = "E"     # Rotate rot
    
    if isinstance(source, ConnSvgBase):
      self.copy_from(source)


  def copy_from(self, source):
    """ Copy number and position from old to new connector. """
    assert isinstance(source, ConnSvgBase)
    self.num = source.num
    self.pos = source.pos
    self.rot = source.rot
    

  @property
  def dim(self):
    return self._dim
    
  @dim.setter
  def dim(self, value):
    assert isinstance(value, tuple)
    self._dim = value
    self._update_dim()


  @property
  def rot(self):
    return self._rot
    
  @rot.setter
  def rot(self, value):
    value = value.upper()
    rot   = {"E":0, "N":-90, "W":-180, "S":-270}    
    if value not in rot:
      return      
    self._rot = value
    self._update_pos()


  @property
  def num(self):
    return self._num
    
  @num.setter
  def num(self, value):
    self._num = int(value)
    self._update_num()


  @property
  def pos(self):
    return self._pos
    
  @pos.setter
  def pos(self, value):
    """
    Translate and rotate connector. 
    Value is a tuple for trasformation (x, y, rotation)
    """    
    self._pos = value
    self._update_pos()


  def _update_pos(self):    
    """ Translate and rotate connector. """    
    try:
      del self.attribs["transform"]  
    except KeyError:
      pass
    rot     = {"E":0, "N":-90, "W":-180, "S":-270}
    matrix  = _TransformMatrix(self._pos[0], -self._pos[1], rot[self._rot])
    self.update({ "transform": matrix.tostring() })


  @abc.abstractclassmethod
  def _update_dim(self):
    """ Update dimensions of svg element. """
    pass

  @abc.abstractclassmethod
  def _update_num(self):
    """ Update id attribute of svg element. """
    pass



class ConnSvgHole(ConnSvgBase, SW.shapes.Circle):
  def __init__(self, *args, **kwargs):
    SW.shapes.Circle.__init__(self)
    ConnSvgBase.__init__(self, *args, **kwargs)
    self.dim = (0.9, 1.9)

  
  def _update_dim(self):
    radius = round((self._dim[0] + self._dim[1]) / 4, 4)
    sw     = round(abs(self._dim[0] - self._dim[1]) / 2, 4)
    self.update({"fill"         : "none",
                 "stroke"       : "#F7BD13",
                 "r"            : radius,
                 "stroke_width" : sw})   


  def _update_num(self):
    """ Update id attribute of svg element. """
    self.update({"id" : "connector%dpad" % self._num})



class ConnSvgRhole(ConnSvgBase, SW.container.Group):
  def __init__(self, *args, **kwargs):
    SW.container.Group.__init__(self)
    ConnSvgBase.__init__(self, *args, **kwargs)
    self.add(SW.shapes.Rect())
    self.add(SW.shapes.Circle())
    self.dim = (0.9, 1.9)
    
    
  def _update_dim(self):
    radius = round((self._dim[0] + self._dim[1]) / 4, 4)
    sw     = round(abs(self._dim[0] - self._dim[1]) / 2, 4)
    self.elements[0].update({ "fill"          : "none",
                              "stroke"        : "#F7BD13",
                              "x"             : -radius,
                              "y"             : -radius,
                              "height"        : 2*radius,
                              "width"         : 2*radius,
                              "stroke_width"  : sw })
    self.elements[1].update({ "fill"          : "none",
                              "stroke"        : "#F7BD13",
                              "r"             : radius,
                              "stroke_width"  : sw })
  
  
  def _update_num(self):
    """ Update id attribute of svg element. """
    self.update({"id" : "connector%dpad" % self._num})
    
   
   
class ConnSvgPad(ConnSvgBase, SW.shapes.Rect):
  def __init__(self, *args, **kwargs):
    SW.shapes.Rect.__init__(self)
    ConnSvgBase.__init__(self, *args, **kwargs)
    self.dim = (1.6, 1.0)
  
  
  def _update_dim(self):
    w = round(self._dim[0], 3)
    h = round(self._dim[1], 3)
    self.update({"fill"   : "#F7BD13",
                 "stroke" : "none",
                 "x"      : -w/2,
                 "y"      : -h/2,
                 "height" : h,
                 "width"  : w})


  def _update_num(self):
    """ Update id attribute of svg element. """
    self.update({"id" : "connector%dpad" % self._num})
