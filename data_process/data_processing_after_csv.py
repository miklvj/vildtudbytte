import pandas as pd
import numpy as np

df = pd.read_csv("data.csv", sep=",")


df['Area'] = np.where(df['Year'] <= 2005, 'Amt', 'Kommune')

# apply more prodessing steps if needed

df.to_csv("data_processed.csv", index=False, sep=";")