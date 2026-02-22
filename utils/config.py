# --- Board Settings ---
BOARD_SIZE = 10

""" Maximum time (in seconds) a player has to make a move."""
TURN_TIME_LIMIT = 30

"""How many turns must pass before the 3x3 cloud event is triggered."""
CLOUD_TRIGGER_INTERVAL = 5
"""Duration (in turns) the cloud stays on the board."""
CLOUD_DURATION = 3
"""Dimension of the storm cloud (3x3)."""
CLOUD_SIZE = 3

"""These will be used to populate the army in the setup phase."""
ARMY_COMPOSITION = {
    'MARSHAL' : 1,
    'GENERAL' : 1,
    'COLONEL' : 2,
    'MAJOR' : 3,
    'CAPTAIN' : 4,
    'LIEUTENANT' : 4,
    'SERGEANT' : 4,
    'MINER' : 5,
    'SCOUT' : 8,
    'SPY' : 1,
    'BOMB' : 6,
    'FLAG' : 1
}