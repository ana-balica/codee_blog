from __future__ import absolute_import
from __future__ import unicode_literals
from urlparse import urljoin

from markdown import Extension
from markdown.treeprocessors import Treeprocessor


class AbsoluteImagesExtension(Extension):
    """ Absolute Images Extension """

    def __init__(self, configs=[]):
        self.config = {
            'base_url': [None,
                         "The base URL to which the relative paths will be appended"],
        }

        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        absolute_images = AbsoluteImagesTreeprocessor(md)
        absolute_images.config = self.getConfigs()
        md.treeprocessors.add("absoluteimages", absolute_images, "_end")

        md.registerExtension(self)


class AbsoluteImagesTreeprocessor(Treeprocessor):
    """ Absolute Images Treeprocessor """
    def run(self, root):
        imgs = root.getiterator("img")
        for image in imgs:
            if self.is_relative(image.attrib["src"]):
                image.set("src", self.make_external(image.attrib["src"]))

    def make_external(self, path):
        return urljoin(self.config["base_url"], path)

    def is_relative(self, link):
        if link.startswith('http'):
            return False
        return True


def makeExtension(configs=[]):
    """ Return an instance of the AbsoluteImagesExtension """
    return AbsoluteImagesExtension(configs=configs)
