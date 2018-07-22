label_str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

#A column to be binned in 10 bins
col = 'col_name'
uniques = sorted(df[col].unique())
no_bins = 10
bins = [uniques[i*int(df[col].nunique()/no_bins)] for i in range(no_bins)]
bins.append(uniques[len(uniques)-1])
labels = [label_str[i-1:i] for i in range(1,no_bins+1)]
df[col + '_binned'] = pd.cut(df[col], bins=bins, labels=labels,right=True,include_lowest=True)
df.drop(col,axis=1,inplace=True)



#create bins where 5 unique values have to be binned together
col_bins = ['col1','col2','col3']
for col in col_bins: #5 unique values in each bin
    uniques = sorted(df[col].unique())
    no_bins = int(df[col].nunique()/5)
    bins = [uniques[i*5] for i in range(no_bins)]
    bins.append(uniques[len(uniques)-1])
    labels = [label_str[i-1:i] for i in range(1,no_bins+1)]
    df[col + '_binned'] = pd.cut(df[col], bins=bins, labels=labels,right=True,include_lowest=True)
    
df.drop(col_bins,axis=1,inplace=True)
