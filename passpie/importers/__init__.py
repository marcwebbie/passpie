import inspect
import os
import glob
import logging

import pkg_resources


class BaseImporter(object):

    def log(self, message):
        logging.debug(message)

    @property
    def name(self):
        return self.__class__.__name__.lower().replace('importer', '')

    def match(self, filepath):
        """Return True if file for filepath parseable by importer
        """
        raise NotImplementedError('Handle should be implemented by base class')

    def handle(self, filepath):
        """Return all credentials decrypted from filepath
        """
        raise NotImplementedError('Handle should be implemented by base class')


__all__ = [os.path.basename(f)[:-3]
           for f in glob.glob(os.path.dirname(__file__) + "/*.py")]


def _import_all_importer_files():
    __import__(__name__, globals(), locals(), __all__, 0)


def _get_importers_from_entry_points():
    for ep in pkg_resources.iter_entry_points('passpie_importers'):
        try:
            module = __import__(ep.module_name, globals(), locals(), ep.attrs, 0)
            klass = getattr(module, ep.attrs[0])
            if klass is not BaseImporter and issubclass(klass, BaseImporter):
                yield klass
        except (ImportError, AttributeError):
            pass


def get_all():
    """Get all subclasses of BaseImporter from module and return and generator
    """

    _import_all_importer_files()

    for module in (value for key, value in globals().items()
                   if key in __all__):
        for klass_name, klass in inspect.getmembers(module, inspect.isclass):
            if klass is not BaseImporter and issubclass(klass, BaseImporter):
                yield klass

    for klass in _get_importers_from_entry_points():
        yield klass


def get_instances():
    """Get instances of all found detected importer classes"""
    return (wclass() for wclass in get_all())


def get_names():
    return [i.name for i in get_instances()]


def get(name):
    try:
        return next(i for i in get_instances() if i.name == name)
    except StopIteration:
        return None


def find_importer(filepath):
    for importer in get_instances():
        if importer.match(filepath):
            return importer
