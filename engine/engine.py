from stockfish import Stockfish
import chess
import os

# Initialize Stockfish engine
stockfish = Stockfish(path="/usr/local/bin/stockfish") 



stockfish.set_skill_level(20) 
stockfish.set_depth(15)  # Search depth
stockfish.update_engine_parameters({
    "Hash": 128,
    "Threads": 4 
})
