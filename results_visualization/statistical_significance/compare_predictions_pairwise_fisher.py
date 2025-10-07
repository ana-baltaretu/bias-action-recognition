import pandas as pd
import itertools
from collections import Counter

def extract_base_name(name):
    # Extract the base video name: e.g., "cartwheel_0_modified_black" → "cartwheel_0"
    if "_modified_" in name:
        return name.split("_modified_")[0]
    return "_".join(name.split("_")[:2])  # fallback

def find_differing_predictions(file_path):
    df = pd.read_csv(file_path)
    total_possible_changes = df.shape[0] / 7 * 6
    print("total_possible_changes", total_possible_changes)

    # Basic checks
    for col in ['video', 'raw_prediction', 'skin_color_category']:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}'")

    # Extract base names for grouping
    df['base_name'] = df['video'].apply(extract_base_name)

    differing_pairs = []

    for base_name, group in df.groupby('base_name'):
        # Get list of (skin_color_category, prediction)
        rows = list(group[['skin_color_category', 'raw_prediction']].itertuples(index=False))

        for a, b in itertools.combinations(rows, 2):
            if a.raw_prediction != b.raw_prediction:
                differing_pairs.append({
                    'base_name': base_name,
                    'skin_color_1': a.skin_color_category,
                    'skin_color_2': b.skin_color_category
                })

    return differing_pairs, total_possible_changes

if __name__ == "__main__":
    experiment_name = "top_20_kinetics_actions"  # older_runs, top_20_kinetics_actions
    model_name = "x3d_xs"  # mvit_base_16x4, slowfast_r50, tc_clip, slow_r50, x3d_xs
    file_path = f"../model_results/{experiment_name}/filtered_best_background_and_camera_{model_name}.csv"
    output_path = f"differing_pairs_{experiment_name}_{model_name}.csv"

    differences, totals = find_differing_predictions(file_path)

    # Save to CSV
    df_out = pd.DataFrame(differences)
    df_out.to_csv(output_path, index=False)
    print(f"\nSaved {len(differences)} differing prediction pairs to {output_path}")

    # Count appearances of each skin color
    color_counts = Counter()
    for d in differences:
        color_counts[d['skin_color_1']] += 1
        color_counts[d['skin_color_2']] += 1

    print(color_counts)

    print("\nSkin color appearance counts in differing pairs:")
    for color, count in color_counts.items():
        print(f"{color}: {count}")

    # Pairwise Fisher's exact test
    from scipy.stats import fisher_exact
    from statsmodels.stats.multitest import multipletests
    results = []
    pairs = list(itertools.combinations(color_counts.keys(), 2))
    print(pairs)

    for a, b in pairs:
        a_count = color_counts.get(a, 0)
        b_count = color_counts.get(b, 0)
        table = [
            [a_count, totals - a_count],
            [b_count, totals - b_count]
        ]
        _, pval = fisher_exact(table)
        results.append({
            'skin_color_1': a,
            'skin_color_2': b,
            'p_raw': pval
        })

    # Bonferroni correction
    pvals = [r['p_raw'] for r in results]
    reject, p_corrected, _, _ = multipletests(pvals, alpha=0.05, method='bonferroni')

    # Update results
    for i, r in enumerate(results):
        r['p_corrected'] = p_corrected[i]
        r['significant'] = reject[i]

    # Convert to DataFrame
    df = pd.DataFrame(results)
    df.sort_values(by='p_corrected', inplace=True)

    print(df)

    # import ace_tools as tools;
    #
    # tools.display_dataframe_to_user(name="Pairwise Fisher Exact Tests on Skin Color", dataframe=df)

    import matplotlib.pyplot as plt

    # Sort color counts for consistency
    colors = sorted(color_counts.keys())
    observed_counts = [color_counts[color] for color in colors]
    expected_counts = [totals - observed for observed in observed_counts]  # remainder to stack

    # Get min and max observed counts
    min_val = min(observed_counts)
    max_val = max(observed_counts)

    # Create the same stacked bar chart
    plt.figure(figsize=(10, 6))
    bar1 = plt.bar(colors, observed_counts, label='Observed Differences')
    bar2 = plt.bar(colors, expected_counts, bottom=observed_counts, label='Remaining to Max Possible')

    # Draw dotted lines at min and max observed levels
    plt.axhline(y=max_val, color='black', linestyle='--', linewidth=1, label=f"Max Observed ({max_val})")
    plt.axhline(y=min_val, color='gray', linestyle='--', linewidth=1, label=f"Min Observed ({min_val})")

    plt.xlabel("Skin Color")
    plt.ylabel("Total Possible vs Observed Differences")
    plt.title("Observed vs Possible Differing Prediction Pairs by Skin Color")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Annotate observed bars
    for i, (obs, exp) in enumerate(zip(observed_counts, expected_counts)):
        plt.text(i, obs / 2, str(int(obs)), ha='center', va='center', color='white', fontsize=9)

    plt.show()

