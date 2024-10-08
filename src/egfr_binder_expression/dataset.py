import pandas as pd
import polaris as po
from egfr_binder_expression import DATA_DIR

def get_data():
    fp = 'https://raw.githubusercontent.com/adaptyvbio/egfr_competition_1/refs/heads/main/results/replicate_summary.csv'
    df = pd.read_csv(fp)

    # Load the dataset from the Hub
    dataset = po.load_dataset("adaptyv-bio/egfr-binders-v0")

    merged_df = dataset.table.merge(df, how='outer')

    merged_df['length'] = merged_df['sequence'].apply(len)
    return merged_df

def get_data_with_scraped_expression():
    df = get_data()
    expression = pd.read_csv(DATA_DIR / 'scraped_egfr_binder_expression.csv')
    expression['expression'] = expression['expression'].fillna('None')
    
    individuals = expression[expression['designer'].isna()].iloc[1:]
    individuals[['name', 'replicate']] = individuals['design_name'].str.split(' #', expand=True)
    
    clean_exp = individuals[['name', 'replicate', 'expression']]
    clean_exp['replicate'] = clean_exp['replicate'].astype(int)
    
    mdf = df.drop(columns=['expression']).merge(clean_exp, on=['name', 'replicate'], how='outer')
    mdf.loc[:1, 'expression'] = 'Low'
    
    return mdf
