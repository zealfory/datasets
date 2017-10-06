import io
import logging

from ..data import findhandler



class Transform:
    def __init__(self, definition):
        self.definition = definition
       
    @staticmethod
    def create(definition):
        t = TransformerList()
        for item in definition:
            if isinstance(item, list):
                name, d = item
                t.append(findhandler("transform", name, d))
            else:
                t.append(findhandler("transform", item, {}))
        return t

    def __call__(self, input):
        raise NotImplementedError("__call__ should be implemented in subclass %s" % type(self))

class Gunzip(Transform):
    def __call__(self, fileobj):
        import gzip
        return gzip.GzipFile(fileobj=fileobj)

class TransformerList(Transform):
    def __init__(self):
        self.list = []

    def append(self, item):
        self.list.append(item)

    def __call__(self, fileobj):
        for item in self.list:
            fileobj = item(fileobj)
        return fileobj


class LineTransformStream(io.RawIOBase):
    def __init__(self, fileobj, transform):
        self.current = ""
        self.offset = 1
        self.fileobj = fileobj
        self.transform = transform

    def readable(self):
        return True
    
    def readnext(self):
        # Read next line and transform
        self.offset = 0
        self.current = self.transform(self.fileobj.readline().decode("utf-8")).encode("utf-8")

    def readinto(self, b):
        offset = 0
        lb = len(b)
        while lb > 0:
            if self.offset >= len(self.current):
                self.readnext()
                if len(self.current) == 0:
                    return 0

            # How many bytes to read from current line
            l = min(lb, len(self.current) - self.offset)

            b[offset:(offset+l)] = self.current[self.offset:(self.offset+l)]
            lb -= l
            offset += l
            self.offset += l

        return offset

class Replace(Transform):
    """Line by line transform"""
    def __init__(self, content):
        import re
        self.re = re.compile(content["pattern"])
        self.repl = content["repl"]
       
    def __call__(self, fileobj):
        return LineTransformStream(fileobj, lambda s: self.re.sub(self.repl, s))
