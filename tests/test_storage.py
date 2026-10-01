import os
import tempfile
import unittest
from datetime import date

from library.library import Library


class SaveLoadTest(unittest.TestCase):
    def setUp(self):
        handle, self.path = tempfile.mkstemp(suffix=".json")
        os.close(handle)
        self.lib = Library()
        self.lib.add_book("1", "Book One", "Someone", 2)
        self.lib.add_member("M1", "Test", "t@example.com")

    def tearDown(self):
        os.remove(self.path)

    def reload(self):
        self.lib.save(self.path)
        loaded = Library()
        loaded.load(self.path)
        return loaded

    def test_open_loans_are_kept(self):
        self.lib.lend("1", "M1", date(2026, 1, 1))
        loaded = self.reload()
        self.assertEqual(loaded.available("1"), 1)
        self.assertEqual(loaded.members["M1"].borrowed, ["1"])
        self.assertEqual(loaded.loans[0].due_on, date(2026, 1, 15))

    def test_renewals_are_kept(self):
        self.lib.lend("1", "M1", date(2026, 1, 1))
        self.lib.renew("1", "M1", date(2026, 1, 5))
        self.assertEqual(self.reload().loans[0].renewals, 1)

    def test_returned_loans_are_kept(self):
        self.lib.lend("1", "M1", date(2026, 1, 1))
        self.lib.return_book("1", "M1", date(2026, 1, 20))
        loaded = self.reload()
        self.assertEqual(loaded.loans[0].returned_on, date(2026, 1, 20))
        self.assertEqual(loaded.members["M1"].borrowed, [])
        self.assertEqual(loaded.available("1"), 2)

    def test_file_without_loans(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write('{"books": [], "members": []}')
        loaded = Library()
        loaded.load(self.path)
        self.assertEqual(loaded.loans, [])


if __name__ == "__main__":
    unittest.main()
