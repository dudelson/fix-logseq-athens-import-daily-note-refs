''' This script fixes a bug I found in the logseq database I converted from
athens using [1] where links to daily notes weren't converted to match
the date format I'm using in logseq (the Roam-style format). It identifies all
links to daily notes (e.g. "[[November 07, 2021]]") and rewrites them to use the
roam-style form (e.g. "[[November 7th, 2021]]").

[1]: https://github.com/shepheb/athens-export
'''

import argparse
import calendar
import fileinput
import itertools as it
import re
from pathlib import Path


def reformat_day_of_month(date_str):
    '''Given a string representing the day of the month, return the "Anglicized"
    version. For example, given "07" as input, return "7th". The input string
    is expected to be a valid representation of a month date, i.e. in the range
    "01" to "31". This function does not expect single-digit dates to be
    zero-padded, so e.g. "2" is also valid.
    '''
    # compute date suffix
    date_num = int(date_str)
    date_suffix = 'th'
    if date_num % 10 == 1 and date_num != 11:
        date_suffix = 'st'
    elif date_num % 10 == 2 and date_num != 12:
        date_suffix = 'nd'
    elif date_num % 10 == 3 and date_num != 13:
        date_suffix = 'rd'

    return '{}{}'.format(date_num, date_suffix)


def main():
    parser = argparse.ArgumentParser(description="Fix daily page links in logseq db generated from athens conversion")
    parser.add_argument('--db', help="Path to the logseq db to fix")
    parser.add_argument(
        '--dry',
        action='store_true',
        help="Do a dry run (do not actually modify any files)"
    )
    args = parser.parse_args()
    db_path = Path(args.db).expanduser().resolve()

    print('Fixing the db at {}'.format(db_path))

    # compile regex
    months_str = '|'.join(calendar.month_name[1:])
    daily_note_link_regex = re.compile(
        r'\[\[(' + months_str + r') (\d{1,2}), (202[01])\]\]'
    )

    # walk all journals and pages
    journals = db_path.glob('journals/*.md')
    pages = db_path.glob('pages/*.md')

    # for each line in each file, run re.sub on the line
    if args.dry:
        print('Would update the following file lines:')
        with fileinput.input(files=it.chain(journals, pages)) as f:
            for line in f:
                updated_line = daily_note_link_regex.sub(
                    lambda m: '[[{} {}, {}]]'.format(
                        m.group(1), reformat_day_of_month(m.group(2)), m.group(3)),
                    line
                )
                if updated_line != line:  # there's been a change
                    print('  => {}: {}'.format(fileinput.filename(), updated_line))
    else:
        with fileinput.input(files=it.chain(journals, pages), inplace=True) as f:
            for line in f:
                updated_line = daily_note_link_regex.sub(
                    lambda m: '[[{} {}, {}]]'.format(
                        m.group(1), reformat_day_of_month(m.group(2)), m.group(3)),
                    line
                )
                print(updated_line, end='')

    print('\nDone.')


if __name__ == '__main__':
    main()
