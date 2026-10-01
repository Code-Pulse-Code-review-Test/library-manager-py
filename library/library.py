import json
import os
from datetime import date, timedelta

from library.models import Book, Member, Loan

LOAN_DAYS = 14
MAX_BOOKS = 3
MAX_RENEWALS = 2
FINE_PER_DAY = 10


class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.loans = []

    def add_book(self, isbn, title, author, copies=1):
        if isbn in self.books:
            self.books[isbn].copies += copies
        else:
            self.books[isbn] = Book(isbn, title, author, copies)

    def add_member(self, member_id, name, email):
        if member_id in self.members:
            raise ValueError("member already exists")
        self.members[member_id] = Member(member_id, name, email)

    def available(self, isbn):
        book = self.books[isbn]
        out = len([l for l in self.loans if l.isbn == isbn and l.returned_on is None])
        return book.copies - out

    def lend(self, isbn, member_id, today=None):
        today = today or date.today()
        if isbn not in self.books:
            raise ValueError("no such book")
        if member_id not in self.members:
            raise ValueError("no such member")
        member = self.members[member_id]
        if len(member.borrowed) >= MAX_BOOKS:
            raise ValueError("member has too many books")
        if self.available(isbn) <= 0:
            raise ValueError("no copies left")
        loan = Loan(isbn, member_id, today, today + timedelta(days=LOAN_DAYS))
        self.loans.append(loan)
        member.borrowed.append(isbn)
        return loan

    def return_book(self, isbn, member_id, today=None):
        today = today or date.today()
        loan = self._open_loan(isbn, member_id)
        loan.returned_on = today
        self.members[member_id].borrowed.remove(isbn)
        return self.fine(loan, today)

    def renew(self, isbn, member_id, today=None):
        today = today or date.today()
        loan = self._open_loan(isbn, member_id)
        if loan.due_on < today:
            raise ValueError("overdue books cannot be renewed")
        if loan.renewals >= MAX_RENEWALS:
            raise ValueError("loan already renewed " + str(MAX_RENEWALS) + " times")
        loan.due_on = loan.due_on + timedelta(days=LOAN_DAYS)
        loan.renewals += 1
        return loan

    def _open_loan(self, isbn, member_id):
        for loan in self.loans:
            if loan.isbn == isbn and loan.member_id == member_id and loan.returned_on is None:
                return loan
        raise ValueError("loan not found")

    def fine(self, loan, today):
        late_days = (today - loan.due_on).days
        if late_days <= 0:
            return 0
        return late_days * FINE_PER_DAY

    def overdue(self, today=None):
        today = today or date.today()
        return [l for l in self.loans if l.returned_on is None and l.due_on < today]

    def search(self, text):
        text = text.lower()
        return [b for b in self.books.values() if text in b.title.lower() or text in b.author.lower()]

    def save(self, path):
        data = {
            "books": [vars(b) for b in self.books.values()],
            "members": [{"member_id": m.member_id, "name": m.name, "email": m.email} for m in self.members.values()],
            "loans": [_loan_to_dict(loan) for loan in self.loans],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, path):
        if not os.path.exists(path):
            return
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            print("could not read", path)
            return
        for b in data["books"]:
            self.add_book(b["isbn"], b["title"], b["author"], b["copies"])
        for m in data["members"]:
            self.add_member(m["member_id"], m["name"], m["email"])
        # files saved before loans were kept have no "loans" key
        for loan_data in data.get("loans", []):
            loan = _loan_from_dict(loan_data)
            self.loans.append(loan)
            if loan.returned_on is None:
                self.members[loan.member_id].borrowed.append(loan.isbn)


def _loan_to_dict(loan):
    return {
        "isbn": loan.isbn,
        "member_id": loan.member_id,
        "borrowed_on": loan.borrowed_on.isoformat(),
        "due_on": loan.due_on.isoformat(),
        "returned_on": loan.returned_on.isoformat() if loan.returned_on else None,
        "renewals": loan.renewals,
    }


def _loan_from_dict(data):
    returned = data["returned_on"]
    return Loan(
        data["isbn"],
        data["member_id"],
        date.fromisoformat(data["borrowed_on"]),
        date.fromisoformat(data["due_on"]),
        date.fromisoformat(returned) if returned else None,
        data.get("renewals", 0),
    )
