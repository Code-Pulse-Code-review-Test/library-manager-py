import csv
from datetime import date


def book_status(lib, isbn, today=None):
    today = today or date.today()
    book = lib.books.get(isbn)
    if book is None:
        return "unknown"
    active = [l for l in lib.loans if l.isbn == isbn and l.returned_on is None]
    if not active:
        if book.copies == 0:
            return "lost"
        elif book.copies == 1:
            return "on shelf"
        else:
            return "on shelf (" + str(book.copies) + " copies)"
    late = [l for l in active if l.due_on < today]
    if len(active) == book.copies:
        if late:
            if len(late) == len(active):
                return "all copies overdue"
            elif len(late) > 1:
                return "out, some overdue"
            else:
                return "out, one overdue"
        else:
            if book.copies == 1:
                return "out"
            return "all copies out"
    else:
        if late:
            if len(late) > 1:
                return "partly out, some overdue"
            return "partly out, one overdue"
        return "partly out"


# calls add_row with the first three columns of each row after the header
def _import_rows(path, add_row):
    count = 0
    errors = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 3:
                errors += 1
                continue
            try:
                add_row(row[0].strip(), row[1].strip(), row[2].strip())
                count += 1
            except ValueError as e:
                print("skipping row", row, e)
                errors += 1
    print("imported", count, "rows,", errors, "errors")
    return count


def import_books(lib, path):
    return _import_rows(path, lib.add_book)


def import_members(lib, path):
    return _import_rows(path, lib.add_member)
