import requests
headers = {
    'User-Agent': "ozilla/5.0 (Linux; Analytics) [This is a scraper of nardtree's analytics. htts://gink03.github.io/]"
}
r = requests.get('https://www.yahoo.co.jp/', headers=headers)
print(r.headers)
