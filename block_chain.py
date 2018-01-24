import hashlib
import json
from time import time


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

# Block 
# Each block has properties like index, timestamp, a list of transactions, proof, hash of the previous block

