// public/workers/stockfishWorker.js

// Import the Stockfish engine
importScripts('/stockfish/stockfish.js');

// Initialize the Stockfish engine
const stockfish = Stockfish();

// Handle messages from the main thread
onmessage = function (event) {
  const { type, payload } = event.data;

  switch (type) {
    case 'start':
      stockfish.postMessage('uci');
      break;
    case 'position':
      stockfish.postMessage(`position fen ${payload.fen}`);
      stockfish.postMessage(`go depth ${payload.depth || 15}`);
      break;
    default:
      console.warn('Unknown message type:', type);
  }
};

// Forward messages from Stockfish to the main thread
stockfish.onmessage = function (event) {
  postMessage(event.data);
};
