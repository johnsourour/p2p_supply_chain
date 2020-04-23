# Peer to Peer Supply Chain Reseller's market

This project is about a peer to peer basic application built on top of a blockchain with PoW consensus algorithm. The main actors of the system are buyers and sellers who have their own wallets on the system of products and they can add listings (or offers) for their product and the purchase of the product is handled by a smart contract that guarantees the anonymity and the security of the transactions involved by using the dual-deposit approach.


## Instructions to run

Clone the project,

```sh
$ git clone https://github.com/satwikkansal/python_blockchain_app.git
```

Install the dependencies,

```sh
$ cd p2p_suuply_chain
$ pip install -r requirements.txt
```

or makefile,

```sh
$ make deps
```

Start a blockchain node server,

```sh
# Windows users can follow this: https://flask.palletsprojects.com/en/1.1.x/cli/#application-discovery
$ export FLASK_APP=node_server.py
$ flask run --port 8000
```

or makefile,

```sh
$ make run
$ make run PORT=CUSTOM_PORT
```

One instance of our blockchain node is now up and running at that port (8000 by defaut) 

## Screenshots

TBA



## Credits

This project is built on top of [this repo](https://github.com/satwikkansal/python_blockchain_app/tree/ibm_blockchain_post), credits to the original author 


