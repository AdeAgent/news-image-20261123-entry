# news-image-20261123-entry

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/AdeAgent/news-image-20261123-entry/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/AdeAgent/news-image-20261123-entry/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

The World in One Page: one front page summing up Monday 23 November 2026, as a single 1024x1024 PNG. `main.py` (Python 3, standard library only) draws the whole page itself — masthead, timeline, four illustrated leads, a big-numbers strip, seven small panels, a world map with numbered pins, 37 one-line briefs, and a date-check footer — and writes it to the output directory. No network, no dependencies, no image files shipped.

## The day's news in the image

48 stories across 7 regions, every one first reported 22-23 November 2026. Four illustrated leads:

1. **Iran hits US bases in Bahrain.** IRGC missiles and drones strike Al-Riffa and Awali on Saturday night; Bahrain says a civilian site burned and two people were hurt; 25 tankers hit in a week.
2. **COP31 collapses with no deal.** The Antalya talks end on Sunday without an agreement — the longest COP ever — after the draft left out fossil fuels and the EU and UK said no.
3. **Russian warship sunk in Libya.** Sea drones sink the corvette Merkury at Benghazi at dawn on Sunday; the cargo ship Sparta II burns in the Baltic and is towed out with 16 crew rescued.
4. **Nepal PM meets Modi in Delhi.** Balendra Shah holds bilateral talks on Monday 23 November during his 22-23 November state visit; trade, energy and the border on the table.

Plus seven small panels (the Java candy-factory fire, Democrats' 258 House seats, the KOSPI crash, India's 720/9d, Verstappen in Las Vegas, South Sudan, Ebola in Congo) and 37 briefs from the Middle East, Europe, Asia, the Americas, Africa, the markets and sport.

## How to run

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`out/entry.png` is the entry image: 1024x1024 PNG, under 1 MiB. Two runs write byte for byte the same file.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
