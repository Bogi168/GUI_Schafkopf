# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands must be run from the project root, as imports use package-relative paths.

**Run the game (pygame GUI):**
```bash
python3 -m system.run
```

**Run the game in the terminal (no GUI):**
```bash
python3 -m system.run --console
```

**Run all tests:**
```bash
python3 -m pytest tests/
```

**Run a single test file:**
```bash
python3 -m pytest tests/test_card_decision_validator.py
```

**Run a single test by name:**
```bash
python3 -m pytest tests/test_card_decision_validator.py::test_name
```

## Git workflow

After completing any meaningful unit of work — a bug fix, a new feature, a refactor — commit the changes and push to GitHub immediately. This ensures there is always a recoverable state on the remote.

- Commit only the files relevant to the change; do not use `git add .` blindly.
- Write commit messages in the imperative mood and keep the subject line under 72 characters. Add a short body when the *why* is not obvious from the diff.
- Push every commit to `origin/main` straight away — do not batch multiple commits before pushing.

## Architecture

The game is orchestrated by `schafkopf_classes/Schafkopf.py`, which owns the main loop, deals cards, collects game-mode choices, and fires `game.play_game()`. One human `Player` and three `Bot` instances are created at startup; the `Bot` subclass overrides only the card-playing, shooting, and doubling decisions — game-mode selection methods are **not** overridden and currently fall through to the human prompts (a known gap).

### Game mode system

Each game mode lives in `game_classes/game_modes/` and is a subclass of `Game` (ABC). Modes self-register via the `@GameRegistry.register_game` decorator. The rank field on each class determines priority when multiple players want to choose.

Instantiation uses a two-step factory: `Schafkopf.get_game` calls `game_mode.gather_kwargs(chooser, schafkopf)`, which collects all constructor arguments (including interactive player input for things like sau color or trump color), then constructs the game. Each mode's `gather_kwargs` calls `super().gather_kwargs` and then extends the dict.

### Per-game customisation via composition

Rather than putting game-specific logic in `Game`, each concrete game composes the right collaborators in its `__init__`:

| Collaborator | Purpose | Example subclasses |
|---|---|---|
| `CardPowerCalculator` | Card ordering and round winner | `SauspielCardPowerCalculator`, `WenzCardPowerCalculator`, `SoloCardPowerCalculator` |
| `CardDecisionValidator` | Legal-move enforcement | `SauspielCardDecisionValidator` (enforces callsau rules), `WenzCardDecisionValidator` |
| `TeamBuilder` | Team formation | `SauspielTeamBuilder` (finds callsau owner), `AloneTeamBuilder` and subclasses |
| `RunnersCalculator` | Laufende count | `WenzRunnersCalculator` (minimum 2), `RamschRunnersCalculator` (minimum 0) |
| `GameValueCalculator` | Scoring formula | `SauspielGameValueCalculator`, `ToutGameValueCalculator` (doubles, no schneider/black) |
| `WinnersSelector` | Who won | `RamschWinnersSelector` (most points loses), `ToutWinnersSelector` (all-or-nothing) |

### Rendering abstraction

`system/Renderer.py` defines the `Renderer` ABC with semantic render methods (`render`, `render_hand`, `render_played_card`, `render_trick_winner`, `render_game_result`) and ask methods (`ask_player_name`, `ask_play_again`, `ask_yes_no`, `ask_game_mode`, `ask_color`, `ask_card`). All game and player classes receive a `Renderer` instance — no direct `print`/`input` calls outside the renderer implementations. All display strings are pure functions in `system/text.py`; `game_classes/GameRenderer.py` wraps `Renderer` with game-specific render calls.

Two implementations exist:

- `ConsoleRenderer` (in `system/Renderer.py`) — prints to stdout and reads from stdin. Used via `python3 -m system.run --console`.
- `GUIRenderer` (in `system/gui/`) — a pygame table view. Default for `python3 -m system.run`.

#### GUI architecture (`system/gui/`)

- `renderer.py` — `GUIRenderer`. Game logic (`Schafkopf.main()`) runs on a daemon background thread started by `GUIRenderer.run()`; the pygame event/draw loop runs on the main thread (required on macOS). All shared state lives in a `TableState` (`state.py`) guarded by `self.lock` (`threading.RLock`).
- Blocking `ask_*` calls use a request/response pattern: the game thread sets `state.pending` to a `PendingRequest` and blocks on a `threading.Event`; the main loop renders the corresponding modal and calls `_submit(value)` on click/keypress, which sets the result and the event.
- Seats are fixed for the whole game by `Renderer.set_players()`, called once from `Schafkopf.main()` with the canonical turn-order player list: seat 0 is always the human (bottom), and 1/2/3 (left/top/right) follow in turn order, so the next player to act always sits next to whoever just acted. `_ensure_seat` then just looks up the fixed seat for a player.
- `constants.py` holds layout/color/font constants, `cards.py` draws card faces/backs, `widgets.py` has `Button`/`TextInput`.

### Circular-import pattern

All cross-package type references use `from __future__ import annotations` plus a `TYPE_CHECKING` guard. Runtime imports only appear in `__init__` bodies or at module level when truly needed.

### Money and scoring flow

After all rounds: `Game.handle_winners()` → `WinnersSelector` picks winners → `GameValueCalculator.calculate_game_value()` computes a cent value (base + runners + schneider/black + doubles) → `MoneyDistributer.distribute_money()` adjusts `player.money`. Runners are counted before play starts (`calculate_runners_amount`) using cards still in players' hands.
