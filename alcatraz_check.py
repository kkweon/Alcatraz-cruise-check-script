#! /usr/local/bin/python3
import bs4
import requests
import gmail
import datetime as dt
import re
import os
date_rex = re.compile(r"date=(?P<month>\d+)-(?P<day>\d+)-(?P<year>\d+)")
EMAIL_ID = os.environ.get("GMAIL_ID") + "@gmail.com"
EMAIL_PW = os.environ.get("GMAIL_PW")
# test_string= "ChooseTicket.aspx?referrer=SearchEventDaySpan.aspx%3fdate%3d1-2-2017%26qty%3d4&id=3239&date=01-05-2017&time=8%3a45+am"
# test_string = "jjjj"
# result = date_rex.search(test_string)
# print(result)


def check_tickets(year, month, day, quantity=4):
    url = "https://www.alcatrazcruises.com/SearchEventDaySpan.aspx?date={month}-{day}-{year}&qty={quantity}"
    url = url.format(year=year, month=month, day=day, quantity=quantity)
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "en-US,en;q=0.8,ko;q=0.6,zh-CN;q=0.4,zh;q=0.2",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Cookie": "D_SID=24.6.244.93:ydW8Wk1ehlpdxGxPtI/A5olumK8UskUPIPJGpyfvRDY; __qca=P0-1078928979-1481691245868; AWSELB=B18F91051A89482B239407F0332E34ECA96A8EE9ACEDE5329C4C1FAF445E71732AEE0E5AA14A3B7FA2E1631087D7C83B2816A87339BBA077BA3FA6E71F2323A04DAA4D4518; __utma=3737568.1019519237.1481691246.1482907686.1482983618.5; __utmb=3737568.5.10.1482983618; __utmc=3737568; __utmz=3737568.1482905141.3.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); D_PID=7B016EEA-4641-39D5-98B8-F5B8C1821016; D_IID=00F3A4BF-DE0B-37C8-A8D6-73554F8A100D; D_UID=B450F0DF-CD78-3501-961E-B76F96083A5C; D_HID=GUsqkMZhCgsO2uLGR+8rVlbU/fYGCgxGHtc9zYXDheY; D_ZID=13EA9A6B-3C33-39FF-9956-53F84837583C; D_ZUID=D6C321D2-902D-3F1E-9A16-1BFFBFE9B3B4",
        "Host": "www.alcatrazcruises.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
    }
    req = requests.get(url, headers=headers).text
    html = bs4.BeautifulSoup(req, 'html.parser')
    available_seats = html.find_all("a", {"class": "sessionTime"})

    result = []
    for pos in available_seats:
        time = pos.get_text()
        href = pos['href']
        available_spots = pos['title']
        date_found = date_rex.search(href)
        if date_found:
            year = int(date_found.group('year'))
            month = int(date_found.group('month'))
            day = int(date_found.group('day'))
            #print("Date: {}-{}-{} {}".format(year,month,day, time))
            result.append((year, month, day, time, available_spots, href))

    return result


def send_msg(title, msg):
    acc = gmail.GMail(EMAIL_ID, EMAIL_PW)
    msg = gmail.Message(title, to=EMAIL_ID, html=msg)
    return acc.send(msg)

def prepare_msg(result):
    msg = ""
    base_url = "https://www.alcatrazcruises.com/"
    result.sort()
    for year, month, day, time, spots, href in result:
        msg += "<a href='{}'>{}-{}-{} {} ({})</a> <br />".format(base_url + href, year, month, day, time, spots)

    return msg

if __name__ == '__main__':
    today = dt.datetime.today()
    year = today.year
    month = today.month
    day = today.day
    quantity = 4

    # Test 1
    # year = 2017
    # month = 1
    # day = 2
    result = check_tickets(year, month, day, quantity)
    if len(result) > 0:
        msg = prepare_msg(result) 
        send_msg("Alcatraz for {}".format(quantity), msg)
    
