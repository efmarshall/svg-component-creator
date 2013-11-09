@echo off
SET WINPYDIR=C:\WinPython-64bit-3.3.2.3\python-3.3.2.amd64
%WINPYDIR%\python.exe "%WINPYDIR%\Lib\site-packages\PyQt4\uic\pyuic.py" SVGCompCreator.ui > SVGCompCreator.py
%WINPYDIR%\python.exe "%WINPYDIR%\Lib\site-packages\PyQt4\uic\pyuic.py" HelpDialog.ui > HelpDialog.py