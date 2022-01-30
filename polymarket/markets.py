import requests


def get_active_markets(slug=None, look_back=None):
    api_uri = "https://strapi-matic.poly.market/markets?_limit=-1&active=true&closed=false"

    if slug is not None:
        api_uri = f"https://strapi-matic.poly.market/markets?slug={slug}"
    r = requests.get(api_uri)
    return r.json()
