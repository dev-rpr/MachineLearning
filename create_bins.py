#A column to be binned in 10 bins
col = 'col_name'
uniques = sorted(df[col].unique())
no_bins = 10
bins = [uniques[i*int(df[col].nunique()/no_bins)] for i in range(no_bins)]
bins.append(uniques[len(uniques)-1])
labels = [label_str[i-1:i] for i in range(1,no_bins+1)]
df[col + '_binned'] = pd.cut(df[col], bins=bins, labels=labels,right=True,include_lowest=True)
test[col + '_binned'] = pd.cut(test[col], bins=bins, labels=labels,right=True,include_lowest=True)
df.drop(col,axis=1,inplace=True)


##
