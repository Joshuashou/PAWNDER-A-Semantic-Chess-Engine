import { useEffect, useRef, useCallback } from "react";

const useStockfishEngine = ({ onEvaluation }) => {
    const engineRef = useRef(null);
    const onEvaluationRef = useRef(onEvaluation);
    const isReadyRef = useRef(false);

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
                console.log("Analysis info:", data);
                // Parse best moves here
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

    return { sendCommand };
};

export default useStockfishEngine;