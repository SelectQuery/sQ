import selectq
from selectq.predicates import Attr as attr

import requests
import itertools

import pprint
import tqdm
import datetime
import sys

#sQ = selectq.open_browser('https://google.com', browser_type='firefox', executable_path='geckodriver')

def get_proxies_from_previous_run(fname):
    with open(fname, 'rt') as f:
        lines = list(f.readlines())

    r = list(filter(None, (l.strip().split() for l in lines)))
    print(len(r))
    return r


def get_proxies_from_freeproxylists(sQ):
    url = 'https://freeproxylists.net/?c=&pt=&pr=HTTPS&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0'
    sQ.browser.get(url)

    tbl = sQ.select('table', class_='DataGrid')
    selectq.wait_for(tbl == 1)

    # Give me the first 'td' of all the table rows.
    # Then select the links ('a') but give me your parent.
    # This *filters* the 'td' which don't contain a link  <----
    first_column = tbl.select('tr').select('td').at(0).select('a').parent()

    # Now give me the first of the following sibling of each td
    next_column = first_column.children('following-sibling::*').at(0)

    ips = first_column.select('a').text()
    ports = next_column.text()

    r = list(zip(ips, ports, itertools.cycle(['freeproxylists'])))
    print(len(r))
    return r

def get_proxies_from_freeproxycz(sQ):
    url = 'http://free-proxy.cz/en/proxylist/country/all/http/ping/level1/1'
    sQ.browser.get(url)

    tbl = sQ.select('table', id='proxy_list')
    selectq.wait_for(tbl == 1)

    first_column = tbl.select('tr').select('td').at(0)

    next_column = first_column.children('following-sibling::*').at(0)

    ips = list(filter(None, first_column.pluck('innerText')))
    ports = next_column.text()


    r = list(zip(ips, ports, itertools.cycle(['freeproxylists'])))
    print(len(r))
    return r


def get_proxies_from_proxyscrape(sQ):
    url = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite'
    ret = requests.get(url, allow_redirects=True)

    r = [line.split(":", 1) + ['proxyscrape'] for line in ret.text.splitlines()]
    print(len(r))
    return r

def save_good_proxies(proxies, fname):
    with open(f"{fname}-{datetime.datetime.today():%Y%m%d-%H%M}", "wt") as f:
        stats = {}
        seen = set()
        for ip, port, source in tqdm.tqdm(proxies):
            if source not in stats:
                stats[source] = {'count': 0, 'good': 0}

            stats[source]['count'] += 1

            proxy_str = f"http://{ip}:{port}"
            if proxy_str in seen:
                continue
            seen.add(proxy_str)

            cfg = {
                    "timeout": 15,
                    "url": "https://google.com",
                    "proxies": {"http": proxy_str, "https": proxy_str}
                    }
            try:
                ret = requests.get(**cfg)

                if 200 <= ret.status_code < 299:
                    stats[source]['good'] += 1
                    print(proxy_str)
                    f.write(f"{ip} {port} {source}\n")

            except Exception as err:
                pass

        pprint.pprint(stats)

proxies = []
if len(sys.argv) == 2:
    proxies += get_proxies_from_previous_run(sys.argv[1])
#proxies += get_proxies_from_freeproxylists(sQ)
#proxies += get_proxies_from_freeproxycz(sQ)
#proxies += get_proxies_from_proxyscrape(None)
sQ.browser.quit()
save_good_proxies(proxies, fname="goodproxies")
