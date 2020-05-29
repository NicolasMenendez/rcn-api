from urllib3.util import parse_url
import time
import web3

def new_web3(url_node):
    parsed_url = parse_url(url_node)

    if parsed_url.scheme == "wss":
        provider = web3.WebsocketProvider(url_node)
    else:
        provider = web3.HTTPProvider(url_node)
    
    w3_instance = web3.Web3(provider)

    return w3_instance

def getBlock(w3, number):
    i = 0
    block = w3.eth.getBlock(number)

    if block is not None:
        return block
    else:
        while i < 10:
            time.sleep(0.5)
            block = w3.eth.getBlock(number)

            if block is not None:
                return block

            i += 1
        raise Exception("fucking nodo")


def split_every(n, string):
    return [string[i:i + n] for i in range(0, len(string), n)]


def to_address(hex_string):
    return '0x' + hex_string[-40:]


def to_int(hex_string):
    return web3.Web3.toInt(hexstr=hex_string)


def to_bool(hex_string):
    # TODO: fix this
    return hex_string


def add_0x_prefix(string):
    return web3.utils.contracts.add_0x_prefix(string)
