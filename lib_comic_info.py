#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import os
import cv2
import numpy as np
from xml.etree.ElementTree import *
import xml.etree.ElementTree as ET
from xml.dom import minidom
import codecs
import argparse

class ComicInfo:
    @staticmethod
    def new_page(index, width, height):
        xml = Element('info')
        page = SubElement(xml, 'page')
        page.attrib = {'width':width, 'height':height, 'index':index}
        return xml

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
    def read_page(path):
        tree = ET.parse(path)
        root = tree.getroot()

        xml = Element('info')
        #comment = Comment('age = 0:baby, 5:1-9, 10:10-19, 20:20-29 ...., -1:???')
        #xml.append(comment)

        if root.find('page') is not None:
            page_org = root.find('page')
            page = SubElement(xml, 'page')
            page.attrib = page_org.attrib
            for frame_org in page_org.findall('frame'):
                frame = SubElement(page, 'frame')
                frame.attrib = frame_org.attrib
                for elem in frame_org.findall('character'):
                    character = SubElement(frame, 'character')
                    character.attrib = elem.attrib
                    if elem.find('name') is not None:
                        name = SubElement(character, 'name')
                        name.text = elem.find('name').text
                    if elem.find('sex') is not None:
                        sex = SubElement(character, 'sex')
                        sex.text = elem.find('sex').text
                    if elem.find('age') is not None:
                        age = SubElement(character, 'age')
                        age.text = elem.find('age').text
                    for subelem in elem.findall('body'):
                        body = SubElement(character, 'body')
                        body.attrib = subelem.attrib
                    for subelem in elem.findall('face'):
                        face = SubElement(character, 'face')
                        face.attrib = subelem.attrib
                    for subelem in elem.findall('accuracy'):
                        accuracy = SubElement(character, 'accuracy')
                        accuracy.attrib = subelem.attrib
                for elem in frame_org.findall('balloon'):
                    balloon = SubElement(frame, 'balloon')
                    balloon.attrib = elem.attrib
                    if elem.find('dialog') is not None:
                        dialog = SubElement(balloon, 'dialog')
                        dialog.text = elem.find('dialog').text
                    if elem.find('next') is not None:
                        next = SubElement(balloon, 'next')
                        next.text = elem.find('next').text
                    for subelem in elem.findall('who'):
                        who = SubElement(balloon, 'who')
                        who.text = subelem.text
                    for subelem in elem.findall('pair'):
                        pair = SubElement(balloon, 'pair')
                        pair.attrib = subelem.attrib

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
            for subelem in elem.findall('accuracy'):
                accuracy = SubElement(character, 'accuracy')
                accuracy.attrib = subelem.attrib
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
        #print (formatted_xml)
        f = codecs.open(path, 'w', 'utf-8')
        f.write(formatted_xml)
        f.close()

class Page:

    def __init__(self, path=None):
        if path is None:
            self.dir = None
            self.name = 'none'
            self.image = None
            self.info = ComicInfo.new_page(self.name, str(0), str(0))
        else:
            self.load(path)

    # 各情報の読み込み
    def load(self, path):
        if os.name == 'nt': path = path.replace(os.path.sep, '/') # for windows
        dir = os.path.dirname(path)
        name = os.path.splitext(path)[0].split('/')[-1]
        if name is not None:
            self.dir = dir
            self.name = name
            self.image = cv2.imread(self.dir + '/' + self.name + ".jpg", 1)
            try:
                self.info = ComicInfo.read_page(self.dir + '/' + self.name + ".xml")
            except IOError:
                self.info = ComicInfo.new_page(self.name, str(self.image.shape[1]), str(self.image.shape[0]))
            if self.info.find('page') is not None:
                self.width = int(self.info.find('page').attrib['width'])
                self.height = int(self.info.find('page').attrib['height'])
                self.index = int(self.info.find('page').attrib['index'])

    def update_id(self):
        parent_map = {c: p for p in self.info.iter() for c in p}  # parentマップの作成
        frames = self.info.findall('.//frame')
        characters = self.info.findall('.//character')
        faces = self.info.findall('.//face')
        bodies = self.info.findall('.//body')
        balloons = self.info.findall('.//balloon')

        references = dict() # 新旧idの辞書 key:old_id, item:new_id

        # idを打ち直しidの新旧辞書を更新する
        for i, elem in enumerate(frames):
            old_id = elem.attrib['id']
            new_id = self.name + "_" + elem.tag + "_" + str(i)
            if old_id != new_id:
                elem.attrib['id'] = new_id
                references[old_id] = new_id
        for i, elem in enumerate(characters):
            old_id = elem.attrib['id']
            parent = parent_map[elem]
            new_id = parent.attrib['id'] + "_" + elem.tag + "_" + str(i)
            if old_id != new_id:
                elem.attrib['id'] = new_id
                references[old_id] = new_id
        for i, elem in enumerate(faces):
            old_id = elem.attrib['id']
            parent = parent_map[elem]
            new_id = parent.attrib['id'] + "_" + elem.tag + "_" + str(i)
            if old_id != new_id:
                elem.attrib['id'] = new_id
                references[old_id] = new_id
        for i, elem in enumerate(bodies):
            old_id = elem.attrib['id']
            parent = parent_map[elem]
            new_id = parent.attrib['id'] + "_" + elem.tag + "_" + str(i)
            if old_id != new_id:
                elem.attrib['id'] = new_id
                references[old_id] = new_id
        for i, elem in enumerate(balloons):
            old_id = elem.attrib['id']
            parent = parent_map[elem]
            new_id = parent.attrib['id'] + "_" + elem.tag + "_" + str(i)
            if old_id != new_id:
                elem.attrib['id'] = new_id
                references[old_id] = new_id

        # 辞書に基づいて旧idを新idに更新する
        for balloon in balloons:
            try:
                old_next = balloon.find('next').text
                new_next = references[old_next]
                balloon.find('next').text = new_next
            except KeyError:
                pass
            try:
                for pair in balloon.findall('pair'):
                    old_target = pair.attrib['target']
                    new_target = references[old_target]
                    pair.attrib['target'] = new_target
            except KeyError:
                pass
            try:
                for who in balloon.findall('who'):
                    old_who = who.text
                    new_who = references[old_who]
                    who.text = new_who
            except KeyError:
                pass

class Panel:

    def __init__(self, path=None):
        if path is not None: self.load(path)

    # 各情報の読み込み
    def load(self, path):
        if os.name == 'nt': path = path.replace(os.path.sep, '/') # for windows
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
                #cv2.putText(img_copy, "%4.1f%%" % (accuracy * 100), (x1, y2 + 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, color)

        return img_copy

# mini変換メソッド集
# for f in ./test_lovehina/*.xml ; do python ./lib_comic_info.py $f ; done
def convert_ballooncoord(path):
    info = ComicInfo.read_page(path)
    for balloon in info.findall('.//balloon'):
        coord = balloon.find('coord')
        if coord is not None:
            balloon.attrib.update(coord.attrib)
            balloon.remove(coord)
    ComicInfo.write(info, path)

def convert_relative(panel):
    height, width, = panel.image.shape[:2]
    shape = Element('shape', attrib={'width': str(width), 'height': str(height)})
    panel.info.insert(1, shape)
    id = Element('id')
    id.text = panel.name
    panel.info.insert(1, id)
    for elem in panel.info:
        if elem.tag is 'character':
            coord = elem.find('face').attrib
            x1 = int(coord.get('x1')) / float(width)
            y1 = int(coord.get('y1')) / float(height)
            x2 = int(coord.get('x2')) / float(width)
            y2 = int(coord.get('y2')) / float(height)
            coord['x1'] = str(np.clip(x1, 0.0, 1.0))
            coord['y1'] = str(np.clip(y1, 0.0, 1.0))
            coord['x2'] = str(np.clip(x2, 0.0, 1.0))
            coord['y2'] = str(np.clip(y2, 0.0, 1.0))
        if elem.tag is 'balloon':
            coord = elem.find('coord').attrib
            x1 = int(coord.get('x1')) / float(width)
            y1 = int(coord.get('y1')) / float(height)
            x2 = int(coord.get('x2')) / float(width)
            y2 = int(coord.get('y2')) / float(height)
            coord['x1'] = str(np.clip(x1, 0.0, 1.0))
            coord['y1'] = str(np.clip(y1, 0.0, 1.0))
            coord['x2'] = str(np.clip(x2, 0.0, 1.0))
            coord['y2'] = str(np.clip(y2, 0.0, 1.0))

def convert_faceid(panel):
    panel_id = panel.info.find('id').text
    for i, elem in enumerate(panel.info.findall('character')):
        id = Element('id')
        id.text = panel_id + '_c_' + str(i + 1)
        elem.insert(0, id)
    for elem in panel.info.findall('balloon'): # balloon_idにも_b_を追加
        t = elem.find('id').text
        te = t.split('_')[-1]
        ts = t.rstrip(te)
        elem.find('id').text =  ts + 'b_' + te
        t = elem.find('next').text
        if t != 'end':
            te = t.split('_')[-1]
            ts = t.rstrip(te)
            elem.find('next').text = ts + 'b_' + te
        for pair in elem.findall('pair'):
            t = pair.attrib['target']
            te = t.split('_')[-1]
            ts = t.rstrip(te)
            pair.attrib['target'] = ts + 'b_' + te

def convert_accuracy(panel):
    for i, elem in enumerate(panel.info.findall('character')):
        a_face = elem.find('accuracy').text
        a_dir = elem.find('accuracy_dir').text
        a_emo = elem.find('accuracy_emo').text
        elem.find('accuracy').attrib['face'] = a_face
        if a_dir is not None: elem.find('accuracy').attrib['dir'] = a_dir
        if a_emo is not None: elem.find('accuracy').attrib['emo'] = a_emo
        elem.find('accuracy').text = None
        elem.remove(elem.find('accuracy_dir'))
        elem.remove(elem.find('accuracy_emo'))

# mini変換実行部分
#parser = argparse.ArgumentParser(description='ComicInfo Convert')
#parser.add_argument('xml', help='Path to xml')
#args = parser.parse_args()
#convert_ballooncoord(args.xml)

