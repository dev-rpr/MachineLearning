import datetime
import bokeh
import pandas as pd
import numpy as np
import math
import pyodbc
import os
import re

from bokeh.plotting import figure  
from bokeh.models import ColumnDataSource, LabelSet, FuncTickFormatter
from bokeh import resources
from bokeh.embed import components
from bokeh.util.string import encode_utf8
from bokeh.models.tickers import FixedTicker
from bokeh.palettes import d3

import flask

app = flask.Flask(__name__)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

def clean(Anlyz,parm):
#clean to remove out of expected range
    return Anlyz[np.abs(Anlyz[parm]-Anlyz[parm].mean())<=(3*Anlyz[parm].std())][['dCreated',parm,'iClass']]

@app.route("/")
def IV():
    PLOT_OPTIONS = dict(plot_width=800, plot_height=600)
    class_name = [     'class 17.2',
     'class 17.5',
     'class 17.8',
     'class 18.0',
     'class 18.1',
     'class 18.2',
     'class 18.3',
     'class 18.4',
     'class 18.5',
     'class 18.6',
     'class 18.7',
     'class 18.8',
     'class 18.9',
     'efficiency low',
     'front quality',
     'irradiance high',
     'low shunt',
     'shunt r low',
     'special color']
    # Grab the inputs arguments from the URL
    #'2018-03-26'
    args = flask.request.args
    # Get all the form arguments in the url with defaults
    _Lane = getitem(args, 'Lane', 'both')
    _date = getitem(args, 'date', (datetime.datetime.now()).strftime("%Y-%m-%d"))
    _days = getitem(args, 'days', '2')    
    
    from_date = (datetime.datetime.strptime(_date, "%Y-%m-%d") + datetime.timedelta(days=-1*int(_days))).strftime("%Y-%m-%d") + " 06:00:00"   
    to_date = (datetime.datetime.strptime(_date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 06:00:00"
    
    # Fetch data from sql
    #Database Connection String
    #connIV = pyodbc.connect('Driver={SQL Server};Server=0.0.0.0\SQLEXPRESS;Database=IV;UID=sa;PWD=Solar@123')
    connIV = pyodbc.connect('Driver={SQL Server};Server=SERVER_NAME\SQLEXPRESS;Database=IV')
    
    if (_Lane != 'both'):
        queryTemp_Lanes = ("SELECT dCreated,Eff0,Pmpp0,Isc0,Uoc0,Fill0,Rseries_OC,Rshunt_SC,Ireverse_1,Ireverse_2,iClass,sClass,Commentary FROM IV_Lane"+ _Lane + " WHERE Convert(datetime,dCreated) BETWEEN Convert(datetime,'%s') AND Convert(datetime,'%s')\
            " % (from_date, to_date))
        df = pd.read_sql(queryTemp_Lanes,connIV)
    else:
        queryTemp_Lane1 = ("SELECT dCreated,Eff0,Pmpp0,Isc0,Uoc0,Fill0,Rseries_OC,Rshunt_SC,Ireverse_1,Ireverse_2,iClass,sClass,Commentary FROM IV_Lane1" + " WHERE Convert(datetime,dCreated) BETWEEN Convert(datetime,'%s') AND Convert(datetime,'%s')\
            " % (from_date, to_date))
        queryTemp_Lane2 = ("SELECT dCreated,Eff0,Pmpp0,Isc0,Uoc0,Fill0,Rseries_OC,Rshunt_SC,Ireverse_1,Ireverse_2,iClass,sClass,Commentary FROM IV_Lane2" + " WHERE Convert(datetime,dCreated) BETWEEN Convert(datetime,'%s') AND Convert(datetime,'%s')\
            " % (from_date, to_date))
        df1 = pd.read_sql(queryTemp_Lane1,connIV)
        df2 = pd.read_sql(queryTemp_Lane2,connIV)
        df = df1.append(df2)    
    
    def get_batch(val):
        if ((not (('test' in val.lower()) or ('resort' in val.lower()))) and (('eng' in val.lower()) or ('prod' in val.lower()))):
            return(1) #re.findall('(\d\d\d\d\d\d\d\d)',val)[0]
        else:
            return(0)
    
    def get_shift_date(val):
        if (val.strftime("%H") < '06'):
            return (datetime.datetime.strptime(val.strftime("%Y-%m-%d"),'%Y-%m-%d') + datetime.timedelta(days = -1)).strftime("%Y-%m-%d")        
        else:
            return val.strftime("%Y-%m-%d")

    df['Batch'] = df.Commentary.apply(lambda x: get_batch(x))
    df = df[df.Batch != 0]
    
    _total = df.shape[0]
    #good cells
    #df = df[(df.iClass <= 25) | (df.iClass == 29)]
    good_cells = df.shape[0]
    #Plot figures
    #Get all batches
    df['sClass'] =  df['sClass'].apply(lambda x: x.lower())
    df['sClass'] =  df['sClass'].apply(lambda x: 'class 18.0' if x == 'class 18' else x)

    df['Batch'] = df.dCreated.apply(lambda x: get_shift_date(x))
    tot_batch = len(df['Batch'].unique())

    if (_total > 0):
        tot_df = {}
        labels = {}
        for i in range(tot_batch):
            y_val = []
            temp_df = df[df['Batch'] == df['Batch'].unique()[i]]
            y_all = pd.DataFrame(temp_df.groupby('sClass')['Eff0'].count())            
            for m in class_name:
                if (m in y_all.index):
                    y_val.append(y_all.loc[m,'Eff0'])
                else:
                    y_val.append(0)            
            if (i == 0):
                x_val = list(class_name.copy()) #list(y_all.index.astype(str))                
                for j in range(len(x_val)):
                    x_val[j] = j * (tot_batch + 1)
            else:
                x_val = [k+1 for k in x_val]
            tot_df["x"+str(i)] = x_val
            tot_df["y"+str(i)] = y_val
            
        source = ColumnDataSource(tot_df)
        for i in range(tot_batch):
            labels[i] = LabelSet(x='x'+str(i), y='y'+str(i), text='y'+str(i), level='glyph',
                    x_offset=-14, y_offset=0, source=source, render_mode='canvas',text_font_size = "9pt")

        if (tot_batch > 2):
            colors = d3['Category10'][tot_batch]
        else:
            colors = d3['Category10'][3] 
        x_label = "sClass"
        y_label = "Count"
        title = "Count per Class for batch "
        classfig = figure(**PLOT_OPTIONS,
                x_axis_label = x_label,
                y_axis_label = y_label,
                title=title,
                x_minor_ticks=2
                         )
        for i in range(tot_batch):
            classfig.vbar(source=source,x='x'+str(i),top='y'+str(i),bottom=0,width=0.9,alpha=0.8,color=colors[i],legend = df['Batch'].unique()[i])

        classfig.xaxis.major_label_orientation = math.pi/2
        classfig.xaxis.ticker = FixedTicker(ticks = x_val)
        label_dict = {}
                
        if (len(x_val) > 0):
            for i,s in enumerate(x_val):
                label_dict[s] = class_name[i]
            classfig.xaxis.formatter = FuncTickFormatter(code = """var _labels = %s;return _labels[tick];""" % label_dict)
            for i in range(tot_batch):
                classfig.add_layout(labels[i])
    else:
        x_label = "sClass"
        y_label = "Count"
        title = "No value found "
        classfig = figure(**PLOT_OPTIONS,
                x_axis_label = x_label,
                y_axis_label = y_label,
                title=title,
                x_minor_ticks=2
                         )
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    script, div = components({'classfig': classfig})
    html = flask.render_template(
        'IV_class.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        Lane=_Lane,
        date = _date,
        days = _days,
        count = _total,
        good = good_cells
    )
    return encode_utf8(html)

if __name__ == "__main__":
    print(__doc__)
    app.run(port = 5001)
