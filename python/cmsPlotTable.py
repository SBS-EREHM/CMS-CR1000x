import numpy as np
import pandas as pd
import plotly.express as px
from pathlib import Path


cmsBoxPath = Path('/Users/ericrehm/Library/CloudStorage/Box-Box/CMS_shared/')
cmsDataPath = cmsBoxPath / Path('data')
cmsPlotPath = cmsBoxPath / Path('html')
logger = 'CR1000XSeries'

# Declare CMS tables and associated columns (time series) to plot.
# Always skip column [1] : record
# For CR1X     keep everything else
# For SeapHox  skip header [2], datetime [3], rawString [18]
# For SUNA     skip header [2], date [3], time [4], rawString [22]
# For YSI EXO  skip data [2], time [3]
cmsTables = {
    'CR1X' : [2,3,4],
    'SeapHOx' : [4,5,6,7,8,9,10,11,12,13,14,15,16,17],
    'SUNA' : [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21],
    'EcoTriplet' : [3,4,5],
    'EXOData' : [4,5,6,7,8,9,10,11,12,13,14,15,16,17]
}

table = 'SeapHOx'
table = 'SUNA'
table = 'EcoTriplet'
# table="EXOData"
filterWidth = 5

# Path to table file downloaded from logger
tablePath = cmsDataPath / Path(logger+'_'+table+'.dat')
plotPath = cmsPlotPath / Path(table+'.html')

colsToPlot = cmsTables[table]
print(colsToPlot)

# Read in Campbell TOA5 CSV file
#   igore row [0]
#   header is second row [1], skip row [3].  
#   Row [2] is units: read it, save it, then drop it.  
#   (note Row [2] it becomes Row [0] since we ignored rows 0 and 3, and used row 1 as headr)
df = pd.read_csv(tablePath, header=1, skiprows=[3])
vars = df.columns.values.tolist()
units = df.iloc[0].astype(str).values.tolist()
df.drop(0, inplace=True)
df.reset_index(inplace=True)
# print(df.head(3))

# Because the initial read_csv data had text in some columns, need to coerce data to numeric
# While we're at it, do a rolling median filter
for i in colsToPlot :
    print(vars[i])
    df[vars[i]] = df[vars[i]].apply(pd.to_numeric, errors='coerce').rolling(filterWidth).median()

print(vars)
print(units)

# Put selected varible names and units into lists
value_vars = [vars[i] for i in colsToPlot]
units_vars = [units[i] for i in colsToPlot]

# Rearrange ("melt") data frame so that columns become labeled rows (for facetted plotting)
dfm = pd.melt(df, id_vars = ['TIMESTAMP'], value_vars = value_vars)
# dfm = pd.melt(df, id_vars = ['TIMESTAMP'], value_vars = vars[2:])
# print(dfm.head(3))

# -------
# Plot using plotly express facet feature to create subplot for each variable
fig = px.scatter(dfm, x='TIMESTAMP', y='value', facet_row='variable')
fig.update_yaxes(matches=None)                                  # each y-axis can be zoomed separately
fig.for_each_xaxis(lambda x: x.update(showticklabels=True))     # show x-axis on each plot

# Resize layout to give a roughly constant and readable plot height for each variable
# Scrolling using browser controles
fig.update_layout(
    title=table,
    # autosize=True,lo
    height=len(colsToPlot)*300
)
fig.update_xaxes(rangeslider=dict(visible=False))

# Rewrite annotation to add units
i = 0
for annotation in fig.layout.annotations:
    annotation.text = value_vars[i] + ' (' + units[i] + ')'
    i = i + 1

fig.write_html(plotPath, include_plotlyjs='cdn')
fig.show()