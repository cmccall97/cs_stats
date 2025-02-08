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

def analyze_incin_grenades(parser, player_names):
    """Analyze incin grenades and create a DataFrame with counts."""
    incin_throws = parser.parse_event('inferno_startburn')
    incin_throws_per_player = incin_throws['user_name'].value_counts()

    incin_throws_per_player_df = pd.DataFrame(incin_throws_per_player).reset_index()
    incin_throws_per_player_df = (incin_throws_per_player_df
                                  .set_index('user_name')
                                  .reindex(player_names,fill_value=0)
                                  .reset_index())
    return incin_throws_per_player_df

def analyze_he_damage(parser, player_names):
    """Analyze HE grenade damage and create a DataFrame with damage stats."""
    player_hurt_df = parser.parse_event("player_hurt")
    he_dmg = player_hurt_df[player_hurt_df["weapon"] == "hegrenade"]
    
    dmg_per_player = he_dmg.groupby('attacker_name')['dmg_health'].sum()
    dmg_df = pd.DataFrame(dmg_per_player).reset_index()
    dmg_df.rename(columns={'attacker_name': 'user_name','dmg_health':'he_damage'}, inplace=True)
    
    return dmg_df

def analyze_incin_damage(parser, player_names):
    """Analyze incin grenade damage and create a DataFrame with damage stats"""
    player_hurt_df = parser.parse_event("player_hurt")
    incin_dmg = player_hurt_df[player_hurt_df["weapon"] == "inferno"]

    incin_dmg_per_player = incin_dmg.groupby('attacker_name')['dmg_health'].sum()
    incin_dmg_df = pd.DataFrame(incin_dmg_per_player).reset_index()
    incin_dmg_df.rename(columns={'attacker_name':'user_name','dmg_health':'incin_damage'},inplace=True)
    return incin_dmg_df

def calculate_nade_stats(total_nades_df, damage_df):
    """Merge nade counts with damage stats and calculate averages."""
    merged_df = pd.merge(total_nades_df, damage_df, on='user_name', how='left')
    merged_df['he_damage'].fillna(0, inplace=True)
    merged_df['avg_dmg_per_HE'] = (merged_df['he_damage'] / merged_df['count']).round(1)
    
    return merged_df

def calculate_incin_stats(incin_throws_per_player_df, incin_dmg_df):
    merged_incin_df = pd.merge(incin_throws_per_player_df,incin_dmg_df, on='user_name',how='left')
    merged_incin_df['incin_damage'].fillna(0,inplace=True)
    merged_incin_df['avg_dmg_per_incin'] = (merged_incin_df['incin_damage'] / merged_incin_df['count']).round(1)
    # Missing return statement here
    return merged_incin_df  # Add this

def parse_demo_nades(demo_path):
    """Main function to parse a demo file and return HE and incendiary grenade statistics."""
    parser = DemoParser(demo_path)
    
    # Get player names
    player_names = get_player_names(parser)
    
    # Analyze HE grenades and damage
    nade_counts = analyze_he_grenades(parser, player_names)
    damage_stats = analyze_he_damage(parser, player_names)
    
    # Analyze incendiary grenades and damage
    incin_counts = analyze_incin_grenades(parser, player_names)
    incin_damage_stats = analyze_incin_damage(parser, player_names)

    # Calculate final statistics
    HE_final_stats = calculate_nade_stats(nade_counts, damage_stats)
    incin_final_stats = calculate_incin_stats(incin_counts, incin_damage_stats)
    
    # Merge HE and incendiary stats
    final_stats = pd.merge(HE_final_stats, incin_final_stats, on='user_name', how='left')
    
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