from flask import render_template, redirect, request
import datetime
import json
import requests

from .application import app
from .blockchain_api import blockchain
from .configs import APPLICATION_PORT
from . import configs as config

# The node with which our application interacts, there can be multiple
# such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:{}".format(APPLICATION_PORT)

posts = []

def fetch_posts():
    """
    Function to fetch the chain from a blockchain node, parse the
    data and store it locally.
    """
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address)
    if response.status_code == 200:
        content = []
        data = response.json()
        chain = data['response']
        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global posts
        posts = sorted(content, key=lambda k: k['timestamp'],
                       reverse=True)


@app.route('/')
def index():
    fetch_posts()
    wallet = blockchain.account_block
    wallet_hash = blockchain.get_account_wallet_hash()
    print(posts)
    return render_template('index.html',
                           title=config.SERVICE_TITLE,
                           posts=[post for post in posts if wallet_hash in [post['from_account'], post['to_account']]],
                           wallet=wallet,
                           blockchain=blockchain,
                           node_address=CONNECTED_NODE_ADDRESS,
                           readable_time=timestamp_to_string)


@app.route('/submit', methods=['POST'])
def submit_textarea():
    """
    Endpoint to create a new transaction via our application.
    """
    post_content = request.form["content"]
    author = request.form["author"]
    type = request.form["type"]
    target = request.form["target"]

    post_object = {
        'author':  author,
        'content': post_content,
        'type':  type,
        'from_account': blockchain.get_account_wallet_hash(),
        'to_account': target,
    }

    # Submit a transaction
    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)

    requests.post(new_tx_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
