from glob import glob
from lxml import etree
from os.path import abspath, join
from zipfile import ZipFile

class Entry(object):
    def __init__(self, node):
        self._ns = { 'n': node.nsmap[None] }
        self.type = node.type
        self.id = node.get('id')
        self.name = self.get_text('n:name', node)
        self.added = self.get_text('n:added', node)
        self.modified = self.get_text('n:modified', node)
        self.rank = self.get_text('n:rank', node)

    def get_text(self, tag, node):
        return ''.join([n.text for n in node.xpath(tag, namespaces=self._ns)])
    
    def get_attr(self, tag, node):
        return ''.join([n for n in node.xpath(tag, namespaces=self._ns)])

    def get_children(self, tag, node):
        return node.xpath(tag, namespaces=self._ns)


class Data(object):
    """OmniFocus data store."""

    def __init__(self):
        self.data = {}

    def prase_contents(self, contents):
        tree = etree.fromstring(contents)

        for element in tree.xpath('*'):
            if (element.get('op') == 'delete' and
                element.get('id') in self.data):
                del self.data[element.get('id')]
            else:
                
                self.data[element.id] = element


class LocalData(Data):
    """A local OmniFocus data store."""

    def __init__(self, path):
        Data.__init__(self)

        zip_files = glob(abspath(join(path, '*.zip')))

        for filename in zip_files:
            with ZipFile(filename, 'r') as zip_obj:
                contents = zip_obj.read('contents.xml')
                self.prase_contents(contents)
