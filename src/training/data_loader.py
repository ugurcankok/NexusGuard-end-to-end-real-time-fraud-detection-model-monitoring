import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class FraudDataLoader:
    def __init__(self, file_name="creditcard.csv"):
        current_path = Path(__file__).resolve()
        
        project_root = current_path.parent.parent.parent
        
        self.file_path = project_root / "data" / file_name
        self.df = None

    def load_data(self):
        if not self.file_path.exists():
            raise FileNotFoundError(f"ERROR: Data file not found! {self.file_path}")
        
        self.df = pd.read_csv(self.file_path)
        return self.df

    def prepare_data(self, target_column='Class'):

        X = self.df.drop([target_column, 'Time'], axis=1)
        y = self.df[target_column]

        scaler = StandardScaler()
        X['Amount'] = scaler.fit_transform(X[['Amount']])
        
        return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)