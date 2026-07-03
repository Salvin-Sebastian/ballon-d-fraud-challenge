import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create visualisations directory if it doesn't exist
os.makedirs('visualizations', exist_ok=True)

# Load data
df = pd.read_csv('dataset/player_stats_2023_24.csv')

# --- Feature Engineering & Fraud Index Calculation ---
# 1. xG Underperformance: (xG - Goals) 
# If a player scores more than xG, it's negative (good). If they score less, it's positive (bad).
df['xG_Underperformance'] = df['xG'] - df['Goals']

# 2. Stat Padding Ratio: Goals vs Bottom Half / Total Goals
# E.g. scoring 15 out of 20 goals vs bottom teams = 0.75 ratio
df['Stat_Pad_Ratio'] = df['Goals_vs_Bottom_Half'] / df['Goals']

# 3. Big Game Ghosting: 1 / (Big_Game_Goals + 1)
# The fewer big game goals, the higher the score.
df['Ghost_Score'] = 1 / (df['Big_Game_Goals'] + 1)

# Normalize components to 0-1 range to combine them equally
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

df['xG_Fraud_Score'] = normalize(df['xG_Underperformance'])
df['Pad_Fraud_Score'] = normalize(df['Stat_Pad_Ratio'])
df['Ghost_Fraud_Score'] = normalize(df['Ghost_Score'])

# Fraud Index Formula = (xG_Fraud_Score + Pad_Fraud_Score + Ghost_Fraud_Score) / 3 * 100
df['Fraud_Index'] = ((df['xG_Fraud_Score'] + df['Pad_Fraud_Score'] + df['Ghost_Fraud_Score']) / 3) * 100

# Rank players by Fraud Index
df = df.sort_values(by='Fraud_Index', ascending=False).reset_index(drop=True)
df['Rank'] = df.index + 1

# Export rankings
df[['Rank', 'Player', 'Fraud_Index', 'xG_Underperformance', 'Stat_Pad_Ratio', 'Ghost_Score']].to_csv('dataset/fraud_index_rankings.csv', index=False)


# --- Visualizations ---
# Style
sns.set_theme(style="whitegrid")

# 1. Goals vs xG Scatter Plot
plt.figure(figsize=(10, 6))
# Using standard palette string to avoid FutureWarnings
sns.scatterplot(data=df, x='xG', y='Goals', s=100, hue='Fraud_Index', palette='flare')

# Add line of equality (y=x)
max_val = max(df['xG'].max(), df['Goals'].max()) + 2
plt.plot([0, max_val], [0, max_val], 'k--', alpha=0.5, label='Goals = xG')

# Annotate points
for i in range(len(df)):
    plt.text(df['xG'][i]+0.3, df['Goals'][i], df['Player'][i], fontsize=9)

plt.title('Actual Goals vs Expected Goals (xG)', fontsize=14)
plt.xlabel('Expected Goals (xG)', fontsize=12)
plt.ylabel('Actual Goals', fontsize=12)
plt.legend()
plt.tight_layout()
plt.savefig('visualizations/goals_vs_xg.png')
plt.close()

# 2. Stat Padder Chart
plt.figure(figsize=(12, 6))
df_sorted_pad = df.sort_values(by='Stat_Pad_Ratio', ascending=False)
sns.barplot(data=df_sorted_pad, x='Stat_Pad_Ratio', y='Player', hue='Player', legend=False, palette='viridis')
plt.title('Stat Padding Ratio (Goals vs Bottom Half / Total Goals)', fontsize=14)
plt.xlabel('Ratio')
plt.ylabel('Player')
plt.tight_layout()
plt.savefig('visualizations/stat_padder_chart.png')
plt.close()

# 3. Final Fraud Index Rankings Bar Chart
plt.figure(figsize=(12, 6))
sns.barplot(data=df, x='Fraud_Index', y='Player', hue='Player', legend=False, palette='Reds_r')
plt.title('Final Player Fraud Index Rankings', fontsize=14)
plt.xlabel('Fraud Index (0-100)')
plt.ylabel('Player')
plt.tight_layout()
plt.savefig('visualizations/fraud_index_rankings.png')
plt.close()

print("Analysis complete. Rankings saved to dataset/fraud_index_rankings.csv and visualizations saved.")
