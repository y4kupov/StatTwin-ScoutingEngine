import csv
import os

# Collects and stores player information.
class Player:
    def __init__(self, name, league, team, stats):
        self.name = name
        self.league = league
        self.team = team
        self.stats = stats # We're gonnna make a list.

# Calcultaing eucledian distance which is the core logic of the project.
def calculate_distance(stats1, stats2):
    total_diff = 0
    
    # We compare each statistic one by one
    for i in range(len(stats1)):
        diff = stats1[i] - stats2[i]
        total_diff = total_diff + diff**2
        
    return total_diff**1/2

# Loading data
def load_players(file_path):
    players_list = []
    
    # 'r' means read mode and utd-8 is the best for not facing errors because of different characters like ğ, ø etc.
    with open(file_path, mode='r', encoding='utf-8') as my_file:
        reader = csv.DictReader(my_file)
        
        for row in reader:
            try:
                # We extract data from the CSV columns
                xg = float(row['xG'])
                assists = float(row['Ast'])
                goals = float(row['Gls'])
                
                # We convert the data into a Player object
                player_stats = [xg, assists, goals]
                new_player = Player(row['Player'], row['Comp'], row['Squad'], player_stats)
                
                # We add the new player to our main list
                players_list.append(new_player)
            except:
                # We skip the player if there's an error
                continue
                
    return players_list

# KNN logic
def find_closest_twins(our_player_name, all_players):
    # Finding our player in the list
    our_player = None
    for player in all_players:
        if player.name.lower() == our_player_name.lower():     # Burası çalışmıyor!!!
            our_player = player
            break
            
    if our_player == None:
        return "Player not found!"

    # Calculating distances between our player and everyone else
    distances = []
    for others in all_players:
        # We don't want to compare the player with himself
        if others.name != our_player.name:
            d = calculate_distance(our_player.stats, others.stats)
            # Storing the distance and the player object together
            distances.append([d, others])
            
    # Sorting the list from the smallest dist (most similar player) to the largest
    # We use a lambda function to ensure sorting is based on index[0] only. 
    distances.sort(key=lambda x: x[0])
    
    # Returning the top 3 closest matches
    return distances[:3]

import os

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    
    file_location = os.path.join(base_dir, "..", "files.data", "player_stats.csv")

    all_players = load_players(file_location)
    print("Total players loaded:", len(all_players))

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

        # Results
        if results == "Player not found!":
            print("Error: We couldn't find that player. Make sure the spelling is correct!")
        else:
            print(f"Top 3 Statistical-Twins for {user_input}:")
            for item in results:
                score = item[0]
                p_info = item[1]
                print(f"- {p_info.name} ( {p_info.team} ) | Similarity Score: {round(score, 2)}")