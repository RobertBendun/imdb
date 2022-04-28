#!/usr/bin/python3
from collections import namedtuple
from datetime    import datetime
from matplotlib  import pyplot as plot
from types       import SimpleNamespace as Namespace
from dataclasses import dataclass
import argparse
import csv
import itertools
import json
import os
import sys
import textwrap
import translate

gt = translate.get

with open(f'{os.path.dirname(__file__)}/color-schemes.json') as f:
    Colors = json.load(f)

@dataclass
class Entry:
    title: str
    rating: float
    date: datetime
    genres: list[str]

    def __lt__(self, other):
        return self.title < other.title

Entries = list[Entry]

def load_ratings(filename: str, encoding: str ='iso-8859-1') -> Entries:
    with open(filename, 'r', encoding=encoding) as f:
        entries = list(csv.reader(f))

        indexes = dict(zip(entries[0], itertools.count(0)))
        assert all(key in entries[0] for key in ['Title', 'Your Rating', 'Release Date', 'Genres'])

        return [Entry(
                title  = entry[indexes['Title']],
                rating = int(entry[indexes['Your Rating']]),
                date   = datetime.strptime(entry[indexes['Release Date']], '%Y-%m-%d'),
                genres = [genre.strip() for genre in entry[indexes['Genres']].split(',')]
                )
                for entry in entries[1:]]

def ratings_occurance(entries : Entries) -> list[int]:
    ratings = [0] * 10
    for entry in entries:
        ratings[entry.rating - 1] += 1
    return ratings

def print_table(rows : Entries):
    max_title_length = max(len(e.title) for e in rows)

    for e in rows:
        print(e.title.ljust(max_title_length+2), e.rating, sep='')

def summary(entries : list[Entry]):
    print('\n================ '+ gt('SUMMARY') + ' ================')
    print(f'{gt("Found")}: ', len(entries))

    if len(set(e.rating for e in entries)) != 1:
        print(f'{gt("Average rating")}: ', '%.2f / 10' % (sum(e.rating for e in entries) / len(entries)))

def ratings(entries : Entries):
    ratings     = ratings_occurance(entries)
    ratings_sum = sum(ratings)
    for i, r in sorted(zip(itertools.count(1), ratings), key = lambda x: x[1], reverse = True):
        print(f'{i}:\t{r}\t%.1f%%' % (r / ratings_sum * 100))

def mk_plot(entries : Entries):
    ratings = ratings_occurance(entries)

    plot.rcParams['axes.edgecolor']  = Colors["foreground"]["dimmer"]
    plot.rcParams['axes.labelcolor'] = Colors["foreground"]["normal"]
    plot.rcParams['lines.color']     = Colors["foreground"]["normal"]
    plot.rcParams['text.color']      = Colors["foreground"]["normal"]
    plot.rcParams['xtick.color']     = Colors["foreground"]["normal"]
    plot.rcParams['ytick.color']     = Colors["foreground"]["normal"]

    plot.figure(facecolor=Colors["background"]["normal"])
    plot.axes().set_facecolor(Colors["background"]["dimmer"])

    rects = plot.bar(list(range(1, 11)), ratings, width=0.7)
    for i, rect in enumerate(rects):
        rect.set_color(Colors["bar"][i * 3 // len(rects)])

        # Add value label to each bar
        height = rect.get_height()
        plot.text(rect.get_x() + rect.get_width() / 2,
                  1.01 * height,
                  '%d' % int(height),
                  color=Colors["bar_value"],
                  ha='center', va='bottom')

    plot.title(gt('IMDB Ratings'))
    plot.xlabel(gt('Rating'))
    plot.xticks(range(1, 11))
    plot.ylabel(gt('Rating count'))


    height = 5 * (max(ratings) // 5 + 1)
    plot.yticks(range(0, height + 5, 5))
    plot.ylim(ymin=0, ymax=height)


def draw_plot(entries: Entries):
    mk_plot(entries)
    plot.show()

def draw_plot_to(path: str):
    def draw(entries: Entries):
        mk_plot(entries)
        plot.savefig(path)
    return draw


def genres(entries: Entries):
    occurances = {}
    for genre in (genre for entry in entries for genre in entry.genres):
        if genre in occurances:
            occurances[genre] += 1
        else:
            occurances[genre] = 1

    genres_count = sum(occurances.values())

    max_genre_length = max(len(genre) for genre in occurances.keys())

    for genre, occurances in sorted(occurances.items(), key=lambda x: x[1], reverse=True):
        print("%s%s  %s%%" % (
            genre.ljust(max_genre_length+2),
            str(occurances).rjust(4),
            ("%.2f" % (occurances / genres_count * 100,)).rjust(5)
        ))

def filter_title(titles: list[str], entries: Entries) -> Entries:
    needles = [title.lower() for title in titles]
    return [entry for entry in entries if any(needle in entry.title.lower() for needle in needles)]

def filter_rating(rating: list[int], entries: Entries) -> Entries:
    return sorted([entry for entry in entries if entry.rating in rating])

def summarize(entries: Entries):
    print_table(entries)
    summary(entries)

def rating_spec(spec: str):
    if '-' in spec:
        start, finish = map(int, spec.split('-'))
        return list(range(start, finish+1))
    return int(spec)

def main():
    global Colors
    rating   = []
    title    = []

    args = {
        "language": "en",
        "path":     "ratings.csv",
        "final":    summarize,
        "language": "en",
        "path":     "ratings.csv",
        "scheme":   "gruvbox"
    }

    def require_argument(flag_name):
        if not sys.argv:
            print(f"Parameter {flag_name} requires an argument", file=sys.stderr)
            exit(1)
        return sys.argv.pop(0)

    def unary_argument(*names: list[str]):
        if command in names:
            args[names[0]] = require_argument(names[0])
            return True
        return False

    def nary_argument(target: list, *names: list[str], mapping = None):
        if command not in names:
            return False

        arg = require_argument(names[0])
        if mapping is not None:
            arg = mapping(arg)

        if isinstance(arg, list):
            target.extend(arg)
        else:
            target.append(arg)
        return True


    def final_argument(f, *names: list[str]):
        if command in names:
            args["final"] = f
            return True
        return False

    def final_argument_unary(f, *names: list[str]) -> bool:
        if command in names:
            args["final"] = f(require_argument(names[0]))
            return True
        return False

    sys.argv.pop(0)
    while sys.argv:
        command = sys.argv.pop(0)

        if unary_argument("language", "lang") or \
           unary_argument("path") or \
           unary_argument("scheme", "color-scheme", "colors") or \
           nary_argument(title,  "with-title",  "wt") or \
           nary_argument(rating, "with-rating", "wr", mapping=rating_spec) or \
           final_argument(ratings,      "r", "ratings") or \
           final_argument(genres,       "g", "genres") or \
           final_argument(draw_plot,    "p", "plot") or \
           final_argument_unary(draw_plot_to, "save-plot"):
            continue
        else:
            print(f"Unrecognized command '{command}'", file=sys.stderr)
            exit(1)


    Colors = Colors[args["scheme"].lower()]
    translate.set_language(args["language"].lower())
    entries = load_ratings(args["path"])
    if rating:
        entries = filter_rating(rating, entries)

    if title:
        entries = filter_title(title, entries)

    if not entries:
        print("All entries has been filtered out")
        return

    args["final"](entries)

if __name__ == '__main__':
    main()
