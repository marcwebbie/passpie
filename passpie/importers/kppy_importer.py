import imp
import os
import platform
import sys

import click
import pkg_resources

from passpie.importers import BaseImporter
from passpie.credential import make_fullname


def prepare_pycrypto_for_import():
    # pycrypto's setup.py does not use setuptools, and this breaks the pycrypto
    # installation on Python3 + Windows. Until pycrypto will update it's
    # setup.py we can use this hack to import the required .pyd-s manually

    if sys.version_info[1] < 3 or platform.system().lower() != 'windows':
        return

    pyds = [
        'Crypto.Cipher._AES',
        'Crypto.Cipher._ARC2',
        'Crypto.Cipher._ARC4',
        'Crypto.Cipher._Blowfish',
        'Crypto.Cipher._CAST',
        'Crypto.Cipher._DES',
        'Crypto.Cipher._DES3',
        'Crypto.Cipher._XOR',
        'Crypto.Hash._MD2',
        'Crypto.Hash._MD4',
        'Crypto.Hash._RIPEMD160',
        'Crypto.Hash._SHA224',
        'Crypto.Hash._SHA256',
        'Crypto.Hash._SHA384',
        'Crypto.Hash._SHA512',
        'Crypto.Random.OSRNG.winrandom',
        'Crypto.Util._counter',
        'Crypto.Util.strxor',
    ]

    crypto_path = pkg_resources.resource_filename('Crypto', '')

    for import_path in pyds:
        try:
            __import__(import_path)
        except ImportError:
            import_path_splitted = import_path.split('.')
            pyd_basename = import_path_splitted[-1]
            pyd_dir = os.path.join(crypto_path, *import_path_splitted[1:-1])

            pyd_path = None
            for pyd_name_format in ('_%s.pyd', '%s.pyd', '%.so'):
                _pyd_path = os.path.join(pyd_dir, pyd_name_format % pyd_basename)
                if os.path.exists(_pyd_path):
                    pyd_path = _pyd_path
                    break
            if not pyd_path:
                continue

            # loaded under the key that setup.py without setuptools can find it
            loaded_module = imp.load_dynamic(pyd_basename, pyd_path)
            # with this it will also be set under the normal path in sys.modules
            sys.modules[import_path] = loaded_module


try:
    prepare_pycrypto_for_import()
    from kppy.database import KPDBv1
    from kppy.entries import v1Entry
    from kppy.exceptions import KPError
    _found_kppy = True
except ImportError:
    _found_kppy = False


class KppyImporter(BaseImporter):

    def match(self, filepath):
        if not _found_kppy:
            self.log('kppy is not installed')
            return False

        if not os.path.isfile(filepath):
            self.log('Filepath "{}" is not a file'.format(filepath))
            return False

        if os.path.splitext(filepath)[1].lower() != '.kdb':
            self.log('Filepath "{}" is not a Keepass database'.format(filepath))
            return False

        return True

    def handle(self, filepath):
        passphrase = click.prompt('Keepass passphrase', hide_input=True)

        try:
            # TODO add keyfile support
            db = KPDBv1(filepath=str(filepath), password=str(passphrase),
                        read_only=True)
            db.load()
        except KPError as e:
            self.log(str(e))
            return []
        except Exception as e:
            self.log(str(e))
            return []
        else:
            try:
                credentials = []

                for entry in db.entries:
                    group_names_str = self.compute_group_name(entry)

                    entry_fullname = make_fullname(
                        entry.username, group_names_str)

                    credential_dict = {
                        'fullname': entry_fullname,
                        'name': group_names_str,
                        'login': entry.username,
                        'password': entry.password,
                        'comment': (entry.comment or '').strip(),
                        'modified': entry.creation,
                    }
                    credentials.append(credential_dict)

                return credentials
            finally:
                db.close()

    @staticmethod
    def compute_group_name(kp_entry):
        if not isinstance(kp_entry, v1Entry):
            raise TypeError('kp_entry is not a kppy.entries.v1Entry')

        group_names = [kp_entry.url]

        group = kp_entry.group
        while group:
            if group.title:
                group_names.insert(0, group.title)
            group = group.parent

        group_names_str = '/'.join(
            e.strip() for e in group_names if e)

        return group_names_str