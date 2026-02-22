import random
from utils.config import ARMY_COMPOSITION
from engine.piece import Piece
from utils.constants import PieceRank, Team, GameState

class AutoSetup:
    """
    Handles the automated deployment of pieces on the board.
    Acts as a pre-game AI assistant.
    """
    def __init__(self, logic):
        self.logic = logic
        self.board = logic.board

    def deploy_all(self):
        """Public method to deploy both armies using smart heuristics."""
        self._smart_setup_team(Team.RED)
        self._smart_setup_team(Team.BLUE)
        self.logic.game_state = GameState.IN_PROGRESS
        print("✅ Smart Auto-setup complete! Armies are deployed strategically by AI.")

    def _smart_setup_team(self, team: Team):
        """Deploys a single team strategically."""
        # 1. Define territory boundaries based on the team
        rows = [0, 1, 2, 3] if team == Team.RED else [6, 7, 8, 9]
        back_row = 0 if team == Team.RED else 9
        forward_dir = 1 if team == Team.RED else -1

        available_pos = [(x, y) for x in range(self.board.size) for y in rows]

        def place(rank, pos):
            self.board.place_piece(Piece(rank, team), pos[0], pos[1])
            available_pos.remove(pos)

        # 2. Place Flag in the back row
        flag_pos = (random.randint(0, self.board.size - 1), back_row)
        place(PieceRank.FLAG, flag_pos)

        # 3. Protect Flag with Bombs
        bombs_to_place = ARMY_COMPOSITION['BOMB']
        protect_candidates = [
            (flag_pos[0] - 1, back_row),
            (flag_pos[0] + 1, back_row),
            (flag_pos[0], back_row + forward_dir)
        ]

        for pos in protect_candidates:
            if pos in available_pos and bombs_to_place > 0:
                place(PieceRank.BOMB, pos)
                bombs_to_place -= 1

        for _ in range(bombs_to_place):
            back_slots = [p for p in available_pos if p[1] in [back_row, back_row + forward_dir]]
            if back_slots:
                place(PieceRank.BOMB, random.choice(back_slots))
            else:
                place(PieceRank.BOMB, random.choice(available_pos))

        # 4. Deploy Scouts and Miners
        front_rows = [rows[2], rows[3]]
        for rank_name in ['SCOUT', 'MINER']:
            for _ in range(ARMY_COMPOSITION[rank_name]):
                front_slots = [p for p in available_pos if p[1] in front_rows]
                if front_slots:
                    place(PieceRank[rank_name], random.choice(front_slots))
                else:
                    place(PieceRank[rank_name], random.choice(available_pos))

        # 5. Fill the rest of the board
        remaining_ranks = []
        for rank_name, count in ARMY_COMPOSITION.items():
            if rank_name not in ['FLAG', 'BOMB', 'SCOUT', 'MINER']:
                remaining_ranks.extend([PieceRank[rank_name]] * count)

        random.shuffle(remaining_ranks)
        for rank in remaining_ranks:
            place(rank, random.choice(available_pos))