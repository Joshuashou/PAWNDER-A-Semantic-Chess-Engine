import { useEffect, useRef, useCallback, useState } from "react";

const useStockfishEngine = ({ onEvaluation }) => {
    const engineRef = useRef(null);
    const onEvaluationRef = useRef(onEvaluation);
    const isReadyRef = useRef(false);
    const [analysisLines, setAnalysisLines] = useState([]);

    // Keep callback updated
    useEffect(() => {
        onEvaluationRef.current = onEvaluation;
    }, [onEvaluation]);

    useEffect(() => {
        console.log("Initializing Stockfish engine");
        const stockfish = new Worker("/workers/stockfish-16.1.js"); // Updated path
        engineRef.current = stockfish;

        // Use worker.onmessage to handle Stockfish responses
        stockfish.onmessage = (event) => {
            const data = event.data;
            console.log("[Stockfish] Received:", data);

            if (data === "uciok") {
                console.log("Stockfish UCI ready");
                isReadyRef.current = true;
                // Configure engine
                stockfish.postMessage("setoption name MultiPV value 5");
                stockfish.postMessage("setoption name UCI_ShowWDL value false");
                stockfish.postMessage("isready");
            }
            else if (data === "readyok") {
                console.log("Stockfish ready");
            }
            else if (data.startsWith("info")) {
                // Parse best moves here
                const analysis_line = parseInfoLine(data);
                console.log("Analysis line:", analysis_line);
                if (analysis_line.depth === 15) {
                    setAnalysisLines(prev => [...prev, analysis_line]);
                }
            }
            else if (data.startsWith("bestmove")) {
                console.log("Best move received:", data);
                const move = data.split(" ")[1];
                if (move && move !== "(none)") {
                    onEvaluationRef.current([move]);
                }
            }
        };

        // Initialize UCI protocol
        console.log("Starting UCI protocol");
        stockfish.postMessage("uci");

        return () => {
            console.log("Cleaning up Stockfish");
            stockfish.terminate();
        };
    }, []);

    const sendCommand = useCallback((cmd) => {
        if (!engineRef.current || !isReadyRef.current) {
            console.error("Engine not ready");
            return;
        }
        console.log("[Stockfish] Sending command:", cmd);
        engineRef.current.postMessage(cmd);
    }, []);

    return { sendCommand, analysisLines };
};

//Parsing function to analyze stockfish engine results. 
const parseInfoLine = (line) => {
    const tokens = line.split(" ");
    const info = {};
    
    // First check for depth
    const depthIndex = tokens.indexOf("depth");
    if (depthIndex === -1 || Number(tokens[depthIndex + 1]) !== 15) {
        return {};
    }
    
    for (let i = 0; i < tokens.length; i++) {
      switch (tokens[i]) {
        case "depth":
          info.depth = Number(tokens[++i]);
          break;
        case "seldepth":
          info.seldepth = Number(tokens[++i]);
          break;
        case "multipv":
          info.multipv = Number(tokens[++i]);
          break;
        case "score":
          info.scoreType = tokens[++i]; // "cp" or "mate"
          info.score = Number(tokens[++i]);
          break;
        case "nodes":
          info.nodes = Number(tokens[++i]);
          break;
        case "nps":
          info.nps = Number(tokens[++i]);
          break;
        case "hashfull":
          info.hashfull = Number(tokens[++i]);
          break;
        case "time":
          info.time = Number(tokens[++i]);
          break;
        case "pv":
          // Capture the entire principal variation (all subsequent tokens)
          info.pv = tokens.slice(i + 1);
          i = tokens.length; // Exit loop after collecting the PV
          break;
        default:
          // Skip any unhandled tokens
          break;
      }
    }
    return info;
  };
  

export default useStockfishEngine;