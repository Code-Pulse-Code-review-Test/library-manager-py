from datetime import date, timedelta

from library.library import Library
from library.reports import member_report, overdue_report

lib = Library()
lib.add_book("9780132350884", "Clean Code", "Robert C. Martin", 2)
lib.add_book("9780201633610", "Design Patterns", "Gamma et al.", 1)
lib.add_member("M001", "Dilini", "dilini@example.com")
lib.add_member("M002", "Sahan", "sahan@example.com")

lib.lend("9780132350884", "M001", date.today() - timedelta(days=20))
lib.lend("9780201633610", "M002")

print(member_report(lib, "M001"))
print()
print("Overdue:")
print(overdue_report(lib))
