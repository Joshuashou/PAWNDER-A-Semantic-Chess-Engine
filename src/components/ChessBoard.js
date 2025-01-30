import React, { useEffect, useRef, useState } from 'react';
import { Chessground } from 'chessground';
import { Chess } from 'chess.js';
import "../../node_modules/chessground/assets/chessground.base.css";
import "../../node_modules/chessground/assets/chessground.brown.css";
import "../../node_modules/chessground/assets/chessground.cburnett.css";


const ChessBoard = () => {
  const boardRef = useRef(null);
  const chess = useRef(new Chess());
  const [turn, setTurn] = useState('white'); // Track whose turn it is
  const [worker, setWorker] = useState(null); // Stockfish worker for engine analysis. 

  useEffect(() => {
    const config = {
      fen: chess.current.fen(),
      orientation: 'white',
      turnColor: turn, // Highlight the current player's turn
      movable: {
        color: turn, // Only allow the current player to move
        free: false,
        dests: getDests(),
        events: {
          after: (orig, dest) => {
            console.log('Move attempted:', { from: orig, to: dest });

            // Attempt to make the move
            const move = chess.current.move({ from: orig, to: dest, promotion: 'q' });

            // If the move is illegal, revert it
            if (move === null) {
              console.log('Invalid move');
              return 'snapback';
            }

            console.log('Move result:', move);

            // Update the board position
            ground.set({ fen: chess.current.fen() });

            // Switch turns
            setTurn(chess.current.turn() === 'w' ? 'white' : 'black');

            // Check for game over conditions
            if (chess.current.isGameOver()) {
              if (chess.current.isCheckmate()) {
                alert(`Checkmate! ${chess.current.turn() === 'w' ? 'Black' : 'White'} wins!`);
              } else if (chess.current.isStalemate()) {
                alert('Stalemate! The game is a draw.');
              } else if (chess.current.isThreefoldRepetition()) {
                alert('Draw by threefold repetition.');
              } else if (chess.current.isInsufficientMaterial()) {
                alert('Draw due to insufficient material.');
              }
            }
          }
        }
      },
      highlight: {
        lastMove: true, // Highlight the last move
        check: true // Highlight the king in check
      }
    };

    const stockfish = new Worker('/workers/stockfishWorker.js');
    setWorker(stockfish);

    stockfish.postMessage({type: 'start' });


    function getDests() {
        const dests = new Map(); 
        chess.current.moves({ verbose:true }).forEach(move => {
            if (!dests.has(move.from)) dests.set(move.from, []);
            dests.get(move.from).push(move.to);
        })
        return dests;
    }

    const ground = Chessground(boardRef.current, config);

    return () => {
      ground.destroy();
    };
  }, [turn]); // Re-run effect when the turn changes

  return <div ref={boardRef} style={{ width: '400px', height: '400px' }}></div>;
};

export default ChessBoard;