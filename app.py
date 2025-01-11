from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    move = request.json.get('move')
    # Here you'll add your engine logic later
    return jsonify({
        'validMoves': {}  # You'll calculate valid moves here
    })

if __name__ == '__main__':
    app.run(debug=True)