import sys
import csv
from web3 import Web3, HTTPProvider

from config import contract_abi, contract_address, RPC_PROVIDER

DEFAULT_START_BLOCK = 5000000
DEFAULT_END_BLOCK = 5001000

web3 = Web3(HTTPProvider(RPC_PROVIDER))
contract = web3.eth.contract(address=contract_address, abi=contract_abi)


def getEvents(start_block, end_block):
    """Get only 'Birth' events from start_block to end_block

    Args:
        start_block(int):
        end_block(int):
    """
    event_filter = contract.events.Birth.createFilter(
        fromBlock=start_block,
        toBlock=end_block
    )
    events = event_filter.get_all_entries()

    return events


def analyzeEvent(event):
    """Analyze a event
    
    Args:
        event (dict): An event object to analyze

    Returns:
        dict: Analysis data which contains kittyId, txHash ...
    """
    txHash = event['transactionHash']
    kittyId = event['args']['kittyId']
    
    tx = web3.eth.getTransaction(txHash)
    block = web3.eth.getBlock(event['blockNumber'])
    
    fromAddress = tx['from']
    toAddress = tx['to']
    timestamp = block['timestamp']

    return {
        'kittyId': kittyId,
        'txHash': txHash.hex(),
        'from': fromAddress,
        'to': toAddress,
        'timestamp': timestamp
    }


def writeToCSV(data, fileName='events.csv'):
    """Write array of dict data to csv

    Args:
        data (array): Array of dictionaries to write into a csv
        fileName(str): A csv file name
    """
    keys = data[0].keys()
    with open(fileName, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def runAnalyzer(start_block=DEFAULT_START_BLOCK, end_block=DEFAULT_END_BLOCK):
    """Start analyzing the events

    Args:
        start_block(int): Height of the starting block to analyze
        end_block(int): Height of the ending block to analyze
    """
    events = getEvents(start_block, end_block)
    print("--------- Read {} events -----------".format(len(events)))

    eventsData = []
    for event in events:
        data = analyzeEvent(event)
        eventsData.append(data)

    print("--------- Processed {} events ----------".format(len(eventsData)))

    writeToCSV(eventsData)


if __name__ == "__main__":
    start_block = DEFAULT_START_BLOCK
    end_block = DEFAULT_END_BLOCK

    try:
        if (sys.argv[1] is not None) and (sys.argv[2] is not None):
            s = sys.argv[1]
            e = sys.argv[2]

            start_block = min(s, e)
            end_block = max(s, e)
    except Exception:
        pass

    print(start_block)
    print(end_block)

    runAnalyzer(start_block, end_block)
