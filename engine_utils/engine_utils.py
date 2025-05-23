piece_dict = {
    'p': 'pawn',
    'r': 'rook', 
    'n': 'knight',
    'b': 'bishop',
    'q': 'queen',
    'k': 'king'
}


def piece_lookup(fen, move_string):
    """
    Finds the piece of a move from the FEN and move string

    r1bqkbnr/pppp1ppp/2n5/4p3/4PP2/2N5/PPPP2PP/R1BQKBNR

    A1 piece look up gives rook
    
    """
    # Parse the FEN string to get the board state
    board = fen.split(' ')[0]
    
    # Convert FEN to 2D array
    board_array = []
    rows = board.split('/')
    for row in rows:
        board_row = []
        for char in row:
            if char.isdigit():
                # Expand empty squares
                board_row.extend([''] * int(char))
            else:
                board_row.append(char)
        board_array.append(board_row)

    row, column = move_string[0], move_string[1]
    
    # Get source coordinates from algebraic notation
    file_idx = ord(row.lower()) - ord('a')  # Convert a-h to 0-7
    rank_idx = 8 - int(column)  # Convert 1-8 to 0-7 (inverted)
    
    # Get piece from board position and convert to full name
    piece_char = board_array[rank_idx][file_idx].lower()
    piece = piece_dict.get(piece_char, 'unknown')
    
    return piece
    
