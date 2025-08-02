import requests
import random

# URL for the latest desktop user agents list
url = "https://cdn.jsdelivr.net/gh/microlinkhq/top-user-agents@master/src/desktop.json"
resp = requests.get(url)
ua_list = resp.json()

# Filter user agents for Chrome/Firefox/Edge >= version 130
filtered = [
    ua for ua in ua_list
    if (
        ("Chrome/" in ua and int(ua.split("Chrome/")[-1].split(".")[0]) >= 130)
        or ("Firefox/" in ua and int(ua.split("Firefox/")[-1].split(".")[0]) >= 130)
        or ("Edg/" in ua and int(ua.split("Edg/")[-1].split(".")[0]) >= 130)
    )
]

# Take the top 30 user agents
USER_AGENTS = random.sample(filtered, k=min(30, len(filtered)))
print(USER_AGENTS)
