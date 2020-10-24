import pandas as pd
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import json
import dash_bootstrap_components as dbc
import csv
import base64
import datetime
import io



def votecalculate_dashboard(df):
    #Load in data, remove timestamp column
    df=df.drop(["Timestamp"],axis=1)
    vals=df.values
    
    
    testprint=""
    printarray=[]
    #Turn the df into an array with proper names and inputs
    test2=[]
    names=[]
    for item in df.columns:
        names.append(item.split("[")[-1].replace("]",""))
    test2.append(names)
    for item in vals:
        test2.append(item)
    
    #Begin the calculations
    #Count_list is returned for sankey making later
    Count_list=[]
    #test is a list of the votes
    test = []
    
    testprint+="INITIAL FIRST PREFERENCE VOTES\n"
    printarray.append("INITIAL FIRST PREFERENCE VOTES")
    
    j=1
    while j<len(test2):
        k=0
        temp = []
        while k<len(test2[1]):
            temp = temp+[int(test2[j][k].split()[-1])]

            k=k+1
        test = test + [temp]
        j=j+1
    
    #Set up the eliminated array
    eliminated = [1]*len(test[0])
    
    #count is for the number of 1st preferences
    count = [0]*len(test[0])
    for entry in test:
        i=0
        while i<len(entry):
            if entry[i]==1:
                count[i] +=1
                i=i+1
                continue
            i=i+1
    
    #Eliminate all those with 0 votes
    i=0
    namevector = []
    numelim=0
    while i<len(count):
        if count[i]==0:
            namevector = namevector + ["ELIMINATED"]
            numelim+=1
            eliminated[i]=-1
        else:
            namevector = namevector + [names[i]]
        i = i + 1
    testprint+="[{}]\n".format(",".join(str(elem) for elem in namevector))
    printarray.append("[{}]".format(",".join(str(elem) for elem in namevector)))
    testprint+="[{}]\n".format(",".join(str(elem) for elem in count))
    printarray.append("[{}]".format(",".join(str(elem) for elem in count)))
    Count_list.append(count)
    #So the initial count is done
    
    
    
    
    

    i=numelim+1
    q=1
    #Set it up to repeat n-1 times
    while i<(len(test[1])-1):
        testprint+="REDISTRIBUTION ROUND {}\n".format(q)
        printarray.append("REDISTRIBUTION ROUND {}".format(q))
        #Set it up so that if there are n-1 eliminations, the code ends
        if numelim >=len(test[0])-1:
            return
        
        
        #Find the minimum number of votes
        testmin = []
        t=0
        while t<len(count):
            if count[t] == 0:
                t+=1
                continue
            else:
                testmin = testmin + [count[t]]
            t+=1
        minimumvote = min(testmin)
        testprint+="the minimum number of votes is: {}\n".format(minimumvote)
        printarray.append("the minimum number of votes is: {}".format(minimumvote))
        
        #See if anybody ties for the minimum number of votes
        tie = False
        s=0
        while s<len(count):
            temporary = count[s]
            t=s+1
            while t<len(count) and tie==False:
                if ((count[s]==count[t]) and (count[s]==minimumvote) and (count[s]!=0)):
                    testprint+="THERE IS A TIE"
                    printarray.append("THERE IS A TIE")
                    tie = True
                t = t+1
            s = s+1
        if tie:
            testprint+="which candidate would you like to eliminate?\n"
            printarray.append("which candidate would you like to eliminate?")
            
            inputbool=False
            while not inputbool:
                user_elim=input()
                if user_elim in names:
                    inputbool=True
                else:
                    testprint+="That is not a candidate. Which candidate would you like to eliminate?\n"
                    printarray.append("That is not a candidate. Which candidate would you like to eliminate?")
            elim = names.index(user_elim)
        else:
            elim = count.index(minimumvote)
        testprint+="the person to be eliminated is: {}\n".format(names[elim])
        printarray.append("the person to be eliminated is: {}".format(names[elim]))
        
        #record the elimination
        eliminated[elim] = -1
        p=0
        while p<len(test):
            j=0
            while j<len(test[p]):
                if test[p][j]==1 and j==elim:
                    k=0
                    while k<len(test[p]):
                        test[p][k] = test[p][k]-1
                        k=k+1
                    
                j+=1
            
            #Redistribute votes
            
            completed = False
            while not completed:
                k=0
                if eliminated[test[p].index(1)] == 1:
                    completed = True
                    continue
                else:
                    while k<len(test[p]):
                        test[p][k] = test[p][k]-1
                        if test[p][k]<0:
                            test[p][k]=0
                        k=k+1
                if sum(test[p])==0:
                    testprint+="vote exhausted\n"
                    printarray.append("vote exhausted")
                    completed = True

        
                
            p+=1


        count = [0]*len(test[1])
        for entry in test:
            l=0
            while l<len(count):
                if entry[l]==1:
                    count[l]+=1
                l=l+1

        m=0
        namevector = []
        while m<len(count):
            if count[m]==0:
                namevector = namevector + ["ELIMINATED"]
            else:
                namevector = namevector + [names[m]]
            m = m + 1
        testprint+="[{}]\n".format(",".join(str(elem) for elem in namevector))
        printarray.append("[{}]".format(",".join(str(elem) for elem in namevector)))
        testprint+="[{}]\n".format(",".join(str(elem) for elem in count))
        printarray.append("[{}]".format(",".join(str(elem) for elem in count)))
        Count_list.append(count)
        i+=1
        q+=1
    return testprint,printarray
    
    
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SUPERHERO])
server=app.server


app.layout =html.Div([
    html.H1("Election calculator"),
    dbc.Row([
        dbc.Col([
            html.Div("This dashboard is designed to take in csv which was made through google forms,\
            and perform the process of preferential voting to it."),
            html.Div("It could be used for basic elections, or for educational purposes"),
            html.Br(),
            html.Div("For best performance, use the following format for the google form:"),
            html.Div("Single question (Multiple Choice Grid), with ROWS being the names of candidates and COLUMNS being \"Preference #\"\
            with # being the numbers from 1 to the number of candidates."),
            html.Div("Check \"Require a response in each row\" and \"Limit to one response per column\"."),
            html.Div("Optionally, you could shuffle rows to ensure fairness of candidate order."),
            html.Br(),
            html.Div("In it's current iteration, it cannot deal with ties in votes, though \
            this is a feature being actively worked on"),
            html.Br(),
            html.Div("Upload the file below:"),
            dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    )
        ],
        width=4
        ),

        dbc.Col([
            html.Div(id='output-data-upload')
            
        ],
        width=8)
    ])
]
)


def parse_contents(content, filename, date):
    content_type, content_string = content.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    test1,test2=votecalculate_dashboard(df)
    children=[]
    for item in test2:
        children.append(html.Div(item))
    return children


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children[0]




if __name__ == '__main__':
    app.run_server()
