#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import wx
import numpy as np
import math
np.seterr(divide='ignore', invalid='ignore')

class InkPen:

    def __init__(self, dc, pen):
        self.setDC(dc)
        self.setColor(pen.GetColour())
        self.setWidth(pen.GetWidth())
        self.moveTo((0, 0))
        self.pr = 0.0

    def setDC(self, dc):
        self.dc = dc

    def setColor(self, color):
        self.color = color

    def setWidth(self, width):
        self.width = width

    def moveTo(self, p):
        self.pr = 0.0
        self.pos = p

    def lineTo(self, p):
        self.dc.SetPen(wx.Pen(self.color, self.width))
        self.dc.DrawLine(self.pos, p)
        self.pos = p

    def curveTo(self, cp, p):
        # make spine of curve
        bezier = Bezier()
        bezier.make(self.pos, cp, p)
        bezier.simplify()

        # make ink-pressured outline
        outline_points = []
        edge0 = self.getEdge(bezier.points[1], bezier.points[0], self.pr) # get width of the start point and set it to ouline
        outline_points.insert(0, edge0[1])
        outline_points.append(edge0[0])
        for j in range(1, len(bezier.points)):
            self.pr = self.getPresssure(bezier.points[j-1], bezier.points[j]) # get pressure of point 'j'
            edge = self.getEdge(bezier.points[j-1], bezier.points[j], self.pr) # get width of point 'j'
            # make outline
            if np.linalg.norm(edge[0] - edge[1]) > 0.0:
                outline_points.insert(0, edge[0])
                outline_points.append(edge[1])

        # draw
        self.dc.SetPen(wx.Pen(self.color, 0.0))
        self.dc.SetBrush(wx.Brush(self.color))
        self.dc.DrawCircle(bezier.points[-1], self.pr) # draw the end point
        self.dc.DrawPolygon(outline_points) # draw outline

        # for debug
        '''
        self.dc.SetPen(wx.Pen('red', 1.0))
        self.dc.SetBrush(wx.Brush('red', wx.TRANSPARENT))
        self.dc.DrawCircle(bezier.points[-1], self.pr * 1.05) # draw the end point
        self.dc.DrawPolygon(outline_points) # draw outline
        self.dc.SetPen(wx.Pen('red', 1))
        self.dc.DrawLines(bezier.points)
        self.dc.SetPen(wx.Pen('green', 4))
        self.dc.DrawPointList(bezier.points)
        '''

        del outline_points
        del bezier
        self.pos = p

    def getEdge(self, lp, cp, pr):
        nlp, ncp = np.array(lp), np.array(cp)

        vp = (ncp - nlp) / np.linalg.norm(ncp - nlp) * pr
        r1 = np.array((vp[1], -vp[0])) + ncp
        r2 = np.array((-vp[1], vp[0])) + ncp

        l = []
        l.append(r1)
        l.append(r2)

        return l

    def getPresssure(self, lp, cp):
        nlp, ncp = np.array(lp), np.array(cp)

        dis = np.linalg.norm(ncp - nlp) / 16.0
        try:
            pressure = float(self.width) / math.pow(dis, 1.2)
        except ZeroDivisionError:
            pressure = float(self.width)
        pressure = min(pressure, float(self.width) * 1.0)

        return pressure


class Bezier:

    def __init__(self):
        self.points = []

    def make(self, pp, cp, p, curveResolution=16):
        self.points = []

        bx = 3.0 * (cp[0] - pp[0])
        ax = p[0] - pp[0] - bx

        by = 3.0 * (cp[1] - pp[1])
        ay = p[1] - pp[1] - by

        for i in range(curveResolution):
            t = float(i) / float(curveResolution-1)
            t2 = t * t
            t3 = t2 * t
            x = (ax * t3) + (bx * t2) + pp[0]
            y = (ay * t3) + (by * t2) + pp[1]
            self.points.append((x, y))

    def simplify(self, flatness=1.2):
        n = len(self.points)
        sV = [None] * n

        tol2 = flatness * flatness  # tolerance squared
        vt = [None] * n
        mk = [0] * n;

        # STAGE 1.  Vertex Reduction within tolerance of prior vertex cluster
        vt[0] = self.points[0]  # start at the beginning
        k, pv = 1, 0
        for i in range(1, n):
            a = np.array(self.points[i])
            b = np.array(self.points[pv])
            d2 = np.dot(a - b, a - b)
            if d2 < tol2: continue
            vt[k] = self.points[i]
            k = k + 1
            pv = i
        if pv < (n - 1):
            vt[k] = self.points[n - 1] # finish at the end
            k = k + 1

        # STAGE 2.  Douglas-Peucker polyline simplification
        mk[0] = mk[k - 1] = 1; # mark the first and last vertices
        self.simplifyDP(flatness, vt, 0, k - 1, mk)

        # copy marked vertices to the output simplified polyline
        m = 0
        for i in range(k):
            if mk[i]:
                sV[m] = vt[i]
                m = m + 1

        # get rid of the unused points
        if m < len(sV):
            self.points = [e for e in sV if e is not None]
        else:
            self.points = sV

    def simplifyDP(self, tol, v, j, k, mk):
        if k <= j + 1: return  # there is nothing to simplify

        # check for adequate approximation by segment S from vt[0] to vt[k-1]
        maxi = j  # index of vertex farthest from S
        maxd2 = 0.0  # distance squared of farthest vertex
        tol2 = tol * tol  # tolerance squared
        S0 = np.array(v[j])
        S1 = np.array(v[k])
        u = S1 - S0  # segment direction vector
        cu = np.dot(u, u) # segment length squared

        # test each vertex vt[i] for max distance from S
        # compute using the Feb 2001 Algorithm's dist_ofPoint_to_Segment()
        # Note: this works in any dimension (2D, 3D, ...)
        # Pb is base of perpendicular from vt[i] to S
        # dv2 = distance vt[i] to S squared

        for i in range(j + 1, k):
            # compute distance squared
            w = v[i] - S0
            cw = np.dot(w, u)
            if cw <= 0.0:
                dv2 = np.dot(v[i] - S0, v[i] - S0)
            elif cu <= cw:
                dv2 = np.dot(v[i] - S1, v[i] - S1)
            else:
                b = float(cw / cu)
                Pb = S0 + u * b
                dv2 = np.dot(v[i] - Pb, v[i] - Pb)
            # test with current max distance squared
            if dv2 <= maxd2: continue

            # vt[i] is a new max vertex
            maxi = i
            maxd2 = dv2


        if maxd2 > tol2:  # error is worse than the tolerance
            # split the polyline at the farthest vertex from S
            mk[maxi] = 1  # mark vt[maxi] for the simplified polyline
            # recursively simplify the two subpolylines at vt[maxi]
            self.simplifyDP(tol, v, j, maxi, mk)  # polyline vt[0] to vt[maxi]
            self.simplifyDP(tol, v, maxi, k, mk)  # polyline vt[maxi] to vt[k-1]
        # else the approximation is OK, so ignore intermediate vertices

        return
