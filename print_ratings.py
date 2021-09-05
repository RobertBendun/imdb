#!/usr/bin/python3
from csv import reader
from itertools import count, chain
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

from types import SimpleNamespace as Namespace

Colors = Namespace(
  Background        = '#3c3836',
  Background_Dimmer = '#282828',
  Bar               = [
    '#fb4934',
    '#fabd2f',
    '#b8bb26',
  ],
  Bar_Value         = '#d5c4a1',
  Foreground        = '#ebddb2',
  Foreground_Dimmer = '#bdae93',
)

if graph_flag:
  from matplotlib.pyplot import *

  rcParams['axes.edgecolor']  = Colors.Foreground_Dimmer
  rcParams['axes.labelcolor'] = Colors.Foreground
  rcParams['lines.color']     = Colors.Foreground
  rcParams['text.color']      = Colors.Foreground
  rcParams['xtick.color']     = Colors.Foreground
  rcParams['ytick.color']     = Colors.Foreground

  figure(facecolor=Colors.Background)
  axes().set_facecolor(Colors.Background_Dimmer)

  rects = bar(list(range(1, 11)), ratings, width=0.7)
  for i, rect in enumerate(rects):
    height = rect.get_height()
    text(rect.get_x() + rect.get_width() / 2.0, 1.01 * height, '%d' % int(height), ha='center', va='bottom', color=Colors.Bar_Value)
    rect.set_color(Colors.Bar[i * 3 // len(rects)])

  title('IMDB Ratings')
  xlabel('Rating')
  xticks(range(1, 11))
  ylabel('Ratings count')
  show()
