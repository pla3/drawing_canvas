#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from direct.showbase.ShowBase import ShowBase
from panda3d.core import PandaNode, LightNode, TextNode
from panda3d.core import Filename, NodePath
from panda3d.core import PointLight, AmbientLight
from panda3d.core import LightRampAttrib, AuxBitplaneAttrib
from panda3d.core import CardMaker
from panda3d.core import Shader, Texture
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.BufferViewer import BufferViewer
from direct.filter.CommonFilters import CommonFilters
from direct.wxwidgets.WxPandaWindow import OpenGLPandaWindow
import sys
import os
import wx

class ToonMaker(ShowBase, OpenGLPandaWindow):

    def __init__(self, *args, **kwargs):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)
        OpenGLPandaWindow.__init__(self, *args, **kwargs)

        self.cam.node().getLens().setNear(10.0)
        self.cam.node().getLens().setFar(200.0)
        camera.setPos(0, -50, 0)

        # Enable a 'light ramp' - this discretizes the lighting,
        # which is half of what makes a model look like a cartoon.
        # Light ramps only work if shader generation is enabled,
        # so we call 'setShaderAuto'.

        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setAttrib(LightRampAttrib.makeSingleThreshold(0.5, 0.4))
        tempnode.setShaderAuto()
        self.cam.node().setInitialState(tempnode.getState())

        # Use class 'CommonFilters' to enable a cartoon inking filter.
        # This can fail if the video card is not powerful enough, if so,
        # display an error and exit.

        self.separation = 1  # Pixels
        self.filters = CommonFilters(self.win, self.cam)
        filterok = self.filters.setCartoonInk(separation=self.separation)

        # Load a dragon model and animate it.
        self.character = Actor()
        self.character.loadModel('panda3d_samples/cartoon-shader/models/nik-dragon')
        self.character.reparentTo(render)
        self.character.loadAnims({'win': 'panda3d_samples/cartoon-shader/models/nik-dragon'})
        self.character.loop('win')
        self.character.hprInterval(15, (360, 0, 0)).loop()

        # Create a non-attenuating point light and an ambient light.
        plightnode = PointLight("point light")
        plightnode.setAttenuation((1, 0, 0))
        plight = render.attachNewNode(plightnode)
        plight.setPos(30, -50, 0)
        alightnode = AmbientLight("ambient light")
        alightnode.setColor((0.8, 0.8, 0.8, 1))
        alight = render.attachNewNode(alightnode)
        render.setLight(alight)
        render.setLight(plight)

        # Panda contains a built-in viewer that lets you view the
        # results of all render-to-texture operations.  This lets you
        # see what class CommonFilters is doing behind the scenes.
        self.accept("v", self.bufferViewer.toggleEnable)
        self.accept("V", self.bufferViewer.toggleEnable)
        self.bufferViewer.setPosition("llcorner")
        self.accept("s", self.filters.manager.resizeBuffers)

        # These allow you to change cartooning parameters in realtime
        self.accept("escape", sys.exit, [0])
        self.accept("arrow_up", self.increaseSeparation)
        self.accept("arrow_down", self.decreaseSeparation)

    def increaseSeparation(self):
        self.separation = self.separation * 1.11111111
        print("separation: %f" % (self.separation))
        self.filters.setCartoonInk(separation=self.separation)

    def decreaseSeparation(self):
        self.separation = self.separation * 0.90000000
        print("separation: %f" % (self.separation))
        self.filters.setCartoonInk(separation=self.separation)

ID_MAINFRAME = wx.NewId()

class MainFrame(wx.Frame):

    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, ID_MAINFRAME, title=title, size=(500, 400))

        self.canvas = ToonMaker(self, size=(500, 400))
        sz=wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.canvas, wx.ID_ANY, wx.EXPAND)
        self.SetSizer(sz)

        self.tx, self.ty = 0, 0

        self.menu_file = wx.Menu()
        self.menu_file.Append(wx.ID_ABOUT, '&About', 'Informations')
        self.menu_file.AppendSeparator()
        self.menu_file.Append(wx.ID_EXIT, 'E&xit', 'Exit program')
        self.menu_bar = wx.MenuBar()
        self.menu_bar.Append(self.menu_file, 'ファイル')

        self.Bind(wx.EVT_MENU, self.SelectMenu)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        self.SetMenuBar(self.menu_bar)
        self.SetBackgroundColour("WHITE")

    def OnAbout(self,event):
        dlg = wx.MessageDialog(self, 'by Kazushi Mukaiyama\nFuture University Hakodate, 2018', 'My Panda', wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        print 'good bye'
        sys.exit()

    def SelectMenu(self, event):
        id = event.GetId()


if __name__ == "__main__":
    app = wx.App()
    mainFrame = MainFrame(None, 'Drawing Canvas')
    mainFrame.Show()
    app.SetTopWindow(mainFrame)
    app.MainLoop()

