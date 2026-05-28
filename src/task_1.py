import hashlib
import time
import json
import os

# ==========================================
# 1. Block Structure
# ==========================================
class Block:
    def __init__(self, index, timestamp, vote_data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.vote_data = vote_data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        # We use json.dumps with sort_keys=True to ensure the dictionary is always converted
        # to a string in the exact same order, preventing accidental hash mismatches.
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.vote_data, sort_keys=True)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()


# ==========================================
# 2. Blockchain Class & Management
# ==========================================
class Blockchain:
    def __init__(self, difficulty=3):
        self.chain = []
        # Pre-registered entities as per requirements
        self.registered_voters = ["VOTER101", "VOTER102", "VOTER103"]
        self.candidates = ["Alice", "Bob", "Charlie"]
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        """Creates the first block of the blockchain with dummy data."""
        genesis_block = Block(0, time.time(), {"voter_id": "NONE", "candidate": "NONE"}, "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)

    def get_latest_block(self):
        return self.chain[-1]

    def validate_vote(self, voter_id, candidate):
        """Simple Voting contract"""
        if voter_id not in self.registered_voters:
            print(f"Rejected: Voter '{voter_id}' is not registered.")
            return False
        
        if candidate not in self.candidates:
            print(f"Rejected: Candidate '{candidate}' does not exist.")
            return False
            
        # Check if voter has already voted by reading the chain
        for block in self.chain:
            if block.vote_data.get("voter_id") == voter_id:
                print(f"Rejected: Voter '{voter_id}' has already cast a vote.")
                return False
                
        return True

    def add_vote(self, voter_id, candidate):
        """Validates the vote and adds a new block to the chain."""
        if self.validate_vote(voter_id, candidate):
            latest_block = self.get_latest_block()
            new_block = Block(
                index=latest_block.index + 1,
                timestamp=time.time(),
                vote_data={"voter_id": voter_id, "candidate": candidate},
                previous_hash=latest_block.hash
            )
            print(f"Mining block {new_block.index}...")
            new_block.mine_block(self.difficulty)
            self.chain.append(new_block)
            print("Vote successfully added to the blockchain!")

    def is_valid(self):
        """Checks the cryptographic integrity of the entire chain."""
        voters_seen = set()
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # 1. Verify that the data wasn't changed (Current Hash check)
            if current_block.hash != current_block.calculate_hash():
                print(f"TAMPERING DETECTED: Block {current_block.index}'s data has been changed!")
                return False

            # 2. Verify the chain link (Previous Hash check)
            if current_block.previous_hash != previous_block.hash:
                print(f"CHAIN BROKEN: Block {current_block.index}'s previous hash doesn't match Block {previous_block.index}!")
                return False

            # 3. Verify no double voting occurred
            voter_id = current_block.vote_data.get("voter_id")
            if voter_id in voters_seen:
                print(f"INVALID STATE: Duplicate vote detected for '{voter_id}'.")
                return False
            voters_seen.add(voter_id)

        print("Blockchain is valid and secure.")
        return True

    def count_votes(self):
        """Tallying the votes."""
        vote_counts = {candidate: 0 for candidate in self.candidates}
        for i in range(1, len(self.chain)):
            candidate = self.chain[i].vote_data.get("candidate")
            if candidate in vote_counts:
                vote_counts[candidate] += 1
        return vote_counts

    def declare_winner(self):
        """Election Result Declaration."""
        counts = self.count_votes()
        if sum(counts.values()) == 0:
            print("No votes have been cast yet.")
            return

        max_votes = max(counts.values())
        winners = [cand for cand, votes in counts.items() if votes == max_votes]

        print("\n --- Election Results --- ")
        for cand, votes in counts.items():
            print(f"{cand}: {votes} votes")

        if len(winners) > 1:
            print(f"\n The election is a TIE between: {', '.join(winners)} (with {max_votes} votes each).")
        else:
            print(f"\n The WINNER is {winners[0]} with {max_votes} votes! ")

    def save_chain(self, filename="blockchain_data.json"):
        """Save Blockchain."""
        chain_data = []
        for block in self.chain:
            chain_data.append({
                "index": block.index,
                "timestamp": block.timestamp,
                "vote_data": block.vote_data,
                "previous_hash": block.previous_hash,
                "hash": block.hash,
                "nonce": block.nonce
            })
        with open(filename, "w") as file:
            json.dump(chain_data, file, indent=4)
        print(f" Blockchain saved permanently to {filename}")

    def load_chain(self, filename="blockchain_data.json"):
        """Load Blockchain."""
        if not os.path.exists(filename):
            print(f" File '{filename}' not found.")
            return
            
        with open(filename, "r") as file:
            chain_data = json.load(file)
            
        self.chain = []
        for data in chain_data:
            block = Block(
                index=data["index"],
                timestamp=data["timestamp"],
                vote_data=data["vote_data"],
                previous_hash=data["previous_hash"],
                nonce=data["nonce"]
            )
            block.hash = data["hash"] # Restore the original hash
            self.chain.append(block)
        print(f" Blockchain loaded from {filename}")


# ==========================================
# 3. Command Line Interface (CLI)
# ==========================================
def main():
    # Initialize our system with a Proof-of-Work difficulty of 3
    voting_system = Blockchain(difficulty=3)
    
    while True:
        print("\n" + "="*30)
        print(" Decentralized Voting System ")
        print("="*30)
        print("1. Register Vote")
        print("2. View Blockchain")
        print("3. Count Votes")
        print("4. Check Chain Validity")
        print("5. Declare Winner")
        print("6. Save Chain to Disk")
        print("7. Load Chain from Disk")
        print("8. Simulate Tampering (Test)")
        print("9. Exit")
        
        choice = input("\nSelect an option (1-9): ")
        
        if choice == "1":
            print("\nValid Voters: VOTER101, VOTER102, VOTER103")
            print("Valid Candidates: Alice, Bob, Charlie")
            voter = input("Enter Voter ID: ").strip()
            candidate = input("Enter Candidate Name: ").strip()
            voting_system.add_vote(voter, candidate)
            
        elif choice == "2":
            print("\n--- Current Blockchain ---")
            for block in voting_system.chain:
                print(f"\n[Block {block.index}]")
                print(f"  Timestamp: {block.timestamp}")
                print(f"  Vote Data: {block.vote_data}")
                print(f"  Prev Hash: {block.previous_hash}")
                print(f"  Curr Hash: {block.hash}")
                print(f"  Nonce:     {block.nonce}")
                
        elif choice == "3":
            print("\n--- Current Vote Count ---")
            counts = voting_system.count_votes()
            for cand, count in counts.items():
                print(f"{cand}: {count} votes")
                
        elif choice == "4":
            print("\n--- Running Security Check ---")
            voting_system.is_valid()
            
        elif choice == "5":
            voting_system.declare_winner()
            
        elif choice == "6":
            voting_system.save_chain()
            
        elif choice == "7":
            voting_system.load_chain()
            
        elif choice == "8":
            if len(voting_system.chain) > 1:
                print("\nHacker activated... Changing candidate in Block 1 to 'Hacker'")
                voting_system.chain[1].vote_data["candidate"] = "Hacker"
                print("Data modified successfully. Run Option 4 to see if the blockchain catches it!")
            else:
                print("\nYou need to add at least one vote before you can tamper with it.")
                
        elif choice == "9":
            print("\nExiting system. Goodbye!")
            break
            
        else:
            print("\nInvalid choice. Please select a number from 1 to 9.")

if __name__ == "__main__":
    main()
