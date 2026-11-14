# evaluate_ai.py

import numpy as np
import game_ai
import game_functions as gf
import matplotlib.pyplot as plt
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
import csv
import os

def get_tile_frequencies_from_score(score_increment, tile_values=[16384, 8192, 4096, 2048, 1024]):
    """
    Decompose the score_increment into tile frequencies.

    Args:
        score_increment (int): The score increment from tile merges.
        tile_values (list): List of tile values to consider, ordered from highest to lowest.

    Returns:
        dict: Dictionary with tile values as keys and their frequency as values.
    """
    freq = {tile: 0 for tile in tile_values}
    remaining = score_increment
    for tile in tile_values:
        while remaining >= tile:
            freq[tile] += 1
            remaining -= tile
    return freq

def play_game(ai_move_func):
    """
    Plays a single game using the provided AI move function.

    Args:
        ai_move_func (function): Function that takes a board and returns (new_board, move_made, score_increment).

    Returns:
        dict: Metrics collected from the game.
    """
    board = gf.initialize_game()
    score = 0
    highest_tile = 0
    moves = 0
    tile_frequency = {1024: 0, 2048: 0, 4096: 0, 8192: 0, 16384: 0}
    moves_until_2048_found = None
    game_over_moves = None

    while True:
        # AI decides and makes a move
        new_board, move_made, score_increment = ai_move_func(board.copy())

        if not move_made:
            # No move possible, game over
            game_over_moves = moves
            break

        score += score_increment
        current_highest_tile = np.max(new_board)
        highest_tile = max(highest_tile, current_highest_tile)
        moves += 1

        # Check if 2048 tile is found for the first time
        if highest_tile >= 2048 and moves_until_2048_found is None:
            moves_until_2048_found = moves

        # Update tile frequency based on score_increment
        merged_tile_freq = get_tile_frequencies_from_score(score_increment)
        for tile, count in merged_tile_freq.items():
            tile_frequency[tile] += count

        # Add a new tile
        board = gf.add_new_tile(new_board)

        # Debugging: Log the current board state and move details
        # Comment out or remove these print statements for large evaluations
        # print(f"Move {moves}:")
        # print(board)
        # print(f"Score Increment: {score_increment}, Total Score: {score}")
        # print(f"Highest Tile: {highest_tile}, Moves until 2048: {moves_until_2048_found}")
        # print(f"Tile Frequencies: {tile_frequency}\n")

        # Check if game is over
        if gf.check_game_over(board):
            game_over_moves = moves
            break

    # Determine if the game was won (2048 tile achieved)
    win = highest_tile >= 2048

    return {
        'score': score,
        'highest_tile': highest_tile,
        'moves_until_2048_found': moves_until_2048_found if moves_until_2048_found is not None else moves,
        'moves_until_game_over': game_over_moves if game_over_moves is not None else moves,
        'win': win,
        'tile_frequency_1024': tile_frequency.get(1024, 0),
        'tile_frequency_2048': tile_frequency.get(2048, 0),
        'tile_frequency_4096': tile_frequency.get(4096, 0),
        'tile_frequency_8192': tile_frequency.get(8192, 0),
        'tile_frequency_16384': tile_frequency.get(16384, 0),
        'final_board': board  # Included for potential further analysis
    }

def init_worker():
    """
    Optional initializer for worker processes to set up any necessary state.
    """
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)  # Ignore KeyboardInterrupt in workers

def run_evaluation_parallel(num_games):
    """
    Runs multiple games in parallel and collects performance metrics.

    Args:
        num_games (int): Number of games to run.

    Returns:
        list: List of metrics dictionaries for each game.
    """
    metrics = []
    try:
        with Pool(processes=cpu_count(), initializer=init_worker) as pool:
            # Prepare a list with the ai_move function repeated num_games times
            ai_move_funcs = [game_ai.ai_move] * num_games
            for result in tqdm(pool.imap_unordered(play_game, ai_move_funcs), total=num_games, desc="Running Games"):
                metrics.append(result)
    except KeyboardInterrupt:
        print("Interrupted by user")
    return metrics

def save_metrics_to_csv(metrics, filename="game_metrics.csv"):
    """
    Saves the collected metrics to a CSV file.

    Args:
        metrics (list): List of metrics dictionaries.
        filename (str): Name of the CSV file to save.
    """
    # Define CSV columns
    fieldnames = [
        'score',
        'highest_tile',
        'moves_until_2048_found',
        'moves_until_game_over',
        'win',
        'tile_frequency_1024',
        'tile_frequency_2048',
        'tile_frequency_4096',
        'tile_frequency_8192',
        'tile_frequency_16384'
    ]

    # Check if file exists to write header only once
    file_exists = os.path.isfile(filename)

    with open(filename, mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for metric in metrics:
            writer.writerow({
                'score': metric['score'],
                'highest_tile': metric['highest_tile'],
                'moves_until_2048_found': metric['moves_until_2048_found'],
                'moves_until_game_over': metric['moves_until_game_over'],
                'win': metric['win'],
                'tile_frequency_1024': metric['tile_frequency_1024'],
                'tile_frequency_2048': metric['tile_frequency_2048'],
                'tile_frequency_4096': metric['tile_frequency_4096'],
                'tile_frequency_8192': metric['tile_frequency_8192'],
                'tile_frequency_16384': metric['tile_frequency_16384']
            })

def analyze_metrics(metrics, csv_filename="game_metrics.csv"):
    """
    Analyzes the collected metrics, prints summary statistics, and saves detailed data to a CSV file.

    Args:
        metrics (list): List of metrics dictionaries.
        csv_filename (str): Name of the CSV file to save detailed metrics.
    """
    # Save detailed metrics to CSV
    save_metrics_to_csv(metrics, filename=csv_filename)
    print(f"Detailed metrics saved to {csv_filename}")

    # Extract data for summary statistics
    scores = [m['score'] for m in metrics]
    highest_tiles = [m['highest_tile'] for m in metrics]
    wins = [m['win'] for m in metrics]
    moves_until_2048 = [m['moves_until_2048_found'] for m in metrics]
    moves_until_game_over = [m['moves_until_game_over'] for m in metrics]
    tile_freq_1024 = [m['tile_frequency_1024'] for m in metrics]
    tile_freq_2048 = [m['tile_frequency_2048'] for m in metrics]
    tile_freq_4096 = [m['tile_frequency_4096'] for m in metrics]
    tile_freq_8192 = [m['tile_frequency_8192'] for m in metrics]
    tile_freq_16384 = [m['tile_frequency_16384'] for m in metrics]

    # Calculate summary statistics
    average_score = np.mean(scores)
    median_score = np.median(scores)
    max_score = np.max(scores)
    average_highest_tile = np.mean(highest_tiles)
    median_highest_tile = np.median(highest_tiles)
    win_rate = np.sum(wins) / len(wins) * 100
    average_moves_until_2048 = np.mean(moves_until_2048)
    median_moves_until_2048 = np.median(moves_until_2048)
    average_moves_until_game_over = np.mean(moves_until_game_over)
    median_moves_until_game_over = np.median(moves_until_game_over)

    # Print summary statistics
    print(f"Number of Games Played: {len(metrics)}")
    print(f"Average Score: {average_score:.2f}")
    print(f"Median Score: {median_score}")
    print(f"Maximum Score: {max_score}")
    print(f"Average Highest Tile: {average_highest_tile:.2f}")
    print(f"Median Highest Tile: {median_highest_tile}")
    print(f"Win Rate (2048+): {win_rate:.2f}%")
    print(f"Average Moves until 2048 Found: {average_moves_until_2048:.2f}")
    print(f"Median Moves until 2048 Found: {median_moves_until_2048}")
    print(f"Average Moves until Game Over: {average_moves_until_game_over:.2f}")
    print(f"Median Moves until Game Over: {median_moves_until_game_over}")

    # Optionally, plot tile frequencies
    tile_labels = ['1024', '2048', '4096', '8192', '16384']
    total_freq = [
        np.sum(tile_freq_1024),
        np.sum(tile_freq_2048),
        np.sum(tile_freq_4096),
        np.sum(tile_freq_8192),
        np.sum(tile_freq_16384)
    ]

    plt.figure(figsize=(10,6))
    plt.bar(tile_labels, total_freq, color='skyblue')
    plt.xlabel('Tile Value')
    plt.ylabel('Frequency')
    plt.title('Tile Frequency (1024 and Higher)')
    plt.savefig('tile_frequency.png')  # Save the plot as an image file
    plt.show()
    print("Tile frequency plot saved as 'tile_frequency.png'.")

def main():
    num_games = 100  # Adjust the number of games as needed
    print(f"Starting evaluation with {num_games} games...")
    metrics = run_evaluation_parallel(num_games=num_games)
    print("Evaluation completed.\n")
    analyze_metrics(metrics, csv_filename="game_metrics.csv")

if __name__ == "__main__":
    main()