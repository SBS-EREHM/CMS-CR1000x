import sys
import argparse
import numpy as np
import pandas as pd
import plotly.express as px
from pathlib import Path
import gsw 

def processCommandLine(cmsTables, cmsBoxDirDefault) :
    # Instantiate the parser
    parser = argparse.ArgumentParser(description='Plot CR1000X logger tables as time series')

    # Required positional argument
    parser.add_argument('table', type=str,
                    help='One of : CR1X, SeapHOx, SUNA, EcoTriplet, or EXOData', default='SeapHOx')

    # Optional positional argument
    # parser.add_argument('opt_pos_arg', type=int, nargs='?',
                    # help='An optional integer positional argument')
    
    # Optional argument
    parser.add_argument('-cbd', '--cmsboxdir', type=str,
                    help='cms root directory on Box.com', default=cmsBoxDirDefault)
    
    # Optional argument
    parser.add_argument('-fw', '--filterwidth', type=int,
                    help='Median filter width (default = 5; set to 1 to disable)', default=5)

    # save plot Sswitch
    parser.add_argument('-save', '--saveplot', action='store_true',
                    help='Save plot to cmsBoxDir/html')
    args = parser.parse_args()

    table = args.table
    if table in cmsTables:
        return args
    else:
        tables = list(cmsTables.keys())
        sys.exit('table must be one of : '+ str(tables))

def main() :

    # Define some defaults before processing command line args
    cmsBoxDirDefault = '/Users/ericrehm/Library/CloudStorage/Box-Box/CMS_shared/'

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
        # 'EXOData' : [4,5,6,7,8,9,10,11,12,13,14,15,16,17]
        'EXOData' : [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
    }

    # Process command line
    args = processCommandLine(cmsTables, cmsBoxDirDefault)
    
    # Go....
    print('Plotting table: ' + args.table)
    # print(args.cmsboxdir)
    # print(args.saveplot)

    # Where is the data?  Where do the plots go?
    cmsBoxPath = Path(args.cmsboxdir)
    cmsDataPath = cmsBoxPath / Path('data')
    cmsPlotPath = cmsBoxPath / Path('html')

    # What to do?
    logger = 'CR1000XSeries'
    table = args.table
    savePlot = args.saveplot
    filterWidth = args.filterwidth

    # table = 'SeapHOx'
    # table = 'SUNA'
    # table = 'EcoTriplet'
    # table="EXOData"

    # Path to table file downloaded from logger
    tablePath = cmsDataPath / Path(logger+'_'+table+'.dat')
    plotPath = cmsPlotPath / Path(table+'.html')

    # Which columns in table to plot? It depends on the table....
    colsToPlot = cmsTables[table]
    # print(colsToPlot)

    # Read in Campbell TOA5 CSV file
    #   igore row [0]
    #   header is second row [1], skip row [3].  
    #   Row [2] is units: read it, save it, then drop it.  
    #   (note Row [2] it becomes Row [0] since we ignored rows 0 and 3, and used row 1 as headr)
    df = pd.read_csv(tablePath, header=1, skiprows=[3])
    vars = df.columns.values.tolist()
    units = df.iloc[0].astype(str).values.tolist()
    df.drop(0, inplace=True)
    df.reset_index(inplace=True, drop=True)
    # print(df.head(3))

    # Because the initial read_csv data had text in some columns, need to coerce data to numeric
    # While we're at it, do a rolling median filter
    for i in colsToPlot :
        print(vars[i])
        df[vars[i]] = df[vars[i]].apply(pd.to_numeric, errors='coerce').rolling(filterWidth).median()

    # df['SPHOX_S'] = gsw.SP_from_C(df['SPHOX_C']*10,  df['SPHOX_T'],  df['SPHOX_P'])
    # print(vars)
    # print(units)

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

    # Rewrite annotation to add units  (BROKEN)
    # i = 0
    # for annotation in fig.layout.annotations:
    #     annotation.text = value_vars[i] + ' (' + units_vars[i] + ')'
    #     i = i + 1

    if savePlot :
        print('Saving plot to: ' + str(plotPath))
        fig.write_html(plotPath, include_plotlyjs='cdn')
    fig.show()


if __name__ == '__main__' :
    main()