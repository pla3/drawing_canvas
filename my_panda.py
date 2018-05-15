#!/usr/bin/env python

# Author: Kwasi Mensah
# Date: 7/11/2005
#
# This is a tutorial to show some of the more advanced things
# you can do with Cg. Specifically, with Non Photo Realistic
# effects like Toon Shading. It also shows how to implement
# multiple buffers in Panda.

from direct.showbase.ShowBase import ShowBase
from panda3d.core import PNMImage, PNMImageHeader
from panda3d.core import PandaNode, LightNode, TextNode
from panda3d.core import Filename
from panda3d.core import NodePath
from panda3d.core import Shader
from panda3d.core import LVecBase4
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.BufferViewer import BufferViewer
import sys
import os


class ToonMaker(ShowBase):

    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        #self.disableMouse()
        self.camera.setPos(0, -6, 2)
        self.camLens.setNear(0.01)
        self.camLens.setFov(50)

        # Check video card capabilities.
        if not self.win.getGsg().getSupportsBasicShaders():
            print("Toon Shader: Video driver reports that Cg shaders are not supported.")
            return

        # This shader's job is to render the model with discrete lighting
        # levels.  The lighting calculations built into the shader assume
        # a single nonattenuating point light.

        #tempnode = NodePath(PandaNode("temp node"))
        #tempnode.setShader(loader.loadShader("shader/lightingGen.sha"))
        #self.cam.node().setInitialState(tempnode.getState())

        # This is the object that represents the single "light", as far
        # the shader is concerned.  It's not a real Panda3D LightNode, but
        # the shader doesn't care about that.

        light = render.attachNewNode("light")
        light.setPos(30, -50, 0)

        # this call puts the light's nodepath into the render state.
        # this enables the shader to access this light by name.

        render.setShaderInput("light", light)

        # The "normals buffer" will contain a picture of the model colorized
        # so that the color of the model is a representation of the model's
        # normal at that point.

        normalsBuffer = self.win.makeTextureBuffer("normalsBuffer", 0, 0)
        normalsBuffer.setClearColor(LVecBase4(0.5, 0.5, 0.5, 1))
        self.normalsBuffer = normalsBuffer
        normalsCamera = self.makeCamera(
            normalsBuffer, lens=self.cam.node().getLens())
        normalsCamera.node().setScene(render)
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(loader.loadShader("shader/normalGen.sha"))
        normalsCamera.node().setInitialState(tempnode.getState())

        # what we actually do to put edges on screen is apply them as a texture to
        # a transparent screen-fitted card

        drawnScene = normalsBuffer.getTextureCard()
        drawnScene.setTransparency(1)
        drawnScene.setColor(1, 1, 1, 0)
        drawnScene.reparentTo(render2d)
        self.drawnScene = drawnScene

        # this shader accepts, as input, the picture from the normals buffer.
        # it compares each adjacent pixel, looking for discontinuities.
        # wherever a discontinuity exists, it emits black ink.

        self.separation = 0.001
        self.cutoff = 0.3
        inkGen = loader.loadShader("shader/inkGen.sha")
        drawnScene.setShader(inkGen)
        drawnScene.setShaderInput("separation", LVecBase4(self.separation, 0, self.separation, 0))
        drawnScene.setShaderInput("cutoff", LVecBase4(self.cutoff))

        # Panda contains a built-in viewer that lets you view the results of
        # your render-to-texture operations.  This code configures the viewer.

        self.accept("v", self.bufferViewer.toggleEnable)
        self.bufferViewer.setPosition("llcorner")

        # Load a dragon model and start its animation.
        self.character = Actor()
        self.character.loadModel('models/miku/tda_miku')
        self.character.reparentTo(render)
        self.character.loadAnims({'win': 'models/miku/tda_miku-Anim0'})
        self.character.play('win')
        self.character.pose('win', 1)

        # These allow you to change cartooning parameters in realtime
        self.accept("escape", sys.exit, [0])
        self.accept("arrow_up", self.increaseSeparation)
        self.accept("arrow_down", self.decreaseSeparation)
        self.accept("arrow_left", self.increaseCutoff)
        self.accept("arrow_right", self.decreaseCutoff)
        self.accept("s", self.saveImage)
        self.accept("p", self.play)
        self.accept("o", self.stop)
        self.accept("n", self.forward)
        self.accept("b", self.rewind)
        self.accept("l", self.lookAt)

    def increaseSeparation(self):
        self.separation = self.separation * 1.11111111
        print("separation: %f" % (self.separation))
        self.drawnScene.setShaderInput(
            "separation", LVecBase4(self.separation, 0, self.separation, 0))

    def decreaseSeparation(self):
        self.separation = self.separation * 0.90000000
        print("separation: %f" % (self.separation))
        self.drawnScene.setShaderInput(
            "separation", LVecBase4(self.separation, 0, self.separation, 0))

    def increaseCutoff(self):
        self.cutoff = self.cutoff * 1.11111111
        print("cutoff: %f" % (self.cutoff))
        self.drawnScene.setShaderInput("cutoff", LVecBase4(self.cutoff))

    def decreaseCutoff(self):
        self.cutoff = self.cutoff * 0.90000000
        print("cutoff: %f" % (self.cutoff))
        self.drawnScene.setShaderInput("cutoff", LVecBase4(self.cutoff))

    def saveImage(self):
        self.graphicsEngine.renderFrame()
        image = PNMImage()
        dr = self.camNode.getDisplayRegion(0)
        dr.getScreenshot(image)
        image.write(Filename('testImg.png'))

    def play(self):
        frame = self.character.getCurrentFrame('win')
        self.character.play('win', fromFrame=frame)

    def stop(self):
        frame = self.character.getCurrentFrame('win')
        self.character.pose('win', frame)

    def forward(self):
        frame = self.character.getCurrentFrame('win') + 10
        frame = min(frame, self.character.getNumFrames('win'))
        self.character.pose('win', frame)

    def rewind(self):
        frame = self.character.getCurrentFrame('win') - 10
        frame = max(0, frame)
        self.character.pose('win', frame)

    def lookAt(self):
        geom = self.character.getGeomNode()
        self.camera.lookAt(self.character.getGeomNode().getPos()+(0, 0, 3))

t = ToonMaker()
t.run()
