#!/usr/bin/env python3
"""
Transaction dates and prices extractor for BPI eSOA

Usage:

1.) Prepare the input file.

Open your BPI eSOA and copypasta your transaction table and paste it in a text
file and save it.

2.) Run the script

```
python bpi_esoa_extract.py <input_file.txt>
```

3.) Prepare the spreadsheet

The script will produce 2 files:
    - <input_filename>_dates.txt
    - <input_filename>_prices.txt

Copypasta the contents of the dates and prices in a spreadsheet. Note that the
prices text file might have foreign currency prices so just delete those.

The dates and prices should align nicely after.

"""
import argparse
import re
import sys
from pathlib import Path


PRICE_PAT = re.compile(
    r'[0-9\,]{1,}\.[0-9]{2}'
)
DATE_PAT = re.compile(
    r'((January|February|March|April|May|June|July|August|September|October|'
    r'November|December) [1-9]{1,2})'
)


def main(input_file):
    # Extract data
    fp = Path(input_file)
    prices = PRICE_PAT.findall(fp.read_text())
    dates = DATE_PAT.findall(fp.read_text())

    if not dates or not prices:
        print('No valid transactions found!')
        sys.exit(1)

    # Write transactions dates
    fo = fp.parent.joinpath(f'{fp.stem}_dates.txt')
    group_dates, iter_dates = [], iter(dates)
    for d in iter_dates:
        group_dates.append(
            f'{d[0]}\t{next(iter_dates)[0]}'
        )
    fo.write_text('\n'.join(group_dates))
    print(f'Transaction dates file written to: {fo}')

    # Write transactions prices
    fo = fp.parent.joinpath(f'{fp.stem}_prices.txt')
    fo.write_text('\n'.join(prices))
    print(f'Transaction prices file written to: {fo}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('INPUT_FILE')
    args = parser.parse_args()

    main(args.INPUT_FILE)
