#!/usr/bin/env python3
"""
Generates a CSV report file from screenshots of your BPI eSOA statement.

This is used to circumvent encrypted PDF text extraction of the eSOA.

NOTE:
Another way to solve this, is to simply print to PDF the eSOA which will
effectively create a new PDF without encryption.

"""

import csv
import itertools as it
import re
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    import Image

import pytesseract


MONTHS = 'jan feb mar apr may jun jul aug sep oct nov dec'.split()
AMOUNT_PAT = re.compile(r'^[0-9,\-]{1,}\.[0-9]{2}$')
IGNORE_LINES = (
    'U.S. Dollar',
)


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return it.zip_longest(*args, fillvalue=fillvalue)


def to_string(img_path):
    return pytesseract.image_to_string(Image.open(img_path))


def is_date(text):
    txt_len, txt_low = len(text), text.lower()
    return True if any(
        txt_low.startswith(i)
        if txt_len > len(i) else
        i.startswith(txt_low)
        for i in MONTHS
    ) else False


def is_ignored(text):
    return True if any(i in text for i in IGNORE_LINES) else False


def parse_data(img_text):
    img_text = (i.strip() for i in img_text.split('\n') if i.strip())
    dates, description, amounts = [], [], []
    for text in img_text:
        if is_ignored(text):
            continue
        if is_date(text):
            dates.append(text)
        elif AMOUNT_PAT.match(text):
            amounts.append(text)
        else:
            description.append(text)
    dates = [i for i in grouper(dates, 2, '')]
    return dates, description, amounts


def main(images):
    report_fh = Path(
        'bpi_soa_extract_{:%m%Y}.csv'.format(datetime.now())
    )
    headers = 'transaction_date post_date description amount'.split()
    report_csv = csv.DictWriter(report_fh.open('w'), fieldnames=headers)
    report_csv.writeheader()

    img_data = (parse_data(to_string(i)) for i in images)
    for data in img_data:
        try:
            for (trans_date, post_date), desc, amount in (
                it.zip_longest(*data, fillvalue='')):
                report_csv.writerow({
                    'transaction_date': trans_date,
                    'post_date': post_date,
                    'description': desc,
                    'amount': amount,
                })
        except ValueError:
            import pdb
            pdb.set_trace()

    print('Report file written in {}'.format(report_fh))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'IMAGES',
        nargs='+',
    )

    args = parser.parse_args()

    main(args.IMAGES)
