import hashlib
import json


from time import time
from uuid import uuid4

# for using this blockchain as api
from flask import Flask, jsonify, request

# This Blockchain class is responsible for managing the chain
class BlockChain:
    def __init__(self):
        self.chain = []
        self.current_transactions = [] 

        # Create the genesis(origin) block
        self.newBlock(previous_hash=1, proof=100) 
        
    def newBlock(self, proof, previous_hash = None):
        # Creates a new block in the chain
        """
        proof : (int) Proof given by proof of work algo
        previous hash - (optional) : (str) Hash of the previous block
        return : (dict) New block
        """
        
        block = {
            'index'         : len(self.chain) + 1,
            'timestamp'     : time(),
            'transactions'  : self.current_transactions,
            'proof'         : proof,
            'previous_hash' : previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def newTransactions(self, sender, recipient, amount):
        # Add new transactions to the list of tranasactions
        
        """
            sender : Address of the sender
            reciever : Address of the reciever
            amount : The amout that has been transacted
            
            It return's the index of the block that will hold this transaction
        """


        self.current_transactions.append({
            'sender'    :   sender,
            'recipent'  :   recipient,
            'amount'    :   amount,
        })
        
        #returning the index of this block
        return self.lastBlock['index'] + 1


    def proofOfWork(self, last_proof):
        """ 
        A proof of work algo which is quite simple
        -Find a number p' such that hash(pp') contains leading 4 zeros , where P is the previous p'
        -p is the previous proof and p is the new proof

        last_proof : <int>
        return : <int>
        """

        proof = 0

        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        """ 
        Validates the proof by checking if hash(last_proof, proof) contains 4 leading zeros

        last_proof : <int> previous proof
        proof : <int> Current proof
        return : <bool> True or False
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        # Hash function
        """
        Creates a SHA-256 hash of block 

        block : (dict) block
        returns : (str)
        """
        
        # Making sure that the dictionary is ordered
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    @property
    def lastBlock(self):
        # Returns the last Block in the chain
        
        pass



# Instantiate our Node
app = Flask(__name__)

# We will create three methods in our flask app
# 1) /transactions/new : to create a new tranasaction block
# 2) /mine : to tell our server to mine a new block
# 3) /chain : to return a full Blockchain

# Genereate a globlally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate our BlockChain
blockchain = BlockChain()


@app.route('/mine', methods=['GET'])
# This has to do three things 
# 1) Calculate proof of work 
# 2) Reward the miner (us) by adding  a transaction granting us 1 coin
# 3) Forge the new Block by adding it to the chain
def mine():
    # we want to run proof of work algorithm to get the next proof....
    last_block = blockchain.lastBlock
    last_proof = last_block['proof']
    proof = blockchain.proofOfWork(last_proof)

    # we must recieve reward for finding the proof 
    # the sender is "0" to signify that this node has new coin
    blockchain.newTransactions(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    #forge the new block by adding it to the chain
    previous_hash=blockchain.hash(last_block)
    block=blockchain.newBlock(proof, previous_hash)

    response = {
        'message'       :"New Block Forged",
        'index'         :block['index'],
        'transactions'  :block['transactions'],
        'proof'         :block['proof'],
        'previous_hash' :block['previous_hash'],
    }

    return jsonify(response), 200
    


@app.route('/transactions/new', methods=['POST'])
# A request for transaction will look like
#  {
#   "sender"    : "my_address",
#   "recipient" : "someone else's address",
#   "amount"    : 5,
#  }
def new_transaction():
    vlaues = request.get_json()

    # Check if the required field are given in the request
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # create new transaction
    index = blockchain.new_transaction(vlaues['sender'], vlaues['recipient'], vlaues['amount'])

    response = {'message' : f'Transaction will be added to Block {index}'}
    return jsonify(response), 201




@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain' : blockchain.chain,
        'length' : len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)