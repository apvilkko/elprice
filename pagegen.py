import os
from datetime import date, datetime, timedelta
from data import get_data

RANGES = (3, 6)

COLORS = [
    (18, 97, 96),
    (77, 62, 64),
    (93, 14, 34)
]  # cheap to expensive
LIMITS = [0.01, 0.10]


def ass(expected, value):
    assert expected == value, f"{expected} != {value}"


def rgb2hex(c):
    if c is None:
        return ""
    assert 0 <= c[0] <= 255
    assert 0 <= c[1] <= 255
    assert 0 <= c[2] <= 255
    return f"#{c[0]:02x}{c[1]:02x}{c[2]:02x}"


def lin_interp(a, c1, c2):
    c = 1.0 - a
    return (
        round(c2[0] * a + c1[0] * c),
        round(c2[1] * a + c1[1] * c),
        round(c2[2] * a + c1[2] * c),
    )


def color_for_price(priceEur: float) -> (int, int, int):
    if priceEur is None:
        return None
    if priceEur <= LIMITS[0]:
        return COLORS[0]
    elif priceEur >= LIMITS[-1]:
        return COLORS[-1]
    pos = priceEur / (LIMITS[-1] - LIMITS[0])
    if pos < 0.5:
        return lin_interp(pos * 2.0, COLORS[0], COLORS[1])
    else:
        return lin_interp((pos - 0.5) * 2.0, COLORS[1], COLORS[2])


def test_color_for_price():
    ass(COLORS[0], color_for_price(-0.01))
    ass(COLORS[0], color_for_price(0.001))
    ass(COLORS[-1], color_for_price(0.11))
    ass((44, 81, 82), color_for_price(0.02))
    ass((79, 57, 61), color_for_price(0.05))
    ass((91, 19, 37), color_for_price(0.085))
    ass(COLORS[-1], color_for_price(LIMITS[-1]))


def dateToStr(d: datetime, fmt: str) -> str:
    return d.strftime(fmt.replace('%-', '%#') if os.name == 'nt' else fmt)


TEMPLATE = r'''
<!DOCTYPE html>
<html lang="fi">
<head>
<meta charset="utf-8">
<title>Sähkön hinta</title>
<style>%STYLE%</style>
</head>
<body>
%BODY%
<table>
<thead>
<tr>
<th class="time">Klo</th><th>Tänään %TODAY%</th><th>PK</th><th>Huomenna %TOMORROW%</th><th>PK</th>
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


def arrow_up():
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-up-circle-fill" viewBox="0 0 16 16">
  <path d="M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0zm-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707V11.5z"/>
</svg>
"""


def arrow_down():
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-down-circle-fill" viewBox="0 0 16 16">
  <path d="M16 8A8 8 0 1 1 0 8a8 8 0 0 1 16 0zM8.5 4.5a.5.5 0 0 0-1 0v5.793L5.354 8.146a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l3-3a.5.5 0 0 0-.708-.708L8.5 10.293V4.5z"/>
</svg>
"""


def calc_range(data, x, now: datetime):
    items = [y for day in data for y in day]
    items = [y for y in items if y[0] >= now.hour]  # only look at future
    sums = []
    for i in range(0, len(items)):
        r = items[i:i+x]
        if len(r) == x and all(v[1] is not None for v in r):
            s = sum([a[1] for a in r])
            sums.append([s, r])

    return sorted(sums)


def safe_list_get(l, i, default):
    try:
        return l[i]
    except IndexError:
        return default


def calc_pk(data, data2=None):
    items = [y[1] for y in data]
    if data2:
        items.extend([x[1] for x in data2])
    out = []
    for i in range(0, len(items)):
        pk = [safe_list_get(items, j, None) for j in range(i, i + RANGES[0])]
        if all([z is not None for z in pk]):
            out.append(sum(pk) * 1.8 / RANGES[0])
        else:
            out.append(None)
    return out[0:len(data)]


def render_best(best, index, amount) -> str:
    res = []
    try:
        best[index][0]
    except IndexError:
        return ""
    for i in range(0, amount):
        hour = best[index][i][1][0][0]
        if hour is not None:
            if hour < 24:
                res.append(f"tänään {hour}:00")
            else:
                res.append(f"huomenna {hour - 24}:00")
    return ", ".join(res)


def render_cell(i: int, t: int, rows, stats):
    hour = rows[0][t][0]
    cents = rows[i][t][1]
    min = stats['min'][i]
    percent = None if cents is None else round(
        100 * ((cents-min) / (stats['max'][i] - min)))
    pk_max_val = arrow_up() if stats['pk'][i][hour] == stats['pk_max'][i] and \
        stats['pk_max'][i] is not None else ""
    pk_min_val = arrow_down() if stats['pk'][i][hour] == stats['pk_min'][i] and \
        stats['pk_min'][i] is not None else ""
    color = rgb2hex(color_for_price(cents))
    inv_percent = None if percent is None else 100 - percent
    style = ""
    if color:
        if percent == 100:
            style = f"background-color: {color};"
        else:
            style = f"background: linear-gradient(to right, {color} 0% {percent}%, rgba(0,0,0,0) {percent}% {inv_percent}%);"
    return f"""<td style="{style}">{format_cents(cents)}</td>
<td>{format_cents(stats['pk'][i][hour])}{pk_max_val}{pk_min_val}</td>
"""


def safe_max(a):
    try:
        return max(a)
    except ValueError:
        return None


def safe_min(a):
    try:
        return min(a)
    except ValueError:
        return None


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
    stats['max'] = (
        safe_max([x[1] for x in rows[0] if x[1] is not None]),
        safe_max([x[1] for x in rows[1] if x[1] is not None]),
    )
    stats['min'] = (
        safe_min([x[1] for x in rows[0] if x[1] is not None]),
        safe_min([x[1] for x in rows[1] if x[1] is not None]),
    )
    print(stats['max'], stats['min'])
    stats['pk'] = (
        calc_pk(rows[0], rows[1]),
        calc_pk(rows[1])
    )
    stats['pk_max'] = (
        safe_max([x for x in stats['pk'][0] if x is not None]),
        safe_max([x for x in stats['pk'][1] if x is not None]),
    )
    stats['pk_min'] = (
        safe_min([x for x in stats['pk'][0] if x is not None]),
        safe_min([x for x in stats['pk'][1] if x is not None]),
    )
    stats['best'] = [calc_range(rows, x, now) for x in RANGES]

    outdata = []
    for t in range(0, 24):
        hour = rows[0][t][0]
        outdata.append(f"""
<tr id="row-{hour}">
<td class="time">{hour:0>2}</td>
{render_cell(0, t, rows, stats)}
{render_cell(1, t, rows, stats)}
</tr>
""")
    best = [
        f"""Halvin {RANGES[i]} tuntia: {render_best(stats['best'], i, 3)}""" for i in range(
            0, len(RANGES))]

    footer = f"""<p>Keskihinta tänään {format_cents(
        stats['average'][0])} snt; huomenna {format_cents(
        stats['average'][1])} snt</p><p>{"<br>".join(best)}</p>"""

    uijs = ""
    with open('ui.js', 'r', encoding='utf-8') as js:
        uijs = js.read()
    styledata = ""
    with open('style.css', 'r', encoding='utf-8') as sf:
        styledata = sf.read()

    out = TEMPLATE.replace(
        "%BODY%", nowf).replace(
        "%TODAY%", dateToStr(today, "%-d.%-m.")).replace(
        "%TOMORROW%", dateToStr(tomorrow, "%-d.%-m.")).replace(
        "%TBODY%", "".join(outdata)).replace(
        "%FOOTER%", footer).replace(
        "%UIJS%", uijs).replace(
        "%STYLE%", styledata)

    return out


def generate():
    data = get_data()
    return generate_page(data)


if __name__ == "__main__":
    test_color_for_price()
