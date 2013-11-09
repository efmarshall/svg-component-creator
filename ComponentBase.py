# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 12:43:01 2013

@author: snoozerworks
"""

import abc
import svgwrite
import re
from ConnectorBase import ConnectorBase as Con

SVGWRITE_DEBUG = False

class ComponentBase(metaclass=abc.ABCMeta):
  """ This is the base clas for all components """

  font_size_label = 6     # 6 mm
  stroke_width    = 0.847 # 0,847 mm
  MOUNT_HYB       = 0     # Hybrid mount. Not yet supported by Fritzing.
  MOUNT_SMD       = 1     # SMD mount
  MOUNT_THT       = 2     # THT mount
  MOUNTS          = (MOUNT_HYB, MOUNT_SMD, MOUNT_THT)
  
  DRW_SCH_DEFAULTS = {"font_family"     : "OCRA",
                      "fill"            : "none",
                      "stroke"          : "#000000",
                      "stroke-width"    : stroke_width,
                      "stroke-linecap"  : "round",
                      "stroke-linejoin" : "round"}
  
  def __init__(self):
    self.connectors = list() # Pins o pads
    self._mount     = ComponentBase.MOUNT_THT
    self._part_name  = "IC"
    
    self.drw_sch  = svgwrite.Drawing(profile="tiny", debug=SVGWRITE_DEBUG)
    self.drw_sch.update(ComponentBase.DRW_SCH_DEFAULTS)
    
    grid          = self.drw_sch.add(self.drw_sch.g())
    schematic     = self.drw_sch.add(self.drw_sch.g(id="schematic"))
    self.sch_layers = {"pins" : schematic.add(self.drw_sch.g()),  # For component connectors
                       "body" : schematic.add(self.drw_sch.g()),  # For component body
                       "grid" : grid }                   # For grid (not exported)
    
    self.drw_pcb    = svgwrite.Drawing(profile="tiny", debug=SVGWRITE_DEBUG)
    self.pcb_layers = {
      "copper1"     : self.drw_pcb.g(id="copper1"), # Copper top
      "copper0"     : self.drw_pcb.g(id="copper0"), # Copper bottom
      "silkscreen"  : self.drw_pcb.path(id           = "silkscreen", 
                               transform    = "scale(1,-1)",
                               d            = "M 0 0",
                               fill         = "none",
                               stroke       = "#CCCCCC",
                               stroke_width = "0.5"),
      "keepout"     : self.drw_pcb.g(id="keepout", transform="scale(1,-1)"),
      "outline"     : self.drw_pcb.g(id="outline", transform="scale(1,-1)")
    }

    
  @property
  def part_name(self):
    return self._part_name
    
    
  @part_name.setter
  def part_name(self, value):
    self._part_name = value
    
    
  @property
  def mount(self):
    """ Get mount type to surface mount (SMD) or through hole type (THT). """
    return self._mount
    
  @mount.setter
  def mount(self, mount):
    """ Set mount type to surface mount (SMD) or through hole type (THT). """
    assert mount in (ComponentBase.MOUNTS)
    if mount==self.MOUNT_HYB:
      raise Exception("Unsupported mount.")
    self._mount = mount
    self._check_mount()
    
    
  @property    
  def silkscreen_commands(self):
    """ Get all path segment commands of silkscreen. """
    return self.pcb_layers["silkscreen"].commands

  @silkscreen_commands.setter
  def silkscreen_commands(self, commands):
    """ Set path segment commands for silkscreen. No data validation. """
    self.pcb_layers["silkscreen"].commands = commands


  def _check_mount(self):
    """ Check and force all connectors to have the correct mount type. """
    if self.mount == ComponentBase.MOUNT_SMD:
      valid_shapes  = [Con.SHAPE_PAD]
      default_shape = Con.SHAPE_PAD
    elif self.mount == ComponentBase.MOUNT_THT:
      valid_shapes  = [Con.SHAPE_HOLE, Con.SHAPE_RHOLE]
      default_shape = Con.SHAPE_HOLE
      
    for con in self.connectors:
      if con.p_shape not in valid_shapes:
        con.p_shape = default_shape
        

  def add_connector(self):
    """ Add a connector to the component and return it. """
    c         = Con()
    c.no      = len(self.connectors)
    c.s_pin   = c.no
    c.p_pin   = c.no
    c.s_label = "C%d" % (c.no)
    if self.mount == self.MOUNT_THT:
      c.p_shape = Con.SHAPE_HOLE
    elif self.mount == self.MOUNT_SMD:
      c.p_shape = Con.SHAPE_PAD
    
    self.sch_layers["pins"].add(c.s_svg)
    self.pcb_layers["copper1"].add(c.p_svg)
    self.connectors.append(c)
    

  def remove_connector(self, n):
    """ Remove a connector """
    no = self.connectors[n].no
    del self.pcb_layers["copper1"].elements[no]
    del self.sch_layers["pins"].elements[no]
    del self.connectors[n]

    
#  def silkscreen(self):
#    """ Return the silkscreen svg path element """
#    return self.pcb_layers["silkscreen"]


  def set_silkscreen_segment(self, command, i=-1):
    """ 
    Add, remove or update a silkscreen path segment. 
    Segment number i>=0 will be removed if command is an empty string. 
    Segment number i>=0 will be updated if command is a valid and non-empty.    
    A segment may be added (appended) by providing a valid command string.
    
    A valid segement command is any of the svg path d attribute shapes. 
    """
    assert(isinstance(command, str))
    
    if i<0:
      # Add segment
      command = ComponentBase.validate_path_cmd(command)
      if not command:
        return False
      self.pcb_layers["silkscreen"].push(command)
    elif command=="":
      # Remove segment
      try:
        del self.pcb_layers["silkscreen"].commands[i] 
      except IndexError:
        return False
    else:
      # Update segment
      try:
        self.pcb_layers["silkscreen"].commands[i] = command
      except IndexError:
        return False
      
    return True
    

  def validate_path_cmd(txt):
    """
    Return the string txt if it is a svg path command.
    If string is invalid return False. 
    """
    
    nf    = "([-+]?([0-9]*\.[0-9]+|[0-9]+))"  # Expression matching a number
    
    # Expressions for validating svg path commands (the "d" attribute)
    expr  = (
      "^[lLmMtT](\s+%s){2}$" % (nf), # Line, move and smooth quadratic beizer commands
      "^[hHvV]\s+%s$" % (nf),        # Horisontal and vertical commands
      "^[cC](\s+%s){6}$" % (nf),     # Cubic beizer command
      "^[qQsS](\s+%s){4}$" % (nf),   # Quadratic and Smooth beizer command
      "^[aA](\s+%s){3}\s[0-1]\s[0-1](\s+%s){2}$" % (nf,nf), # Eliptical arc command
      "^[zZ]$")                      #  Close path command

    for val in expr:
      m = re.match(val, txt)
      if m:
        return m.group(0)
        
    return False
    
    
  def get_state(self):
    """
    Return a dict describing the state of the component. Useful for saving 
    object data to a file.
    The state can be reloaded using set_state().    
    """
    #print("ComponentBase.get_state")
    state = {"part_name"            : self.part_name,
             "mount"                : self.mount,
             "silkscreen_commands"  : self.pcb_layers["silkscreen"].commands,
             "connectors"           : [c.get_state() for c in self.connectors] }
    return state             
    

  def set_state(self, state):
    """ Set state as returned by get_state(). """
    #print("ComponentBase.set_state")
    for k,v in state.items():
      #print("  Set {:14s} to {:s}".format(k,str(v)))
      if k == "connectors":
        for con_state in v:
          self.add_connector() 
          self.connectors[-1].set_state(con_state)
      else:
        setattr(self, k, v)

    
    
  @abc.abstractclassmethod
  def body_resize(self):    
    """ Resize size of schematic body. """
    
    
  @abc.abstractclassmethod
  def build_schematic(self, bg=None):
    """ Build the component svg g schematic element. """


  @abc.abstractclassmethod
  def build_pcb(self, bg=None):
    """ Build the component svg g pcb element. """

