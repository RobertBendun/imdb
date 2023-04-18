#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import mplcyberpunk

plt.style.use("cyberpunk")

df = pd.read_csv("ratings.csv")
df.rename(columns={"Const": "ID"}, inplace=True)
means = df[["Year", "Your Rating"]].groupby("Year").mean()

sns.set_palette(sns.color_palette("pastel6"))

years = df[["Year"]]
min, max = years.min()[0], years.max()[0]

plot = sns.lineplot(x="Year", y="Your Rating", data=df[["Year", "Your Rating"]])
plot.set(title=f"Average ratings across years ({min}-{max})")
fig = plot.get_figure()
mplcyberpunk.make_lines_glow()
fig.savefig("output.png")


