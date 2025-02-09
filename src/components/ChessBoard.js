import React, { useEffect, useRef, useState, useCallback } from "react";
import { Chessground } from "chessground";
import { Chess } from "chess.js";
import useStockfishEngine from "./useStockfishEngine";
import "../../node_modules/chessground/assets/chessground.base.css";
import "../../node_modules/chessground/assets/chessground.brown.css";
import "../../node_modules/chessground/assets/chessground.cburnett.css";

const ChessBoard = () => {
  const boardRef = useRef(null);
  const chess = useRef(new Chess());
  const groundRef = useRef(null);
  const [topMoves, setTopMoves] = useState([]);
  const [fen, setFen] = useState(chess.current.fen());
  const turn = chess.current.turn() === 'w' ? 'white' : 'black';
  console.log("Hi")

  const handleEvaluation = useCallback((data) => {
    console.log("handleEvaluation called");
    setTopMoves(parseStockfishOutput(data));
  }, []);

  const { sendCommand, analysisLines } = useStockfishEngine({ onEvaluation: handleEvaluation });

  const getDests = useCallback(() => {
    const dests = new Map();
    chess.current.moves({ verbose: true }).forEach(move => {
      dests.set(move.from, (dests.get(move.from) || []).concat(move.to));
    });
    return dests;
  }, [fen]);

  const handleMove = useCallback((orig, dest) => {
    try {
      const move = chess.current.move({ from: orig, to: dest, promotion: "q" });
      if (!move) return "snapback";
      
      const newFen = chess.current.fen();
      setFen(newFen);
      
      if (sendCommand) {
        console.log("stockfish sending move command");
        sendCommand(`position fen ${newFen}`);
        sendCommand("go depth 15");
      }
    } catch (error) {
      console.error("Move error:", error);
    }
  }, [sendCommand]);

  useEffect(() => {
    groundRef.current = Chessground(boardRef.current, {
      fen,
      turnColor: turn,
      movable: {
        color: turn,
        free: false,
        dests: getDests(),
        events: { after: handleMove }
      },
      highlight: { lastMove: true, check: true }
    });

    return () => groundRef.current?.destroy();
  }, []);

  useEffect(() => {
    groundRef.current?.set({
      fen,
      turnColor: turn,
      movable: { color: turn, dests: getDests() }
    });
  }, [fen, turn, getDests]);

  const parseStockfishOutput = (output) => {
    if (Array.isArray(output)) {
      // If the output is already an array, return it directly
      return output.slice(0, 5);
    }
  
    if (typeof output !== "string") {
      console.error("Invalid output:", output);
      return [];
    }
  
    // Parse the string output
    const matches = [];
    const regex = /pv\s+(\w+)/g;
    let match;
    while ((match = regex.exec(output)) !== null) {
      matches.push(match[1]);
    }
    return matches.slice(0, 5);
  };

  return (
    <div style={{ display: "flex" }}>
        <div ref={boardRef} style={{ width: "400px", height: "400px" }}></div>
        <div style={{ width: "200px", marginLeft: "20px" }}>
            <h3>Top Moves</h3>
            {analysisLines.map((line, index) => (
                <div key={index}>
                    <div>Line {index + 1}:</div>
                    {line.score && (
                        <div>Score: {line.scoreType === 'cp' ? line.score / 100 : `Mate in ${line.score}`}</div>
                    )}
                    {line.pv && <div>Moves: {line.pv.join(' ')}</div>}
                </div>
            ))}
        </div>
    </div>
);
};

export default ChessBoard;