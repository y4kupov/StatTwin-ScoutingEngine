import streamlit as st
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
import requests
import urllib.parse

# Configuring the Streamlit web page settings
st.set_page_config(page_title="StatsTwin Scouting Engine", page_icon="⚽", layout="wide")

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
        self.stats = stats # I'm using a dictionary for position-based features.

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
    # I compare each statistic one by one based on the player's position
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

# Fetches player photos directly from Wikipedia
@st.cache_data(show_spinner=False)
def fetch_player_image_url(player_name):
    try:
        # To avoid random people that has a similar name with the players 
        search_query = urllib.parse.quote(f"{player_name} footballer")
        
        # Find the most relevant article and take the photo
        url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={search_query}&gsrlimit=1&prop=pageimages&pithumbsize=400&format=json"
        
        # To avoid being detected as a harmful bot
        headers = {"User-Agent": "StatsTwinScoutingEngine/1.0"}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        
        # Getting page details
        pages = data.get('query', {}).get('pages', {})
        if pages:
            # Retrieving the thumbnail URL from the first page found.
            first_page = list(pages.values())[0]
            if 'thumbnail' in first_page:
                return first_page['thumbnail']['source']
    except Exception:
        pass
        
    return None # If no photo

# Caching the data loading process so it only runs once, significantly speeding up the app
@st.cache_data
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
                
                # If player is not in my dictionary, add them
                if merge_key not in temp_data:
                    temp_data[merge_key] = {
                        'original_name': raw_name,
                        'age': age,
                        'position': position,
                        'total_90s': played_90s,
                        'teams': [team],
                        'stats': p_stats
                    }
                # If I found the same player in another team (transfer)
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
                # I skip the row if there's a missing/broken data
                continue

    players_list = []
    
    # Converting aggregated dictionary data to Player objects
    for key, data in temp_data.items():
        combined_teams = " / ".join(data['teams'])
        new_player = Player(data['original_name'], combined_teams, data['age'], data['position'], data['stats'])
        players_list.append(new_player)
                
    normalize_all_players(players_list)            
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
            suggestions = [f"- {m.name} ({m.team})" for m in pot_matches]
            return f"Multiple players found. Please enter the full name:\n" + "\n".join(suggestions)
        # If more than 5 players matches
        elif match_count > 5:
            return "Too many players found. Please enter the full name!"
        # If no player matches
        else:
            return "No player found. Please check the spelling!"        
    
    # Calculating distances between my player and everyone else
    distances = []
    our_pos = our_player.position.upper()
    for others in all_players:
        # I don't want to compare the player with himself, and I check broad positional match
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
    # Identifying the player's position and extracting the relevant features
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
    
    # Statistics for both players
    val1 = [target_player.stats.get(f, 0.0) for f in features]
    val2 = [twin_player.stats.get(f, 0.0) for f in features]

    # To close the radar chart
    val1 += val1[:1]
    val2 += val2[:1]
    
    # Calculating the highest stat value among both players to scale the chart dynamically
    max_val = max(max(val1), max(val2))
    if max_val == 0: 
        max_val = 1.0 # Safety fallback just in case all stats are zero
        
    # Setting the boundary 15% higher than the max value so the polygon doesn't hit the ceiling
    dynamic_limit = max_val * 1.15
    
    # Generating 4 background circles based on the dynamic limit
    dynamic_ticks = [dynamic_limit * 0.25, dynamic_limit * 0.5, dynamic_limit * 0.75, dynamic_limit]
    
    # Dividing the circle into equal segments for each feature
    angles = [n / float(len(features)) * 2 * np.pi for n in range(len(features))]
    angles += angles[:1]

    # Creating the plotting area 
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    # Making background transparent and hiding outer circle
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    ax.spines['polar'].set_visible(False)
    
    # Target Player (Blue)
    ax.plot(angles, val1, linewidth=2, linestyle='solid', label=target_player.name, color='#1badcf')
    ax.fill(angles, val1, '#1badcf', alpha=0.25)
    
    # Twin Player (Red)
    ax.plot(angles, val2, linewidth=2, linestyle='solid', label=twin_player.name, color='#c0392b')
    ax.fill(angles, val2, '#c0392b', alpha=0.25)
    
    # Configuring axes and labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(features, fontsize=9, fontweight='bold', color='white')
    
    # Applying the dynamic ticks and limit boundaries to the y-axis
    ax.set_yticks(dynamic_ticks)
    ax.set_yticklabels([], color="grey", size=8)
    ax.set_ylim(0, dynamic_limit)
    
    # Title and legend
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    return fig

# STREAMLIT WEB INTERFACE
# Displaying the main title and description on the web page
st.title("⚽ StatsTwin: Football Scouting Engine")
st.markdown("Find the **Statistical Twins** of players in Europe's Top 5 leagues using data-driven algorithms.")

base_dir = os.path.dirname(__file__)
file_location = os.path.join(base_dir, "..", "files.data", "player_stats.csv")

# Loading the dataset and displaying a success or error message
try:
    all_players = load_players(file_location)
    st.success(f"System Ready! A total of {len(all_players)} players loaded and normalized.")
except FileNotFoundError:
    st.error("Dataset (player_stats.csv) not found. Please check the file path.")
    st.stop()

st.divider()

# Creating a form to bind the text input "Enter" key directly to the submit button
with st.form(key="search_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Enter the name of the player to find their twins (e.g., Kvaratskhelia):")
    with col2:
        st.write("")
        st.write("")
        search_button = st.form_submit_button("Start Scouting 🔍", use_container_width=True)
        
# Triggering the search and distance calculation process when the user clicks the button
if search_button and search_query:
    results = find_closest_twins(search_query, all_players)

    if isinstance(results, str):
        st.warning(results)
    else:
        target_player = results[0]
        twins_list = results[1]

        st.subheader(f"Target Player: {target_player.name}")
        st.write(f"**Team:** {target_player.team} | **Position:** {target_player.position} | **Age:** {target_player.age}")
        
        st.markdown("### Top 5 Statistical Twins")
        
        # Splitting the results area into two equal columns: one for the top 5 list, one for the radar chart
        res_col1, res_col2 = st.columns([1, 1])
        
        with res_col1:
            # Looping through the top 5 twins and displaying their information
            for rank, item in enumerate(twins_list, 1):
                sim_perc = item[1]
                p_info = item[2]
                
                card_col1, card_col2 = st.columns([0.6, 3])
                
                with card_col1:
                    # Dynamically fetching the real image URL from Wikipedia
                    img_url = fetch_player_image_url(p_info.name)
                    
                    if img_url:
                        st.markdown(
                            f"""
                            <div style="
                                display: flex;
                                justify-content: center;
                                align-items: center;
                                height: 137px;
                                width: 100%;
                            ">
                                <img src="{img_url}" style="
                                    max-height: 100%;
                                    max-width: 100%;
                                    border-radius: 12px;
                                    object-fit: cover;
                                    border: 2px solid rgba(255,255,255,0.1);
                                ">
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("😭🤬 Image Not Found") 
                        
                with card_col2:
                    # Creating a dynamic Transfermarkt search URL for the player
                    tm_search_url = f"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query={urllib.parse.quote(p_info.name)}"
                    
                    # Displaying the player name as a clickable hyperlink that opens in a new tab
                    st.info(
                        f"**{rank}. [{p_info.name}]({tm_search_url})**\n\n"
                        f"Team: {p_info.team} | Position: {p_info.position} | Age: {p_info.age}\n\n"
                        f"**Similarity: {sim_perc:.1f}%**"
                    )

        with res_col2:
            st.markdown(f"#### 🕸️ {target_player.name} vs {twins_list[0][2].name} Radar Analysis")
            
            # Generating the Matplotlib radar chart for the best match and showing it
            best_twin = twins_list[0][2]
            fig = plot_radar_chart(target_player, best_twin)
            st.pyplot(fig)