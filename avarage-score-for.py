#!/usr/bin/python3
import argparse
import csv
import datetime
from collections import namedtuple

parser = argparse.ArgumentParser()

parser.add_argument('needle', help='phrase to match against titles')
parser.add_argument('-r', '--rating-date', help='Sorts output by rating date', action='store_true')

args = parser.parse_args()
needle = args.needle.lower()

avg_rating, matched_count, max_title_length = 0, 0, 0
output = []

with open('ratings.csv', 'r', encoding='iso-8859-1') as f:
    # Skip header, we are assuming that order of columns never changes

    # Imperative
    for entry in list(csv.reader(f))[1:]:
        title, rating, date = entry[3], entry[1], entry[11]

        if needle in title.lower():
            avg_rating += int(rating)
            matched_count += 1
            max_title_length = max(max_title_length, len(title))
            output.append((title, rating, date))

    avg_rating /= matched_count

    # Declarative
    Entry = namedtuple('Entry', 'title rating date')
    entries = list(Entry(entry[3], entry[1], entry[11]) for entry in csv.reader(f))[1:]
    entries = [e for e in entries if needle in e.title.lower()]
    avg_rating = sum(int(e.rating) for e in entries) / len(entries)
    max_title_length = max(len(e.title) for e in entries)




if not args.rating_date:
    output.sort(key=lambda x: datetime.datetime.strptime(x[2], '%Y-%m-%d'))

for title, rating, _ in output:
    spacing = " " * (max_title_length - len(title) + 2)
    print(title, spacing, rating, sep='')

print('=========== SUMMARY ===========')
print('Matched: ', matched_count)
print('Avarage rating: %.2f / 10' % avg_rating)

def print_help():
    import os
    filename = os.path.basename(__file__)
    print(f"""
USAGE
    {filename} [searched phrase]

DESCRIPTION
    This script searches for matching titles to given phrase
    in provided ratings CSV file from IMDB to find avarage score.
    Useful for finding avarage score of the show.
""".strip())
