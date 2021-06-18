import importlib_resources as resources
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from .markets import get_active_markets


def get_positions(user):
    gql_uri = "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic"
    transport = RequestsHTTPTransport(gql_uri)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql(resources.read_text('polymarket.gql', 'positions.gql'))

    return client.execute(query, {"user": user.lower()})


def list_positions(user):
    markets = get_active_markets()
    mkt_pos = get_positions(user)

    mkts = {mkt['marketMakerAddress'].lower(): mkt for mkt in markets}

    positions = {}
    for pos in mkt_pos['marketPositions']:
        # If you don't currently own any shares in this position, don't list it.
        if pos['netQuantity'] == '0':
            continue

        mkt_id = pos['market']['id']
        if not positions.get(mkt_id):
            positions[mkt_id] = {}

        if not positions[mkt_id].get('question'):
            positions[mkt_id] = {'question': mkts[mkt_id]['question']}

        if not positions[mkt_id].get('positions'):
            positions[mkt_id]['positions'] = [None] * len(mkts[mkt_id]['outcomes'])

        outcome_label = mkts[mkt_id]['outcomes'][int(pos['outcomeIndex'])]
        outcome_price = mkts[mkt_id]['outcomePrices'][int(pos['outcomeIndex'])]
        positions[mkt_id]['positions'][int(pos['outcomeIndex'])] = (outcome_label, pos['netQuantity'], outcome_price,
                                                                    pos['netValue'])

    print("-"*80)
    print("Question")
    print("    position / number shares / share price / position value ")
    for _, v in positions.items():
        print("-" * 80)
        print(v['question'])

        for z in v['positions']:
            if z is not None:
                position_name = z[0]
                num_shares = int(z[1])/10**6
                share_price = float(z[2])
                position_value = int(z[3])/10**6

                print(f"    {position_name} / {num_shares:.6f} / {share_price:.4f} / ${position_value:.4f}")
