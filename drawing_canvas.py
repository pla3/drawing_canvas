#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import sys
import wx
from graphics_lib import InkPen
from skimage.morphology import skeletonize
from line_segmentation import *
from line_simplification import *

ID_MAINFRAME = wx.NewId()
ID_FILE_LOAD = wx.NewId()
ID_FILE_SAVE = wx.NewId()

class MainFrame(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, ID_MAINFRAME, title=title, size=(500, 400))

        self.tx, self.ty = 0, 0
        self.path = []

        self.menu_file = wx.Menu()
        self.menu_file.Append(wx.ID_ABOUT, '&About', 'Informations')
        self.menu_file.AppendSeparator()
        self.menu_file.Append(ID_FILE_LOAD, '読込\tCtrl+O')
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

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, 'by Kazushi Mukaiyama\nFuture University Hakodate, 2018', 'Drawing Canvas', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def SelectMenu(self, event):
        id = event.GetId()
        if id == ID_FILE_LOAD:
            self._drawSkelton()
        elif id == ID_FILE_SAVE:
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

    def _drawSkelton(self):
        # load an image
        img = cv2.imread('testImg_mikuface.png', -1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        img = cv2.bitwise_not(img)
        h, w = img.shape[:2]
        self.SetSize(wx.Size(w, h))

        # perform skeletonization
        skeleton = skeletonize(img / 255)  # 0-255 -> 0-1
        img_thin = skeleton.astype(np.uint8) * 255
        dstPts = divideBranchedChain(img_thin.ravel(), w, h, False)

        # simplify points
        dstPts_simplified = []
        for pts in dstPts:
            if len(pts) > 12:
                simplified = ramerdouglas(pts, dist=1.4)
                u = np.array(simplified[-1]) - np.array(simplified[0])
                if np.linalg.norm(u) > 15.0: dstPts_simplified.append(simplified)

        self.path = dstPts_simplified
        self.Repaint()

        bdc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        for i, pts in enumerate(dstPts_simplified):
            color = [0, 0, 0]
            color[i % 3] = 255
            bdc.SetPen(wx.Pen(color, 1.0))
            bdc.DrawLines(pts)


    def _draw(self, dc):
        #inkPen_line = InkPen(bdc, wx.Pen('black', 1))
        #for line in self.path:
        #    inkPen_line.moveTo(line[0])
        #    for i in range(1, len(line)):
        #        inkPen_line.lineTo(line[i])
        inkPen = InkPen(dc, wx.Pen('black', 3.5))
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
