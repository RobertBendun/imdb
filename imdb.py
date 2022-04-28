#!/usr/bin/python3
"""
This module parses IMDB ratings data and produce summaries, statistics and plots out of them.
It's a versatile utility for IMDB data transformations.
"""

import csv
from   dataclasses import dataclass
from   datetime    import datetime
import itertools
import json
import os
import sys
import typing
from   matplotlib  import pyplot # type: ignore
import terminal
import textwrap
import translate

gt = translate.get

with open(f'{os.path.dirname(__file__)}/color-schemes.json') as color_scheme:
    colors = json.load(color_scheme)

@dataclass
class Entry:
    "Entry in ratings.csv IMDB data"

    title: str
    rating: int
    date: datetime
    genres: list[str]

    def __lt__(self, other):
        return self.title < other.title

Entries = list[Entry]

def load_ratings(filename: str, encoding: str ='iso-8859-1') -> Entries:
    "Loads ratings file content as list of Entry"
    with open(filename, 'r', encoding=encoding) as csv_file:
        entries = list(csv.reader(csv_file))

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
    "Returns ratings occurance list"
    occurance = [0] * 10
    for entry in entries:
        occurance[entry.rating - 1] += 1
    return occurance

def print_table(rows : Entries) -> int:
    "Prints table of titles & ratings. Returns max line length"
    max_title_length = max(len(e.title) for e in rows)

    max_line_length = 0
    for entry in rows:
        line = entry.title.ljust(max_title_length+2) + str(entry.rating)
        print(line)
        max_line_length = max(max_line_length, len(line))

    return max_line_length

def summary(entries : list[Entry], max_line_length: int):
    "Prints summary of entries"
    title = gt('SUMMARY')
    length = max(max_line_length - len(title) - 2, 6)
    left_length, right_length = length // 2, length // 2 + (length % 2)
    print(f"\n{left_length * '='} {terminal.bold(title)} {right_length * '='}")
    print(f'{gt("Found")}: ', len(entries))

    if len(set(entry.rating for entry in entries)) != 1:
        avg = sum(entry.rating for entry in entries) / len(entries)
        print(f'{gt("Average rating")}: {avg:.2f} / 10')

def ratings(entries : Entries):
    "Prints ratings summary"
    occurs      = ratings_occurance(entries)
    ratings_sum = sum(occurs)
    for i, rating in sorted(zip(itertools.count(1), occurs), key = lambda x: x[1], reverse = True):
        print(f'{i}:\t{rating}\t{rating / ratings_sum * 100:.1f}%')

def mk_plot(entries : Entries):
    "Creates bar plot of ratings"
    occurs = ratings_occurance(entries)

    pyplot.rcParams['axes.edgecolor']  = colors["foreground"]["dimmer"]
    pyplot.rcParams['axes.labelcolor'] = colors["foreground"]["normal"]
    pyplot.rcParams['lines.color']     = colors["foreground"]["normal"]
    pyplot.rcParams['text.color']      = colors["foreground"]["normal"]
    pyplot.rcParams['xtick.color']     = colors["foreground"]["normal"]
    pyplot.rcParams['ytick.color']     = colors["foreground"]["normal"]

    pyplot.figure(facecolor=colors["background"]["normal"])
    pyplot.axes().set_facecolor(colors["background"]["dimmer"])

    rects = pyplot.bar(list(range(1, 11)), occurs, width=0.7)
    for i, rect in enumerate(rects):
        rect.set_color(colors["bar"][i * 3 // len(rects)])

        # Add value label to each bar
        height = rect.get_height()
        pyplot.text(rect.get_x() + rect.get_width() / 2,
                  1.01 * height,
                  str(int(height)),
                  color=colors["bar_value"],
                  ha='center', va='bottom')

    pyplot.title(gt('IMDB Ratings'))
    pyplot.xlabel(gt('Rating'))
    pyplot.xticks(range(1, 11))
    pyplot.ylabel(gt('Rating count'))

    height = 5 * (max(occurs) // 5 + 1)
    pyplot.yticks(range(0, height + 5, 5))
    pyplot.ylim(ymin=0, ymax=height)


def draw_plot(entries: Entries):
    "Draws plot and renders it as window"
    mk_plot(entries)
    pyplot.show()

def draw_plot_to(path: str):
    "Draws plot to file"
    def draw(entries: Entries):
        mk_plot(entries)
        pyplot.savefig(path)
    return draw


def genres(entries: Entries):
    "Prints genres summary"
    occurances : dict[str, int] = {}
    for genre in (genre for entry in entries for genre in entry.genres):
        if genre in occurances:
            occurances[genre] += 1
        else:
            occurances[genre] = 1

    genres_count = sum(occurances.values())
    max_genre_length = max(len(genre) for genre in occurances)
    for genre, occurs in sorted(occurances.items(), key=lambda x: x[1], reverse=True):
        print("%s%s  %s%%" % (
            genre.ljust(max_genre_length+2),
            str(occurs).rjust(4),
            ("%.2f" % (occurs / genres_count * 100,)).rjust(5)
        ))

def filter_title(titles: list[str], entries: Entries) -> Entries:
    "Filters entries that contains one of given phrases"
    needles = [title.lower() for title in titles]
    return [entry for entry in entries if any(needle in entry.title.lower() for needle in needles)]

def filter_rating(rating: list[int], entries: Entries) -> Entries:
    "Filters entries that contains one of given ratings"
    return sorted([entry for entry in entries if entry.rating in rating])

def summarize(entries: Entries):
    "Prints summary"
    summary(entries, print_table(entries))

def rating_spec(spec: str):
    "Parses rating specification"
    if '-' in spec:
        start, finish = map(int, spec.split('-'))
        return list(range(start, finish+1))
    return int(spec)

def print_help():
    languages = ', '.join(translate.available_languages)
    schemes   = ', '.join(sorted(colors.keys()))

    print(textwrap.dedent(f"""
    imdb.py queries
      where queries is one or more commands from the list below:

        {terminal.bold("with-title <phrase>")}
        {terminal.bold("wt <phrase>")}
          Leaves only those titles that contains <phrase> in them

        {terminal.bold("with-rating <rating>")}
        {terminal.bold("wr <rating>")}
          Leaves only those titles that have rating rating
          Can be specified as range, for example 5-7, will leave only those with rating 5, 6, 7

        {terminal.bold("genres")}
        {terminal.bold("g")}
          Prints genre statistics

        {terminal.bold("ratings")}
        {terminal.bold("r")}
          Prints ratings statistics

        {terminal.bold("plot")}
        {terminal.bold("p")}
          Generates bar plot of ratings

        {terminal.bold("save-plot <path>")}
        {terminal.bold("sp <path>")}
          Saves generated bar plot in <path>

        {terminal.bold("path <path>")}
          Sets ratings file path (default: './ratings.csv')

        {terminal.bold("language <language>")}
          Sets language used in output.
          Available languages: {languages}

        {terminal.bold("color-scheme <color-scheme>")}
        {terminal.bold("colors <color-scheme>")}
        {terminal.bold("scheme <color-scheme>")}
          Sets color scheme used in graphical output (default: gruvbox)
          Available color schemes: {schemes}

        {terminal.bold("help")}
          Prints this message.
    """).strip())
    sys.exit(1)

def main():
    global colors
    rating, title = [], []

    args = {
        "language": "en",
        "path":     "ratings.csv",
        "final":    summarize,
        "scheme":   "gruvbox"
    }

    class Matched(Exception):
        "Signals that given branch was matched"

    def require_argument(flag_name: str):
        if not sys.argv:
            print(f"Parameter {terminal.bold(flag_name)} requires an argument", file=sys.stderr)
            sys.exit(1)
        return sys.argv.pop(0)

    def unary_argument(*names: list[str]):
        if command in names:
            args[names[0]] = require_argument(names[0])
            raise Matched()

    def nary_argument(target: list, *names: list[str], mapping = None):
        if command not in names:
            return

        arg = require_argument(names[0])
        if mapping is not None:
            arg = mapping(arg)

        if isinstance(arg, list):
            target.extend(arg)
        else:
            target.append(arg)
        raise Matched()

    def final_argument(final: typing.Callable, *names: list[str]):
        if command in names:
            args["final"] = final
            raise Matched()

    def final_argument_unary(final: typing.Callable, *names: list[str]) -> bool:
        if command in names:
            args["final"] = final(require_argument(names[0]))
            raise Matched()

    sys.argv.pop(0)
    if not sys.argv:
        print_help()

    while sys.argv:
        command = sys.argv.pop(0)
        if command == "help":
            print_help()

        try:
            unary_argument("language", "lang")
            unary_argument("path")
            unary_argument("scheme", "color-scheme", "colors")

            nary_argument(rating, "with-rating", "wr", mapping=rating_spec)
            nary_argument(title,  "with-title",  "wt")

            final_argument(draw_plot, "p", "plot")
            final_argument(genres,    "g", "genres")
            final_argument(ratings,   "r", "ratings")

            final_argument_unary(draw_plot_to, "save-plot", "sp")
        except Matched:
            continue

        print(f"Unrecognized command '{command}'", file=sys.stderr)
        sys.exit(1)

    colors = colors[args["scheme"].lower()]
    translate.set_language(args["language"].lower())

    try:
        entries = load_ratings(args["path"])
    except FileNotFoundError as file_not_found:
        print(f"Cannot find file '{file_not_found.filename}'.", file=sys.stderr)
        print(f"Try specifing file with 'imdb.py path /path/to/ratings/file.csv'", file=sys.stderr)
        sys.exit(1)

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
