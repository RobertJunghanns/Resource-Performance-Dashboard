import pandas as pd
import os

def save_as_pickle(df, filename, pickle_dir='src/data/pickle'):
    # Define the full path to the pickle file
    pickle_path = os.path.join(pickle_dir, filename + '.pkl')
    
    # Ensure the directory exists
    os.makedirs(pickle_dir, exist_ok=True)
    
    # Save the DataFrame
    df.to_pickle(pickle_path)

def load_from_pickle(filename, pickle_dir='src/data/pickle'):
    if filename:
        # Define the full path to the pickle file
        pickle_path = os.path.join(pickle_dir, filename + '.pkl')
        
        # Load the DataFrame
        return pd.read_pickle(pickle_path)
    else:
        return pd.DataFrame({})