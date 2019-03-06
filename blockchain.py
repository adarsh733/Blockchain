# Creating a Blockchain
import datetime #for timestamp of each block
import hashlib # to hash functions
import json# o use DOm's functionn to encode the block before hashing
from flask import Flask,jsonify# jsonify to display the response of the request
                                #and to return key information for block in json format
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=1,previous_hash='0') # genesis block  #'0' bcoz sha256 algo takes encoded strings as input
    
    def create_block(self,proof,previous_hash):
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof': proof,
               'previous_hash': previous_hash}
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

#part 2 mining the block
        #Creating a web application
        
app = Flask(__name__)
blockchain = Blockchain()
    
    # mining a block
@app.route('/mine_block', methods= ['GET']) #decorartor  
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof,previous_hash)
    response = {'message': 'Congratulations, You Just Mined A block',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash']}
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

# running the app
app.run(host = '0.0.0.0', port = 5000)#If you have the debugger disabled or trust the users on your network, you can make the server publicly available simply by adding --host=0.0.0.0 to the command line:
                                        #500 is port number
                                        

            
            