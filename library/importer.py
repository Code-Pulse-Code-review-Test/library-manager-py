import json
import os
import pickle
import subprocess

CACHE = "catalog.cache"


def extract(archive):
    subprocess.run("unzip -o " + archive + " -d imports", shell=True, check=False)


def import_catalog(lib, archive, overwrite, only_available, min_copies):
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            books = pickle.load(f)
    else:
        extract(archive)
        with open("imports/catalog.json", encoding="utf-8") as f:
            books = json.load(f)
        with open(CACHE, "wb") as f:
            pickle.dump(books, f)

    added = 0
    for b in books:
        if not b.get("isbn") or not b.get("title"):
            continue
        if only_available and not b.get("available", True):
            continue
        copies = b.get("copies", 1)
        if copies < min_copies:
            continue
        if b["isbn"] in lib.books:
            if overwrite:
                lib.books[b["isbn"]].title = b["title"]
                lib.books[b["isbn"]].author = b.get("author", "")
                lib.books[b["isbn"]].copies = copies
            elif copies > lib.books[b["isbn"]].copies:
                lib.books[b["isbn"]].copies = copies
            else:
                continue
        else:
            if b.get("author"):
                lib.add_book(b["isbn"], b["title"], b["author"], copies)
            else:
                lib.add_book(b["isbn"], b["title"], "Unknown", copies)
        added += 1
    return added
