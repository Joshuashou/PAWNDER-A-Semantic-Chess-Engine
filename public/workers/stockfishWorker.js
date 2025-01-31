// stockfishWorker.js
importScripts('https://cdn.jsdelivr.net/npm/stockfish.js@10/stockfish.js');
self.onmessage = (event) => {
  const { type, payload } = event.data;

  if (type === 'start') {
    stockfish.postMessage('uci');
    stockfish.postMessage('isready');
  } else if (type === 'position') {
    stockfish.postMessage(`position fen ${payload.fen}`);
  } else if (type === 'go') {
    stockfish.postMessage('go depth 15');
  }
};

stockfish.onmessage = (event) => {
  const message = event.data;

  if (message.startsWith('bestmove')) {
    const bestmove = message.split(' ')[1];
    self.postMessage({ type: 'bestmove', payload: { bestmove } });
  }
};