#!/usr/bin/python3
import csv
import sys

needle = int(sys.argv[1])

matched_count = 0

with open('ratings.csv', 'r', encoding='iso-8859-1') as f:
    # Skip header, we are assuming that order of columns never changes
    for entry in list(csv.reader(f))[1:]:
        title, rating = entry[3], entry[1]
        if needle == int(rating):
            print(title)
            matched_count += 1


print('=========== SUMMARY ===========')
print('Matched: ', matched_count)
