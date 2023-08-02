import os
import requests
import json
from datetime import date, datetime, timedelta

DUMMY = False
URL = 'https://api.spot-hinta.fi/TodayAndDayForward'
RANGES = (3,6)

def dateToStr(d: datetime, fmt: str) -> str:
    return d.strftime(fmt.replace('%-', '%#') if os.name == 'nt' else fmt)

def fetch_data():
    print("fetching from " +URL)
    res = requests.get(URL)
    response = json.loads(res.text)
    return response

def fetch_data_dummy():
    print("using dummy fetch")
    with open('dummy.json', 'r', encoding='utf-8') as f:
        response = f.read()
    return json.loads(response)

TEMPLATE = r'''
<!DOCTYPE html>
<html lang="fi">
<head>
<meta charset="utf-8">
<title>Sähkön hinta</title>
<style>
html, body {
  font-size: 4vw;
}
body {
  margin: 1rem;
}
table {
  margin: 0;
  padding: 0;
  margin-top: 1rem;
}
th {
  text-align: left;
}
td, th {
  padding: 0;
  padding-left: 0.5rem;
}
td {
  border-top: 1px dashed #ccc;
  border-left: 1px dashed #ccc;
  text-align: center;
}
td.time, th.time {
  border-left: none;
  padding-left: 0;
  text-align: left;
}
</style>
</head>
<body>
%BODY%
<table>
<thead>
<tr>
<th class="time">Klo</th><th>Tänään %TODAY%</th><th>Huomenna %TOMORROW%</th>
</tr>
</thead>
<tbody>
%TBODY%
</tbody>
</table>
%FOOTER%
<script type="text/javascript">
(function(){
%UIJS%
})();
</script>
</body>
</html>
'''

def init_rows(i):
    return [[x, None] for x in range(i+0, i+24)]

def format_cents(value: float):
    if value is None:
        return ""
    return str(round(value * 100, 2)).replace('.', ',')

def calc_average(data):
    items = [x[1] for x in data if x[1] is not None]
    if len(items) > 0:
        return sum(items) / len(items)
    return None

def calc_range(data, x):
    items = [y for day in data for y in day]

    sums = []
    for i in range(0, len(items)):
        r = items[i:i+x]
        if len(r) == x and all(v[1] is not None for v in r):
            s = sum([a[1] for a in r])
            sums.append([s, r])

    return sorted(sums)

def render_best(best, amount):
    res = []
    for i in range(0, amount):
        hour = best[i][1][0][0]
        if hour is not None:
            if hour < 24:
                res.append(f"tänään {hour}:00")
            else:
                res.append(f"huomenna {hour - 24}:00")
    return ", ".join(res)

def generate_page(data):
    now = datetime.now()
    nowf = dateToStr(now, "Luotu %-d.%-m.%Y %a %H:%M.%S")
    today = date.today()
    tomorrow = date.today() + timedelta(days=1)
    
    rows = [init_rows(0), init_rows(24)]

    for d in data:
        if d['DateTime']:
            dataDate = datetime.fromisoformat(d['DateTime'])
            index = -1
            if dataDate.day == today.day:
                index = 0
            elif dataDate.day == tomorrow.day:
                index = 1
            hourIndex = dataDate.hour
            if index == 0 or index == 1:
                value = d['PriceWithTax']
                if value is not None:
                    rows[index][hourIndex][1] = value

    stats = {}
    stats['average'] = (
        calc_average(rows[0]),
        calc_average(rows[1])
    )
    stats['best'] = [calc_range(rows, x) for x in RANGES]
    outdata = []
    for t in range(0, 24):
        hour = rows[0][t][0]
        outdata.append(f"""
<tr id="row-{hour}">
<td class="time">{hour:0>2}</td>
<td>{format_cents(rows[0][t][1])}</td>
<td>{format_cents(rows[1][t][1])}</td></tr>
""")
    best = [
        f"""Halvin {RANGES[i]} tuntia: {render_best(stats['best'][i], 3)}""" for i in range(
            0, len(RANGES))]


    footer = f"""<p>Keskihinta tänään {format_cents(
        stats['average'][0])} snt; huomenna {format_cents(
        stats['average'][1])} snt</p><p>{"<br>".join(best)}</p>"""

    uijs = ""
    with open('ui.js', 'r', encoding='utf-8') as js:
        uijs = js.read()
    
    out = TEMPLATE.replace(
        "%BODY%", nowf).replace(
        "%TODAY%", dateToStr(today, "%-d.%-m.")).replace(
        "%TOMORROW%", dateToStr(tomorrow, "%-d.%-m.")).replace(
        "%TBODY%", "".join(outdata)).replace(
        "%FOOTER%", footer).replace(
        "%UIJS%", uijs)

    return out

def generate():
    data = fetch_data_dummy() if DUMMY else fetch_data()
    return generate_page(data)
