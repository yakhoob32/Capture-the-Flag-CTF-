from engine.board import Board
from ai.auto_setup import AutoSetup
from engine.game_logic import GameLogic
from utils.constants import PieceRank, Team, GameState
from ai.ai_bot import AIBot

def main():
    # 1. Initialize the board and the referee
    game_board = Board()
    logic = GameLogic(game_board)

    # 2. Smart Auto-Setup Phase via AI Package
    setup_manager = AutoSetup(logic)
    setup_manager.deploy_all()

    # 3. Initialize the AI Opponent (Playing as BLUE, Level 2)
    ai_opponent = AIBot(Team.BLUE, logic, level=2)

    print("=== Super Stratego Elite: Phase 1 (CLI Version) ===")
    print("Instructions: Enter move as 'start_x start_y end_x end_y' (e.g., 0 3 0 4)")

    # 4. Game Loop
    while True:
        game_board.display_terminal(logic.current_turn)
        print(f"Current Turn: {logic.current_turn.name}")

        # === AI TURN (BLUE) ===
        if logic.current_turn == Team.BLUE:
            import time
            print("🤖 AI is thinking...")
            time.sleep(1)

            ai_move = ai_opponent.get_move()
            if ai_move:
                start_pos, end_pos = ai_move
                logic.execute_move(start_pos, end_pos)
            else:
                print("🏆 AI has no legal moves left! RED WINS!")
                break

        # === PLAYER TURN (RED) ===
        else:
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

                # Validate and Execute
                if logic.validate_move(start_pos, end_pos):
                    logic.execute_move(start_pos, end_pos)

            except ValueError:
                print("Invalid input! Please enter numbers only.")

        # Check for Win Condition after ANY turn
        if logic.game_state == GameState.FINISHED:
            game_board.display_terminal(logic.winner)
            print(f"🏆 CONGRATULATIONS! Team {logic.winner.name} has won the match!")
            break


if __name__ == "__main__":
    main()