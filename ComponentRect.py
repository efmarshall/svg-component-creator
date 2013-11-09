# -*- coding: utf-8 -*-
"""
Created on Sat Sep 21 13:06:40 2013

@author: snoozerworks
"""


from ComponentBase import ComponentBase as Cmp
from ConnectorBase import ConnectorBase as Con

class ComponentRect(Cmp):
  """ Represents a component with rectangular schematics. """
  
  def __init__(self):
    super().__init__()
    self.p_spacing_h    = 2.540   # Pcb rectangular pattern width
    self.p_spacing_v    = 2.540   # Pcb rectangular pattern width
    self._s_add_height  = 0       # Any extra height for schematic (multiples of 7,5mm)
    self._s_add_width   = 0       # Any extra width for schematic (multiples of 7,5mm)
    self._body_dim      = (0, 0)  # Width and height of schema body
    
    stroke        = Cmp.stroke_width
    width, height = (1, 1)
    body          = self.drw_sch.rect()
    text          = self.drw_sch.text(self._part_name)
    body.update({ "x"             : round((stroke-width)/2.0, 4),
                  "y"             : round((stroke-height)/2.0, 4),
                  "width"         : round(width-stroke, 4),
                  "height"        : round(height-stroke, 4) })
    text.update({ "font_size"     : Cmp.font_size_label,
                  "fill"          : "#000000",
                  "stroke"        : "none",
                  "text_anchor"   : "middle"})
                     
                     
    self.sch_layers["body"].add(body)
    self.sch_layers["body"].add(text)
    self.body_resize()
    
    
    
  @property
  def part_name(self):
    return self._part_name
    
    
  @part_name.setter
  def part_name(self, value):
    self._part_name = value
    self.sch_layers["body"].elements[1].text = value
    
    
  @property
  def s_add_height(self):
    return self._s_add_height  
    
  @s_add_height.setter
  def s_add_height(self, value):
    self._s_add_height = value
    self.body_resize()


  @property
  def s_add_width(self):
    return self._s_add_width  
    
  @s_add_width.setter
  def s_add_width(self, value):
    self._s_add_width = value
    self.body_resize()

    
  def add_connector(self):
    super().add_connector()
    self.body_resize()
    

  def remove_connector(self, n):
    super().remove_connector(n)
    self.body_resize()

    
  def body_resize(self):
    """ Calculate rectangle height and width of schematic body rectangle. """
    dims = {"E":0, "N":0, "W":0, "S":0}

    for c in self.connectors:
      dims[c.s_dir] += c.s_before + c.s_after
      
    height  = max(dims["E"], dims["W"]) + 1  # height
    width   = max(dims["N"], dims["S"]) + 1  # width
    width   = 7.5 * (max(width, 2) + self._s_add_width)
    height  = 7.5 * (max(height, 2) + self._s_add_height)
    self._body_dim = (width, height)
    
    stroke  = Cmp.stroke_width
    body    = self.sch_layers["body"].elements[0]
    body.update({ "x"      : round((stroke-width)/2.0, 4),
                  "y"      : round((stroke-height)/2.0, 4),
                  "width"  : round(width-stroke, 4),
                  "height" : round(height-stroke, 4) })



  def build_schematic(self, bg=None):
    """ Build the schematic svg. A background element bg may be added. """

    if bg:
      self.sch_layers["grid"].add(bg)
    else:
      del self.sch_layers["grid"].elements[:]


    # Place svg connector on drawing.
    width, height = self._body_dim
    y     = 0
    x     = 0 
    ofs   = {"E":0, "N":0, "W":0, "S":0} 

    for con in self.connectors:
      side = con.s_dir
      ofs[side] += con.s_before*7.5  # Space before connector
      
      # Place connectors (anti-clockewise).
      if   side == Con.DIR_E:
        y, x = (-height/2.0+ofs[side], width/2.0)
      elif side == Con.DIR_N:
        y, x = (height/2.0, width/2.0-ofs[side])
      elif side == Con.DIR_W:
        y, x = (height/2.0-ofs[side], -width/2.0)
      elif side == Con.DIR_S:
        y, x = (-height/2.0, -width/2.0+ofs[side])

      con.set_schematic_pos(x, y)
      ofs[side] += con.s_after*7.5 


  def build_pcb(self, bg=None):
    """ Build the pcb svg. A background element bg may be added. """
    del self.drw_pcb.elements[:]
    del self.pcb_layers["copper0"].elements[:]
    pcb = self.drw_pcb

    if bg:
      pcb.add(bg)    
      grp = pcb.add(pcb.g(id="pcb"))
    else:
      # Layers copper1, copper0 must be root elements in fritzing svg
      grp = pcb

    # Get connectors for directions east, nort, west and south
    conns = {Con.DIR_E : [],
             Con.DIR_N : [],
             Con.DIR_W : [],
             Con.DIR_S : []}
      
    conns[Con.DIR_E] = [c for c in self.connectors if c.p_elm.rot == Con.DIR_E]
    conns[Con.DIR_N] = [c for c in self.connectors if c.p_elm.rot == Con.DIR_N]
    conns[Con.DIR_W] = [c for c in self.connectors if c.p_elm.rot == Con.DIR_W]
    conns[Con.DIR_S] = [c for c in self.connectors if c.p_elm.rot == Con.DIR_S]

    le = len(conns[Con.DIR_E])
    ln = len(conns[Con.DIR_N])
    lw = len(conns[Con.DIR_W])
    ls = len(conns[Con.DIR_S])

    dx = self.p_spacing_h if (ln+ls>0 or le*lw>0) else 0 
    dy = self.p_spacing_v if (le+lw>0 or ln*ls>0) else 0 
    
    
    # Expand vertical space to at least 2 if both S and N pads included
    v = dy * max(le, lw, (ln*ls>0) * 2)
    height = dx * max(ln, ls)  
    
    # Place connectors 
    x0 = ( height+dx)*0.5
    y0 = (-v+dy)*0.5
    for c in conns[Con.DIR_E]:
      c.set_pcb_pos(x0, y0)
      y0 += dy 
    
    x0 = (-height-dx)*0.5
    y0 = ( v-dy)*0.5
    for c in conns[Con.DIR_W]:
      c.set_pcb_pos(x0, y0)
      y0 -= dy 

    x0 = ( height-dx)*0.5
    y0 = ( v-dy)*0.5
    for c in conns[Con.DIR_N]:
      c.set_pcb_pos(x0, y0)
      x0 -= dx 

    x0 = (-height+dx)*0.5
    y0 = (-v+dy)*0.5
    for c in conns[Con.DIR_S]:
      c.set_pcb_pos(x0, y0)
      x0 += dx 


    grp.add(self.pcb_layers["silkscreen"])

    # Create pcb view layers. Use scale=(0,-1) to use conventional coordinates
    if self.mount == Cmp.MOUNT_THT:
      # Use both copper0 and cooper1 for tht parts.
      self.pcb_layers["copper0"].add(self.pcb_layers["copper1"])
      grp.add(self.pcb_layers["copper0"])
    else:
      # Use only copper1 for smd parts.
      grp.add(self.pcb_layers["copper1"])      

    grp.add(self.pcb_layers["keepout"])
    grp.add(self.pcb_layers["outline"])


  def get_state(self):
    """
    Return a dict describing the state of the component. Useful for saving 
    object data to a file.
    The state can be reloaded using set_state().    
    """
    #print("ComponentRect.get_state")
    state = super().get_state()
    state.update({"s_add_height"  : self.s_add_height,
                  "s_add_width"   : self.s_add_width } )
    return state
    
    