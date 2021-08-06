#!/usr/bin/python3
from collections import namedtuple
from datetime import datetime
from itertools import count
import argparse
import csv
import sys
import textwrap

Entry = namedtuple('Entry', 'title rating date')

def load_ratings(filename, encoding='iso-8859-1'):
    with open(filename, 'r', encoding=encoding) as f:
        entries = list(csv.reader(f))

        indexes = dict(zip(entries[0], count(0)))
        assert all(key in entries[0] for key in ['Title', 'Your Rating', 'Release Date'])

        return [Entry(
                title = entry[indexes['Title']],
                rating = int(entry[indexes['Your Rating']]),
                date = datetime.strptime(entry[indexes['Release Date']], '%Y-%m-%d'))
                for entry in entries[1:]]

def print_table(rows):
    max_title_length = max(len(e.title) for e in rows)

    for title, rating, _ in rows:
        spacing = " " * (max_title_length - len(title) + 2)
        print(title, spacing, rating, sep='')

def summary(entries, avg = False):
    print('\n================ SUMMARY ================')
    print('Found: ', len(entries))

    if avg:
        print('Avarage rating: ', '%.2f / 10' % (sum(e.rating for e in entries) / len(entries)))

def on_with_rating(args, entries):
    entries = [entry for entry in entries if entry.rating in args.rating]
    print_table(entries)
    summary(entries)

def on_with_title(args, entries):
    needle = args.title.lower()
    entries = [entry for entry in entries if needle in entry.title.lower()]

    if not args.rating_date:
        entries.sort(key=lambda entry: entry.date)

    print_table(entries)
    summary(entries, avg=True)

def on_ratings(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            prog='imdb',
            description=textwrap.dedent("""
                This is a collection of useful tools for browsing user ratings
                data collected by IMDB. To download source data, login to your IMDB account
                and in 'Your ratings' click on Export link.
                Exported CSV file is necessary for this application.
            """).strip())

    parser.add_argument('-p', '--path', help='Path to a ratings file (default: ratings.csv)', default='ratings.csv')

    subparsers = parser.add_subparsers()

    with_rating = subparsers.add_parser('with-rating', help='Shows all entries with given rating', aliases=['wr'])
    with_rating.add_argument('rating', type=int, nargs='+', help='Rating to search for')
    with_rating.set_defaults(handler=on_with_rating)

    with_title = subparsers.add_parser('with-title', help='Shows all entries with given title', aliases=['wt'])
    with_title.add_argument('title', help='Phrase to look for in titles')
    with_title.add_argument('-r', '--rating-date', help='Sorts output by rating date', action='store_true')
    with_title.set_defaults(handler=on_with_title)

    ratings = subparsers.add_parser('ratings', help='Shows statistics about ratings', aliases='r')
    ratings.set_defaults(handler=on_ratings)

    if len(sys.argv) == 1:
        parser.print_help()
        exit()

    args = parser.parse_args()
    args.handler(args, load_ratings(args.path))
