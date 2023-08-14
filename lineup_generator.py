import pandas as pd

# Specify the full path to the CSV file
file_path = r'D:\MLB STATISTICS PROJECT\finalsheet.csv'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path)

def get_rows_by_date(date, df):
    filtered_df = df[df['date'] == date]
    return filtered_df.values.tolist()
# Create a dictionary to track selected players by position
position_counts = {'C1B': 0,'2B': 0, '3B': 0, 'SS': 0, 'OF': 0,'UTL': 0}

# get stats from a list, given the index (column)
def get_player_stats(player_info, column):
    player_name = player_info[0]
    player_stat = player_info[column]
    return player_name, player_stat

scores = {}

# generate an infinite amount of lineups. 
def generate_lineups_with_constraints(players, k, budget, positions_dict, selected_players=[], start_index=0, lineup_num = 1):
    total_score_per_lineup = 0
    # base recursion, ensures that it is under budget. 
    if k == 0 and budget >= 0:
        # prints out the lineup
        print("Selected players:", selected_players)
        # prints out the positions of each player in the lineup
        print("Positions:", [positions_dict[player_name] for player_name in selected_players])
        # prints out the stats of each player in each lineup. indices are interchangable dependent on what stat you want. 
        for player_name in selected_players:
            player_info = next(player for player in players if player[0] == player_name)
            _, player_slg = get_player_stats(player_info, 18) 
            player_info = next(player for player in players if player[0] == player_name)
            _, player_consensus = get_player_stats(player_info, 9 )
            player_info = next(player for player in players if player[0] == player_name)
            _, player_avg_fp = get_player_stats(player_info, 9 )
            player_info = next(player for player in players if player[0] == player_name)
            _, player_savant_grade = get_player_stats(player_info, 13 )
            player_info = next(player for player in players if player[0] == player_name)
            _, player_opp_pitcher_era = get_player_stats(player_info, 19 )

            # uses min-max scaling to rate each player, then combines it to get the total score in a lineup
            values = [player_consensus, player_slg, player_avg_fp, player_savant_grade, player_opp_pitcher_era]
            min_value = min(values)
            max_value = max(values)
            normalized_values = [(x - min_value) / (max_value - min_value) for x in values]
            combined_score = sum(normalized_values)

            print(f"combined score {combined_score}")
            total_score_per_lineup += combined_score
            print(f"{player_name}-  consensus: {player_consensus} slg: {player_slg} avg fp: {player_avg_fp} savant grade: {player_savant_grade} opp pitcher era: {player_opp_pitcher_era}")
        print(total_score_per_lineup)
        scores[str(selected_players)] = total_score_per_lineup
        return
    # recursion, this allows it to test every possibility under the position constraint
    for i in range(start_index, len(players)):
        player_name, player_positions, _, player_salary, _, _, _, _, _, player_consensus, player_avg_fp, _, _, _, player_savant_grade, _, _, _, _, player_slg, player_opp_era, _, = players[i]

        # Split the player's positions separated by slashes
        positions = player_positions.split('/')

        for position in positions:
            if position_counts[position] < max_position_counts[position]:
                if player_salary <= budget:
                    selected_players.append(player_name)
                    position_counts[position] += 1
                    generate_lineups_with_constraints(players, k - 1, budget - player_salary, positions_dict, selected_players, i + 1)
                    selected_players.pop()
                    position_counts[position] -= 1

new_arr = get_rows_by_date('July 31, 2023', df)
budget_limit = 26000
num_selections = 8
# Define the maximum count of players per position
max_position_counts = {'C1B': 1, '2B': 1, '3B': 1, 'SS': 1, 'OF': 3, 'UTL': 1}

# Create the player_positions dictionary
player_positions = {player[0]: player[1] for player in new_arr}

generate_lineups_with_constraints(new_arr, num_selections, budget_limit, player_positions)
sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)
top_10_items = sorted_items[:10]
top_10_dict = dict(top_10_items)
print(top_10_dict)