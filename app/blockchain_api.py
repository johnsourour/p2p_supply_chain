from flask import Flask, request, jsonify, make_response
import requests
import json
import time
import os

from app.blockchain.transaction import Transaction
from .blockchain import Blockchain, Block
from .configs import APPLICATION_PORT, APPLICATION_SERVICES_ANNONCE
from .application import app

# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()
blockchain.init_account()

# the address to other participating members of the network
peers = set()


def json_text_response(text, status=200):
    if status != 200:
        return make_response(jsonify({"response": text}), status)
    return jsonify({"response": text})


def commit_blockchain_changes(bc):
    """
    After adding of the new block we have to share
    the information with the all nodes in the network
    """
    # Making sure we have the longest chain before announcing to the network
    chain_length = len(bc.chain)
    consensus(bc)
    if chain_length == len(bc.chain):
        # announce the recently mined block to the network
        print("debug:", len(bc.chain))
        announce_new_block(bc.last_block)
        return True
    else:
        return False


def create_chain_from_dump(chain_dump):
    print("debug: create_chain_from_dump")
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    generated_blockchain.init_account()
    if not commit_blockchain_changes(generated_blockchain):
        print("Invalid account generated")
    return generated_blockchain


def register_new_nodes(node_address):
    # request.host_url}
    node_address = node_address.rstrip('/')
    current_host = 'http://localhost:' + APPLICATION_PORT
    data = {"node_address": current_host}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        data = response.json()['response']
        chain_dump = data['chain']
        peers.add(node_address)
        peers.update(data['peers'])
        peers.remove(current_host)
        blockchain = create_chain_from_dump(chain_dump)
        return ("Registration successful", 200)
    else:
        # if something goes wrong, pass it on to the API response
        return (response.content, response.status_code)


def register_service(server_hostname):
    anonce_address = "{}/register_with".format(server_hostname)
    post_object = {"node_address": "http://127.0.0.1:" + APPLICATION_PORT}
    response = requests.post(anonce_address,
                  json=post_object,
                  headers={'Content-type': 'application/json'})
    return response


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
# transaction types: [send_money, offer, verification]
# send_money: money transaction sent from 'from_account' to 'to_account' addresses
# offer: a product offered by 'from_account' the content should have
    # {description, price, deposit, smart contract address}
# verification: product key (content) sent from buyer 'from_account' to smart contract 'to_account'

@app.route('/new_transaction', methods=['POST'])
def new_transaction():

    tx_data = request.get_json()
    required_fields = ["author", "from_account", "to_account", "type"]

    for field in required_fields:
        if not tx_data.get(field):
            return json_text_response("Invalid transaction data", 404)
    if not tx_data.get("timestamp"):
        tx_data["timestamp"] = time.time()
        if not (tx_data.get("type") == Transaction.SEND_MONEY):
            announce_new_transaction(tx_data)

    # smart contract wallet created
    if blockchain.add_new_transaction(tx_data):
        commit_blockchain_changes(blockchain)


    return json_text_response("Success", 201)

# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to dis
# play.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    return json_text_response({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return json_text_response("No transactions to mine")
    else:
        commit_blockchain_changes(blockchain)
        return json_text_response(
            "Block #{} is mined.".format(blockchain.last_block.index),
        )


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return json_text_response("Invalid data", 400)

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return json_text_response("Invalid data", 400)
    
    return json_text_response(*register_new_nodes(node_address))


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return json_text_response("The block was discarded by the node", 400)

    return json_text_response("Block added to the chain", 201)


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def consensus(blockchain):
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global peers

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}/chain'.format(node))
        data = response.json()
        response = data['response']
        length = response['length']
        chain = response['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False

# endpoint to query unconfirmed transactions
@app.route('/get_offers', methods=['GET'])
def get_offers():
    return json.dumps([x.__dict__ for x in blockchain.offers])



def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    print("debug: announcing block to", len(peers), "peers")
    for peer in peers:
        url = "{}/add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        response = requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)
        print(url, response)

def announce_new_transaction(tx):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}/new_transaction".format(peer)
        headers = {'Content-Type': "application/json"}
        response = requests.post(url,
                      data=json.dumps(tx, sort_keys=True),
                      headers=headers)
        print(url, response)


# Register service before start server
for node_address in APPLICATION_SERVICES_ANNONCE:
    register_new_nodes(node_address.rstrip('/')+'/') if node_address else None
    # peers.add(node_address.rstrip('/')+'/') if node_address else None
