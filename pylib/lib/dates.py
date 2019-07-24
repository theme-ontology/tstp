from dateutil.parser import parse
from datetime import datetime, time, timedelta


def iter_days(dtfrom, dtuntil, daysofweek=None, attime='00:00'):
    """
    Yield every matching datetime between dtfrom and dtuntil.

    :param dtfrom: str, date, datetime
    :param dtuntil: str, date, datetime
    :param daysofweek: int, str or list thereof
    :param attime: str or time
    :return: datetimes
    """
    if isinstance(dtfrom, str):
        dtfrom = parse(dtfrom)
    if isinstance(dtuntil, str):
        dtuntil = parse(dtuntil)
    lu = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    if daysofweek is None:
        daysofweek = [0, 1, 2, 3, 4, 5, 6]
    if not isinstance(daysofweek, list):
        daysofweek = [daysofweek]
    daysofweek = set(lu.index(x[:3].lower()) if isinstance(x, str) else x for x in daysofweek)
    if isinstance(attime, str):
        attime = parse(attime).time()

    dt1, dt2 = dtfrom.date(), dtuntil.date()
    while dt1 <= dt2:
        if dt1.weekday() in daysofweek:
            yield datetime.combine(dt1, attime)
        dt1 += timedelta(days=1)



def main():
    data = list(iter_days("2019-07-01", "2019-07-31", 'wed', '00:00'))
    print(data)

