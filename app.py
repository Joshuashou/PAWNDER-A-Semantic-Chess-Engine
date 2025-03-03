from flask import Flask, render_template, jsonify, request
import chess
import uvicorn
from engine.evaluator import gpt_analysis
from flask_cors import CORS
import logging

app = Flask(__name__)

# Simple CORS configuration
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

logging.basicConfig(level=logging.INFO)
logging.info("Starting server")
game_board = chess.Board()

@app.route('/')
def index():
    # Reset the board when starting a new game
    global game_board
    game_board = chess.Board()
    return render_template('index.html')

@app.route('/pawnder_move', methods=['POST', 'OPTIONS'])
def pawnder_move():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200

    logging.info("Received pawnder_move request")
    try:
        data = request.get_json()
        move = data.get('move')
        position = data.get('position')

        print("Last move: ", move)
        print("Current position: ", position)


        semantic_engine_response = gpt_analysis(position)
        logging.info("Semantic engine response: %s", semantic_engine_response)



        return jsonify({'analysis': semantic_engine_response, 'status': 'OK'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)