import pandas as pd
import polaris as po

def get_data():
    fp = 'https://raw.githubusercontent.com/adaptyvbio/egfr_competition_1/refs/heads/main/results/replicate_summary.csv'
    df = pd.read_csv(fp)

    # Load the dataset from the Hub
    dataset = po.load_dataset("adaptyv-bio/egfr-binders-v0")

    merged_df = dataset.table.merge(df)
    return merged_df