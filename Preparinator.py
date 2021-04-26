from comics import *
import os
from pathlib import Path


class PrepComics:
    def __init__(self, f):
        self.comic = COMICParser(f)
        self.comic.read_book()
        new_path = Path.cwd() / Path(self.comic.temp.name).name / self.comic.Path.stem
        if not Path.exists(new_path):
            Path.mkdir(new_path)
            if self.comic.Path.suffix == ".cbz":
                self.comic.unzip(f, new_path)
            else:
                self.comic.unrar(f, new_path)
        self.comic.places = new_path
        self.comic.generate_metadata()
