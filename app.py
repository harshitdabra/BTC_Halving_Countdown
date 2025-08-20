import flask
import requests
import datetime
import math

app = flask.Flask(__name__)

@app.route('/')
def index():
 
    halving_data = requests.get('https://api.blockchair.com/tools/halvening').json()['data']['bitcoin']
    current_block = halving_data['current_block']
    current_reward = halving_data['current_reward'] / 100000000  
    next_halving_block = halving_data['halvening_block']
    next_reward = halving_data['halvening_reward'] / 100000000  
    time_left_seconds = halving_data['seconds_left']
    blocks_left = halving_data['blocks_left']
    next_halving_date = datetime.datetime.strptime(halving_data['halvening_time'], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y')

   
    btc_data = requests.get(
        'https://api.coingecko.com/api/v3/coins/bitcoin?localization=false&market_data=true'
    ).json()['market_data']
    current_price = btc_data['current_price']['usd']
    market_cap = btc_data['market_cap']['usd']
    circulating_supply = btc_data['circulating_supply']

    max_supply = 21000000

 
    avg_block_time = time_left_seconds / blocks_left if blocks_left > 0 else 600  
    avg_block_time_min = avg_block_time / 60

   
    known_halvings = [
        {"number": "Genesis", "block": "Genesis Block", "reward": 50, "price": "$0", "date": "01/03/2009"},
        {"number": 1, "block": 210000, "reward": 25, "price": "$12.35", "date": "11/28/2012"},
        {"number": 2, "block": 420000, "reward": 12.5, "price": "$652.14", "date": "07/09/2016"},
        {"number": 3, "block": 630000, "reward": 6.25, "price": "$8,601.80", "date": "05/11/2020"},
        {"number": 4, "block": 840000, "reward": 3.125, "price": "$64,968.87", "date": "04/19/2024"},
    ]
    halvings = known_halvings.copy()
    halving_interval = 210000 
    current_height = current_block
    
    for num in range(5, 34):  
        block = num * halving_interval
        reward = 50 / (2 ** num)
        price = "-"
        blocks_from_now = block - current_height
        if blocks_from_now > 0:
            time_from_now = blocks_from_now * avg_block_time
            est_date = datetime.datetime.now() + datetime.timedelta(seconds=time_from_now)
            date_str = est_date.strftime("%m/%d/%Y") if num < 10 else f"~{est_date.year}"
            halvings.append(
                {"number": num, "block": block, "reward": f"{reward:.8f}", "price": price, "date": date_str}
            )

   
    halvings = halvings[::-1]

   
    past_halvings = known_halvings
    halving_labels = [str(h['number']) for h in past_halvings]
    prices = []
    for h in past_halvings: 
        if h['price'] == '$0':
            prices.append(0)
        else:
            prices.append(float(h['price'][1:].replace(',', '')))

    return flask.render_template(
        'index.html',
        current_block=current_block,
        next_halving_block=next_halving_block,
        blocks_left=blocks_left,
        next_halving_date=next_halving_date,
        time_left_seconds=time_left_seconds,
        current_price=f"${current_price:,.2f}" if current_price else "N/A",
        market_cap=f"${market_cap:,.0f}" if market_cap else "N/A",
        avg_block_time=f"{avg_block_time_min:.2f} minutes",
        circulating_supply=f"{circulating_supply:,.0f}" if circulating_supply else "N/A",
        max_supply=max_supply,
        halvings=halvings,
        current_reward=current_reward,
        next_reward=next_reward,
        halving_labels=halving_labels,
        prices=prices
    )

if __name__ == '__main__':
    app.run(debug=True)