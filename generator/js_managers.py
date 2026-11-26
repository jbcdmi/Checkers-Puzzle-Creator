# generator/js_managers.py

JS_MANAGERS_CONTENT = r'''
/**
 * CHECKERS SIMPLE LEVEL CREATOR - MANAGERS
 * Handles Storage, History, Validation, and Import/Export
 * Compact Board Export Format:
 * "board": [
 *   { "pIndex": 1, "isKing": false, "pos": [3, 0] },
 *   { "pIndex": 0, "isKing": true,  "pos": [5, 6] }
 * ]
 * STRICTLY STRIPS: schemaVersion, name, ruleset, player, solutionSequences, settings, tags, metadata
 */

class StorageManager {
  /**
   * Serializes squares to compact piece list:
   * [ { pIndex: 0|1, isKing: boolean, pos: [r, c] } ]
   */
  static serializeBoard(squares) {
    if (!Array.isArray(squares)) return [];
    const result = [];
    for (const sq of squares) {
      if (sq && sq.piece) {
        const pIndex = sq.piece.startsWith("RED") ? 0 : 1;
        const isKing = sq.piece === "RED_KING" || sq.piece === "BLACK_KING";
        result.push({
          pIndex: pIndex,
          isKing: isKing,
          pos: [sq.column, sq.row]
        });
      }
    }
    return result;
  }

  /**
   * Parses compact piece list, 2D matrix, or legacy { rows, columns, squares }
   */
  static parseBoard(boardData, configuredRows = 8, configuredCols = 8) {
    if (!boardData) return { rows: configuredRows, columns: configuredCols, squares: [] };

    if (Array.isArray(boardData)) {
      // Check if 2D Matrix (array of arrays)
      if (boardData.length > 0 && Array.isArray(boardData[0])) {
        const rows = boardData.length;
        const cols = boardData[0].length || 8;
        const squares = [];
        for (let r = 0; r < rows; r++) {
          const rowArr = boardData[r];
          if (!Array.isArray(rowArr)) continue;
          for (let c = 0; c < rowArr.length; c++) {
            const cell = rowArr[c];
            if (cell && cell.c) {
              const pIndex = cell.c.pIndex;
              const isKing = !!cell.c.isKing;
              const piece = (pIndex === 0) ? (isKing ? "RED_KING" : "RED_NORMAL") : (isKing ? "BLACK_KING" : "BLACK_NORMAL");
              const posR = (cell.pos && Array.isArray(cell.pos)) ? cell.pos[0] : r;
              const posC = (cell.pos && Array.isArray(cell.pos)) ? cell.pos[1] : c;
              squares.push({ row: posR, column: posC, piece: piece });
            }
          }
        }
        return { rows, columns: cols, squares };
      }

      // Compact 1D Piece List: [ { pIndex: 0, isKing: false, pos: [col, row] } ]
      let maxR = configuredRows - 1;
      let maxC = configuredCols - 1;
      const squares = [];

      for (const item of boardData) {
        if (!item) continue;
        const pos = Array.isArray(item.pos) ? item.pos : [item.column || 0, item.row || 0];
        const c = pos[0];
        const r = pos[1];
        if (r > maxR) maxR = r;
        if (c > maxC) maxC = c;

        const pIndex = (item.pIndex !== undefined) ? item.pIndex : (item.piece && item.piece.startsWith("RED") ? 0 : 1);
        const isKing = !!item.isKing || (item.piece && item.piece.includes("KING"));
        const piece = (pIndex === 0) ? (isKing ? "RED_KING" : "RED_NORMAL") : (isKing ? "BLACK_KING" : "BLACK_NORMAL");

        squares.push({ row: r, column: c, piece: piece });
      }

      let dim = configuredRows || 8;
      if (maxR >= 10 || maxC >= 10) dim = Math.max(dim, 12);
      else if (maxR >= 8 || maxC >= 8) dim = Math.max(dim, 10);

      return { rows: dim, columns: dim, squares };
    }

    if (boardData.squares && Array.isArray(boardData.squares)) {
      return {
        rows: boardData.rows || configuredRows,
        columns: boardData.columns || configuredCols,
        squares: boardData.squares.map(sq => ({
          row: sq.row,
          column: sq.column,
          piece: sq.piece
        }))
      };
    }

    return { rows: configuredRows, columns: configuredCols, squares: [] };
  }

  static extractBoardSize(lvl) {
    if (!lvl) return 8;
    if (typeof lvl.boardSize === "number" && lvl.boardSize >= 6) return lvl.boardSize;
    if (typeof lvl.boardSize === "string") {
      const m = lvl.boardSize.match(/\d+/);
      if (m) return parseInt(m[0], 10);
    }
    if (lvl.board && typeof lvl.board.rows === "number") return lvl.board.rows;
    if (typeof lvl.rows === "number") return lvl.rows;
    return 8;
  }

  static normalizeFirstTurn(val) {
    if (val === 1 || val === "1") return 1;
    if (typeof val === "string") {
      const upper = val.trim().toUpperCase();
      if (upper === "OPPONENT" || upper === "BLACK" || upper === "AI" || upper === "ROBOT") return 1;
    }
    return 0;
  }

  static normalizeRobotMoves(arr) {
    if (!Array.isArray(arr)) return [];
    const out = [];
    for (const m of arr) {
      if (!m || !Array.isArray(m.from) || !Array.isArray(m.to)) continue;
      if (m.from.length < 2 || m.to.length < 2) continue;
      out.push({
        from: [Number(m.from[0]) || 0, Number(m.from[1]) || 0],
        to: [Number(m.to[0]) || 0, Number(m.to[1]) || 0]
      });
    }
    return out;
  }

  /**
   * Internal memory level representation:
   * board is { rows, columns, squares }
   */
  static cleanInternalLevel(lvl) {
    if (!lvl) return null;
    const configuredSize = this.extractBoardSize(lvl);
    const configuredCols = (lvl.board && lvl.board.columns) || configuredSize;
    const boardObj = this.parseBoard(lvl.board, configuredSize, configuredCols);

    return {
      levelId: String(lvl.levelId || "CHK_001"),
      difficulty: lvl.difficulty || "BEGINNER",
      boardSize: boardObj.rows || configuredSize,
      firstTurn: this.normalizeFirstTurn(lvl.firstTurn),
      robotMoves: this.normalizeRobotMoves(lvl.robotMoves),
      board: boardObj,
      challenge: {
        type: (lvl.challenge && lvl.challenge.type) || "CAPTURE_COUNT",
        target: (lvl.challenge && lvl.challenge.target !== undefined) ? lvl.challenge.target : 1,
        moveLimit: (lvl.challenge && lvl.challenge.moveLimit !== undefined) ? lvl.challenge.moveLimit : 3
      }
    };
  }

  static cleanLevel(lvl) {
    return this.cleanInternalLevel(lvl);
  }

  /**
   * Compact Export Format:
   * Board is strictly the compact piece array:
   * [ { pIndex: 1, isKing: false, pos: [col, row] }, ... ]
   */
  static cleanLevelForExport(lvl) {
    if (!lvl) return null;
    const configuredSize = this.extractBoardSize(lvl);
    const configuredCols = (lvl.board && lvl.board.columns) || configuredSize;
    const boardObj = this.parseBoard(lvl.board, configuredSize, configuredCols);
    const pieceArray = this.serializeBoard(boardObj.squares);
    const robotMoves = this.normalizeRobotMoves(lvl.robotMoves);

    const out = {
      levelId: String(lvl.levelId || "CHK_001"),
      difficulty: lvl.difficulty || "BEGINNER",
      boardSize: boardObj.rows || configuredSize,
      firstTurn: this.normalizeFirstTurn(lvl.firstTurn),
      board: pieceArray,
      challenge: {
        type: (lvl.challenge && lvl.challenge.type) || "CAPTURE_COUNT",
        target: (lvl.challenge && lvl.challenge.target !== undefined) ? lvl.challenge.target : 1,
        moveLimit: (lvl.challenge && lvl.challenge.moveLimit !== undefined) ? lvl.challenge.moveLimit : 3
      }
    };
    if (robotMoves.length > 0) {
      out.robotMoves = robotMoves;
    }
    return out;
  }

  static load() {
    try {
      const raw = localStorage.getItem(CONSTANTS.STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed.level) {
          return { level: this.cleanInternalLevel(parsed.level) };
        }
        if (parsed.levels && Array.isArray(parsed.levels) && parsed.levels.length > 0) {
          const found = parsed.levels.find(l => l.levelId === parsed.activeLevelId) || parsed.levels[0];
          return { level: this.cleanInternalLevel(found) };
        }
      }
    } catch (e) {
      console.warn("StorageManager load error:", e);
    }
    return { level: this.cleanInternalLevel(CONSTANTS.DEFAULT_LEVELS[0]) };
  }

  static save(level) {
    try {
      const exportedLevel = this.cleanLevelForExport(level);
      localStorage.setItem(CONSTANTS.STORAGE_KEY, JSON.stringify({
        level: exportedLevel
      }));
      return true;
    } catch (e) {
      console.error("StorageManager save error:", e);
      return false;
    }
  }

  static resetAll() {
    try {
      localStorage.removeItem(CONSTANTS.STORAGE_KEY);
      return true;
    } catch (e) {
      return false;
    }
  }
}

class HistoryManager {
  constructor(maxHistory = 40) {
    this.maxHistory = maxHistory;
    this.undoStack = [];
    this.redoStack = [];
  }

  push(state) {
    const snapshot = StorageManager.cleanInternalLevel(state);
    this.undoStack.push(snapshot);
    if (this.undoStack.length > this.maxHistory) {
      this.undoStack.shift();
    }
    this.redoStack = [];
    this.notify();
  }

  undo(currentState) {
    if (!this.canUndo()) return null;
    this.redoStack.push(StorageManager.cleanInternalLevel(currentState));
    const prev = this.undoStack.pop();
    this.notify();
    return prev;
  }

  redo(currentState) {
    if (!this.canRedo()) return null;
    this.undoStack.push(StorageManager.cleanInternalLevel(currentState));
    const next = this.redoStack.pop();
    this.notify();
    return next;
  }

  canUndo() { return this.undoStack.length > 0; }
  canRedo() { return this.redoStack.length > 0; }

  notify() {
    window.dispatchEvent(new CustomEvent("history-changed", {
      detail: { canUndo: this.canUndo(), canRedo: this.canRedo() }
    }));
  }
}

class ValidationManager {
  static validate(level, allLevels = []) {
    const errors = [];
    const warnings = [];

    const boardObj = StorageManager.parseBoard(level.board, level.board ? level.board.rows : 8, level.board ? level.board.columns : 8);
    const rows = boardObj.rows;
    const cols = boardObj.columns;
    const squares = boardObj.squares;

    if (!level.levelId || String(level.levelId).trim() === "") {
      errors.push({ field: "levelId", message: "Level ID cannot be empty." });
    } else {
      const duplicate = allLevels.find(l => l.levelId === level.levelId && l !== level);
      if (duplicate) {
        errors.push({ field: "levelId", message: `Duplicate Level ID '${level.levelId}'.` });
      }
    }

    if (rows < 6 || rows > 14 || cols < 6 || cols > 14) {
      errors.push({ field: "boardSize", message: `Dimensions must be between 6 and 14.` });
    }

    const squareCoordSet = new Set();
    let redCount = 0;
    let blackCount = 0;

    for (const sq of squares) {
      if (!sq.piece) continue;

      if (!CheckersEngine.isPlayable(sq.row, sq.column)) {
        errors.push({
          field: "boardPiece",
          row: sq.row,
          column: sq.column,
          message: `Piece at ${CheckersEngine.getAlgebraic(sq.row, sq.column, rows)} is on a non-playable light square.`
        });
      }

      if (sq.row < 0 || sq.row >= rows || sq.column < 0 || sq.column >= cols) {
        errors.push({
          field: "boardBounds",
          message: `Piece at (${sq.row}, ${sq.column}) is out of board bounds.`
        });
      }

      const coordKey = `${sq.row},${sq.column}`;
      if (squareCoordSet.has(coordKey)) {
        errors.push({
          field: "boardPiece",
          row: sq.row,
          column: sq.column,
          message: `Multiple pieces occupy square ${CheckersEngine.getAlgebraic(sq.row, sq.column, rows)}.`
        });
      }
      squareCoordSet.add(coordKey);

      if (sq.piece.startsWith("RED")) redCount++;
      if (sq.piece.startsWith("BLACK")) blackCount++;
    }

    if (redCount === 0) {
      errors.push({ field: "pieceCount", message: "Place at least one Red piece." });
    }
    if (blackCount === 0) {
      warnings.push({ field: "pieceCount", message: "No Black pieces placed." });
    }

    if (level.challenge) {
      if (level.challenge.type === "CAPTURE_COUNT" && level.challenge.target > blackCount) {
        warnings.push({
          field: "challengeTarget",
          message: `Target captures (${level.challenge.target}) exceeds black pieces (${blackCount}).`
        });
      }
    }

    const status = errors.length > 0 ? "error" : (warnings.length > 0 ? "warning" : "success");
    return { status, errors, warnings };
  }
}

class ImportExportManager {
  static getCleanJSONString(level) {
    const clean = StorageManager.cleanLevelForExport(level);
    return JSON.stringify(clean, null, 2);
  }

  static async copyLevelJSON(level) {
    const dataStr = this.getCleanJSONString(level);
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
      try {
        await navigator.clipboard.writeText(dataStr);
        return true;
      } catch (e) {
        // Fallback below
      }
    }
    try {
      const ta = document.createElement("textarea");
      ta.value = dataStr;
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      ta.style.top = "0";
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      const ok = document.execCommand("copy");
      document.body.removeChild(ta);
      return ok;
    } catch (e) {
      return false;
    }
  }

  static exportLevel(level) {
    const clean = StorageManager.cleanLevelForExport(level);
    const dataStr = JSON.stringify(clean, null, 2);
    this.downloadFile(`${clean.levelId || "level"}.json`, dataStr);
  }

  static exportLevelPack(levels, filename = "checkers_levels.json") {
    const cleanList = levels.map(l => StorageManager.cleanLevelForExport(l));
    const dataStr = JSON.stringify(cleanList, null, 2);
    this.downloadFile(filename, dataStr);
  }

  static downloadFile(filename, content) {
    const blob = new Blob([content], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  static parseImportJSON(jsonString) {
    try {
      const parsed = JSON.parse(jsonString);
      let list = [];
      if (Array.isArray(parsed)) {
        list = parsed;
      } else if (parsed.levels && Array.isArray(parsed.levels)) {
        list = parsed.levels;
      } else if (parsed.board) {
        list = [parsed];
      } else {
        return { success: false, error: "JSON does not contain board data." };
      }

      const cleanList = list.map((item, idx) => {
        if (!item.levelId) item.levelId = String(idx + 1);
        return StorageManager.cleanInternalLevel(item);
      }).filter(Boolean);

      return { success: true, levels: cleanList };
    } catch (e) {
      return { success: false, error: `Invalid JSON syntax: ${e.message}` };
    }
  }
}
'''
