# Peer to Peer Supply Chain Reseller's market

A simple tutorial for developing a blockchain application from scratch in Python.

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

## Instructions to run

TBA



## Credits

This project is built on top of [this repo](https://github.com/satwikkansal/python_blockchain_app/tree/ibm_blockchain_post), credits to the original author 


