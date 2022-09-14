import asyncio
import requests
import aiohttp
import pandas as pd
from datetime import datetime
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

def async_get_all(url, payloads):
    """
    performs asynchronous get requests from url and payload
    requests are capped at 0.05s pre request to avoid rate limit
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
    """
    parses data from response, % total share holding is calculated
    using Total number of Issued Shares/Warrants/Units (last updated figure)
    instead of directly from table, because of rounding accuracy
    :param data: response data from hhtp request
    :return: dataframe containing shareholding information
    """
    result = []
    for d, date in data:
        if "</table>" in d:
            df = pd.read_html(d)[0]
            total = d.split('summary-value">')[1].split("</div>")[0]
            df["total"] = int(total.replace(",",""))
            df["date"] = pd.to_datetime(date).date()
            result.append(df)
    df = pd.concat(result)
    for c in df.columns[:-2]:
        df[c] = df[c].apply(lambda x: x.split(": ")).apply(lambda x: x[1] if len(x) > 1 else None)
    df.Shareholding = df.Shareholding.str.replace(',', '').astype(float)
    df.columns = ["id", "name", "address", "shareholding", "pct total", "total", "date"]
    df["pct total calc"] = df.shareholding / df.total
    df["pct total"] =  df["pct total"].str.replace("%", "").astype(float) / 100

    return df

def trend_plot(stockCode, start, end):
    """
    function used to get data for task 1
    :param stockCode:
    :param start:
    :param end:
    :return: dataframe with index date, columns participantID of top 10 shareholders
    """
    resp = create_request(stockCode, start, end)
    df = parse_data(resp)
    plot = df.pivot_table(values="shareholding", columns="id", index="date")
    keep = plot.iloc[-1,:].dropna().sort_values(ascending=False).index[:10]
    return plot[keep]

def transaction_finder(stockCode, start, end, thsld):
    """
    function to get and process data for task 2
    function looks at daily change in share holdings
    and if the change is shareholdings are larger than thsld
    then transaction will be recorded
    :param stockCode:
    :param start:
    :param end:
    :param thsld: float in % 1% will be 1
    :return: plot10 (data for task1), output (dataframe containing all transactions
             that satisfy thershold requirement)
    """
    thsld = thsld/100.
    resp = create_request(stockCode, start, end)
    df = parse_data(resp)
    plot = df.pivot_table(values="shareholding", columns="id", index="date")
    keep = plot.iloc[-1, :].dropna().sort_values(ascending=False).index[:10]
    plot_10 = plot[keep]
    pct_shs = df.pivot_table(values="pct total calc", columns="id", index="date")
    shares = df.pivot_table(values="shareholding", columns="id", index="date")
    diff = pct_shs.diff()
    id_name_map = df.set_index("id")["name"].drop_duplicates().to_dict()
    output = []
    # loop through daily to search for all valid transactions
    for i,r in diff.iterrows():
        trans = r[r.abs()>thsld]
        if len(trans) > 0:
            def _po_trade(data):
                name = [id_name_map.get(n) for n in data.index]
                ids = ", ".join(data.index)
                name = ", ".join(name)
                amount = ", ".join(data.apply("{0:.3%}".format).values)
                return name, ids, amount

            add = _po_trade(r[r>0])
            sub = _po_trade(r[r<0])

            trans = trans.to_frame()
            trans.columns = ["% shs exchanged"]
            trans["date"] = r.name
            trans["name"] = trans.index.map(id_name_map.get)
            trans[["potential name", "potential id", "trans % shs"]] = \
                pd.DataFrame(trans.iloc[:,0].apply(lambda x: add if x<0 else sub).tolist(), index=trans.index)
            trans = trans.reset_index()
            trans = trans.sort_values("% shs exchanged", ascending=False)
            output.append(trans)
    output = pd.concat(output)
    output = output[['date','id', 'name', '% shs exchanged', 'potential name', 'potential id', "trans % shs"]]
    return plot_10, output






