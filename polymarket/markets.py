import requests


def get_active_markets(slug=None):
    api_uri = "https://strapi-matic.poly.market/markets?_limit=-1&active=true"

    if slug is not None:
        api_uri += f"&slug={slug}"
    r = requests.get(api_uri)
    return r.json()
