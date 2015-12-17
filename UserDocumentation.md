# Disclaimer #
No guarantees whatsoever will be given that the Svg Component Creator will produce valid svg files. No responsibility is taken for any cost or damage related to the use of this application. Use at your own risk.


# Introduction #
The Svg Component Creator creates svg files for use with Fritzing http://fritzing.org/

Svg files - a vector graphic format - are created for the schematic and pcb view. It will have pins and pads made so these are detected by the Fritzing component editor. The pcb view is defined by measurements in millimeters to make it easy to use real dimensions available in component datasheets.


# Installation #
The Svg Component Creator is written in the Python 3 programming language. You need to install a Python 3 scripting interpreter to run it. For Windows check out for example
http://code.google.com/p/winpython/. WinPython includes PyQt for the GUI which is also required.


# Usage #
There are 3 tabs Schematic, Footprint and Silkscreen which are used to create the graphics. Each of them explained below.
The result will be immediately shown on the drawing area to the left. When done, save the svg files using File->Save... or export the svg files with File->Export... Exported files will be named schematic.svg and pcb.svg.


## Schematics ##
Number of connectors can be set using the connectors spin box. If the text is too long the width and height can be increased by using adding a width and height.
For each connector added, there will be a new row in the connectors list. Default values are given to new connectors but can be edited by clicking in the list. The list have 5 columns;
  1. Label: A text label which shows next to the pin in the schematics view.
  1. Dir: Connector direction. May be any of E, N, W, or S. That is East, North, West or south.
  1. Bef: This is the spacing to the pin before (anti-clockwise) or the edge of the schematic rectangular box it is the first pin for the direction.
  1. Aft: This is the spacing to the pin after (clockwise) or the edge of the schematic rectangular box it is the last pin for the direction.

The schematic view work units equal to the Fritzing grid. That will give straight lines on the Fritzing schematics.

A connector label text can be hidden if it starting with a "`*`". This is useful in cases when there are internal connections between several connectors in pcb view. Then the spacing is set to make the connector overlap with its sibling and the label is hidden to avoid text overlap.

![http://wiki.svg-component-creator.googlecode.com/git/schematic_view.png](http://wiki.svg-component-creator.googlecode.com/git/schematic_view.png)

## Footprint ##
The PCB footprint is defined using the Footprint tab. Dimensions on the Footprint tab are millimeters.
Connectors are spaced by a horizontal and vertical spacing. Adjust it by typing a number in corresponding text field.
All connectors added in the Schematic tab are listed here. New columns are;
  1. Dir: Direction of the connector; E, N, W or S.
  1. Shape: 0=hole, 1=hole with rectangular outer and 2=rectangular pad
  1. dx: x-coordinate offset from the original position of the connector.
  1. dy: y-coordinate offset from the original position of the connector.
  1. d1: If shape is a hole; inner diameter. If shape is a pad; pad width.
  1. d2: If shape is a hole; outer diameter. If shape is a pad; pad height.

![http://wiki.svg-component-creator.googlecode.com/git/footprint_view.png](http://wiki.svg-component-creator.googlecode.com/git/footprint_view.png)

## Silkscreen ##
A slikscreen can be defined by hand using commands available for an svg path element. By writing commands in the text box, segments can added to the silkscreen. A segment may e.g. a line or a beizer curve.

After a command is typed in, e.g. "L 2 3.5", use keypad Enter to add the segment. Segments can be edited by marking them in the list or use the up or down key, change the command and update by using Ctrl+Enter. Segment may also be removed by double clicking in the list or setting an empty string.
Note that nothing will be added to the list if the command is invalid!

Learn more about different commands here http://tutorials.jenkov.com/svg/path-element.html#path-commands

![http://wiki.svg-component-creator.googlecode.com/git/silkscreen_view.png](http://wiki.svg-component-creator.googlecode.com/git/silkscreen_view.png)