# 2048 AI Agent — Dynamic-Depth Expectimax

An AI agent designed to play **2048** using Expectimax search, adaptive search depth, and heuristic board evaluation. The project explores how an agent can plan ahead while accounting for the randomness of new tile spawns.

Developed for **COMP 3106 (Artificial Intelligence)**.

## Features

- **Expectimax search:** considers possible future moves and random tile spawns.
- **Adaptive search depth:** allocates more search effort to challenging board states.
- **Heuristic evaluation:** combines monotonicity, empty-cell availability, and merge opportunities to favor stable boards.
- **Performance evaluation:** measures success rates, scores, and highest tiles reached over multiple games.

## Repository Files

| File | Purpose |
| --- | --- |
| `display.py` | Game display/interface. |
| `evaluate_ai.py` | Runs evaluations and collects AI performance metrics. |
| `game_ai.py` | AI move selection and search logic. |
| `game_functions.py` | Core 2048 game mechanics and board operations. |

*File roles are based on the project report and filenames; exact entry points and dependencies should be confirmed against the source code.*

## Approach

The agent evaluates candidate moves with **Expectimax**, which models random tile spawns as chance events. Rather than using the same search depth throughout the game, the proposed approach adjusts search depth according to board conditions, allowing shallower searches in open positions and deeper searches in more constrained ones.

Board states are scored using three complementary heuristics:

1. **Monotonicity:** encourages ordered tile arrangements that facilitate future merges.
2. **Empty cells:** preserves space for future moves.
3. **Merges:** rewards opportunities to combine equal-valued tiles.

The project report also describes offline heuristic-weight optimization with **Optuna**; the optimization script is not among the four files listed in this repository.

## Results

The project report presents the following results from **100 evaluation runs**:

| Metric | Reported result |
| --- | ---: |
| Win rate (reaching 2048 or higher) | **97%** |
| Mean score | **82,152.48** |
| Maximum score | **243,160** |
| Average moves to reach 2048 | **971.63** |
| Average moves per completed game | **3,636.27** |

These are results reported in the course project report, not independently reproduced here.

## Running the Project

The repository includes `display.py` for the game interface and `evaluate_ai.py` for performance evaluation. Refer to their `__main__` blocks and imports for the supported commands and required Python packages; these have not yet been verified against the source files.

## Limitations and Future Work

The approach uses heuristic weights tuned offline, which may be less effective in unusual board states. Deeper searches can also increase computation time. Future improvements could include online weight adaptation through reinforcement learning and testing on other stochastic puzzle environments.

## Project Report

For detailed methodology, experiments, charts, and references, see the **2048 AI project report** (if included in this repository under `docs/2048_AI_Report.pdf`).
