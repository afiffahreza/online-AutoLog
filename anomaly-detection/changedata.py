import pandas as pd

df = pd.read_csv('./dataset/scores_labeled.csv')
df.head()

# add dummy column
df['dummy'] = 0
df.head()

# order last 2 column to first 2
cols = df.columns.tolist()
cols = cols[-2:] + cols[:-2]
df = df[cols]
df.head()

# export to csv file, without the header
df.to_csv('./dataset/BGLVector_new.csv', header=False, index=False)
