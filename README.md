# Curtis Kwan Coding Interview

## About

This includes my submission to the single page webapp for HKEX CCASS data visualization.

A demo is hosted at AWS: https://zfzqc2myqu.us-east-1.awsapprunner.com/


I used Flask, Dash and Plotly to implement the server on port `8080`

`getDataHkex.py` 

includes all the function used to make http request and parse response data.
module uses asyncio to make parallel calls for data, but because of rate limit issue, 
request is throttled at 0.05s per request

`application.py`

main script to run program, contains the DASH code to generate html elements and callback functions to support

## Instructions

- Install required modules using pip `pip install -r requirements.txt`
- Start the server by running `python application.py`
- If ran properly the follow results will show in CLI
```commandline
 * Serving Flask app "application"
 * Environment: development
 * Debug mode: off
 * Running on http://0.0.0.0:8080/  (Press CTRL+C to quit)
```
## Webapp Visualization
![Alt text](asset/trend_plot.png?raw=true "Front Page")

There are two buttons: `Plot` and `Transaction Finder`

`Plot` will take input `Stock Code, Start Date, End Date`
and update the graph and corresponding table with shareholding history

![Alt text](asset/trend_table.png?raw=true "Front Page")

Shareholding table can be sorted and filtered by value. Columns could be filtered by using the search bar. 
Search can be done using single word, or comma separated values for multiple searches.
Table is paginated, click through to see more history

![Alt text](asset/trend_table_filter.png?raw=true "Front Page")

`Transaction Finder` will take input from required fields:
`Stock Code, Start Date (max 1 year history), End Date, Threshold`
this function will update all the charts, including from `Plot` and also add the data into Transaction history table
Table is paginated, click through to see more history

![Alt text](asset/trans_table.png?raw=true "Front Page")




