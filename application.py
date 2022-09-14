from dash import Dash, dcc, html
import getDataHkex
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import Dash, dash_table, ctx
import pandas as pd
from dash.dash_table.Format import Format
from dash.dash_table import FormatTemplate
from datetime import date, timedelta
import dash_bootstrap_components as dbc


app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Curtis Kwan"
application = app.server

@app.callback(
    Output('trend-plot', 'figure'),
    Output('trend_data_table', 'data'),
    Output('trend_data_table', 'columns'),
    Output("loading-output-1", "children"),
    Output("table-raw-value", "data"),
    Output('trans_data_table', 'data'),
    Output('trans_data_table', 'columns'),
    Input('submit-button-state', 'n_clicks'),
    Input('trans-button-state', 'n_clicks'),
    State('input-stock-code', 'value'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    Input('filter-id', 'value'),
    State("input-thshld", "value"),
    State('trans_data_table', 'data'),
    State('trans_data_table', 'columns'),
    State("table-raw-value", "data"),
    prevent_initial_call=True,)
def update_trend_plot(n_clicks, trans_clicks,
                      stock, start, end,
                      search, thshld,
                      trans_data, trans_col,
                      raw):
    """
    Main function controlling the callbacks from buttons
    to update all graphs and table
    :param n_clicks: placeholder value for trend plot click trigger
    :param trans_clicks: placeholder value for transaction button click trigger
    :param stock: stock code
    :param start: start date
    :param end: end date
    :param search: search value to filter columns in historical shareholding values
                   search value can be of single value or comma seperated values for
                   multiple searches
    :param thshld: float value in % for transaction threshold, 1% will be entered as 1
    :param trans_data: current data in the transaction table
    :param trans_col: current data in transaction column
    :param raw: stored value in memory of trend plot table
    :return: function updates trend plot, trend table and transaction data
    """
    empty = (None, pd.DataFrame(), [], "", pd.DataFrame(), pd.DataFrame(), [])
    triggered_id = ctx.triggered_id
    if triggered_id == 'submit-button-state':
        if stock is None:
            return empty
        df = getDataHkex.trend_plot(stock, start, end).reset_index()
        trans_data = pd.DataFrame().to_dict('records')
        trans_col = []
    elif triggered_id == 'trans-button-state':
        if stock is None:
            return empty
        df, trans = getDataHkex.transaction_finder(stock, start, end, thshld)
        df = df.reset_index()
        trans_data = trans.to_dict('records')
        trans_col = [{"name": i, "id": i} if i!= "% shs exchanged"
                     else {"name": i, "id": i, "format": FormatTemplate.percentage(3), "type":'numeric'}
                     for i in trans.columns]
    else:
        df = pd.DataFrame(raw)

    table_data = df.to_dict('records')
    fig = px.line(df, x="date", y=df.columns,
                  title=f'{stock} Top 10 Shareholding')
    fig.update_xaxes(
        rangeslider_visible=True)
    fig.update_yaxes(
        type="log",
        title="Shareholding (Log Scale)")

    table_col = [{"name": i, "id": i, "format": Format().group(True), "type":'numeric'} for i in df.columns]
    if triggered_id == 'filter-id':
        cols = df.columns
        if search is None or search == "":
            table_col = [{"name": i, "id": i, "format": Format().group(True), "type": 'numeric'}
                         for i in df.columns]
            return fig, table_data, table_col, "", table_data, trans_data, trans_col

        search = search.lower()
        search = [s.strip() for s in search.split(",")]
        def _find(search, cols):
            if search=="":
                return []
            return [c for c in cols if search in c.lower() and c != "date"]
        filtered_col = []
        for s in search:
            filtered_col += _find(s,cols)
        filtered_col = ["date"] + list(set(filtered_col))

        df_new = df[filtered_col]
        table_col = [{"name": i, "id": i, "format": Format().group(True), "type": 'numeric'}
                     for i in df_new.columns]
        new_table_data = df_new.to_dict('records')
        return fig, new_table_data, table_col, "", table_data, trans_data, trans_col
    return fig, table_data, table_col, "", table_data, trans_data, trans_col

# get date range for input, HKEX only allows for 1 year data
max_start = date.today() - timedelta(days=365)
max_end = date.today() - timedelta(days=1)
# create HTML app layout
app.layout = html.Div(style={"padding": "25px"}, children=[
    html.H1(children='Curtis Kwan Interview'),
    html.H4(children='''A web application for HKEX CCASS shareholding search'''),
    html.Div([
        dbc.Row([
            dbc.Col(dbc.Input(id='input-stock-code', type='text', placeholder='Stock Code')),
            dbc.Col(dcc.DatePickerRange(
                    id='date-range',
                    min_date_allowed=max_start,
                    max_date_allowed=max_end,
                    initial_visible_month=max_end,
                    end_date=max_end,),width=2),
            dbc.Col(dbc.Button(id='submit-button-state', n_clicks=0, children='Plot'))
        ]),
        dbc.Row([
            dbc.Col(html.Div(dbc.Input(id='input-thshld', type='number',
                                       placeholder='threshold in %',min=0, max=1))),
            dbc.Col(dbc.Button(id='trans-button-state', n_clicks=0, children='Transaction Finder'))
        ])
    ]),
    dcc.Loading(id="loading-input-1", children=[html.Div([html.Div(id="loading-output-1")])], type="default"),
    dcc.Graph(id='trend-plot'),
    html.Div([
        html.H4(children="""Shareholding History"""),
        dbc.Input(id='filter-id', type='text', placeholder='Search ID'),
        html.H4(children=""""""),
        dash_table.DataTable(
            id="trend_data_table",
            filter_action="native",
            sort_action="native",
            page_current=0,
            page_size=10,
        )], className='top10ShsHolding'),
    html.Div([
        html.H4(children="""Transaction History"""),
        html.H4(children=""""""),
        dbc.Row([dbc.Col(dash_table.DataTable(
                            id="trans_data_table",
                            filter_action="native",
                            sort_action="native",
                            page_current=0,
                            page_size=10,
                            style_cell={"white-space": "pre-wrap"}))]),
    ], className='transData'),
    dcc.Store(id='table-raw-value')
    ])



if __name__ == '__main__':
    #app.run_server(debug=True)
    application.run(host='0.0.0.0', port='8080')

