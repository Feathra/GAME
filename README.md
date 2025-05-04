
<br>

# <div align="center">“BOTFIGHTERS: Space Duel Arena”</div> 



<div align="center"> Real-time 2D space labyrinth shooter where you pilot a spaceship through waves of enemies. The survival comes down to collecting as many coin as possible, while encountering and shooting the enemies. But the enemies will also shoot at you! As you play, the number of enemies increases, and you’ll need to keep adjusting your strategy. The game focuses on keeping you on your toes and forcing you to think quickly. Each run feels different, and you’ll get better the more you play. Play it yourself, or let the Dummy Agent take control. Are you ready to face the battle and see how long you can last?</div>

<br><br>

   
# <div align="center"> Instruction</div>

<div align="center"> This instruction explains how to install, use, and compete the “BOTFIGHTERS: Space Duel Arena”.</div>




<br><br>






## <div align="center"> 1) System requirements</div>


- Python 3.x+
 
- Python libraries to run the game and the server. These imports require installation via pip:
    * 'pygame' for the game environment.
	 * 'fastapi' for the server-side logic.
	 * 'uvicorn' to serve the FastAPI application.
	 * 'requests' to send HTTP requests.
	 * 'pydantic' for data validation.

To install these, run the following command in the terminal:

```bash
pip install pygame fastapi uvicorn pydantic requests
```
<br>

## <div align="center"> 2) Run the game </div>



-	Ensure you have the following files in the same directory or Python path:
    *	engine.py
    *	minimap.py
    *	dummy_agent.py
    *	server.py
    *	server_demo.html
    *	galaxie.jpg
<br>

-	Start the server (optional):

To start the server, run the following command in the terminal:

```bash
uvicorn server:app --reload
```


If you are using an agent or game state server, ensure it's running at http://localhost:8000.

<br>


-	Run the game (in the 2nd terminal, if the server is started):

```bash
python3 engine.py
```


<br>

-	Run the map (in the 3rd terminal, if the server and game are started):

```bash
python3 minimap.py
```

<br>














### If you control the ship yourself:  

Arrow keys:  
- up: accelerate  
- right/left: turn

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
