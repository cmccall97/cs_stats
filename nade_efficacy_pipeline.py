from demoparser2 import DemoParser
import pandas as pd

def get_player_names(parser):
    """Extract unique player names from the demo."""
    player_info = parser.parse_player_info()
    return player_info['name'].unique()

def analyze_he_grenades(parser, player_names):
    """Analyze HE grenade detonations and create a DataFrame with counts."""
    frag_exploded = parser.parse_event("hegrenade_detonate")
    nades_thrown = frag_exploded['user_name'].value_counts()
    
    total_nades_df = pd.DataFrame(nades_thrown).reset_index()
    total_nades_df = (total_nades_df
                     .set_index('user_name')
                     .reindex(player_names, fill_value=0)
                     .reset_index())
    
    return total_nades_df

def analyze_he_damage(parser, player_names):
    """Analyze HE grenade damage and create a DataFrame with damage stats."""
    player_hurt_df = parser.parse_event("player_hurt")
    he_dmg = player_hurt_df[player_hurt_df["weapon"] == "hegrenade"]
    
    dmg_per_player = he_dmg.groupby('attacker_name')['dmg_health'].sum()
    dmg_df = pd.DataFrame(dmg_per_player).reset_index()
    dmg_df.rename(columns={'attacker_name': 'user_name'}, inplace=True)
    
    return dmg_df

def calculate_nade_stats(total_nades_df, damage_df):
    """Merge nade counts with damage stats and calculate averages."""
    merged_df = pd.merge(total_nades_df, damage_df, on='user_name', how='left')
    merged_df['dmg_health'].fillna(0, inplace=True)
    merged_df['avg_dmg_per_HE'] = (merged_df['dmg_health'] / merged_df['count']).round(1)
    
    return merged_df

def parse_demo_nades(demo_path):
    """Main function to parse a demo file and return HE grenade statistics."""
    parser = DemoParser(demo_path)
    
    # Get player names
    player_names = get_player_names(parser)
    
    # Analyze HE grenades
    nade_counts = analyze_he_grenades(parser, player_names)
    
    # Analyze damage
    damage_stats = analyze_he_damage(parser, player_names)
    
    # Calculate final statistics
    final_stats = calculate_nade_stats(nade_counts, damage_stats)
    
    return final_stats

def process_multiple_demos(demo_paths):
    """Process multiple demos and return a dictionary of results."""
    results = {}
    for demo_path in demo_paths:
        try:
            stats = parse_demo_nades(demo_path)
            results[demo_path] = stats
        except Exception as e:
            print(f"Error processing demo {demo_path}: {str(e)}")
    
    return results