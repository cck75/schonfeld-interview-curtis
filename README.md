# Curtis Kwan Coding Interview

## About

This includes my submission to the single page webapp for HKEX CCASS data visualization.

A demo is hosted at AWS: https://zfzqc2myqu.us-east-1.awsapprunner.com/


I used Flask, Dash and Plotly to implement the server on port `8080`

`getDataHkex` 

includes all the function used to make http request and parse response data.
module uses asyncio to make parallel calls for data, but because of rate limit issue. request is throttled at 0.05s per request

`application`

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



