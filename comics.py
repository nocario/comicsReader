# -*- coding: utf-8 -*-
"""
Created on Thu Apr 29 14:28:21 2020

@author: HHAGBE
"""
from pathlib import Path
import os
import time
import zipfile
import rarfile
import sqlite3
import tempfile

try:
    rarfile.UNRAR_TOOL = Path.cwd() / 'UnRAR.exe'
except:
    pass


class COMICParser:
    def __init__(self, filename):
        self.Path = Path(filename)
        self.temp = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.book = filename
        self.image_list = None
        self._metadata = {}
        self.places = ''

    def read_book(self):
        if self.Path.suffix == '.cbz':
            self.book = zipfile.ZipFile(
                self.Path, mode='r', allowZip64=True)
            self.image_list = [
                i.filename for i in self.book.infolist()
                if not i.is_dir() and is_image(i.filename)]
        elif self.Path.suffix == '.cbr':
            self.book = rarfile.RarFile(self.Path)
            self.image_list = [
                i.filename for i in self.book.infolist()
                if not i.isdir() and is_image(i.filename)]
        self.image_list.sort()
        return self.image_list

    def generate_metadata(self, author='<Unknown>', tags='[]', quality=0):
        title = self.Path.stem

        connect = sqlite3.connect('datasql.db')
        cur = connect.cursor()
        cur.execute("SELECT name_id,title FROM info WHERE name_id=?", (title,))
        test = cur.fetchone()

        if test is None:
            with open(self.places / self.image_list[0], 'rb') as f:
                cover = f.read()

            creation_time = time.ctime(os.path.getctime(self.Path))
            year = creation_time.split()[-1]

            cur.execute("INSERT INTO info VALUES (?, ?, ?,?,?,?,?);",
                        (cover, title, author, year, tags, quality, title))

        connect.commit()
        cur.close()
        connect.close()

    def generate_content(self):
        return self.image_list

    def get_filename(self):
        return self.filename

    @staticmethod
    def unzip(source_filename, dest_dir):
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir)

    @staticmethod
    def unrar(source_filename, dest_dir):
        with rarfile.RarFile(source_filename) as rf:
            rf.extractall(dest_dir)


def is_image(filename):
    valid_image_extensions = ['.png', '.jpg', '.bmp', '.jpeg']
    if Path(filename).suffix.lower() in valid_image_extensions:
        return True
    else:
        return False
