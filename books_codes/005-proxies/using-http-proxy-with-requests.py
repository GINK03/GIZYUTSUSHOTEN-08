# proxy の例

import requests

proxies = {
        "https": "http://user:user@133.130.97.98:3128/",
        "http": "http://user:user@133.130.97.98:3128/"
}

r = requests.get('https://ifconfig.co/', proxies=proxies, verify=False)

print(r.text)
