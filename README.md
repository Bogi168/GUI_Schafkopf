# GUI Schafkopf

A Bavarian Schafkopf card game for one human player and three computer
opponents, written in Python. It comes with a pygame table view and a
plain-terminal mode, and the bots play with rule-aware heuristics: they
choose games by hand strength, infer teams and voids from the cards played,
schmier, pull trumps, run away with the callsau, and defend Touts.

## Game modes

| Mode | Description |
|---|---|
| Sauspiel | The classic partner game: the chooser calls a Sau, its owner is the secret teammate. Sau-Zwang and Davonlaufen are enforced. |
| Hochzeit | A player with exactly one trump offers it; chooser and partner swap a card. |
| Wenz | Only the four Unter are trump, the chooser plays alone. |
| Solo | Ober, Unter and a chosen color are trump, the chooser plays alone. |
| Wenz Tout / Solo Tout | The chooser must win every single trick; doubled value. |
| Ramsch | Nobody wanted to play: most points loses, Durchmarsch wins. |

Doubling (Legen), shooting (Schießen/Zurückschießen), Schneider, Schwarz and
Laufende are all part of the scoring, and every player's money balance is
tracked across games.

## Requirements

- Python 3.12+
- [pygame](https://www.pygame.org/) (only for the GUI mode): `pip install pygame`

## Running

From the project root:

```bash
# pygame GUI (default)
python3 -m system.run

# terminal mode, no pygame needed
python3 -m system.run --console
```

## Tests

```bash
python3 -m pytest tests/
```

## Project layout

```
card_classes/       Cards, deck, card power calculators
game_classes/       Game (ABC), game modes, rounds, teams, runners
input_validators/   Legal-move and game-choice validation
money_handling/     Winners selection, game value, money distribution
player_classes/     Player/Bot, bot heuristics, team-knowledge inference
schafkopf_classes/  Schafkopf orchestrator (main loop)
system/             Renderer ABC, console renderer, pygame GUI, display texts
tests/              pytest suite
```

The architecture is described in more detail in [CLAUDE.md](CLAUDE.md).
