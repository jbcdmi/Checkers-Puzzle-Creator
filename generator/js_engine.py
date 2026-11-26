# generator/js_engine.py

JS_ENGINE_CONTENT = r'''
/**
 * CHECKERS PUZZLE LEVEL CREATOR - SIMPLE CORE ENGINE & EVALUATOR
 */
"use strict";

const CONSTANTS = {
  STORAGE_KEY: "CHECKERS_SIMPLE_CREATOR_V1",
  
  PIECE_TYPES: {
    RED_NORMAL: "RED_NORMAL",
    RED_KING: "RED_KING",
    BLACK_NORMAL: "BLACK_NORMAL",
    BLACK_KING: "BLACK_KING"
  },

  DIFFICULTIES: ["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"],

  CHALLENGE_TYPES: [
    { type: "CAPTURE_COUNT", label: "Capture X Pieces", defaultTarget: 2, defaultMoves: 3, hasTarget: true },
    { type: "WIN_IN_X_MOVES", label: "Win in X Moves", defaultTarget: 1, defaultMoves: 6, hasTarget: false },
    { type: "MAKE_KINGS", label: "Make X Kings", defaultTarget: 1, defaultMoves: 3, hasTarget: true },
    { type: "CAPTURE_ALL_OPPONENTS", label: "Capture All Opponents", defaultTarget: 0, defaultMoves: 8, hasTarget: false },
    { type: "WIN_NO_LOSS", label: "Win Without Losing Pieces", defaultTarget: 1, defaultMoves: 5, hasTarget: false },
    { type: "CAPTURE_KING", label: "Capture Opponent King", defaultTarget: 1, defaultMoves: 4, hasTarget: true },
    { type: "SURVIVE_MOVES", label: "Survive X Moves", defaultTarget: 4, defaultMoves: 4, hasTarget: true }
  ],

  // SIMPLE SAMPLE LEVELS WITH COMPACT BOARD ARRAY FORMAT
  // STRICTLY NO: schemaVersion, name, ruleset, player, solutionSequences, settings, tags, metadata
  DEFAULT_LEVELS: [
    {
      levelId: "CHK_001",
      difficulty: "BEGINNER",
      boardSize: 8,
      board: [
        { pIndex: 1, isKing: false, pos: [3, 0] },
        { pIndex: 1, isKing: false, pos: [3, 6] },
        { pIndex: 0, isKing: true,  pos: [5, 6] },
        { pIndex: 0, isKing: false, pos: [7, 2] },
        { pIndex: 0, isKing: false, pos: [7, 4] }
      ],
      challenge: {
        type: "CAPTURE_COUNT",
        target: 1,
        moveLimit: 2
      }
    },
    {
      levelId: "CHK_002",
      difficulty: "BEGINNER",
      board: [
        { pIndex: 0, isKing: false, pos: [6, 1] },
        { pIndex: 1, isKing: false, pos: [5, 2] },
        { pIndex: 1, isKing: false, pos: [3, 4] }
      ],
      challenge: {
        type: "CAPTURE_COUNT",
        target: 2,
        moveLimit: 2
      }
    },
    {
      levelId: "CHK_003",
      difficulty: "INTERMEDIATE",
      board: [
        { pIndex: 0, isKing: false, pos: [2, 3] },
        { pIndex: 1, isKing: false, pos: [1, 4] },
        { pIndex: 1, isKing: true,  pos: [3, 6] }
      ],
      challenge: {
        type: "MAKE_KINGS",
        target: 1,
        moveLimit: 2
      }
    },
    {
      levelId: "CHK_004",
      difficulty: "INTERMEDIATE",
      board: [
        { pIndex: 0, isKing: true,  pos: [6, 1] },
        { pIndex: 1, isKing: false, pos: [4, 3] },
        { pIndex: 1, isKing: false, pos: [2, 5] }
      ],
      challenge: {
        type: "CAPTURE_COUNT",
        target: 2,
        moveLimit: 2
      }
    },
    {
      levelId: "CHK_005",
      difficulty: "ADVANCED",
      board: [
        { pIndex: 0, isKing: false, pos: [5, 2] },
        { pIndex: 0, isKing: false, pos: [6, 3] },
        { pIndex: 1, isKing: false, pos: [4, 5] },
        { pIndex: 1, isKing: false, pos: [3, 4] },
        { pIndex: 1, isKing: true,  pos: [2, 3] }
      ],
      challenge: {
        type: "CAPTURE_ALL_OPPONENTS",
        target: 0,
        moveLimit: 4
      }
    },
    {
      levelId: "CHK_006",
      difficulty: "EXPERT",
      boardSize: 10,
      board: [
        { pIndex: 0, isKing: true,  pos: [8, 1] },
        { pIndex: 0, isKing: false, pos: [7, 4] },
        { pIndex: 1, isKing: false, pos: [5, 4] },
        { pIndex: 1, isKing: false, pos: [3, 6] },
        { pIndex: 1, isKing: true,  pos: [2, 7] }
      ],
      challenge: {
        type: "CAPTURE_COUNT",
        target: 3,
        moveLimit: 3
      }
    }
  ]
};

/**
 * STANDARD CHECKERS ENGINE
 */
class CheckersEngine {
  static isPlayable(r, c) {
    return (r + c) % 2 === 1;
  }

  static getAlgebraic(r, c, totalRows) {
    const colLetter = String.fromCharCode(65 + c);
    const rowNum = totalRows - r;
    return `${colLetter}${rowNum}`;
  }

  static getPieceColor(piece) {
    if (!piece) return null;
    return piece.startsWith("RED") ? "RED" : "BLACK";
  }

  static isKing(piece) {
    return piece === "RED_KING" || piece === "BLACK_KING";
  }

  static cloneBoard(squares) {
    return squares.map(sq => ({ row: sq.row, column: sq.column, piece: sq.piece }));
  }

  static getPieceMap(squares) {
    const map = new Map();
    for (const sq of squares) {
      if (sq.piece) {
        map.set(`${sq.row},${sq.column}`, sq.piece);
      }
    }
    return map;
  }

  /**
   * Generates all legal moves for playerTurn under standard rules (mandatory capture).
   */
  static getAllLegalMoves(squares, totalRows = 8, totalCols = 8, playerTurn = "RED", mandatory = true) {
    const pieceMap = this.getPieceMap(squares);

    let allJumps = [];
    let allSteps = [];

    for (const sq of squares) {
      if (!sq.piece) continue;
      const pieceColor = this.getPieceColor(sq.piece);
      if (pieceColor !== playerTurn) continue;

      const pieceJumps = this.getJumpsForPiece(sq.row, sq.column, sq.piece, pieceMap, totalRows, totalCols);
      if (pieceJumps.length > 0) {
        allJumps.push(...pieceJumps);
      }
      const pieceSteps = this.getStepsForPiece(sq.row, sq.column, sq.piece, pieceMap, totalRows, totalCols);
      if (pieceSteps.length > 0) {
        allSteps.push(...pieceSteps);
      }
    }

    // Mandatory capture rule
    if (mandatory && allJumps.length > 0) {
      return allJumps;
    }

    return [...allJumps, ...allSteps];
  }

  static getStepsForPiece(r, c, piece, pieceMap, totalRows, totalCols) {
    const steps = [];
    const color = this.getPieceColor(piece);
    const isKingPiece = this.isKing(piece);
    const forwardR = (color === "RED") ? -1 : 1;

    const directions = isKingPiece ? [[-1, -1], [-1, 1], [1, -1], [1, 1]] : [[forwardR, -1], [forwardR, 1]];

    for (const [dr, dc] of directions) {
      const nr = r + dr;
      const nc = c + dc;
      if (nr >= 0 && nr < totalRows && nc >= 0 && nc < totalCols) {
        if (!pieceMap.has(`${nr},${nc}`) && this.isPlayable(nr, nc)) {
          steps.push({
            from: { row: r, column: c },
            to: { row: nr, column: nc },
            piece: piece,
            player: color,
            captured: [],
            isJump: false,
            notation: `${this.getAlgebraic(r, c, totalRows)}-${this.getAlgebraic(nr, nc, totalRows)}`
          });
        }
      }
    }

    return steps;
  }

  static getJumpsForPiece(r, c, piece, pieceMap, totalRows, totalCols) {
    const color = this.getPieceColor(piece);
    const isKingPiece = this.isKing(piece);
    const forwardR = (color === "RED") ? -1 : 1;

    let jumpDirections = isKingPiece ? [[-1, -1], [-1, 1], [1, -1], [1, 1]] : [[forwardR, -1], [forwardR, 1]];
    const allChains = [];

    const findJumpsRecursive = (currR, currC, currPiece, visitedCaptures, path) => {
      let foundNext = false;
      const currIsKing = this.isKing(currPiece);
      let dirs = currIsKing ? [[-1, -1], [-1, 1], [1, -1], [1, 1]] : jumpDirections;

      for (const [dr, dc] of dirs) {
        const midR = currR + dr;
        const midC = currC + dc;
        const landR = currR + 2 * dr;
        const landC = currC + 2 * dc;

        if (landR >= 0 && landR < totalRows && landC >= 0 && landC < totalCols) {
          const midKey = `${midR},${midC}`;
          const landKey = `${landR},${landC}`;

          if (pieceMap.has(midKey)) {
            const enemyPiece = pieceMap.get(midKey);
            if (this.getPieceColor(enemyPiece) !== color && !visitedCaptures.some(v => v.row === midR && v.column === midC)) {
              const isLandEmpty = !pieceMap.has(landKey) || (landR === r && landC === c);
              if (isLandEmpty && this.isPlayable(landR, landC)) {
                foundNext = true;
                let nextPiece = currPiece;
                if (!currIsKing && landR === ((color === "RED") ? 0 : totalRows - 1)) {
                  nextPiece = (color === "RED") ? "RED_KING" : "BLACK_KING";
                }
                findJumpsRecursive(landR, landC, nextPiece, [...visitedCaptures, { row: midR, column: midC, piece: enemyPiece }], [...path, { row: landR, column: landC }]);
              }
            }
          }
        }
      }

      if (!foundNext && visitedCaptures.length > 0) {
        const finalDest = path[path.length - 1];
        let notation = `${CheckersEngine.getAlgebraic(r, c, totalRows)}`;
        for (const cap of visitedCaptures) {
          notation += ` x ${CheckersEngine.getAlgebraic(cap.row, cap.column, totalRows)}`;
        }
        allChains.push({
          from: { row: r, column: c },
          to: finalDest,
          piece: piece,
          player: color,
          captured: visitedCaptures,
          isJump: true,
          notation: notation
        });
      }
    };

    findJumpsRecursive(r, c, piece, [], []);
    return allChains;
  }

  static applyMove(squares, move, totalRows = 8) {
    const newSquares = this.cloneBoard(squares);
    const color = move.player;

    const startIdx = newSquares.findIndex(sq => sq.row === move.from.row && sq.column === move.from.column);
    let movingPiece = move.piece;
    if (startIdx !== -1) {
      movingPiece = newSquares[startIdx].piece;
      newSquares.splice(startIdx, 1);
    }

    for (const cap of move.captured) {
      const capIdx = newSquares.findIndex(sq => sq.row === cap.row && sq.column === cap.column);
      if (capIdx !== -1) {
        newSquares.splice(capIdx, 1);
      }
    }

    let isPromotion = false;
    const promoRow = (color === "RED") ? 0 : totalRows - 1;
    if (!this.isKing(movingPiece) && move.to.row === promoRow) {
      movingPiece = (color === "RED") ? "RED_KING" : "BLACK_KING";
      isPromotion = true;
    }

    const destIdx = newSquares.findIndex(sq => sq.row === move.to.row && sq.column === move.to.column);
    if (destIdx !== -1) newSquares.splice(destIdx, 1);

    newSquares.push({ row: move.to.row, column: move.to.column, piece: movingPiece });

    return { newSquares, captured: move.captured, isPromotion, resultingPiece: movingPiece };
  }

  static evaluateGameState(squares, totalRows = 8, playerOnTurn = "RED") {
    let redCount = 0;
    let blackCount = 0;

    for (const sq of squares) {
      if (sq.piece) {
        if (sq.piece.startsWith("RED")) redCount++;
        else if (sq.piece.startsWith("BLACK")) blackCount++;
      }
    }

    if (redCount === 0) return { winner: "BLACK", reason: "Red has no pieces left" };
    if (blackCount === 0) return { winner: "RED", reason: "Black has no pieces left" };

    const legalMoves = this.getAllLegalMoves(squares, totalRows, totalRows, playerOnTurn);
    if (legalMoves.length === 0) {
      const winner = (playerOnTurn === "RED") ? "BLACK" : "RED";
      return { winner, reason: `${playerOnTurn} has no legal moves` };
    }

    return { winner: null };
  }

  static getBestAIMove(squares, totalRows = 8, player = "BLACK") {
    const legalMoves = this.getAllLegalMoves(squares, totalRows, totalRows, player);
    if (legalMoves.length === 0) return null;

    legalMoves.sort((a, b) => {
      const capA = a.captured ? a.captured.length : 0;
      const capB = b.captured ? b.captured.length : 0;
      if (capB !== capA) return capB - capA;

      const isKingA = CheckersEngine.isKing(a.piece) ? 1 : 0;
      const isKingB = CheckersEngine.isKing(b.piece) ? 1 : 0;
      return isKingB - isKingA;
    });

    return legalMoves[0];
  }
}

/**
 * SIMPLE CHALLENGE EVALUATOR
 */
class ChallengeEvaluator {
  static evaluate(challenge, gameState) {
    if (!challenge) {
      return { satisfied: true, failed: false, progress: 1.0, label: "No Objective" };
    }

    const type = challenge.type || "CAPTURE_COUNT";
    const target = challenge.target !== undefined ? challenge.target : 1;
    const moveLimit = challenge.moveLimit || 0;
    const movesTaken = gameState.movesTaken || 0;

    let currentVal = 0;
    let satisfied = false;
    let label = "";

    switch (type) {
      case "WIN_IN_X_MOVES":
        satisfied = gameState.winner === "RED";
        currentVal = satisfied ? 1 : 0;
        label = `Win Game (${satisfied ? "Victory!" : "In Progress"})`;
        break;

      case "CAPTURE_COUNT":
        currentVal = gameState.capturesByRed || 0;
        satisfied = currentVal >= target;
        label = `Capture Pieces (${currentVal}/${target})`;
        break;

      case "MAKE_KINGS":
        currentVal = gameState.kingsMadeByRed || 0;
        satisfied = currentVal >= target;
        label = `Crown Kings (${currentVal}/${target})`;
        break;

      case "CAPTURE_ALL_OPPONENTS":
        currentVal = gameState.currentPiecesBlack || 0;
        satisfied = currentVal === 0;
        label = `Opponents Remaining: ${currentVal}`;
        break;

      case "WIN_NO_LOSS":
        const lost = (gameState.initialPiecesRed || 0) - (gameState.currentPiecesRed || 0);
        satisfied = (gameState.winner === "RED") && (lost === 0);
        label = `Win Without Loss (Lost: ${lost})`;
        break;

      case "CAPTURE_KING":
        currentVal = gameState.kingsCapturedByRed || 0;
        satisfied = currentVal >= target;
        label = `Capture Opponent Kings (${currentVal}/${target})`;
        break;

      case "SURVIVE_MOVES":
        currentVal = movesTaken;
        satisfied = (currentVal >= target) && ((gameState.currentPiecesRed || 0) > 0);
        label = `Survive Moves (${currentVal}/${target})`;
        break;

      default:
        satisfied = gameState.winner === "RED";
        label = "Win Puzzle";
        break;
    }

    let isFailed = false;
    let failReason = "";

    if (type === "WIN_NO_LOSS") {
      const lost = (gameState.initialPiecesRed || 0) - (gameState.currentPiecesRed || 0);
      if (lost > 0) {
        isFailed = true;
        failReason = "You lost a piece!";
      }
    }

    if (!isFailed && moveLimit > 0 && movesTaken >= moveLimit && !satisfied) {
      isFailed = true;
      failReason = `Move limit reached (${movesTaken}/${moveLimit} moves)`;
    }

    if (gameState.winner === "BLACK") {
      isFailed = true;
      failReason = "Opponent eliminated all Red pieces or forced stalemate";
    }

    let progress = 0;
    if (target > 0) {
      progress = Math.min(1.0, currentVal / target);
    } else {
      progress = satisfied ? 1.0 : 0.0;
    }

    return { satisfied, failed: isFailed, failReason, progress, label };
  }
}
'''
