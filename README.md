# imdb

This repository is a collection of scripts that we find useful for browsing data collected on IMDB.
To get your ratings data go to 'Your Ratings' and export.

## Capabilities

| Command | Functionality |
| --- | --- |
| `imdb.py plot` | Plots in a window ratings occurance |
| `imdb.py ratings` | Shows statistics about ratings |
| `imdb.py with-rating <rating>` | Shows all entries with given rating |
| `imdb.py with-title <phrase>` | Shows all entries having `phrase` in the title |

### Example plot
```
$ imdb.py plot -o example.png
```
![picture of example plot](./example.png)

Used color scheme is [Gruvbox](https://github.com/morhetz/gruvbox).
