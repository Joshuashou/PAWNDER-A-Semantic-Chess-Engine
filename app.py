from flask import Flask, render_template, jsonify, request
import chess
import uvicorn
from engine.evaluator import semantic_tree_search, gpt_analysis_final
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
        previous_position = data.get('previous_position')

        print("Last move: ", move)
        print("Current position: ", position)
        print("Previous position: ", previous_position)

        alternative_summarizer, last_move_summarizer, previous_evaluation, current_evaluation = semantic_tree_search(position,previous_position,move)

        semantic_engine_response = gpt_analysis_final(position, move, previous_evaluation, current_evaluation, alternative_summarizer, last_move_summarizer)
        logging.info("Semantic engine response: %s", semantic_engine_response)

        # The response is already being returned correctly as part of the JSON response
        # The frontend can access it from response.data.analysis
        return jsonify({'analysis': semantic_engine_response, 'status': 'OK'}), 200
    except Exception as e:
        print("Ran into error")
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    #Run server locally with 
    #Use 
    app.run(debug=True, port=5000)          