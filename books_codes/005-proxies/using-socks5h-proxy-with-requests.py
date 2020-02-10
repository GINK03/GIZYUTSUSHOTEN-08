
import requests

proxies=dict(http='socks5h://133.130.97.98:9150',
                                 https='socks5h://133.130.97.98:9150')
r = requests.get('https://ipinfo.tw/ip', proxies=proxies)

print(r.text)
