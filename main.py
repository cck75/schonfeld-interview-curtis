from dash import Dash, dcc, html
import getDataHkex
from dash.dependencies import Input, Output, State
import plotly.express as px
from dash import Dash, dash_table, ctx
import pandas as pd
from dash.dash_table.Format import Format
from datetime import date, timedelta

app = Dash(__name__)

@app.callback(
    Output('trend-plot', 'figure'),
    Output('trend_data_table', 'data'),
    Output('trend_data_table', 'columns'),
    Output("loading-output-1", "children"),
    Output("table-raw-value", "data"),
    Input('submit-button-state', 'n_clicks'),
    Input('trans-button-state', 'n_clicks'),
    State('input-stock-code', 'value'),
    State('date-range', 'start_date'),
    State('date-range', 'end_date'),
    State('trend_data_table', 'data'),
    State('trend_data_table', 'columns'),
    Input('filter-id', 'value'),
    State("table-raw-value", "data"),
    State("input-thshld", "value"),
    prevent_initial_call=True,)
def update_trend_plot(n_clicks, trans_clicks, stock, start, end, data, columns, search, raw, thshld):
    triggered_id = ctx.triggered_id
    if triggered_id == 'submit-button-state':
        if stock is None:
            return None, pd.DataFrame(), [], None
        print("working")
        df = getDataHkex.trend_plot(stock, start, end).reset_index()
    elif triggered_id == 'trans-button-state':
        if stock is None:
            return None, pd.DataFrame(), [], None
        print("working")
        df, trans = getDataHkex.transaction_finder(stock, start, end, thsld).reset_index()
    else:
        df = pd.DataFrame(raw)
    table_data = df.to_dict('records')
    fig = px.line(df, x="date", y=df.columns,
                  title=f'{stock} Top 10 Shareholding')
    fig.update_xaxes(
        rangeslider_visible=True)


    table_col = [{"name": i, "id": i, "format": Format().group(True), "type":'numeric'} for i in df.columns]
    if triggered_id == 'filter-id':
        cols = df.columns
        if search is None or search == "":
            print("refreshing")
            table_col = [{"name": i, "id": i, "format": Format().group(True), "type": 'numeric'}
                         for i in df.columns]
            return fig, table_data, table_col, "", table_data

        search = search.lower()
        filter = ["date"]+[c for c in cols if search in c.lower() and c != "date"]
        df_new = df[filter]
        table_col = [{"name": i, "id": i, "format": Format().group(True), "type": 'numeric'}
                     for i in df_new.columns]
        new_table_data = df_new.to_dict('records')
        return fig, new_table_data, table_col, "", table_data
    return fig, table_data, table_col, "", table_data

max_start = date.today() - timedelta(days=365)
max_end = date.today() - timedelta(days=1)
app.layout = html.Div(children=[
    html.H1(children='Curtis Kwan Interview'),
    html.H4(children='''
        A web application for HKEX CCASS shareholding search
    '''),
    html.Div([
        dcc.Input(id='input-stock-code', type='text', placeholder='Stock Code'),
        # dcc.Input(id='input-start', type='text', placeholder='start'),
        # dcc.Input(id='input-end', type='text', placeholder='end'),
        dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=max_start,
                max_date_allowed=max_end,
                initial_visible_month=max_end,
                end_date=max_end,
            ),
        html.Button(id='submit-button-state', n_clicks=0, children='Plot'),
        dcc.Loading(
            id="loading-input-1",
            children=[html.Div([html.Div(id="loading-output-1")])],
            type="default",
        ),
    ],  style={'display': 'flex'}),
    html.H4(children=""""""),
    html.Div([dcc.Input(id='input-thshld', type='number', placeholder='% threshold'),
        html.Button(id='trans-button-state', n_clicks=0, children='Transaction Finder')],
             style={'display': 'flex', "font-size":"12px"}),
    dcc.Graph(
        id='trend-plot'
    ),
    html.Div([
            html.H4(children="""Shareholding history"""),
            dcc.Input(id='filter-id', type='text', placeholder='Search ID'),
            html.H4(children=""""""),
            dash_table.DataTable(
                id="trend_data_table",
                filter_action="native",
                sort_action="native",
                page_current=0,
                page_size=10,
            )], className='top10ShsHolding'),
    dcc.Store(id='table-raw-value')
    ])



if __name__ == '__main__':
    app.run_server(debug=True)

