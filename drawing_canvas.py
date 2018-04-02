#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import sys
import wx
from graphics_lib import InkPen

ID_MAINFRAME = wx.NewId()
ID_FILE_SAVE = wx.NewId()

class MainFrame(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, ID_MAINFRAME, title=title, size=(500, 400))

        self.tx, self.ty = 0, 0
        self.path = []

        self.menu_file = wx.Menu()
        self.menu_file.Append(wx.ID_ABOUT, '&About', 'Informations')
        self.menu_file.AppendSeparator()
        self.menu_file.Append(ID_FILE_SAVE, '保存\tCtrl+S')
        self.menu_file.Append(wx.ID_EXIT, 'E&xit', 'Exit program')
        self.menu_bar = wx.MenuBar()
        self.menu_bar.Append(self.menu_file, 'ファイル')

        self.Bind(wx.EVT_MENU, self.SelectMenu)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)

        self.SetMenuBar(self.menu_bar)
        self.SetBackgroundColour("WHITE")
        self.OnSize(None)

    def OnAbout(self,event):
        dlg = wx.MessageDialog(self, 'by Kazushi Mukaiyama\nFuture University Hakodate, 2018', 'Drawing Canvas', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def SelectMenu(self, event):
        id = event.GetId()
        if id == ID_FILE_SAVE:
            print 'saved'
            self.Save()

    def OnExit(self, event):
        print 'good bye'
        sys.exit()

    def OnSize(self, event):
        size = self.GetClientSize()
        self.buffer = wx.Bitmap(max(1, size.width), max(1, size.height))
        self.Repaint()

    def OnPaint(self, event):
        wx.BufferedPaintDC(self, self.buffer)

    def OnMouse(self, event):
        self.tx, self.ty = event.GetPosition()

        if event.LeftDown():
            self.path.append([])
            self.path[-1].append((self.tx, self.ty))
        elif event.LeftUp():
            self.Repaint()
        elif event.RightDown():
            pass
        elif event.RightUp():
            self.path = []
            self.Repaint()
        elif event.Dragging():
            self.path[-1].append((self.tx, self.ty))
            self.Repaint()
            pass
        elif event.Moving():
            pass
        elif event.Leaving():
            pass

    def Repaint(self):
        bdc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        bdc.Clear()
        self._draw(bdc)
        self.Refresh()
        self.Update()

    def Save(self):
        size = self.GetClientSize()
        sdc = wx.SVGFileDC('test.svg', width=size.width, height=size.height)
        self._draw(sdc)

    def _draw(self, dc):
        #inkPen_line = InkPen(bdc, wx.Pen('black', 1))
        #for line in self.path:
        #    inkPen_line.moveTo(line[0])
        #    for i in range(1, len(line)):
        #        inkPen_line.lineTo(line[i])
        inkPen = InkPen(dc, wx.Pen('black', 4.0))
        for line in self.path:
            inkPen.moveTo(line[0])
            for i in range(1, len(line)):
                    pp, tp = line[i-1], line[i]
                    cp = ((pp[0] + tp[0]) / 2.0, (pp[1] + tp[1]) / 2.0)
                    inkPen.curveTo(pp, cp)

if __name__ == "__main__":
    app = wx.App()
    mainFrame = MainFrame(None, 'Drawing Canvas')
    mainFrame.Show()
    app.SetTopWindow(mainFrame)
    app.MainLoop()
