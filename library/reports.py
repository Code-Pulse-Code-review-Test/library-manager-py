from datetime import date


def member_report(lib, member_id, today=None):
    today = today or date.today()
    member = lib.members[member_id]
    lines = []
    lines.append("Member: " + member.name)
    lines.append("Email: " + member.email)
    total_fine = 0
    for loan in lib.loans:
        if loan.member_id == member_id:
            title = lib.books[loan.isbn].title
            if loan.returned_on is None:
                if loan.due_on < today:
                    fine = lib.fine(loan, today)
                    total_fine += fine
                    lines.append("  " + title + " - OVERDUE, fine so far " + str(fine))
                else:
                    lines.append("  " + title + " - due " + str(loan.due_on))
            else:
                if loan.returned_on > loan.due_on:
                    lines.append("  " + title + " - returned late")
                else:
                    lines.append("  " + title + " - returned")
    if total_fine > 0:
        lines.append("Total fine: " + str(total_fine))
    return "\n".join(lines)


def overdue_report(lib, today=None):
    today = today or date.today()
    lines = []
    for loan in lib.overdue(today):
        book = lib.books[loan.isbn]
        member = lib.members[loan.member_id]
        days = (today - loan.due_on).days
        lines.append(book.title + " with " + member.name + " (" + str(days) + " days late)")
    return "\n".join(lines)
