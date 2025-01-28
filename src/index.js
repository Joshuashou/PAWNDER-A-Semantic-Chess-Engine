import React from "react";
import ReactDOM from "react-dom/client";
import App from "./app";

// Import CSS from chessground package
import "chessground/assets/chessground.base.css";
import "chessground/assets/chessground.brown.css";
import "chessground/assets/chessground.cburnett.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
