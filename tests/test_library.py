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

    def test_renew_pushes_due_date(self):
        start = date(2026, 1, 1)
        self.lib.lend("1", "M1", start)
        loan = self.lib.renew("1", "M1", start + timedelta(days=10))
        self.assertEqual(loan.due_on, date(2026, 1, 29))

    def test_renew_limit_and_overdue(self):
        start = date(2026, 1, 1)
        self.lib.lend("1", "M1", start)
        self.lib.renew("1", "M1", start)
        self.lib.renew("1", "M1", start)
        with self.assertRaises(ValueError):
            self.lib.renew("1", "M1", start)
        with self.assertRaises(ValueError):
            self.lib.renew("1", "M1", date(2026, 3, 1))


if __name__ == "__main__":
    unittest.main()
