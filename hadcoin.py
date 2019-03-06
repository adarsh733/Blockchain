# Creating a Cryptocurrency
import datetime #for timestamp of each block
import hashlib # to hash functions
import json# o use DOm's functionn to encode the block before hashing
from flask import Flask,jsonify,request# jsonify to display the response of the request
                                #and to return key information for block in json format
                                #request for making the blockchain decentralized with nodes
import requests #to check that all the nodes in decentralized blockchain have same Chain
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:
    def __init__(self):
        self.chain = []
        self.transactions= []
        self.create_block(proof=1,previous_hash='0') # genesis block  #'0' bcoz sha256 algo takes encoded strings as input
        self.nodes = set()
    def create_block(self,proof,previous_hash):
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof': proof,
               'previous_hash': previous_hash,
               'transactions' : self.transactions}
        self.transactions = [] # making list empty
        self.chain.append(block)
        return block
    def get_previous_block(self):
        return self.chain[-1]
    
    
    def proof_of_work(self,previous_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof=True
            else: 
                new_proof+=1
        return new_proof
    
    
    def hash(self,block):
        encoded_block=json.dumps(block,sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    
    
    def is_chain_valid(self,chain):
        previous_block=chain[0]
        block_index=1
        while block_index < len(chain):
            block=chain[block_index]
            if block['previous_hash']!=self.hash(previous_block):
                return False
            previous_proof=previous_block['proof']
            new_proof=block['proof']
            hash_operation=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block=block
            block_index+=1
        return True

    def add_transactions(self,sender ,receiver,amount): #specifying format for transactions
        self.transactions.append({'sender' : sender,
                                  'reciever' : receiver,
                                  'amount' : amount})
        previous_block = self.get_previous_block()
        return previous_block['index']+1   
#part 2 mining the block
        #Creating a web application
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)        

    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code==200:
                length= response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            return True
        return False               
app = Flask(__name__)

# it will generate a unique address for the sender on port 5000
node_address = str(uuid4()).replace('-','') 


blockchain = Blockchain()
    
    # mining a block
@app.route('/mine_block', methods= ['GET']) #decorartor  
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(sender= node_address, receiver = 'Adarsh', amount = 100) 
    block = blockchain.create_block(proof,previous_hash)
    response = {'message': 'Congratulations, You Just Mined A block',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions' : block['transactions']}
    return jsonify(response), 200 # returning the response in json format and 200 for http response of OK

# getting the full blockchain displayed in blockchain
@app.route('/get_chain', methods = ['GET'])    
def get_chain():
    response = {'chain' : blockchain.chain,
                'length' : len(blockchain.chain)}
    return jsonify(response), 200 # returning the response in json format and 200 for http response of OK

@app.route('/is_valid', methods= ['GET']) #decorartor
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : 'All good.Blockchain is valid.'}
    else:
        response = {'message' : 'Adarsh , we have some problem.The Blockchain is not valid'}
    return jsonify(response), 200    

#Adding new transaction in the blockchain
@app.route('/add_transaction', methods= ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return "some elements of transaction are missing",400
    index = blockchain.add_transactions(json['sender'],json['receiver'],json['amount'])
    response = {'mesage' : f'this transaction will be added to block {index}'}# f string syntax
    return jsonify(response),201 # created

# running the app
app.run(host = '0.0.0.0', port = 5000)#If you have the debugger disabled or trust the users on your network, you can make the server publicly available simply by adding --host=0.0.0.0 to the command line:
                                        #500 is port number
                                        

            
   #PART 3 : decentralizing the blockchain
   
#creating new nodes
@app.route('/connect_node', methods= ['POST'])
def connect_node():
    json = request.get_json() 
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message' : "All the nodes are now connected. The hadcoin Blockchain now contains the following nodes: ",
                'Total Nodes' : list(blockchain.nodes)}
    return jsonify(response),200
# Replacing the chain by longest chain  
@app.route('/replace_chain', methods= ['GET']) #decorartor
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message' : 'The nodes had different chains so the chain was replaced by the longer one.',
                    'new_chain' : blockchain.chain}
    else:
        response = {'message' : 'Alright, the chain is larger one',
                    'actual_chain' : blockchain.chain }
    return jsonify(response), 200    
