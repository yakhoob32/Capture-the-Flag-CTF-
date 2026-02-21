from engine.board import Board
from engine.piece import Piece
from engine.game_logic import GameLogic
from utils.constants import PieceRank, Team


def main():
    # 1. Setup
    game_board = Board()
    logic = GameLogic(game_board)

    # 2. Place pieces for testing
    # Red Scout at (0, 0)
    scout = Piece(PieceRank.SCOUT, Team.RED)
    game_board.place_piece(scout, 0, 0)

    # Blue Bomb at (0, 4) - to block path
    bomb = Piece(PieceRank.BOMB, Team.BLUE)
    game_board.place_piece(bomb, 0, 4)

    print("=== Super Stratego Phase 1 Test ===")

    # 3. Game Loop
    while True:
        game_board.display_terminal(logic.current_turn)
        print(f"Current Turn: {logic.current_turn.name}")

        # Get input (format: x1 y1 x2 y2)
        try:
            user_input = input("Enter move (start_x start_y end_x end_y) or 'q' to quit: ")
            if user_input.lower() == 'q':
                break

            coords = list(map(int, user_input.split()))
            if len(coords) != 4:
                print("Invalid input! Please enter 4 numbers.")
                continue

            start_pos = (coords[0], coords[1])
            end_pos = (coords[2], coords[3])

            # 4. Validate and Execute
            if logic.validate_move(start_pos, end_pos):
                logic.execute_move(start_pos, end_pos)

        except ValueError:
            print("Invalid input! Please enter numbers only.")


if __name__ == "__main__":
    main()