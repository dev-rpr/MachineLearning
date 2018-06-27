import random
import pandas as pd

folder = "../input"

#Find % of null values
def missing(df):
    total = df.isnull().sum().sort_values(ascending = False)
    percent = (df.isnull().sum()/df.isnull().count()*100).sort_values(ascending = False)
    missing_train_data  = pd.concat([total, percent], axis=1, keys=['Total', 'Percent'])
    missing_train_data.to_csv(os.path.join(folder,"missing.csv"))        
    
missing(df)
