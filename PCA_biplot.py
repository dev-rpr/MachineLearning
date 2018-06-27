import random
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt
import seaborn as sns

random.seed(21)
n = 35 #generate 35 columns
n_rows = 10000 # generate 10,000 records

df_dict = {}
for i in range(n):
    df_dict['feature_'+str(i+1)] = [random.uniform(1,random.randint(0,10*i)) for j in range(n_rows)]

df = pd.DataFrame(df_dict,
             index=[i for i in range(n_rows)])
         
scaler = StandardScaler()
df_sc = scaler.fit_transform(df)

pca = PCA().fit(df_sc)
ex_var = list(pca.explained_variance_ratio_)
ex_sum = 0
n_comp = 0
#Take parameters with explained variance of 80%
for i,j in enumerate(ex_var):
    ex_sum = ex_sum + j
    if (ex_sum < 0.8):
        n_comp = i+2
        
pca_n = PCA(n_components=n_comp).fit(df_sc)
reduced_data = pca_n.transform(df_sc)

plt.figure(figsize=(18, 18))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1])
plt.show()

PCA_dict = {}
for i in range(len(pca_n.components_)):
    PCA_dict['pca' + (str(i+1))] = pca_n.components_[i]

PCA_df = pd.DataFrame(PCA_dict,
             index=list(df.columns))
             
from bokeh.plotting import figure,show,output_file
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource,Legend,LabelSet
from bokeh.palettes import viridis
PLOT_OPTIONS = dict(plot_width=1400, plot_height=700)
PCAfig = figure(title="Mapping",**PLOT_OPTIONS)
PCAfig.scatter(PCA_df['pca1'],PCA_df['pca2'], color='navy',line_width=2, alpha=0.8)

colors = viridis(int(256/PCA_df.shape[0]) * PCA_df.shape[0])
figs = {}
legends = []
source = ColumnDataSource(PCA_df) 
PCA_index = list(PCA_df.index)

for i in range(len(PCA_index)):
    figs[PCA_df.index[i]] = PCAfig.line([0,PCA_df.loc[PCA_df.index[i],'pca1']], [0, PCA_df.loc[PCA_df.index[i],'pca2']], line_width=3,color = colors[int(256/PCA_df.shape[0]) *i])
    legends.append((PCA_df.index[i],[figs[PCA_df.index[i]]]))
legend = Legend(items=legends, location=(0, 0))

labels = LabelSet(x='pca1', y='pca2', text='index', level='glyph',
            x_offset=-14, y_offset=0, source=source, render_mode='canvas',text_font_size = "9pt")

PCAfig.add_layout(labels, 'right')
PCAfig.add_layout(legend, 'right')
show(PCAfig)
