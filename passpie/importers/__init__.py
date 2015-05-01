import inspect
import os
import glob


class BaseImporter(object):
    pass


__all__ = [os.path.basename(f)[:-3]
           for f in glob.glob(os.path.dirname(__file__) + "/*.py")]


def _import_all_importer_files():
    __import__(__name__, globals(), locals(), __all__, 0)


def get_all():
    """Get all subclasses of BaseImporter from module and return and generator
    """

    _import_all_importer_files()

    for module in (value for key, value in globals().items() if key in __all__):
        for klass_name, klass in inspect.getmembers(module, inspect.isclass):
            if klass is not BaseImporter and issubclass(klass, BaseImporter):
                yield klass


def get_instances():
    """Get instances of all found detected importer classes"""
    return (wclass() for wclass in get_all())


def find_importer(filepath):
    for importer in get_instances():
        if importer.match(filepath):
            return importer
