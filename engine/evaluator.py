from openai import OpenAI
from engine.engine import Engine
import math

CONTINUATION_RANGE = 2

def semantic_tree_search(current_position,previous_position, last_move, threshold=2, top_k=8):
    
    #Main logic of backend, we want to search through variations from current position depending on evaluation (Default to 3 in mate situations)
    #Iterate through variations based off of threshold (max 5), find continuations for each of the variations, and then use LLM analysis to summarize 
    #the above continuations. Then finally produce semantic reasoning of the position. 


    #First, we want to know how the current move changed the 
    engine = Engine()

    current_move_analysis = engine.analyze_current_move(current_position, previous_position, last_move)


    #Tree search throughout variations

    top_k_moves = engine.get_top_moves(top_k)
    best_move_eval= top_k_moves[0]['Centipawn'] / 100


    #Continuation paths from the current position that we want to explore, defined by threshold
    tree_nodes = [move for move in top_k_moves if math.abs(best_move_eval) - (move['Centipawn'] / 100) < threshold]
    if len(tree_nodes) < 5: #Minimum 5 lines
        tree_nodes = top_k_moves(5)



    tree_search_string = "Here are the current top engine responses and the continuations "
    #Second degree continuations
    for i, node in enumerate(tree_nodes):

        tree_search_string += "The " + str(i+1) + " best move from this position is the move " + node['Move'] + " with an evaluation of " + str(node['Centipawn'] / 100) + " centipawns"
        tree_search_string += "the top continuations from this move are the following "                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
        engine.make_moves_from_current_position(node['Move'])

        for i in CONTINUATION_RANGE: #How long we want to go down each continuation range
            #Make the next top 5 move in the engine (can be fuzzy)
            current_best_move = engine.get_top_moves(1)[0]['Move']
            tree_search_string += current_best_move
            engine.make_moves_from_current_position(current_best_move)

        continuation_evaluation = engine.get_evaluation()

        tree_search_string += "Evaluation from this continuation is " + str(continuation_evaluation)


    return tree_search_string




def gpt_analysis(position, tree_search_string):
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
        
        Keep the analysis concise (3-4 sentences). """

        user_prompt = f"""
        
        Position: {position}

        Top Continuations from here: {tree_search_string}
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