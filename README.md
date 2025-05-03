# BotFighters Arena

Our version of the project implements a 2D arena with a labyrinth.
In this you can either move yourself or our DummyAgend.
The aim is to collect as many points as possible.
This is done by collecting coins or shooting enemies.
But the enemies will also shoot at you!
Each enemy killed leads to 2 new ones, making the game increasingly difficult.

If you control the ship yourself:
Arrow keys:       up (accelerate), 
                  right/left: turn
Space bar: shoot


## File Descriptions

* **`engine.py`**:
    * This file contains the core game logic using Pygame.
    * It defines the `SpaceObject` (ships), `Bullet`, and `GameEngine` classes.
    * Handles ship movement, physics, collisions, bullet mechanics, and the main game loop.
    * Implements the labyrinth, coin generation, and drawing routines.
    * Provides functionality to run the game in either player or agent-controlled mode.

* **`dummy_agent.py`**:
    * This file defines a basic agent (`DummyAgent`) that controls a ship.
    * The agent can rotate, thrust, and shoot.
    * It includes simple logic for enemy detection (using a laser), wall avoidance, and basic combat.
    * This agent serves as an example and can be replaced with more sophisticated AI.

* **`agent_process.py`**:
    * This script connects the `DummyAgent` to a server (`server.py`).
    * It retrieves the game state from the server,  passes it to the agent to get actions, and sends those actions back to the server.
    * This enables the agent to operate independently of the Pygame visualization.

* **`server.py`**:
    * This file sets up a FastAPI server.
    * It defines API endpoints for:
        * `/game_state`:  Returns the current state of the game (ship positions, wall locations).  *(Note:  Currently returns a static example.)*
        * `/decide/`:  Receives the game state and sends it to the `DummyAgent` to get the agent's actions.
    * This server acts as a communication layer between the game engine and external agents.

## Instructions for Use

1.  **Dependencies:**
    * Make sure you have Python 3.x installed.
    * Install the necessary Python packages:
        ```bash
        pip install pygame requests fastapi uvicorn
        ```

2.  **Running the Server:**
    * Open a terminal and navigate to the directory containing the files.
    * Start the FastAPI server:
        ```bash
        uvicorn server:app --reload
        ```
        * The `--reload` flag is helpful for development as it automatically restarts the server when you make changes to `server.py`.
    * The server will typically run at `http://localhost:8000`.

3.  **Running the Game Engine:**
    * In a separate terminal, run the game engine:
        ```bash
        python engine.py
        ```
    * A Pygame window will open, displaying the game.
    * You'll be presented with a start menu:
        * Press 'P' to play as player
        * Press 'A' to watch the dummy agent play
        * Press 'Q' to quit

4.  **Running the Agent Process (Optional, for external agents):**
    * If you want to run the `DummyAgent` (or your own agent) in a separate process:
        ```bash
        python agent_process.py
        ```
        * This script will continuously communicate with the server to get the game state and send back agent actions.
        * Ensure the server is running before starting this.
