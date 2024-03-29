#!/usr/bin/python3
"""
This module parses IMDB ratings data and produce summaries, statistics and plots out of them.
It's a versatile utility for IMDB data transformations.
"""

import pandas
import csv
import collections
from   dataclasses import dataclass
from   datetime    import datetime
import itertools
import json
import os
import sys
import typing
import terminal
import textwrap
import translate
from copy import copy
pyplot = None

gt = translate.get

with open(f'{os.path.dirname(__file__)}/color-schemes.json') as color_scheme:
    colors = json.load(color_scheme)

def ensure_pyplot_is_imported():
    global pyplot
    if pyplot is None:
        from   matplotlib  import pyplot as pyplot_ # type: ignore
        pyplot = pyplot_

@dataclass
class Entry:
    "Entry in ratings.csv IMDB data"

    title: str
    rating: int
    date: datetime
    genres: list[str]
    title_type: str

    def __lt__(self, other):
        return self.title < other.title

Entries = list[Entry]

def load_ratings(filename: str, encoding: str ='iso-8859-1') -> Entries:
    "Loads ratings file content as list of Entry"
    with open(filename, 'r', encoding=encoding) as csv_file:
        entries = list(csv.reader(csv_file))

        indexes = dict(zip(entries[0], itertools.count(0)))
        assert all(key in entries[0] for key in ['Title', 'Your Rating', 'Release Date', 'Genres', 'Title Type'])

        return [Entry(
                title  = entry[indexes['Title']],
                rating = int(entry[indexes['Your Rating']]),
                date   = datetime.strptime(entry[indexes['Release Date']], '%Y-%m-%d'),
                genres = [genre.strip() for genre in entry[indexes['Genres']].split(',')],
                title_type = entry[indexes['Title Type']]
                )
                for entry in entries[1:]]

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
    occurs = collections.Counter(entry.rating for entry in entries)
    ratings_sum = sum(occurs.values())
    for key in sorted(occurs.keys(), reverse=True):
        rating = occurs[key]
        print(f'{key}:\t{rating}\t{rating / ratings_sum * 100:.1f}%')

def mk_plot(entries : Entries):
    "Creates bar plot of ratings"
    ensure_pyplot_is_imported()
    occurs = collections.Counter(entry.rating for entry in entries)

    pyplot.rcParams['axes.edgecolor']  = colors["foreground"]["dimmer"]
    pyplot.rcParams['axes.labelcolor'] = colors["foreground"]["normal"]
    pyplot.rcParams['lines.color']     = colors["foreground"]["normal"]
    pyplot.rcParams['text.color']      = colors["foreground"]["normal"]
    pyplot.rcParams['xtick.color']     = colors["foreground"]["normal"]
    pyplot.rcParams['ytick.color']     = colors["foreground"]["normal"]

    pyplot.figure(facecolor=colors["background"]["normal"])
    pyplot.axes().set_facecolor(colors["background"]["dimmer"])

    indicies = list(range(1, 11))
    rects = pyplot.bar(indicies, [occurs[index] for index in indicies], width=0.7)
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

    height = 5 * (max(occurs.values()) // 5 + 1)
    pyplot.yticks(range(0, height + 5, 5))
    pyplot.ylim(ymin=0, ymax=height)

def draw_ascii_plot(entries: Entries):
    occurs = collections.Counter(entry.rating for entry in entries)
    max_count = max(occurs.values())
    increment = max_count / 25
    longest_label_length = 2 # len("10")

    # https://alexwlchan.net/2018/ascii-bar-charts/
    def draw_ascii_bar(label, count):
        nonlocal increment, longest_label_length
        bar_chunks, r = divmod(int(count * 8 // increment), 8)
        bar = '█' * bar_chunks
        if r > 0:
            bar += chr(ord('█') + (8 - r))
        bar = bar or  '▏'
        print(f'{label.rjust(longest_label_length)} ▏ {count:#4d} {bar}')

    for rating in range(1, 11):
        draw_ascii_bar(str(rating), occurs[rating])


def draw_plot(entries: Entries):
    "Draws plot and renders it as window"
    ensure_pyplot_is_imported()
    mk_plot(entries)
    pyplot.show()

def draw_plot_to(path: str):
    "Draws plot to file"
    ensure_pyplot_is_imported()
    def draw(entries: Entries):
        mk_plot(entries)
        pyplot.savefig(path)
    return draw

def genres(entries: Entries):
    "Prints genres summary"
    occurances = collections.Counter(genre for entry in entries for genre in entry.genres)

    genres_count = sum(occurances.values())
    max_genre_length = max(len(genre) for genre in occurances)
    for genre, occurs in sorted(occurances.items(), key=lambda x: x[1], reverse=True):
        print("%s%s  %s%%" % (
            genre.ljust(max_genre_length+2),
            str(occurs).rjust(4),
            ("%.2f" % (occurs / genres_count * 100,)).rjust(5)
        ))

def years(entries: Entries):
    "Prints how many ratings are for given years"
    occurs = collections.Counter(entry.date.year for entry in entries)

    for year in sorted(occurs.keys()):
        percent = occurs[year] / len(entries) * 100
        print(f"{year}: {occurs[year]} ({percent:.2f})")

def top(entries: Entries):
    "Prints top movies (max rating) that I watched from given year"
    years: dict[int, list[Entry]] = {}
    for entry in entries:
        years[entry.date.year] = years.get(entry.date.year, [])
        years[entry.date.year].append(entry)

    for year, xs in years.items():
        xs.sort(key=lambda x: x.rating, reverse=True)
        years[year] = [x for x in xs if x.rating == xs[0].rating]

    for year in sorted(years.keys()):
        print(f"{year} (max rating = {years[year][0].rating}):")
        for x in years[year]:
            print(f"  {x.title}")


def filter_title(titles: list[str], entries: Entries) -> Entries:
    "Filters entries that contains one of given phrases"
    needles = [title.lower() for title in titles]
    return [entry for entry in entries if any(needle in entry.title.lower() for needle in needles)]

def filter_rating(rating: list[int], entries: Entries) -> Entries:
    "Filters entries that contains one of given ratings"
    return sorted([entry for entry in entries if entry.rating in rating])

def filter_years(years: list[int], entries: Entries) -> Entries:
    return sorted([entry for entry in entries if entry.date.year in years])

def filter_out_title_types(tt: list[str], entries: Entries) -> Entries:
    return sorted([entry for entry in entries if entry.title_type not in tt])

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

        {terminal.bold("with-year <year>")}
        {terminal.bold("wy <year>")}
          Leaves only those titles that have year `year`
          Can be specified as range, for example 2010-2013, will leave only those with years 2010, 2011, 2012, 2013

        {terminal.bold("without-type <type>")}
        {terminal.bold("wty <type>")}
                          TODO

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
    rating, title, with_year, without_title_type = [], [], [], []

    args = {
        "language": "en",
        "path":     "ratings.csv",
        "final":    summarize,
        "scheme":   "gruvbox"
    }

    class Matched(Exception):
        "Signals that given branch was matched"

    def require_argument(flag_name: str):
        if not argv_clone:
            print(f"Parameter {terminal.bold(flag_name)} requires an argument", file=sys.stderr)
            sys.exit(1)
        return argv_clone.pop(0)

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

    argv_clone = copy(sys.argv)
    argv_clone.pop(0)
    if not argv_clone:
        print_help()


    while argv_clone:
        command = argv_clone.pop(0)
        if command == "help":
            print_help()

        try:
            unary_argument("language", "lang")
            unary_argument("path")
            unary_argument("scheme", "color-scheme", "colors")

            nary_argument(rating, "with-rating", "wr", mapping=rating_spec)
            nary_argument(with_year, "with-year",   "wy", mapping=rating_spec)
            nary_argument(title,  "with-title",  "wt")
            nary_argument(without_title_type, "without-type", "wty") # This is awful

            final_argument(draw_ascii_plot, "ap", "ascii-plot")
            final_argument(draw_plot,       "p", "plot")
            final_argument(genres,          "g", "genres")
            final_argument(ratings,         "r", "ratings")
            final_argument(top,             "t", "top")
            final_argument(years,           "y", "years")

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

    if without_title_type:
        entries = filter_out_title_types(without_title_type, entries)

    if with_year:
        entries = filter_years(with_year, entries)

    if title:
        entries = filter_title(title, entries)



    if not entries:
        print("All entries has been filtered out")
        return

    args["final"](entries)

if __name__ == '__main__':
    main()
