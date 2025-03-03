from openai import OpenAI

def gpt_analysis(position):
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
        prompt = f"""
        Analyze this chess position (in FEN notation) and provide a brief natural language analysis 
        focusing on key tactical and strategic elements. 
        
        Most importantly is to not hallucinate! Make sure each piece you mention is specifically on the position you indicated, and each tactic is supported by the position.
        If unsure, do not make bold claims. 
        
        Keep the analysis concise (2-3 sentences).
        
        Position: {position}
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a chess expert providing brief position analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        
        # Extract and return the analysis
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating analysis: {str(e)}"