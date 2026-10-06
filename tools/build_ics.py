#!/usr/bin/env python3
"""יוצר פיד יומן חי לכל אחראי מתוך Firebase. רץ ב-GitHub Actions."""
import json, re, os, urllib.request
from datetime import datetime, timedelta, timezone

DB   = 'https://home-picks-47450-default-rtdb.europe-west1.firebasedatabase.app'
OUT  = os.path.join(os.path.dirname(__file__), '..', 'cal')
FEED = {'רועי': 'roi-8f3a.ics', 'יעל': 'yael-2c71.ics'}
EMO  = re.compile(r'^[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F\s]+')
TIME = re.compile(r'\b([01]?\d|2[0-3]):([0-5]\d)\b')

def esc(v):
    return (str(v or '').replace('\\', '\\\\').replace(',', '\\,')
            .replace(';', '\\;').replace('\r\n', '\n').replace('\n', '\\n'))

def fold(line):
    """RFC 5545 מגביל ל-75 אוקטטים לשורה. עברית היא שני בתים לתו,
       אז הקיפול חייב לספור בתים אבל לחתוך על גבול תו."""
    out, cur, used, limit = [], [], 0, 73
    for ch in line:
        n = len(ch.encode())
        if used + n > limit:
            out.append(''.join(cur)); cur, used, limit = [ch], n, 72
        else:
            cur.append(ch); used += n
    out.append(''.join(cur))
    return '\r\n '.join(out)

def events_for(who, tasks):
    ev = []
    for t in tasks:
        if t.get('done') or t.get('ongoing') or not t.get('due'): continue
        owner = t.get('owner')
        if owner != who and owner != 'שנינו': continue
        try: y, m, d = (int(x) for x in t['due'].split('-'))
        except Exception: continue
        hm = TIME.search(t.get('notes') or '')
        st = datetime(y, m, d, int(hm.group(1)) if hm else 9, int(hm.group(2)) if hm else 0)
        en = st + timedelta(minutes=15)
        f  = lambda x: x.strftime('%Y%m%dT%H%M00')
        title = EMO.sub('', t.get('title', '')).strip()
        if owner == 'שנינו': title += ' [שנינו]'
        body = re.sub(r'<[^>]*>', '', t.get('notes') or '')[:700]
        ev += ['BEGIN:VEVENT', f'UID:{t["id"]}@avgil-board',
               'DTSTAMP:' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
               f'DTSTART:{f(st)}', f'DTEND:{f(en)}',
               fold('SUMMARY:' + esc(title)),
               fold('DESCRIPTION:' + esc(body + '\n\nhttps://yaelavgil.github.io/avgil-board/')),
               'BEGIN:VALARM', 'TRIGGER:PT0S', 'ACTION:DISPLAY',
               fold('DESCRIPTION:' + esc(title)), 'END:VALARM',
               'BEGIN:VALARM', 'TRIGGER:-PT2H', 'ACTION:DISPLAY',
               fold('DESCRIPTION:' + esc(title)), 'END:VALARM',
               'END:VEVENT']
    return ev

def main():
    data = json.load(urllib.request.urlopen(DB + '/board/tasks.json')) or {}
    tasks = [dict(v, id=k) for k, v in data.items() if isinstance(v, dict)]
    os.makedirs(OUT, exist_ok=True)
    for who, fname in FEED.items():
        ev = events_for(who, tasks)
        ics = '\r\n'.join(['BEGIN:VCALENDAR', 'VERSION:2.0',
            'PRODID:-//avgil-board//HE', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
            fold('X-WR-CALNAME:' + esc('משימות ' + who)),
            'X-PUBLISHED-TTL:PT30M', 'REFRESH-INTERVAL;VALUE=DURATION:PT30M'] +
            ev + ['END:VCALENDAR']) + '\r\n'
        with open(os.path.join(OUT, fname), 'w', encoding='utf-8', newline='') as fh:
            fh.write(ics)
        print(f'{fname}: {len(ev)//13} אירועים')

if __name__ == '__main__':
    main()
