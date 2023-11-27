import pandas as pd
import os

# Function to save a DataFrame as a pickle file
def save_as_pickle(df, filename):
    # Define the path to the pickle directory relative to the current file
    current_dir = os.path.dirname(__file__)
    pickle_dir = os.path.join(current_dir, "../data/pickle")
    pickle_path = os.path.join(pickle_dir, filename + '.pkl')
    
    # Ensure the directory exists
    os.makedirs(pickle_dir, exist_ok=True)
    
    # Save the DataFrame
    df.to_pickle(pickle_path)

# Function to load a DataFrame from a pickle file
def load_from_pickle(filename):
    if filename:
        # Define the path to the pickle directory relative to the current file
        current_dir = os.path.dirname(__file__)
        pickle_dir = os.path.join(current_dir, "../data/pickle")
        pickle_path = os.path.join(pickle_dir, filename + '.pkl')
        
        # Load the DataFrame
        return pd.read_pickle(pickle_path)
    else:
        return pd.DataFrame({})