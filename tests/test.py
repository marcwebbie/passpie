import inspect
import os
import shutil
import sys
import unittest


__file__ = os.path.abspath(inspect.getsourcefile(lambda _: None))

TEST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
TEST_DATABASE_DIR = os.path.join(TEST_DIR, "database", "data")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pysswords


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.path = TEST_DATABASE_DIR

    def tearDown(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def test_create_makedirs_at_path(self):
        test_path = os.path.join(self.path, "creation")
        pysswords.db.create(path=test_path)
        self.assertTrue(os.path.exists(test_path))


if __name__ == "__main__":
    unittest.main()
