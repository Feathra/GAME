Phase 1 Delivery: Game Simulation Engine + API

Physics Engine: It can be a real-time (recommended: asyncio) or tick-based simulation update loop. You should be able to simulate agent movement (e.g. rotation, thrust...) and collisions (recommended: pymunk).
Game world: 2D arena with obstacles. It may contain walls, pickups, ammo, health....
Game objects: agents and interactive elements (e.g. ships, bullets, mines, shields, pickups, etc.).
Mobile Agent sensors: API exposes data on demand (e.g. radar scan, velocity/angle, agent status...) (recommended: fastAPI).
Mobile Agent actuators: API exposes agent actuation commands (e.g. thrust, fire, dropMine, activateShield).
Dummy Agent: The group should deliver a dummy agent capable of completing the task in the simplest way (e.g. fly randomly and shot if the enemy is detected).
World Visualizer: Real-time 2D graphics (recommended: pygame, arcade).
Demo Launch: Instructions to launch the whole system with copies of the dummy agent and the visualizer.
Installation, usage, and competition instructions. (recommended: github, requirements).
Work Distribution Report.
