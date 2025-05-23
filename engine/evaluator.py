from openai import OpenAI
from engine.engine import Engine
import math
import logging

CONTINUATION_RANGE = 4

def semantic_tree_search(current_position, previous_position, last_move, threshold=2, top_k=8):
    
    #Main logic of backend, we want to search through variations from current position depending on evaluation (Default to 3 in mate situations)
    #Iterate through variations based off of threshold (max 5), find continuations for each of the variations, and then use LLM analysis to summarize 
    #the above continuations. Then finally produce semantic reasoning of the position. 


    #First, we want to know how the current move changed the 
    engine = Engine()

    #Tree search throughout variations
    engine.set_position_by_fen(previous_position)
    previous_evaluation = engine.get_evaluation()

    engine.set_position_by_fen(current_position)
    current_evaluation = engine.get_evaluation()

    #Analyze alternatives to current move
    alternative_moves_tree_search_strings = find_continuation_string_from_position(engine, previous_position, threshold, top_k)

    #Analyze how opponent can respond to current move
    last_move_tree_search_string = find_continuation_string_from_position(engine, current_position, threshold, top_k)

    print(f"Alternative moves tree search strings: {alternative_moves_tree_search_strings}")
    print(f"Last move tree search string: {last_move_tree_search_string}")
   
    # Create tasks for each continuation string
    alternative_moves_summarizer = continuation_summarizer(previous_position, last_move, previous_evaluation, current_evaluation, alternative_moves_tree_search_strings, alternative=True)
    last_move_summarizer = continuation_summarizer(current_position, last_move, previous_evaluation, current_evaluation, last_move_tree_search_string, alternative=False)
    

    print(f"Alternative moves summarizer: {alternative_moves_summarizer}")
    print(f"Last move summarizer: {last_move_summarizer}")


    return alternative_moves_summarizer, last_move_summarizer, previous_evaluation, current_evaluation


def find_continuation_string_from_position(engine, position, last_move,threshold=2, top_k=5):
    engine.set_position_by_fen(position)
    top_k_moves = engine.get_top_moves(top_k)
    best_move_eval = top_k_moves[0]['Centipawn'] / 100

    tree_search_strings = []

    tree_nodes = [move for move in top_k_moves if abs(best_move_eval - (move['Centipawn'] / 100)) < threshold]
    if len(tree_nodes) < 5: #Minimum 5 lines
        tree_nodes = top_k_moves[:5]

    tree_search_string = f"Here are the current top engine moves and the continuations "

    #Second degree continuations
    for i, node in enumerate(tree_nodes):
        engine.set_position_by_fen(position)
        engine.make_move(node['Move'])
        position = engine.get_current_position()

        tree_search_string = "The " + str(i+1) + " best move from the current FEN position of " + position + " is the move " + node['Move'] + " with an evaluation of " + str(node['Centipawn'] / 100)
        tree_search_string += "the top continuations from this move are the following "

        for i in range(CONTINUATION_RANGE): #How long we want to go down each continuation range
            #Make the next top 5 move in the engine (can be fuzzy)
            current_best_move = engine.get_top_moves(1)[0]['Move']
            tree_search_string += current_best_move + " "
            engine.make_move(current_best_move)

        tree_search_strings.append(tree_search_string)
    return tree_search_strings


def continuation_summarizer(position, last_move, previous_evaluation, current_evaluation, tree_search_string, alternative=False):
    #Async Function to take in continuations from multiple lines and summarize them into main points and extract 
    #Relevant information that helps the analysis of the initial move. 
    #Since doing different continuations, we can ASYNC generate as they are independent

    client = OpenAI()


    if alternative: #Looking at alternative to last move. 
        print(f"ALT LAST MOVE {last_move}")
        context_string = f"We are currently at position {position} and the player made the following move: {last_move}. The engine evaluation before this move was {previous_evaluation}, and it has now changed to {current_evaluation} Here are the alternatives to this move and the respective continuations: "

    else: #Looking at continuations
        context_string = f"We are currently at position {position} and the last move was {last_move} As a result the engine evaluation is {evaluation}. Here are the continuations from this move: "

    system_prompt = f"""
    You are a semantic chess engine expert. Your role is to analyze input strings that describe engine move evaluations and continuation trees, then provide a clear, human-readable explanation of the position and move quality. For each input, do the following:

    You will be provided a string that describes the current FEN position, the move that was made, and the continuations. You can trust that the continuations/evaluation are from Stockfish and are accurate.
    Identify the list of top continuation moves that follow this move.
    Explain in Human Terms:

    Describe which piece is being moved (using full names like "bishop," "knight," etc.) and from which square to which square.
    Explain the meaning of the evaluation score (e.g., a positive value indicates an advantage for White, a negative value favors Black).
    Comment on why the move might be considered good or bad in context—consider factors such as development, center control, potential weaknesses, and tactical ideas.
    If applicable, mention how the provided continuations support the evaluation (e.g., "The top continuations suggest aggressive counterplay on the queenside" or "These moves help consolidate the position").
    Contextualize the Position:

    Briefly note any relevant features from the FEN position (e.g., missing pawns, advanced central pawns, castling rights).
    Pay attention specifically to whether certain moves are much better or others, as well as emphasis on captures and checks.

    Summarize whether the move improves the position for White or Black, and indicate any strategic or tactical plans hinted at by the continuations.
    For example, format of an output can look something like: (make sure to ground all the variations in the engine evaluation responses, and do not hallucinate)

    "The best move from the current FEN position of is the move pawn from e2 to e4, moving the pawn into the center gives white good development, with a slight advantage of 0.33. 
    The best followup for black is to play pawn c7 to c5 which is the sicilian defense, fighting for control in the center. 
    Another good followup for black is to play pawn g7 to g6 which leads to a bishop exchange and a slight advantage for black. "

    Remember to include piece names, square references, and human-friendly explanations of engine evaluation concepts."""

    user_prompt = context_string + str(tree_search_string)


    continuation_summary_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    return continuation_summary_response.choices[0].message.content.strip()

def gpt_analysis_final(position, last_move, previous_evaluation, current_evaluation, alternative_summarizer, last_move_summarizer):
    """
    Analyze chess position using OpenAI GPT API and return natural language analysis.
    
    Args:
        position (str): Chess position in FEN notation
        
    Returns:
        str: Natural language analysis of the position
    """
    try:
    
        client = OpenAI()
        
        # Default prompt for single position
        system_prompt = f"""
        You are a chess master that knows how to analyze engine positions and let the user know why a certain move is so strong/weak. 
        Analyze this chess position (in FEN notation) and provide a brief natural language analysis 
        focusing on key tactical and strategic elements. You will additionally be given lines from stockfish that are the objective best followups from the position. 
        Pay attention to key moves that a human analysis might have missed, and the main themes of the continuations that may not be completely obvious to the player. 
        
        Most importantly is to not hallucinate! Make sure each piece you mention is specifically on the position you indicated, and each tactic is supported by the position.
        If unsure, do not make bold claims. 

        Pay attention to the evaluation of the position, + is equal to white is ahead by that many points, - is black is ahead by that many points, where Pawn=1, Knight=Bishop=3, Rook=5, Queen=9
        
        Keep the analysis concise (3-4 sentences). 

        Here is an example to demonstrate format of the analysis: 

        The reason the move e5 can be considered a blunder is that it leaves the queen unprotected which then leads to a pin that black can exploit. 
        The continuations from this move are the following: Black bishop to c3, and here no matter what white does black can capture the queen. 
        
        
        """

        user_prompt = f"""
        
        This is the Original Position: {position}

        Your goal is to analyze this move: {last_move}

        Evaluation before move: {previous_evaluation}

        Evaluation after move: {current_evaluation}

        Here is a summary of the continuations from alternative moves to the last move: {alternative_summarizer}. Use this summary to determine if other moves could have been better/worse. 

        Here is the summary of continuations that happen from this move: {last_move_summarizer} Use this summary to describe why the move is good or it could be a mistake. 


        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Extract and return the analysis
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating analysis: {str(e)}"