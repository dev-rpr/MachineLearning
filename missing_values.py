'''
Find data type, percentage of null values and number of unique values for all features
'''
def info(df,sort = True,save = "No"):
    size = df.shape[0]
    null = df.isnull().sum()
    nuni = df.nunique()
    dtype = df.dtypes
    missing_pct = null*100/size
    df_info  = pd.concat([dtype, missing_pct.round(2),nuni], axis=1, keys=['type','missing','nunique'])
    if sort == True:
        df_info.sort_values (['missing'],ascending=False,inplace=True)
    if (save == "Yes")
        df_info.to_csv(os.path.join(folder,'info.csv'))
    return df_info
