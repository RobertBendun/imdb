#!/usr/bin/python3
from collections import namedtuple
from datetime import datetime
from itertools import count
import argparse
import csv
import sys

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

def on_with_rating(args):
    pass

def on_with_title(args):
    pass

def on_ratings(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='imdb')

    parser.add_argument('-p', '--path', help='Path to a ratings file (default: ratings.csv)', default='ratings.csv')

    subparsers = parser.add_subparsers()

    parser_with_rating = subparsers.add_parser('with-rating', help='Shows all entries with given rating', aliases=['wr'])
    parser_with_rating.add_argument('rating', type=int, help='Rating to search for')
    parser_with_rating.set_defaults(handler=on_with_rating)

    parser_find = subparsers.add_parser('with-title', help='Shows all entries with given title', aliases=['wt'])
    parser_find.add_argument('title', help='Phrase to look for in titles')
    parser_find.set_defaults(handler=on_with_title)

    parser_ratings = subparsers.add_parser('ratings', help='Shows statistics about ratings', aliases='r')
    parser_ratings.set_defaults(handler=on_ratings)

    if len(sys.argv) == 1:
        parser.print_help()
        exit()

    args = parser.parse_args()
    args.handler(args)
