# agent_process.py
import requests
import time
import json
from dummy_agent import DummyAgent  # Import the DummyAgent class

SERVER_URL = "http://localhost:8000"  # Adjust if necessary

# Initialize the DummyAgent
agent = DummyAgent(ship_index=0)  # Assuming this agent controls ship 0

def get_game_state():
    try:
        response = requests.get(f"{SERVER_URL}/game_state")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting game state: {e}")
        return None

def send_agent_actions(actions):
    try:
        response = requests.post(f"{SERVER_URL}/decide/", json=actions)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending agent actions: {e}")

def main():
    while True:
        game_state_data = get_game_state()
        if game_state_data:
            try:
                # The server's /game_state endpoint returns a dictionary
                # We need to ensure it matches what the DummyAgent expects.
                # Assuming the keys are 'ships' and 'walls'.
                game_state = game_state_data
                walls = game_state.get("walls", [])  # Extract walls

                # The DummyAgent's decide method expects the full game state dictionary and the list of walls
                actions = agent.decide(game_state, walls)
                send_agent_actions(actions)
                #time.sleep(0.1)  # Optional: Add a small delay
            except Exception as e:
                print(f"Error processing game state or deciding actions: {e}")
                print(traceback.format_exc()) # Good practice to include traceback
        #else:
        #    time.sleep(1) # Wait and retry if game state couldn't be fetched

if __name__ == "__main__":
    import traceback
    main()