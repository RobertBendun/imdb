#!/usr/bin/python3
from csv import reader
from itertools import count
from sys import argv

graph_flag = any(flag in ['-g', '--graph'] for flag in argv)

ratings = list(0 for _ in range(10))
with open('ratings.csv', 'r', encoding='iso-8859-1') as f:
	for entry in list(reader(f))[1:]:
		ratings[int(entry[1]) - 1] += 1

# ------------------------------------------------------
# Print ratings by popularity
# ------------------------------------------------------
if not graph_flag:
    ratings_sum = sum(ratings)
    ratings_by_popularity = sorted(
        zip(count(1), ratings),
        key=lambda x: x[1],
        reverse=True)

    for i, r in ratings_by_popularity:
        print(f'{i}:\t{r}\t%.1f%%' % (r / ratings_sum * 100))

# ------------------------------------------------------
# Show graph of ratings
# ------------------------------------------------------
if graph_flag:
	from matplotlib.pyplot import *
	bar(list(range(1, 11)), ratings, width=0.5)
	xlabel('Ocena')
	ylabel('Liczba udzielonych ocen')
	title('IMDB Ratings')
	show()
