from stockfish import Stockfish
import chess
import os
print(os.getcwd())

class Engine():

    def __init__(self):
        STOCKFISH_PATH = "/opt/homebrew/Cellar/stockfish/17/bin/stockfish"
        self.stockfish = Stockfish(path=STOCKFISH_PATH, depth=15 , parameters={"Threads": 2, "Minimum Thinking Time": 5})

    def set_position_by_fen(self, fen):
        try: #Check Valid fen
            self.stockfish.is_fen_valid(fen)

        except Exception as e:
            print("Invalid FEN sent to stockfish")
            print(e)

        self.stockfish.set_fen_position(fen)


    def get_top_moves(self, n):
        return self.stockfish.get_top_moves(n)
    
    def get_evaluation(self):
        return self.stockfish.get_evaluation()
    
    def get_current_position(self):
        return self.stockfish.get_fen_position()

    def make_move(self, move): #Move is string like "e2e4"
        return self.stockfish.make_moves_from_current_position([move])



if __name__ == '__main__':
    #Run server locally with 
    engine_test = Engine()
    engine_test.make_move("e2e4")
    print(engine_test.get_evaluation())
