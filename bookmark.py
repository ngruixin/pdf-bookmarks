import argparse
import json
import sys
from PyPDF2 import PdfFileReader


def _setup_page_id_to_num(pdf, pages=None, _result=None, _num_pages=None):
    """
    Map page ids to page numbers
    From: https://stackoverflow.com/questions/8329748/how-to-get-bookmarks-page-number
    """
    if _result is None:
        _result = {}
    if pages is None:
        _num_pages = []
        pages = pdf.trailer["/Root"].getObject()["/Pages"].getObject()
    t = pages["/Type"]
    if t == "/Pages":
        for page in pages["/Kids"]:
            _result[page.idnum] = len(_num_pages)
            _setup_page_id_to_num(pdf, page.getObject(), _result, _num_pages)
    elif t == "/Page":
        _num_pages.append(1)
    return _result


def get_bookmarks(outlines, pg_id_num_map):
    """
    Return dictionary bookmarks in the form
    {
        <title of page>: <page number>,
        ...
    }
    Params outlines is the list of outlines extracted
           pg_id_num_map is the map of pages to number
    """
    bookmarks = {}
    for outline in outlines:
        try:
            if isinstance(outline, list):
                embedded_bookmarks = get_bookmarks(outline, pg_id_num_map)
                bookmarks = {**bookmarks, **embedded_bookmarks}
            else:
                bookmarks[outline.title] = pg_id_num_map[outline.page.idnum] + 1
        except Exception as e:
            pass
    return bookmarks


def export_bookmarks(bookmarks, filepath):
    """
    Writes the bookmarks to a json file
    """
    with open(filepath, "w") as outfile:
        json.dump(bookmarks, outfile, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Exports PDF bookmarks in json format."
    )
    parser.add_argument("--pdf", type=str, help="PDF file to extract bookmarks from")
    parser.add_argument(
        "--output",
        type=str,
        default="bookmarks.json",
        help="Filename of exported PDF bookmarks (default: bookmarks.json)",
    )
    args = parser.parse_args()
    pdf_path = args.pdf
    output = args.output
    pdf = PdfFileReader(pdf_path, "rb")
    pg_id_num_map = _setup_page_id_to_num(pdf)
    outlines = pdf.getOutlines()
    bookmarks = get_bookmarks(outlines, pg_id_num_map)
    export_bookmarks(bookmarks, output)
