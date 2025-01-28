import React, { useState } from "react";
import Chessground from "@react-chess/chessground";

const ChessBoard = () => {
  const [config, setConfig] = useState({
    draggable: { enabled: true },
    movable: {
      free: false,
      color: "white",
    },
  });

  const sendMove = (orig, dest) => {
    fetch("/make_move", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ move: `${orig}${dest}` }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.validMoves) {
          setConfig((prevConfig) => ({
            ...prevConfig,
            movable: { ...prevConfig.movable, dests: new Map(Object.entries(data.validMoves)) },
          }));
        }
      });
  };

  return (
    <Chessground
      width={600}
      height={600}
      config={{
        ...config,
        events: {
          move: sendMove,
        },
      }}
    />
  );
};

export default ChessBoard;
