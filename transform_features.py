#Create dummies for train set
#Create dummies for test set using categories present only in train set
#Handle multicollinearity


def create_cat(df,col,values):
    prefix = col
    unique_vals = values #list(df[col].unique())    
    dummies = pd.DataFrame()
    for val in unique_vals:
        dummies[prefix + "_" + val] = df[col] == val
        dummies[prefix + "_" + val] = dummies[prefix + "_" + val].apply(lambda x: 1 if x == True else 0)
            #le = LabelEncoder()
            #dummies[prefix + "_" + val] = le.fit_transform(dummies[prefix + "_" + val])
    
    df = pd.concat([df,dummies],axis=1)
    return df 
    
    
#For example, one has to create dummies for zip code
highest_cat = train['zip_code'].value_counts().index[0]
values_cat = [i for i in list(train.zip_code.unique()) if i not in [highest_cat]]

start = time.time()
train = create_cat(train,'zip_code',values_cat)
print("Time taken: ", time.time() - start)
train.drop('zip_code',axis=1, inplace=True)

test = create_cat(test,'zip_code',values_cat)
print("Time taken: ", time.time() - start)
test.drop('zip_code',axis=1, inplace=True)
