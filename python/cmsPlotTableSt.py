import sys
import argparse
import numpy as np
import pandas as pd
import plotly.express as px
from pathlib import Path
import streamlit as st

def main() :

    st.set_page_config(layout='wide') 

    st.title('Plot CR1000X Data Table')

    uploaded_file = st.file_uploader('Select a CR1000X table file', type=['dat'])

    if uploaded_file is not None:

        # Display selected file name
        st.success(f'Selected file: {uploaded_file.name}')

        # Boolean and integer options
        # savePlot = st.checkbox('Save plot')
        filterWidth = st.slider('Median filter width (set to 1 to disable)', min_value=1, max_value=20, value=5)

        if st.button('Plot Data'):

            cmsDataPath = uploaded_file
            # cmsPlotPath = Path(str(cmsDataPath).replace('data','html')).with_suffix('.html')

            
            # Extract Table Nane from selected filename
            table = cmsDataPath.name.split('_')[1].split('.')[0]

     
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

            # Process command line
            # args = processCommandLine(cmsTables, cmsBoxDirDefault)
            
            # Go....
            print('Plotting table: ' + table)
            t = st.empty()   # Steamlit status line (start empty)

            # What to do?
            logger = 'CR1000XSeries'
            # table = args.table
            # savePlot = args.saveplot
            # filterWidth = args.filterwidth

            # table = 'SeapHOx'
            # table = 'SUNA'
            # table = 'EcoTriplet'
            # table="EXOData"

            # Path to table file downloaded from logger
            # tablePath = cmsDataPath / Path(logger+'_'+table+'.dat')
            # plotPath = cmsPlotPath / Path(table+'.html')

            # Which columns in table to plot? It depends on the table....
            colsToPlot = cmsTables[table]
            # print(colsToPlot)

            # Read in Campbell TOA5 CSV file
            #   igore row [0]
            #   header is second row [1], skip row [3].  
            #   Row [2] is units: read it, save it, then drop it.  
            #   (note Row [2] it becomes Row [0] since we ignored rows 0 and 3, and used row 1 as headr)
            df = pd.read_csv(cmsDataPath, header=1, skiprows=[3])
            vars = df.columns.values.tolist()
            units = df.iloc[0].astype(str).values.tolist()
            df.drop(0, inplace=True)
            df.reset_index(inplace=True)
            # print(df.head(3))

            # Because the initial read_csv data had text in some columns, need to coerce data to numeric
            # While we're at it, do a rolling median filter
            for i in colsToPlot :
                # print(vars[i])
                t.markdown(f"#### {vars[i]}")  # Update streamlit status line
                df[vars[i]] = df[vars[i]].apply(pd.to_numeric, errors='coerce').rolling(filterWidth).median()
            t.markdown("")  # clear streamlit status line

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
                height=len(colsToPlot)*300,
                width=1000  )
            
            fig.update_xaxes(rangeslider=dict(visible=False))

            # if savePlot :
            #     print('Saving plot to: ' + str(cmsPlotPath))
            #     fig.write_html(cmsPlotPath, include_plotlyjs='cdn')
            st.plotly_chart(fig, use_container_width=True, width=2000)


if __name__ == '__main__' :
    main()