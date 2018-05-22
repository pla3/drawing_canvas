#!/usr/bin/env python
#! -*- coding: utf-8 -*-

# original code by dbr
# https://stackoverflow.com/questions/2573997/reduce-number-of-points-in-line
# Does Ramer-Douglas-Peucker simplification of a curve with `dist`
# threshold.
# `line` is a list-of-tuples, where each tuple is a 2D coordinate
# Usage is like so:
# >>> myline = [(0.0, 0.0), (1.0, 2.0), (2.0, 1.0)]
# >>> simplified = ramerdouglas(myline, dist = 1.0)

def _vec2d_dist(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

def _vec2d_sub(p1, p2):
    return (p1[0]-p2[0], p1[1]-p2[1])

def _vec2d_mult(p1, p2):
    return p1[0]*p2[0] + p1[1]*p2[1]

def ramerdouglas(line, dist):
    if len(line) < 3:
        return line

    (begin, end) = (line[0], line[-1]) if line[0] != line[-1] else (line[0], line[-2])

    distSq = []
    for curr in line[1:-1]:
        tmp = (
            _vec2d_dist(begin, curr) - _vec2d_mult(_vec2d_sub(end, begin), _vec2d_sub(curr, begin)) ** 2 / _vec2d_dist(begin, end))
        distSq.append(tmp)

    maxdist = max(distSq)
    if maxdist < dist ** 2:
        return [begin, end]

    pos = distSq.index(maxdist)
    return(ramerdouglas(line[:pos + 2], dist) + ramerdouglas(line[pos + 1:], dist)[1:])
