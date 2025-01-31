import React from "react";
import ReactDOM from "react-dom/client";
// import Chessground from "@react-chess/chessground";
import ChessBoard from "./components/ChessBoard";


// Import CSS from chessground package
import "../node_modules/chessground/assets/chessground.base.css";
import "../node_modules/chessground/assets/chessground.brown.css";
import "../node_modules/chessground/assets/chessground.cburnett.css";

const App = () => {
    return (
      <div>
        <h1>Semantic Chess Engine</h1>
        <ChessBoard />
      </div>
    );
  };

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
