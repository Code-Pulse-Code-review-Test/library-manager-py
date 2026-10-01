from dataclasses import dataclass, field
from datetime import date


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    copies: int = 1


@dataclass
class Member:
    member_id: str
    name: str
    email: str
    borrowed: list = field(default_factory=list)


@dataclass
class Loan:
    isbn: str
    member_id: str
    borrowed_on: date
    due_on: date
    returned_on: date = None
    renewals: int = 0
