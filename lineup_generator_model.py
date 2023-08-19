import pandas as pd

# Specify the full path to the CSV file
file_path = r'D:\MLB STATISTICS PROJECT\combined_draft.csv'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(file_path)

# turns the pandas dataframe into a list
def make_list(df):
    return df.head(20).values.tolist()

# function that returns a list of the players above the 80th percentile
def percent_80_list(df):
    selected_rows_above_80 = []  # List to store selected rows
    scores = []  # List to store individual scores
    
    # calculates individual scores based on coeffecients from regression models
    for index, row in df.iterrows():
        variable_values = {
            "hitter_consensus": row['Consensus'],
            "avg_fp": row['PPG'],
            "slg": row['slg'],
            "opp_pitcher": row['opp p era'],
            "pitcher_consensus": row['pitcher consensus'],
            "era": row['era']
        }
        individual_score = intercept
        for variable, coef in coefs.items():
            individual_score += coef * variable_values[variable]
        
        scores.append(individual_score)  # Append the individual score
        
    # Calculate the threshold score for the 80th percentile of individual scores
    threshold_score = pd.Series(scores).quantile(0.8)
    
    for index, row in df.iterrows():
        variable_values = {
            "hitter_consensus": row['Consensus'],
            "avg_fp": row['PPG'],
            "slg": row['slg'],
            "opp_pitcher": row['opp p era'],
            "pitcher_consensus": row['pitcher consensus'],
            "era": row['era']
        }
        individual_score = intercept
        for variable, coef in coefs.items():
            individual_score += coef * variable_values[variable]
        
        if individual_score >= threshold_score:
            selected_row = [
                row['Name'], row['Position'], row['Team'], row['Opp'], row['Salary'],
                row['Consensus'], row['PPG'], row['opp pitcher'], row['slg'],
                row['opp p era'], row['pitcher consensus'], row['era']
            ]
            selected_rows_above_80.append(selected_row)
    
    return selected_rows_above_80

# creates a dictionary to track selected players by position
position_counts = {'C1B': 0,'2B': 0, '3B': 0, 'SS': 0, 'OF': 0,'UTL': 0, 'P':0}

# get stats from a list, given the index (column)
def get_player_stats(player_info, column):
    player_name = player_info[0]
    player_stat = player_info[column]
    return player_name, player_stat

scores = {}
lineup_count = 0
intercept = -3.95478
coefs = {
    "hitter_consensus": 0.515,
    "avg_fp": -0.10741,
    "slg": 16.0915,
    "opp_pitcher": 0.600029,
    "pitcher_consensus": 1.438964,
    "era": -1.14771
}
num = 0
list_80 = percent_80_list(df)

# generate all possible lineups. 
def generate_lineups_with_constraints(players, k, budget, positions_dict, selected_players=[], start_index=0):
    global lineup_count
    global intercept
    global coefs
    lineup_salary = 0
    predicted_score = 0
    count = 0
    # base recursion, ensures that it is under budget. 
    if k == 0 and (budget >= 0):
        # prints out the stats of each player in each lineup. indices are interchangable dependent on what stat you want. 
        for player_name in selected_players:
            player_info = next(player for player in players if player[0] == player_name)
            _, player_salary = get_player_stats(player_info, 4)
            lineup_salary += player_salary

            if player_name in [player[0] for player in list_80]:
                count += 1
        # checks if lineup is between 34000 and 35000, and also if there are 4 or more <80% players
        if (34000 < lineup_salary < 35000):
            if count >= 4:
                for player_name in selected_players:
                    # change these indices for the stats you would like to find
                    player_info = next(player for player in players if player[0] == player_name)
                    _, player_slg = get_player_stats(player_info, 8) 
                    player_info = next(player for player in players if player[0] == player_name)
                    _, player_consensus = get_player_stats(player_info, 5)
                    player_info = next(player for player in players if player[0] == player_name)
                    _, player_avg_fp = get_player_stats(player_info, 6)
                    player_info = next(player for player in players if player[0] == player_name)
                    _, player_opp_pitcher_era = get_player_stats(player_info, 9)
                    player_info = next(player for player in players if player[0] == player_name)
                    _, pitcher_era = get_player_stats(player_info, 11)
                    player_info = next(player for player in players if player[0] == player_name)
                    _, pitcher_consensus = get_player_stats(player_info, 10)

                    variable_values = {
                        "hitter_consensus":  player_consensus,
                        "avg_fp": player_avg_fp,
                        "slg" : player_slg,
                        "opp_pitcher" : player_opp_pitcher_era,
                        "pitcher_consensus" : pitcher_consensus,
                        "era" : pitcher_era
                    }
                    individual_score = intercept
                    # calculates the predicted score of each lineup. 
                    for variable, coef in coefs.items():
                        individual_score += coef * variable_values[variable]
                    predicted_score += individual_score
                lineup_count += 1
                scores[str(selected_players)] = predicted_score
                return
    # recursion, this allows it to test every possibility under the position constraint
    for i in range(start_index, len(players)):
        player_name, player_positions, _, _, player_salary, player_consensus, player_avg_fp, _, player_slg, player_opp_pitcher_era, pitcher_consensus, era = players[i]

        # Split the player's positions separated by slashes
        positions = player_positions.split('/')

        # ensure that the lineup doesn't go over the position limit
        for position in positions:
            if position_counts[position] < max_position_counts[position]:
                if player_salary <= budget:
                    selected_players.append(player_name)
                    prev_count = position_counts[position]
                    position_counts[position] += 1
                    generate_lineups_with_constraints(players, k - 1, budget - player_salary, positions_dict, selected_players, i + 1)
                    selected_players.pop()
                    position_counts[position] = prev_count

new_arr = make_list(df)
budget_limit = 35000
num_selections = 9
# Define the maximum count of players per position
max_position_counts = {'C1B': 1, '2B': 1, '3B': 1, 'SS': 1, 'OF': 3, 'UTL': 1, 'P': 1}

#Create the player_positions dictionary
player_positions = {player[0]: player[1] for player in new_arr}

generate_lineups_with_constraints(new_arr, num_selections, budget_limit, player_positions)
sorted_items = sorted(scores.items(), key=lambda item: item[1], reverse=True)
# change the number dependent on how many lineups you want it to display
top_10_items = sorted_items[:3]
top_10_dict = dict(top_10_items)
print(top_10_dict)