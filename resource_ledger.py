import hashlib
import time
import json
from typing import Dict, List
import logging
from collections import OrderedDict

class ResourceBlock:
    def __init__(self, timestamp, transactions, previous_hash):
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class ResourceLedger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.chain = []
        self.pending_transactions = []
        self._create_genesis_block()
        
    def _create_genesis_block(self):
        genesis_block = ResourceBlock(
            timestamp=time.time(),
            transactions=[],
            previous_hash="0"
        )
        self.chain.append(genesis_block)

    def add_transaction(self, transaction: Dict) -> bool:
        try:
            self.pending_transactions.append({
                'timestamp': time.time(),
                'resource': transaction['resource'],
                'amount': transaction['amount'],
                'source': transaction['source'],
                'destination': transaction['destination']
            })
            return True
        except Exception as e:
            self.logger.error(f"Failed to add transaction: {str(e)}")
            return False

    def mine_block(self) -> Dict:
        try:
            if not self.pending_transactions:
                return {'status': 'no_transactions'}

            new_block = ResourceBlock(
                timestamp=time.time(),
                transactions=self.pending_transactions,
                previous_hash=self.chain[-1].hash
            )
            
            self.chain.append(new_block)
            self.pending_transactions = []
            
            return {
                'status': 'success',
                'block_hash': new_block.hash,
                'transactions_count': len(new_block.transactions)
            }
        except Exception as e:
            self.logger.error(f"Block mining failed: {str(e)}")
            raise

    def get_resource_history(self, resource_id: str) -> List[Dict]:
        history = []
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.get('resource') == resource_id:
                    history.append({
                        'timestamp': transaction['timestamp'],
                        'amount': transaction['amount'],
                        'block_hash': block.hash
                    })
        return history

    def verify_chain(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            if current.previous_hash != previous.hash:
                return False
            if current.hash != current._calculate_hash():
                return False
        return True