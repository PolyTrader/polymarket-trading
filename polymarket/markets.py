import requests


def get_active_markets():
    api_uri = "https://strapi-matic.poly.market/markets?_limit=-1&active=true"
    r = requests.get(api_uri)
    return r.json()
