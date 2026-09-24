import unittest
from datetime import date, timedelta

from library.library import Library


class LibraryTest(unittest.TestCase):
    def setUp(self):
        self.lib = Library()
        self.lib.add_book("1", "Book One", "Someone", 1)
        self.lib.add_member("M1", "Test", "t@example.com")

    def test_lend_and_return(self):
        self.lib.lend("1", "M1")
        self.assertEqual(self.lib.available("1"), 0)
        self.assertEqual(self.lib.return_book("1", "M1"), 0)
        self.assertEqual(self.lib.available("1"), 1)

    def test_no_copies_left(self):
        self.lib.add_member("M2", "Other", "o@example.com")
        self.lib.lend("1", "M1")
        with self.assertRaises(ValueError):
            self.lib.lend("1", "M2")

    def test_late_fine(self):
        start = date(2026, 1, 1)
        self.lib.lend("1", "M1", start)
        fine = self.lib.return_book("1", "M1", start + timedelta(days=17))
        self.assertEqual(fine, 30)


if __name__ == "__main__":
    unittest.main()
