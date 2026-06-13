import csv
import os
import matplotlib.pyplot as plt
import numpy as np

POSITION_WEIGHTS = {
    'GK': {
        'PSxG+/-': 1.4, 'Save%': 1.4, 'AvgDist': 1.0, 
        'Stp%': 1.0, 'Launch%': 0.7, 'Att (GK)': 0.7
    },
    'DF': {
        'TklW': 1.4, 'Int': 1.4, 'Won%': 1.4, 'PrgP': 1.1, 
        'Clr': 1.1, 'Def 3rd': 1.0, 'TklDri%': 0.8, 'Blocks': 0.8
    },
    'MF': {
        'PrgP': 1.4, 'xAG': 1.4, 'SCA': 1.3, 'PrgC': 1.15, 
        '1/3': 1.1, 'Tkl+Int': 1.1, 'Cmp% Long': 0.8, 
        'Att Pen': 0.8, 'Succ': 0.7, 'Recov': 0.8
    },
    'FW': {
        'npxG': 1.4, 'npxG/Sh': 1.3, 'xAG': 1.4, 'Att Pen': 1.2, 
        'GCA': 1.2, 'PrgR': 1.2, 'Succ': 1.0, 'CPA': 0.7, 'Won%': 0.7,
        'Tkl+Int': 0.6, 'Recov': 0.6, 'Blocks': 0.5
    }
}

# Collects and stores player information.
class Player:
    def __init__(self, name, team, age, position, stats):
        self.name = name
        self.team = team
        self.age = age
        self.position = position
        self.stats = stats # We're using a dictionary for position-based features.

# Normalizes all statistics to a 0.0 - 1.0 scale (Min-Max Scaling)
def normalize_all_players(players_list):
    if not players_list:
        return
        
    all_features = players_list[0].stats.keys()
    
    for feat in all_features:
        min_val = min(p.stats.get(feat, 0.0) for p in players_list)
        max_val = max(p.stats.get(feat, 0.0) for p in players_list)
        
        for p in players_list:
            val = p.stats.get(feat, 0.0)
            if max_val - min_val == 0:
                p.stats[feat] = 0.0
            else:
                p.stats[feat] = (val - min_val) / (max_val - min_val)

# Calculating eucledian distance which is the core logic of the project.
def calculate_distance(player1, player2):
    pos = player1.position[:2].upper()
    
    if 'GK' in pos:
        weights = POSITION_WEIGHTS['GK']
    elif 'DF' in pos or 'CB' in pos or 'RB' in pos or 'LB' in pos:
        weights = POSITION_WEIGHTS['DF']
    elif 'MF' in pos or 'CM' in pos or 'DM' in pos or 'AM' in pos:
        weights = POSITION_WEIGHTS['MF']
    else: # FW
        weights = POSITION_WEIGHTS['FW']

    total_diff = 0
    # We compare each statistic one by one based on the player's position
    for feat, weight in weights.items():
        val1 = player1.stats.get(feat, 0.0)
        val2 = player2.stats.get(feat, 0.0)

        total_diff += weight * ((val1 - val2)**2)
    
    dist = total_diff**(1/2)
    max_dist = 1.5

    # Converting to percentage
    similarity_percentage = max(0.0, (1 - (dist / max_dist)) * 100)
        
    return dist, similarity_percentage

# Simplifying names for robust searching and merging
def simplify_name(text):
    if not text:
        return ""
        
    # Converting the text to lowercase
    text = text.lower()
    
    # Foreign character map
    char_map = {
        'á': 'a', 'à': 'a', 'ă': 'a', 'ã': 'a', 'å': 'a', 'ä': 'a',
        'ć': 'c', 'ç': 'c', 'č': 'c',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ę': 'e', 'æ': 'ae',
        'ı': 'i', 'î': 'i', 'í': 'i', 'ï': 'i', 'i̇': 'i',
        'ö': 'o', 'ó': 'o', 'ò': 'o', 'ô': 'o', 'ø': 'o', 'ō': 'o',
        'ü': 'u', 'ú': 'u',
        'ş': 's', 'š': 's', 'ș': 's', 'ß': 'ss',
        'ž': 'z', 'ż': 'z',
        'ð': 'd', 'đ': 'd', 'ț': 't', 'þ': 'th',
        'ğ': 'g', 'ñ': 'n', 'ł': 'l', 'ý': 'y', 'ř': 'r',
        '-': ' ',  
        "'": ""    
    }

    # Changing characters in the text according to the map
    for old_char, new_char in char_map.items():
        text = text.replace(old_char, new_char)
        
    # Removing unnecessary spaces
    return text.strip()

# Loading data & Merging duplicates (Mid-season transfers)
def load_players(file_path):
    temp_data = {}
    
    stat_columns = [
        'xG', 'npxG', 'npxG/Sh', 'G-xG', 'xAG', 'SCA', 'GCA', 'Att Pen', 'PrgC', 'PrgR', 'Succ', 'CPA',
        'PrgP', '1/3', 'Cmp% Long', 'TB', 'Mid 3rd', 'Carries', 'Tkl+Int', 'Recov',
        'TklW', 'TklDri%', 'Int', 'Clr', 'Blocks', 'Won%', 'Def 3rd',
        'PSxG+/-', 'Save%', 'Stp%', 'AvgDist', 'Launch%', 'Att (GK)'
    ]
    
    # 'r' means read mode and utf-8 is the best for not facing errors because of different characters
    with open(file_path, mode='r', encoding='utf-8') as my_file:
        reader = csv.DictReader(my_file)
        
        for row in reader:
            try:
                raw_name = row['Player'].strip()
                # Using simplified name as a unique ID to catch duplicate records
                merge_key = simplify_name(raw_name)
                
                team = row['Squad'].strip()
                raw_age = row['Age'].strip()
                age = str(int(float(raw_age))) if raw_age else "N/A"
                position = row['Pos'].strip()
                played_90s = float(row.get('90s', 1.0))
                
                p_stats = {}
                for col in stat_columns:
                    val = row.get(col, "0")
                    p_stats[col] = float(val) if val and val.strip() != "" else 0.0
                
                # If player is not in our dictionary, add them
                if merge_key not in temp_data:
                    temp_data[merge_key] = {
                        'original_name': raw_name,
                        'age': age,
                        'position': position,
                        'total_90s': played_90s,
                        'teams': [team],
                        'stats': p_stats
                    }
                # If we found the same player in another team (transfer)
                else:
                    # Sum up their stats using weighted average based on 90s played to avoid Simpson's Paradox
                    old_90s = temp_data[merge_key]['total_90s']
                    new_90s = old_90s + played_90s
                    
                    for col in stat_columns:
                        old_val = temp_data[merge_key]['stats'][col]
                        new_val = p_stats[col]
                        temp_data[merge_key]['stats'][col] = ((old_val * old_90s) + (new_val * played_90s)) / new_90s
                        
                    temp_data[merge_key]['total_90s'] = new_90s
                    
                    if team not in temp_data[merge_key]['teams']:
                        temp_data[merge_key]['teams'].append(team)
                        
            except Exception:
                # We skip the row if there's a missing/broken data
                continue

    players_list = []
    
    # Converting aggregated dictionary data to Player objects
    for key, data in temp_data.items():
        combined_teams = " / ".join(data['teams'])
        new_player = Player(data['original_name'], combined_teams, data['age'], data['position'], data['stats'])
        players_list.append(new_player)
                
    return players_list

# KNN logic
def find_closest_twins(our_player_name, all_players):
    # Simplifying the input.
    search_query = simplify_name(our_player_name)
    
    our_player = None
    high_priority_matches = [] # Name or surname exact matches
    low_priority_matches = [] # Only contains the input

    for player in all_players:
        db_name = simplify_name(player.name)
        db_words = db_name.split()

        # If there's a direct match end the search
        if db_name == search_query:
            our_player = player
            break
        # High priority (arda --> Arda Güler)
        elif search_query in db_words or db_name.startswith(search_query + " "):
            high_priority_matches.append(player)
        # Low priority (arda --> Mam-arda-shvili)
        elif search_query in db_name:
            low_priority_matches.append(player)
    
    if our_player is None:
        # If any high priority matches, only focus on them
        if len(high_priority_matches) > 0:
            pot_matches = high_priority_matches
        # If no high priority matches, look at low priority matches
        else:
            pot_matches = low_priority_matches
            
        match_count = len(pot_matches)

        # If only 1 player matched
        if match_count == 1:
            our_player = pot_matches[0]
        # If between 2 and 5 players matches
        elif 1 < match_count <= 5:
            print("\nPotential Players:")
            for match in pot_matches:
                print(f"- {match.name} ({match.team} | {match.position} | {match.age})")
            return "Several players found. Please enter full name!"
        # If more than 5 players matches
        elif match_count > 5:
            return "Too many players found. Please enter full name!"
        # If no player matches
        else:
            return "No player found. Make sure the spelling is correct!"        
    
    # Calculating distances between our player and everyone else
    distances = []
    our_pos = our_player.position.upper()
    for others in all_players:
        # We don't want to compare the player with himself, and we check broad positional match
        if others.name != our_player.name and our_pos[:2] in others.position.upper():
            d, sim_perc = calculate_distance(our_player, others)
            # Storing the distance and the player object together
            distances.append([d, sim_perc, others])
            
    # Sorting the list from the smallest distance (most similar player) to the largest
    distances.sort(key=lambda x: x[0])
    
    # Returning the top 5 closest matches
    return our_player, distances[:5]

# Plots a radar chart comparing the target player and their best twin
def plot_radar_chart(target_player, twin_player):
    # Identify the player's position and extract the relevant features
    pos = target_player.position[:2].upper()
    if 'GK' in pos:
        weights = POSITION_WEIGHTS['GK']
    elif 'DF' in pos or 'CB' in pos or 'RB' in pos or 'LB' in pos:
        weights = POSITION_WEIGHTS['DF']
    elif 'MF' in pos or 'CM' in pos or 'DM' in pos or 'AM' in pos:
        weights = POSITION_WEIGHTS['MF']
    else: # FW
        weights = POSITION_WEIGHTS['FW']

    features = list(weights.keys())
    
    # Get the normalized raw statistics for both players
    val1 = [target_player.stats.get(f, 0.0) for f in features]
    val2 = [twin_player.stats.get(f, 0.0) for f in features]

    # Add the first data point again at the end to close the radar chart
    val1 += val1[:1]
    val2 += val2[:1]
    
    # Divide the circle into equal segments for each feature
    angles = [n / float(len(features)) * 2 * np.pi for n in range(len(features))]
    angles += angles[:1]

    # Create the plotting area
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Target Player (Blue)
    ax.plot(angles, val1, linewidth=2, linestyle='solid', label=target_player.name, color='#1badcf')
    ax.fill(angles, val1, '#1badcf', alpha=0.25)
    
    # Twin Player (Red)
    ax.plot(angles, val2, linewidth=2, linestyle='solid', label=twin_player.name, color='#c0392b')
    ax.fill(angles, val2, '#c0392b', alpha=0.25)
    
    # Configure axes and labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(features, fontsize=10, fontweight='bold')
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=8)
    ax.set_ylim(0, 1.1)
    
    # Title and legend
    plt.title(f"{target_player.name} vs {twin_player.name}\n(Normalized Position Stats)", size=14, color='black', y=1.1, fontweight='bold')
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.1))
    
    # Display the chart
    plt.show()

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    file_location = os.path.join(base_dir, "..", "files.data", "player_stats.csv")

    all_players = load_players(file_location)
    
    # Data Normalization Phase
    normalize_all_players(all_players)
    print("Total players loaded & normalized:", len(all_players))

    while True:
        # Asking the user for a name
        print("\nType a player name to find twins (or type 'exit' to close):")
        user_input = input("Player Name: ")

        # If the user wants to quit
        if user_input.lower() == "exit":
            print("Closing the scouting engine. Hope to see you again!")
            break

        # Finding the twins based on the user's input
        results = find_closest_twins(user_input, all_players)

        # If the return value is a string (which means it's an error/warning message)
        if isinstance(results, str):
            print(results)
        else:
            # The target player and the list of statistical twin
            target_player = results[0]
            twins_list = results[1]

            # Dynamic padding for perfect terminal alignment
            all_teams_in_view = [target_player.team] + [item[2].team for item in twins_list]
            all_pos_in_view = [target_player.position] + [item[2].position for item in twins_list]

            # Determining the maximum width required for team and position columns
            local_max_team = max(len(team) for team in all_teams_in_view)
            local_max_pos = max(len(pos) for pos in all_pos_in_view)

            # Preparing player names for aligned terminal output
            target_name_part = f"**{target_player.name}**"
            local_names = [target_name_part] + [f"- {item[2].name}" for item in twins_list]

            # Width of left column
            left_col_width = max(len(name) for name in local_names) + 2

            print("\nTop 5 Statistical-Twins for;")

            # Formatting and displaying target player info
            target_info_part = f"({target_player.team:<{local_max_team}} | {target_player.position:^{local_max_pos}} | {target_player.age:>2}):"

            print(f"{target_name_part:<{left_col_width}} {target_info_part}\n")

            # Displaying each twin player with similarity percentage
            for item in twins_list:
                score = item[0]
                sim_perc = item[1]
                p_info = item[2]

                twin_name_part = f"- {p_info.name}"
                twin_info_part = f"({p_info.team:<{local_max_team}} | {p_info.position:^{local_max_pos}} | {p_info.age:>2})"
                
                print(f"{twin_name_part:<{left_col_width}} {twin_info_part} | Similarity: {sim_perc:.1f}%")
            
            # Asking the user for graph creation
            best_twin = twins_list[0][2] # Best twin object
            
            print("\n---------------------------------------------------")
            view_chart = input(f"Would you like to see the Radar Chart comparing {target_player.name} and {best_twin.name}? (y/n): ")
            
            if view_chart.lower() == 'y':
                print("Generating chart... Please check your new window.")
                plot_radar_chart(target_player, best_twin)
