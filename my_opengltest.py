# coding:utf-8
import sys
import wx
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from wx.glcanvas import GLCanvas


class myGLCanvas(GLCanvas):
    def __init__(self, *args, **kwargs):
        GLCanvas.__init__(self, *args, **kwargs)

        self.initialized = False
        glutInit()

        self.Bind(wx.EVT_PAINT, self.OnPaint)  # self.OnPaintをEVT_PAINTに登録(glutDisplayFuncの代わり)
        self.Bind(wx.EVT_SIZE, self.OnSize)  # self.OnSizeをEVT_SIZEに登録(glutReshapeFuncの代わり)

    def OnPaint(self, event):
        #self.SetCurrent()
        if self.initialized == False:
            self.reshape(*self.GetSize())
            self.initialized = True
        self.display()

    def OnSize(self,event):
        w,h = event.GetSize()
        self.reshape(w,h)

    def display(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_COLOR_MATERIAL)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        gluLookAt(0, 4, 10, 0, 0, 0, 0, 1, 0)
        glRotatef(-40, 0.0, 1.0, 0.0)
        glColor3f(float(0xbb) / 0xff, float(0xdd) / 0xff, 0xff / 0xff)
        glutSolidCube(3.5)
        glPopMatrix()
        glFlush()

    def reshape(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)  # 投影変換
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


class SimpleMenu(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)

        self.canvas = myGLCanvas(self, size=(500, 500))  # myGLCanvasのインスタンスを生成
        self.sizer = wx.BoxSizer()  # 画面にwidgetを配置する これはBoxSizerでなくともなんでもよい
        self.sizer.Add(self.canvas)  # canvasをwidgetに追加

        menubar = wx.MenuBar()
        file = wx.Menu()
        edit = wx.Menu()

        file.Append(-1, u'新規')
        file.Append(-1, u'開く')
        file.Append(-1, u'保存')
        file.Append(-1, u'名前を付けて保存')
        file.Append(-1, u'終了', 'Quit application')

        edit.Append(-1, u'元に戻す')

        menubar.Append(file, u'&ファイル')
        menubar.Append(edit, u'&編集')
        self.SetMenuBar(menubar)

        self.Centre()
        self.Show(True)


app = wx.App()
SimpleMenu(None, -1, 'simplemenu.py')
app.MainLoop()
