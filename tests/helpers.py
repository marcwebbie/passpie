import unittest

try:
    from unittest.mock import patch, Mock, MagicMock, mock_open
except ImportError:
    from mock import patch, Mock, MagicMock, mock_open


class MockerTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.mock_open = mock_open
        self.Mock = Mock
        self.MagicMock = MagicMock

        super(MockerTestCase, self).__init__(*args, **kwargs)

    def patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def patch_object(self, *args, **kwargs):
        patcher = patch.object(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def patch_multiple(self, *args, **kwargs):
        patcher = patch.multiple(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def patch_dict(self, *args, **kwargs):
        patcher = patch.dict(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing


ENCRYPTED_DATA = """
-----BEGIN PGP MESSAGE-----

hQEMA1xKO0QntlBSAQgAnojr1QGGxd3ihH7ET0mlNkfpvb4tKLySNeKFoj+DqjI2
OxtJgD+adpalSAMQD5L57ttxPWSXzhXgnbCZslxFQWYz30j3BnaNe4cV4JMuL3qF
8/1E0xpZIBIza7I8Loo7IV7fVzKdv00T6gKImQQRgPVdTrLcmHk3xX8xEwTmdIdy
ZCjk3Hnn/i5AkXjIjxJ3NiGsAyAPZWtX91PRN2X4+GuIaN7sWMCGzzOY2roZxmNb
mMRpAb7NzxORORHbWXjH/0Y09DkaqNoZVBDN0fp2bYmFClU98ULW4NlyK6xcuTkp
2c5WMeX70maRzciXC81HnfASvFYPlgm0aquTi+/rstJSAaDQIXPCL5GQX4TQ9Vyy
ni3FsO40+4UBXUm03cLiy8wWTL2OIxs3QmVY2HsUGacypZf+r3NNwV3/4bR757qj
JmNIw2541RSIoUbitA8aw7el/w==
=VRFD
-----END PGP MESSAGE-----
"""
