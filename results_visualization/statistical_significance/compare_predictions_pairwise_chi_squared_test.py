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

    # print(color_counts.values())

    from scipy.stats import chisquare

    observed = list(color_counts.values())
    expected = [sum(observed) / len(observed)] * len(observed)  # uniform expectation
    chi2, p = chisquare(f_obs=observed, f_exp=expected)

    print(p)
    if p < 0.05:
        print("There is a significant difference in the number of apple colors.")
    else:
        print("There is no significant difference; the colors are fairly balanced.")

