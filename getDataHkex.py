import asyncio
import requests
import aiohttp
import pandas as pd
from datetime import datetime
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def async_get_all(url,payloads):
    """
    performs asynchronous get requests
    """
    async def get_all(url, payloads):
        async with aiohttp.ClientSession() as session:
            async def fetch(url, payload):
                async with session.post(url, data=payload) as r:
                    text = await r.text()
                    return (text, payload.get("txtShareholdingDate"))
            result = []
            for payload in payloads:
                result.append(asyncio.ensure_future(fetch(url, payload)))
                await asyncio.sleep(0.05)

            return await asyncio.gather(*result)
    return asyncio.run(get_all(url, payloads))

def create_request(stockCode, start, end):
    url = "https://www3.hkexnews.hk/sdw/search/searchsdw.aspx"
    today = datetime.today().strftime("%Y/%m/%d")
    print(start, end)
    dates = pd.date_range(start, end)
    payloads = [
        {'__EVENTTARGET': 'btnSearch',
         'today': today,
         'sortBy': 'shareholding',
         'sortDirection': 'desc',
         'txtShareholdingDate': d.strftime("%Y/%m/%d"),
         'txtStockCode': stockCode}
        for d in dates]
    return async_get_all(url, payloads)

def parse_data(data):
    result = []
    for d, date in data:
        if "</table>" in d:
            df = pd.read_html(d)[0]
            df["date"] = pd.to_datetime(date).date()
            result.append(df)
    df = pd.concat(result)
    for c in df.columns[:-1]:
        df[c] = df[c].apply(lambda x: x.split(": ")).apply(lambda x: x[1] if len(x) > 1 else None)
    df.Shareholding = df.Shareholding.str.replace(',', '').astype(float)
    df.columns = ["id", "name", "address", "shareholding", "pct total", "date"]
    df["pct total"] =  df["pct total"].str.replace("%", "").astype(float) / 100

    return df

def trend_plot(stockCode, start, end):
    resp = create_request(stockCode, start, end)
    df = parse_data(resp)
    plot = df.pivot_table(values="shareholding", columns="id", index="date")
    keep = plot.iloc[-1,:].dropna().sort_values(ascending=False).index[:10]
    return plot[keep]

def transaction_finder(stockCode, start, end, thsld):
    resp = create_request(stockCode, start, end, thsld)
    df = parse_data(resp)
    plot = df.pivot_table(values="shareholding", columns="id", index="date")
    keep = plot.iloc[-1, :].dropna().sort_values(ascending=False).index[:10]
    plot_10 = plot[keep]
    pct_shs = df.pivot_table(values="pct total", columns="id", index="date")
    shares = df.pivot_table(values="shareholding", columns="id", index="date")
    diff = pct_shs.diff()
    id_name_map = df.set_index("id")["name"].drop_duplicates().to_dict()
    output = []
    for i,r in diff.iterrows():
        trans = r[r.abs()>0]
        if len(trans) > 0:
            def _po_trade(data):
                name = [id_name_map.get(n) for n in data]
                data = ", ".join(data)
                name = ", ".join(name)
                return name, data

            add = _po_trade(trans[trans>0].index)
            sub = _po_trade(trans[trans<0].index)

            trans = trans.to_frame()
            trans.columns = ["% shs exchanged"]
            trans["date"] = r.name
            trans["potential trades"] = trans.iloc[:,0].apply(lambda x: add if x<0 else sub)
            trans = trans.reset_index()
            output.append(trans)
        output = pd.concat(output)
        return plot_10, output






