from enum import Enum, auto

class Team(Enum) :
    """Represents the two competing sides and an empty state."""
    RED = auto()
    BLUE = auto()
    NONE = auto()

class PieceRank(Enum) :
    """Defines all possible ranks in the game, including special units."""
    MARSHAL = 10
    GENERAL = 9
    COLONEL = 8
    MAJOR = 7
    CAPTAIN = 6
    LIEUTENANT = 5
    SERGEANT = 4
    MINER = 3
    SCOUT = 2
    SPY = 'S'
    BOMB = 'B'
    FLAG = 'F'
    UNKNOWN = '?'

class Command(Enum) :
    """Standardized commands for Client-Server communication and UI events."""
    CONNECT = auto()
    START_GAME = auto()
    SETUP_DONE = auto()

    MOVE = auto()
    ATTACK = auto()
    USE_POWER = auto()

    UPDATE_BOARD = auto()
    BATTLE_RESULT = auto()
    CLOUD_EVENT = auto()
    TURN_TIMEOUT = auto()
    GAME_OVER = auto()

class PowerType(Enum) :
    """Specific types of special abilities (Power Tokens)."""
    RADAR = auto()
    REPAIR = auto()
    MINE_ADD = auto()
    SCOUT_REVEAL = auto()
    DOUBLE_MOVE = auto()

class CellType(Enum) :
    """Categorizes the nature of board tiles for movement and visibility."""
    EMPTY = auto()
    LAKE = auto()
    CLOUD = auto()

class GameState(Enum) :
    """Tracks the current state of the global game loop."""
    WAITING_FOR_PLAYERS = auto()
    SETUP_PHASE = auto()
    IN_PROGRESS = auto()
    FOG_STORM = auto()
    FINISHED = auto()