#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import cv2
from xml.etree.ElementTree import *
import xml.etree.ElementTree as ET
from xml.dom import minidom
import codecs

class ComicInfo:
    @staticmethod
    def new(name, width, height):
        xml = Element('info')
        comment = Comment('age = 0:baby, 5:1-9, 10:10-19, 20:20-29 ...., -1:???')
        xml.append(comment)
        id = SubElement(xml, 'id')
        id.text = name
        shape = SubElement(xml, 'shape')
        shape.attrib = {'width':width, 'height':height}
        return xml

    @staticmethod
    def read(path):
        tree = ET.parse(path)
        root = tree.getroot()

        xml = Element('info')
        comment = Comment('age = 0:baby, 5:1-9, 10:10-19, 20:20-29 ...., -1:???')
        xml.append(comment)
        if root.find('id') is not None:
            id = SubElement(xml, 'id')
            id.text = root.find('id').text
        if root.find('shape') is not None:
            shape = SubElement(xml, 'shape')
            shape.attrib = root.find('shape').attrib
        for index, elem in enumerate(root.findall('character')):
            character = SubElement(xml, 'character')
            if elem.find('id') is not None:
                id = SubElement(character, 'id')
                id.text = elem.find('id').text
            name = SubElement(character, 'name')
            name.text = elem.find('name').text
            face = SubElement(character, 'face')
            face.attrib = elem.find('face').attrib
            accurancy = SubElement(character, 'accurancy')
            accurancy.attrib = elem.find('accurancy').attrib
            sex = SubElement(character, 'sex')
            sex.text = elem.find('sex').text
            age = SubElement(character, 'age')
            age.text = elem.find('age').text
        for index, elem in enumerate(root.findall('balloon')):
            balloon = SubElement(xml, 'balloon')
            id = SubElement(balloon, 'id')
            id.text = elem.find('id').text
            coord = SubElement(balloon, 'coord')
            coord.attrib = elem.find('coord').attrib
            dialog = SubElement(balloon, 'dialog')
            dialog.text = elem.find('dialog').text
            next = SubElement(balloon, 'next')
            next.text = elem.find('next').text
            who = SubElement(balloon, 'who')
            who.text = elem.find('who').text
            for subelem in elem.findall('pair'):
                pair = SubElement(balloon, 'pair')
                pair.attrib = subelem.attrib
        return xml

    @staticmethod
    def write(xml, path):
        rough_string = tostring(xml, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        formatted_xml = reparsed.toprettyxml(indent="  ")
        f = codecs.open(path, 'w', 'utf-8')
        f.write(formatted_xml)
        f.close()

class Panel:

    def __init__(self, path=None):
        self.load(path)

    # 各情報の読み込み
    def load(self, path):
        dir = os.path.dirname(path)
        name = os.path.splitext(path)[0].split('/')[-1]
        if name is not None:
            self.dir = dir
            self.name = name
            self.image = cv2.imread(self.dir + '/' + self.name + ".jpg", 1)
            try:
                self.info = ComicInfo.read(self.dir + '/' + self.name + ".xml")
            except IOError:
                self.info = ComicInfo.new(self.name, str(self.image.shape[1]), str(self.image.shape[0]))
            if self.info.find('shape') is not None:
                self.width = int(self.info.find('shape').attrib['width'])
                self.height = int(self.info.find('shape').attrib['height'])

    # 結果表示
    def plot_info(self):
        img_copy = self.image.copy()

        if self.info.find('shape') is not None:
            w = self.width
            h = self.height
        else:
            w, h = 1.0, 1.0

        for elem in self.info:
            if elem.tag is 'character':
                coord = elem.find('face').attrib
                x1 = int(round(w * float(coord.get('x1'))))
                y1 = int(round(h * float(coord.get('y1'))))
                x2 = int(round(w * float(coord.get('x2'))))
                y2 = int(round(h * float(coord.get('y2'))))
                name = elem.find('name').text
                color = (63, 63, 63)
                cv2.rectangle(img_copy, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img_copy, "%s" % name, (x1, y2 + 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, color)
                #cv2.putText(img_copy, "%4.1f%%" % (accurancy * 100), (x1, y2 + 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, color)

        return img_copy
