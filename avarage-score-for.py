#!/usr/bin/python3
import csv
import datetime
import sys

def main():
    needle = sys.argv[1].lower()

    avg_rating = 0
    matched_count = 0
    max_title_length = 0
    output = []

    with open('ratings.csv', 'r', encoding='iso-8859-1') as f:
        # Skip header, we are assuming that order of columns never changes
        for entry in list(csv.reader(f))[1:]:
            title, rating, date = entry[3], entry[1], entry[11]

            if needle in title.lower():
                avg_rating += int(rating)
                matched_count += 1
                max_title_length = max(max_title_length, len(title))
                output.append((title, rating, date))

    avg_rating /= matched_count

    output.sort(key=lambda x: datetime.datetime.strptime(x[2], '%Y-%m-%d'))

    for title, rating, _ in output:
        spacing = " " * (max_title_length - len(title) + 2)
        print("%s%s%s" % (title, spacing, rating))

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


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main()
    else:
        print_help()
