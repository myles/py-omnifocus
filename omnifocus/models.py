from datetime import datetime
from glob import glob
from lxml import etree
from os.path import abspath, join
from zipfile import ZipFile


class Entry(object):
    def __init__(self, node):

        self._ns = {'n': node.nsmap[None]}
        self.type = node.get('type')
        self.id = node.get('id')
        self.name = self.get_text('n:name', node)
        self.added = self.parse_timestamp(self.get_text('n:added', node))
        self.modified = self.parse_timestamp(self.get_text('n:modified', node))
        self.rank = self.get_text('n:rank', node)

    def parse_timestamp(self, timestamp):
        if timestamp:
            return datetime.strptime(timestamp[:19], '%Y-%m-%dT%H:%M:%S')
        else:
            return None

    def get_text(self, tag, node):
        return ''.join([n.text for n in node.xpath(tag, namespaces=self._ns)])

    def get_attr(self, tag, node):
        return ''.join([n for n in node.xpath(tag, namespaces=self._ns)])

    def get_children(self, tag, node):
        return node.xpath(tag, namespaces=self._ns)


class Task(Entry):
    def __init__(self, node):
        Entry.__init__(self, node)

        self.due = self.parse_timestamp(self.get_text('n:due', node))
        self.parent = self.get_attr('n:task/@idref', node)
        self.context = self.get_attr('n:context/@idref', node)
        self.order = self.get_text('n:order', node)

        if len(self.get_children('n:project', node)) > 0:
            p = self.get_children('n:project', node)[0]
            self.project = True
            self.last_review = self.get_text('n:last-review', p)
            self.review_interval = self.get_text('n:review-interval', p)
            self.parent = self.get_attr('n:folder/@idref', p)

        if len(self.get_children('n:inbox', node)) > 0:
            self.inbox = True


class Data(object):
    """OmniFocus data store."""

    def __init__(self):
        self.data = {}

    def parse_setting(self, node):
        return Entry(node)

    def parse_context(self, node):
        return Entry(node)

    def parse_folder(self, node):
        return Entry(node)

    def parse_task(self, node):
        return Task(node)

    def parse_persective(self, node):
        return Entry(node)

    def parse_contents(self, contents):
        # TODO: I don't know how to escape `{}` strings.
        namespace = '{{http://www.omnigroup.com/namespace/OmniFocus/v1}}{}'

        parsers = {
            namespace.format('setting'): self.parse_setting,
            namespace.format('context'): self.parse_context,
            namespace.format('folder'): self.parse_folder,
            namespace.format('task'): self.parse_task,
            namespace.format('perspective'): self.parse_persective
        }

        tree = etree.fromstring(contents)

        for el in tree.xpath('*'):
            if (el.get('op') == 'delete' and
                    el.get('id') in self.data):
                del self.data[el.get('id')]
            else:
                obj = parsers[el.tag](el)
                self.data[el.get('id')] = obj


class LocalData(Data):
    """A local OmniFocus data store."""

    def __init__(self, path):
        Data.__init__(self)

        zip_files = glob(abspath(join(path, '*.zip')))

        for filename in zip_files:
            with ZipFile(filename, 'r') as zip_obj:
                contents = zip_obj.read('contents.xml')
                self.parse_contents(contents)
