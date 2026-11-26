# generator/js_ui.py

JS_UI_CONTENT = r'''
/**
 * CHECKERS SIMPLE LEVEL CREATOR - UI CONTROLLER
 */

class UIManager {
  constructor() {
    this.storage = StorageManager.load();
    this.currentLevel = this.storage.level;
    this.history = new HistoryManager(40);

    // Folder browser state
    this.directoryHandle = null;
    this.folderName = "";
    this.folderFiles = []; // [{ fileName, level, fileHandle }]
    this.activeFileIndex = -1;
    this.folderSearchQuery = "";

    // Editor state
    this.activeTool = "RED_NORMAL"; // RED_NORMAL, RED_KING, BLACK_NORMAL, BLACK_KING, ERASER, MOVE
    this.selectedSquare = null;
    this.legalMovesForSelected = [];
    this.isPickingRobotMove = false;
    this.robotMoveFrom = null;
    this.boardRotation = 0;
    this.isBoardFlipped = false;

    // Preview mode
    this.isPreviewActive = false;
    this.previewState = null;
    this.previewHistory = [];

    this.autoSaveTimer = null;
  }

  getActiveLevel() {
    return this.currentLevel;
  }

  init() {
    this.bindEvents();
    this.renderFolderList();
    this.loadLevelIntoEditor(this.getActiveLevel());
    this.updateStatus();
    this.showToast("Simple Level Creator Ready", "info");
  }

  requestAutoSave() {
    const statusInd = document.getElementById("statusIndicator");
    const statusText = document.getElementById("statusSaveText");
    if (statusInd) statusInd.classList.add("saving");
    if (statusText) statusText.textContent = "Autosaving...";

    clearTimeout(this.autoSaveTimer);
    this.autoSaveTimer = setTimeout(() => {
      this.saveToStorage();
    }, 500);
  }

  async saveToStorage(writeToDisk = false) {
    StorageManager.save(this.currentLevel);

    if (writeToDisk && this.activeFileIndex >= 0 && this.folderFiles[this.activeFileIndex]) {
      const entry = this.folderFiles[this.activeFileIndex];
      entry.level = StorageManager.cleanInternalLevel(this.currentLevel);
      this.renderFolderList();
      if (entry.fileHandle && typeof entry.fileHandle.createWritable === "function") {
        try {
          const writable = await entry.fileHandle.createWritable();
          await writable.write(ImportExportManager.getCleanJSONString(this.currentLevel));
          await writable.close();
        } catch (err) {
          console.warn("Could not write directly to file:", err);
        }
      }
    }

    const statusInd = document.getElementById("statusIndicator");
    const statusText = document.getElementById("statusSaveText");
    if (statusInd) statusInd.classList.remove("saving");
    if (statusText) {
      const now = new Date();
      statusText.textContent = `Saved at ${now.toLocaleTimeString()}`;
    }
  }

  /**
   * SINGLE LEVEL & FOLDER MANAGEMENT
   */
  suggestNextLevelId() {
    let maxNum = 0;
    if (this.folderFiles.length > 0) {
      for (const item of this.folderFiles) {
        const src = item.fileName || (item.level && item.level.levelId) || "";
        const m = src.match(/(\d+)/);
        if (m) {
          const n = parseInt(m[1], 10);
          if (n > maxNum) maxNum = n;
        }
      }
      return String(maxNum + 1);
    }
    const curId = (this.currentLevel && this.currentLevel.levelId) || "";
    const curMatch = curId.match(/^(\d+)$/);
    if (curMatch) {
      return String(parseInt(curMatch[1], 10) + 1);
    }
    return "1";
  }

  openNewLevelModal() {
    const modal = document.getElementById("newLevelModal");
    if (!modal) {
      this.createNewLevel();
      return;
    }

    const nextId = this.suggestNextLevelId();
    const fileInput = document.getElementById("newLevelFileNameInput");
    const idInput = document.getElementById("newLevelIdInput");
    const diffSelect = document.getElementById("newLevelDifficultySelect");
    const sizeSelect = document.getElementById("newLevelBoardSizeSelect");
    const hintEl = document.getElementById("newLevelModalHint");
    const createBtn = document.getElementById("btnCreateLevelOnly");

    if (fileInput) fileInput.value = `${nextId}.json`;
    if (idInput) {
      idInput.value = nextId;
      idInput.dataset.manual = "false";
    }
    if (diffSelect) diffSelect.value = "BEGINNER";
    if (sizeSelect) sizeSelect.value = String((this.currentLevel && this.currentLevel.board && this.currentLevel.board.rows) || 8);

    if (this.directoryHandle) {
      if (hintEl) hintEl.textContent = `Writable folder "${this.folderName}" is connected. Creating will write a new .json file directly into this folder.`;
      if (createBtn) createBtn.textContent = "Create File in Folder";
    } else {
      if (hintEl) hintEl.textContent = `Creates a new level in the editor. Use "Create & Download .json" to save it as a new file.`;
      if (createBtn) createBtn.textContent = "Create in Editor";
    }

    modal.classList.add("active");
    if (fileInput) fileInput.focus();
  }

  async createNewLevelFromModal(downloadFile = false) {
    const fileInput = document.getElementById("newLevelFileNameInput");
    const idInput = document.getElementById("newLevelIdInput");
    const diffSelect = document.getElementById("newLevelDifficultySelect");
    const sizeSelect = document.getElementById("newLevelBoardSizeSelect");

    const levelId = (idInput && idInput.value.trim()) || "1";
    let fileName = (fileInput && fileInput.value.trim()) || `${levelId}.json`;
    if (!fileName.toLowerCase().endsWith(".json")) fileName += ".json";

    const difficulty = (diffSelect && diffSelect.value) || "BEGINNER";
    const boardSize = parseInt((sizeSelect && sizeSelect.value) || "8", 10) || 8;

    const newLevel = StorageManager.cleanInternalLevel({
      levelId,
      difficulty,
      boardSize,
      firstTurn: 0,
      board: [],
      challenge: {
        type: "CAPTURE_COUNT",
        target: 1,
        moveLimit: 2
      }
    });

    this.history.push(this.getActiveLevel());
    this.currentLevel = newLevel;
    this.selectedSquare = null;
    this.legalMovesForSelected = [];

    let createdInFolder = false;
    if (this.directoryHandle && typeof this.directoryHandle.getFileHandle === "function") {
      try {
        const fileHandle = await this.directoryHandle.getFileHandle(fileName, { create: true });
        const writable = await fileHandle.createWritable();
        await writable.write(ImportExportManager.getCleanJSONString(newLevel));
        await writable.close();

        const existingIdx = this.folderFiles.findIndex(f => f.fileName === fileName);
        const entry = { fileName, level: StorageManager.cleanInternalLevel(newLevel), fileHandle };
        if (existingIdx !== -1) {
          this.folderFiles[existingIdx] = entry;
          this.activeFileIndex = existingIdx;
        } else {
          this.folderFiles.push(entry);
          this.folderFiles.sort((a, b) => a.fileName.localeCompare(b.fileName, undefined, { numeric: true, sensitivity: "base" }));
          this.activeFileIndex = this.folderFiles.findIndex(f => f.fileName === fileName);
        }
        createdInFolder = true;
      } catch (err) {
        console.warn("Could not create file in folder:", err);
      }
    } else if (this.folderFiles.length > 0) {
      // Also reflect the new file entry in the open folder list in memory
      const existingIdx = this.folderFiles.findIndex(f => f.fileName === fileName);
      const entry = { fileName, level: StorageManager.cleanInternalLevel(newLevel), fileHandle: null };
      if (existingIdx !== -1) {
        this.folderFiles[existingIdx] = entry;
        this.activeFileIndex = existingIdx;
      } else {
        this.folderFiles.push(entry);
        this.folderFiles.sort((a, b) => a.fileName.localeCompare(b.fileName, undefined, { numeric: true, sensitivity: "base" }));
        this.activeFileIndex = this.folderFiles.findIndex(f => f.fileName === fileName);
      }
    } else {
      this.activeFileIndex = -1;
    }

    if (downloadFile) {
      ImportExportManager.downloadFile(fileName, ImportExportManager.getCleanJSONString(newLevel));
    }

    this.renderFolderList();
    this.loadLevelIntoEditor(this.currentLevel);
    this.requestAutoSave();

    const modal = document.getElementById("newLevelModal");
    if (modal) modal.classList.remove("active");

    if (createdInFolder) {
      this.showToast(`Created ${fileName} in "${this.folderName}"`, "success");
    } else if (downloadFile) {
      this.showToast(`Created & downloaded ${fileName}`, "success");
    } else {
      this.showToast(`Created new level ${levelId}`, "success");
    }
  }

  createNewLevel() {
    this.history.push(this.getActiveLevel());
    this.activeFileIndex = -1;
    this.currentLevel = StorageManager.cleanInternalLevel({
      levelId: this.suggestNextLevelId(),
      difficulty: "BEGINNER",
      boardSize: 8,
      board: [
        { pIndex: 0, isKing: false, pos: [2, 5] },
        { pIndex: 1, isKing: false, pos: [3, 4] }
      ],
      challenge: {
        type: "CAPTURE_COUNT",
        target: 1,
        moveLimit: 2
      }
    });

    this.selectedSquare = null;
    this.legalMovesForSelected = [];
    this.renderFolderList();
    this.loadLevelIntoEditor(this.currentLevel);
    this.requestAutoSave();
    this.showToast("Started new level", "success");
  }

  async selectFolder() {
    if (typeof window.showDirectoryPicker === "function" && window.isSecureContext) {
      try {
        const dirHandle = await window.showDirectoryPicker({ mode: "readwrite" });
        await this.loadDirectoryHandle(dirHandle);
        return;
      } catch (err) {
        if (err && err.name === "AbortError") return;
        // Fall through to <input webkitdirectory> if SecurityError or unsupported
      }
    }
    const picker = document.getElementById("folderPickerInput");
    if (picker) {
      picker.value = "";
      picker.click();
    }
  }

  async loadDirectoryHandle(dirHandle) {
    this.directoryHandle = dirHandle;
    this.folderName = dirHandle.name || "Selected Folder";
    const items = [];

    for await (const entry of dirHandle.values()) {
      if (entry.kind === "file" && entry.name.toLowerCase().endsWith(".json")) {
        try {
          const file = await entry.getFile();
          const text = await file.text();
          const res = ImportExportManager.parseImportJSON(text);
          if (res.success && res.levels.length > 0) {
            res.levels.forEach((lvl, idx) => {
              items.push({
                fileName: res.levels.length > 1 ? `${entry.name} [${idx + 1}]` : entry.name,
                level: lvl,
                fileHandle: res.levels.length === 1 ? entry : null
              });
            });
          }
        } catch (e) {
          console.warn("Skipped unreadable JSON:", entry.name, e);
        }
      }
    }

    items.sort((a, b) => a.fileName.localeCompare(b.fileName, undefined, { numeric: true, sensitivity: "base" }));
    this.folderFiles = items;
    this.activeFileIndex = -1;
    this.updateFolderHeader();
    this.renderFolderList();
    this.showToast(`Loaded ${items.length} level(s) from "${this.folderName}"`, items.length ? "success" : "info");
  }

  async loadFileList(fileList) {
    const files = Array.from(fileList || []).filter(f => f.name.toLowerCase().endsWith(".json"));
    if (files.length === 0) {
      this.folderFiles = [];
      this.activeFileIndex = -1;
      this.folderName = "Empty Folder";
      this.updateFolderHeader();
      this.renderFolderList();
      this.showToast("No .json level files found in folder", "info");
      return;
    }

    const firstRel = files[0].webkitRelativePath || "";
    this.folderName = firstRel.includes("/") ? firstRel.split("/")[0] : "Selected Folder";
    this.directoryHandle = null;

    const items = [];
    for (const file of files) {
      try {
        const text = await file.text();
        const res = ImportExportManager.parseImportJSON(text);
        if (res.success && res.levels.length > 0) {
          res.levels.forEach((lvl, idx) => {
            items.push({
              fileName: res.levels.length > 1 ? `${file.name} [${idx + 1}]` : file.name,
              level: lvl,
              fileHandle: null
            });
          });
        }
      } catch (e) {
        console.warn("Skipped invalid JSON:", file.name, e);
      }
    }

    items.sort((a, b) => a.fileName.localeCompare(b.fileName, undefined, { numeric: true, sensitivity: "base" }));
    this.folderFiles = items;
    this.activeFileIndex = -1;
    this.updateFolderHeader();
    this.renderFolderList();
    this.showToast(`Loaded ${items.length} level(s) from "${this.folderName}"`, items.length ? "success" : "info");
  }

  updateFolderHeader() {
    const nameEl = document.getElementById("folderNameDisplay");
    if (nameEl) {
      nameEl.textContent = this.folderName || "No folder selected";
      nameEl.title = this.folderName || "No folder selected";
    }
  }

  openFolderFile(index) {
    const item = this.folderFiles[index];
    if (!item) return;

    this.history.push(this.getActiveLevel());
    this.activeFileIndex = index;
    this.currentLevel = StorageManager.cleanInternalLevel(item.level);
    this.selectedSquare = null;
    this.legalMovesForSelected = [];

    this.renderFolderList();
    this.loadLevelIntoEditor(this.currentLevel);
    this.requestAutoSave();
    this.showToast(`Opened ${item.fileName}`, "info");
  }

  renderFolderList() {
    const container = document.getElementById("folderFileList");
    if (!container) return;

    const q = (this.folderSearchQuery || "").trim().toLowerCase();
    const filtered = this.folderFiles
      .map((item, idx) => ({ item, idx }))
      .filter(({ item }) => {
        if (!q) return true;
        return item.fileName.toLowerCase().includes(q) ||
          (item.level.levelId || "").toLowerCase().includes(q);
      });

    const countBadge = document.getElementById("folderCountBadge");
    if (countBadge) countBadge.textContent = `${filtered.length} file${filtered.length === 1 ? "" : "s"}`;

    container.innerHTML = "";
    if (this.folderFiles.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding: 24px 12px; color: var(--text-muted); line-height:1.5;">
        Select a folder containing <b>.json</b> levels to list and open them here.
      </div>`;
      return;
    }

    if (filtered.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding: 20px; color: var(--text-muted);">No matching files.</div>`;
      return;
    }

    for (const { item, idx } of filtered) {
      const lvl = item.level;
      const card = document.createElement("div");
      card.className = `level-card ${idx === this.activeFileIndex ? "active" : ""}`;

      const redCount = (lvl.board.squares || []).filter(s => s.piece && s.piece.startsWith("RED")).length;
      const blackCount = (lvl.board.squares || []).filter(s => s.piece && s.piece.startsWith("BLACK")).length;

      card.innerHTML = `
        <div class="level-card-header">
          <span class="level-id-badge">${lvl.levelId || "LEVEL"}</span>
          <span class="badge badge-${(lvl.difficulty || 'beginner').toLowerCase()}">${lvl.difficulty || 'BEGINNER'}</span>
        </div>
        <div class="file-name-sub" title="${item.fileName}">${item.fileName}</div>
        <div class="level-card-footer">
          <span>${lvl.board.rows}×${lvl.board.columns}</span>
          <span><b style="color:var(--accent-danger);">${redCount}R</b> / <b style="color:#94a3b8;">${blackCount}B</b></span>
        </div>
      `;

      card.addEventListener("click", () => {
        this.openFolderFile(idx);
      });

      container.appendChild(card);
    }
  }

  async copyJson() {
    const ok = await ImportExportManager.copyLevelJSON(this.getActiveLevel());
    if (ok) {
      this.showToast("Copied JSON to clipboard", "success");
    } else {
      this.showToast("Failed to copy JSON", "error");
    }
  }

  loadLevelIntoEditor(level) {
    if (!level) return;
    this.renderBoard(level);
    this.populateInspector(level);
    this.runValidation(level);
    this.updateStatus();
  }

  /**
   * BOARD RENDERING & INTERACTION
   */
  renderBoard(level) {
    const boardEl = document.getElementById("checkersBoard");
    const coordsTop = document.getElementById("boardCoordsTop");
    const coordsBottom = document.getElementById("boardCoordsBottom");
    const coordsLeft = document.getElementById("boardCoordsLeft");
    const coordsRight = document.getElementById("boardCoordsRight");
    if (!boardEl) return;

    const rows = level.board.rows || 8;
    const cols = level.board.columns || 8;

    const frameEl = document.getElementById("boardOuterFrame");
    if (frameEl) {
      let t = `rotate(${this.boardRotation}deg)`;
      if (this.isBoardFlipped) t += ` rotate(180deg)`;
      frameEl.style.transform = t;
    }

    boardEl.style.gridTemplateRows = `repeat(${rows}, 60px)`;
    boardEl.style.gridTemplateColumns = `repeat(${cols}, 60px)`;
    boardEl.innerHTML = "";

    if (coordsTop && coordsBottom) {
      coordsTop.innerHTML = "";
      coordsBottom.innerHTML = "";
      for (let c = 0; c < cols; c++) {
        const l1 = document.createElement("div");
        l1.className = "coord-label";
        l1.style.width = "60px";
        l1.textContent = c;
        coordsTop.appendChild(l1);

        const l2 = document.createElement("div");
        l2.className = "coord-label";
        l2.style.width = "60px";
        l2.textContent = c;
        coordsBottom.appendChild(l2);
      }
    }

    if (coordsLeft && coordsRight) {
      coordsLeft.innerHTML = "";
      coordsRight.innerHTML = "";
      for (let r = 0; r < rows; r++) {
        const l1 = document.createElement("div");
        l1.className = "coord-label";
        l1.style.height = "60px";
        l1.textContent = r;
        coordsLeft.appendChild(l1);

        const l2 = document.createElement("div");
        l2.className = "coord-label";
        l2.style.height = "60px";
        l2.textContent = r;
        coordsRight.appendChild(l2);
      }
    }

    const pieceMap = CheckersEngine.getPieceMap(level.board.squares || []);

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const isPlayable = CheckersEngine.isPlayable(r, c);
        const sq = document.createElement("div");
        sq.className = `board-square ${isPlayable ? "sq-dark" : "sq-light"}`;
        sq.dataset.row = r;
        sq.dataset.col = c;

        const coordHint = document.createElement("span");
        coordHint.className = "sq-coord-hint";
        coordHint.textContent = `${c}-${r}`;
        sq.appendChild(coordHint);

        if (this.selectedSquare && this.selectedSquare.row === r && this.selectedSquare.col === c) {
          sq.classList.add("sq-selected");
        }

        const legalMove = this.legalMovesForSelected.find(m => m.to.row === r && m.to.column === c);
        if (legalMove) {
          if (legalMove.captured && legalMove.captured.length > 0) sq.classList.add("sq-legal-capture");
          else sq.classList.add("sq-legal-move");
        }

        const key = `${r},${c}`;
        if (pieceMap.has(key)) {
          const pieceType = pieceMap.get(key);
          sq.innerHTML = SVG_PIECES[pieceType] || "";
          const pieceSvg = sq.querySelector("svg");
          if (pieceSvg) {
            pieceSvg.draggable = true;
            pieceSvg.dataset.row = r;
            pieceSvg.dataset.col = c;
            pieceSvg.dataset.piece = pieceType;
          }
        }

        sq.addEventListener("click", () => this.handleSquareClick(r, c, isPlayable, level));

        sq.addEventListener("dragover", (e) => {
          if (!isPlayable) return;
          e.preventDefault();
          sq.classList.add("sq-drag-over");
        });

        sq.addEventListener("dragleave", () => sq.classList.remove("sq-drag-over"));

        sq.addEventListener("drop", (e) => {
          sq.classList.remove("sq-drag-over");
          if (!isPlayable) return;
          e.preventDefault();
          const fromRow = parseInt(e.dataTransfer.getData("row"), 10);
          const fromCol = parseInt(e.dataTransfer.getData("col"), 10);
          const piece = e.dataTransfer.getData("piece");
          this.handlePieceDragDrop(fromRow, fromCol, r, c, piece, level);
        });

        boardEl.appendChild(sq);
      }
    }

    boardEl.querySelectorAll(".checkers-piece").forEach(p => {
      p.addEventListener("dragstart", (e) => {
        e.dataTransfer.setData("row", p.dataset.row);
        e.dataTransfer.setData("col", p.dataset.col);
        e.dataTransfer.setData("piece", p.dataset.piece);
      });
    });
  }

  handleSquareClick(r, c, isPlayable, level) {
    if (!isPlayable) {
      this.showToast("Pieces can only be placed on dark playable squares.", "warning");
      return;
    }

    if (this.isPickingRobotMove) {
      if (!this.robotMoveFrom) {
        this.robotMoveFrom = { row: r, col: c };
        this.selectedSquare = { row: r, col: c };
        this.renderBoard(level);
        this.showToast(`Robot move from ${c}-${r}: click destination square`, "info");
      } else {
        if (this.robotMoveFrom.row === r && this.robotMoveFrom.col === c) {
          this.robotMoveFrom = null;
          this.selectedSquare = null;
          this.renderBoard(level);
          return;
        }
        level.robotMoves = level.robotMoves || [];
        level.robotMoves.push({
          from: [this.robotMoveFrom.col, this.robotMoveFrom.row],
          to: [c, r]
        });
        this.isPickingRobotMove = false;
        this.robotMoveFrom = null;
        this.selectedSquare = null;
        const pickBtn = document.getElementById("btnPickRobotMove");
        if (pickBtn) pickBtn.classList.remove("robot-move-pick-active");
        this.renderBoard(level);
        this.renderRobotMovesList(level);
        this.requestAutoSave();
        this.showToast("Added scripted Robot move", "success");
      }
      return;
    }

    const squares = level.board.squares;
    const existingIdx = squares.findIndex(s => s.row === r && s.column === c);

    if (this.activeTool === "ERASER") {
      if (existingIdx !== -1) {
        this.history.push(level);
        squares.splice(existingIdx, 1);
        this.renderBoard(level);
        this.runValidation(level);
        this.requestAutoSave();
      }
      return;
    }

    if (this.activeTool === "MOVE") {
      if (this.selectedSquare) {
        const startR = this.selectedSquare.row;
        const startC = this.selectedSquare.col;

        if (startR === r && startC === c) {
          this.selectedSquare = null;
          this.legalMovesForSelected = [];
          this.renderBoard(level);
          return;
        }

        const legalMove = this.legalMovesForSelected.find(m => m.to.row === r && m.to.column === c);
        if (legalMove) {
          this.history.push(level);
          const applied = CheckersEngine.applyMove(squares, legalMove, level.board.rows);
          level.board.squares = applied.newSquares;
          this.selectedSquare = null;
          this.legalMovesForSelected = [];
          this.renderBoard(level);
          this.runValidation(level);
          this.requestAutoSave();
          return;
        }

        if (existingIdx !== -1) {
          this.selectSquareForMove(r, c, squares[existingIdx].piece, level);
        } else {
          this.selectedSquare = null;
          this.legalMovesForSelected = [];
          this.renderBoard(level);
        }
      } else {
        if (existingIdx !== -1) {
          this.selectSquareForMove(r, c, squares[existingIdx].piece, level);
        }
      }
      return;
    }

    // Place piece
    this.history.push(level);
    if (existingIdx !== -1) {
      squares[existingIdx].piece = this.activeTool;
    } else {
      squares.push({ row: r, column: c, piece: this.activeTool });
    }

    this.renderBoard(level);
    this.runValidation(level);
    this.requestAutoSave();
  }

  selectSquareForMove(r, c, piece, level) {
    this.selectedSquare = { row: r, col: c };
    const color = CheckersEngine.getPieceColor(piece);
    const allMoves = CheckersEngine.getAllLegalMoves(level.board.squares, level.board.rows, level.board.columns, color);
    this.legalMovesForSelected = allMoves.filter(m => m.from.row === r && m.from.column === c);
    this.renderBoard(level);
  }

  handlePieceDragDrop(fromR, fromC, toR, toC, piece, level) {
    if (fromR === toR && fromC === toC) return;
    this.history.push(level);

    const squares = level.board.squares;
    const fromIdx = squares.findIndex(s => s.row === fromR && s.column === fromC);
    if (fromIdx !== -1) squares.splice(fromIdx, 1);

    const toIdx = squares.findIndex(s => s.row === toR && s.column === toC);
    if (toIdx !== -1) squares.splice(toIdx, 1);

    squares.push({ row: toR, column: toC, piece: piece });
    this.renderBoard(level);
    this.runValidation(level);
    this.requestAutoSave();
  }

  changeBoardDimensions(newRows, newCols) {
    const level = this.getActiveLevel();
    if (!level) return;
    this.history.push(level);

    newRows = parseInt(newRows, 10);
    newCols = parseInt(newCols, 10);
    if (isNaN(newRows) || newRows < 6 || newRows > 14) newRows = 8;
    if (isNaN(newCols) || newCols < 6 || newCols > 14) newCols = 8;

    level.boardSize = newRows;
    level.board.rows = newRows;
    level.board.columns = newCols;

    level.board.squares = level.board.squares.filter(sq => {
      const inBounds = sq.row < newRows && sq.column < newCols;
      const playable = CheckersEngine.isPlayable(sq.row, sq.column);
      return inBounds && playable;
    });

    this.selectedSquare = null;
    this.legalMovesForSelected = [];
    this.renderBoard(level);
    this.populateInspector(level);
    this.runValidation(level);
    this.updateStatus();
    this.requestAutoSave();
    this.showToast(`Board size: ${newRows}×${newCols}`, "info");
  }

  clearBoard(type = "ALL") {
    const level = this.getActiveLevel();
    if (!level) return;
    this.history.push(level);

    if (type === "ALL") level.board.squares = [];
    else if (type === "RED") level.board.squares = level.board.squares.filter(s => !s.piece.startsWith("RED"));
    else if (type === "BLACK") level.board.squares = level.board.squares.filter(s => !s.piece.startsWith("BLACK"));

    this.selectedSquare = null;
    this.legalMovesForSelected = [];
    this.renderBoard(level);
    this.runValidation(level);
    this.requestAutoSave();
    this.showToast(`Cleared ${type.toLowerCase()}`, "info");
  }

  randomSetup() {
    const level = this.getActiveLevel();
    if (!level) return;
    this.history.push(level);

    const rows = level.board.rows;
    const cols = level.board.columns;
    const squares = [];

    const playable = [];
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (CheckersEngine.isPlayable(r, c)) playable.push({ r, c });
      }
    }
    playable.sort(() => Math.random() - 0.5);

    let red = 0;
    let black = 0;
    for (const { r, c } of playable) {
      if (r >= Math.floor(rows / 2) + 1 && red < 3) {
        squares.push({ row: r, column: c, piece: Math.random() > 0.7 ? "RED_KING" : "RED_NORMAL" });
        red++;
      } else if (r <= Math.floor(rows / 2) - 1 && black < 3) {
        squares.push({ row: r, column: c, piece: Math.random() > 0.7 ? "BLACK_KING" : "BLACK_NORMAL" });
        black++;
      }
    }

    level.board.squares = squares;
    this.selectedSquare = null;
    this.legalMovesForSelected = [];
    this.renderBoard(level);
    this.runValidation(level);
    this.requestAutoSave();
    this.showToast("Generated random layout", "success");
  }

  flipBoard() {
    this.isBoardFlipped = !this.isBoardFlipped;
    this.renderBoard(this.getActiveLevel());
  }

  rotateBoard() {
    this.boardRotation = (this.boardRotation + 90) % 360;
    this.renderBoard(this.getActiveLevel());
  }

  /**
   * SIMPLE RIGHT INSPECTOR PANEL
   */
  populateInspector(level) {
    const idInput = document.getElementById("propLevelId");
    const diffSelect = document.getElementById("propDifficulty");
    const sizeSelect = document.getElementById("propBoardSize");
    const firstTurnSelect = document.getElementById("propFirstTurn");
    const chTypeSelect = document.getElementById("challengeTypeSelect");
    const chTargetInput = document.getElementById("challengeTargetInput");
    const chTargetRow = document.getElementById("challengeTargetRow");
    const chMoveLimit = document.getElementById("challengeMoveLimitInput");

    if (idInput) idInput.value = level.levelId || "";
    if (diffSelect) diffSelect.value = level.difficulty || "BEGINNER";
    if (firstTurnSelect) firstTurnSelect.value = String(level.firstTurn === 1 ? 1 : 0);

    const curSize = `${level.board.rows}x${level.board.columns}`;
    if (sizeSelect) sizeSelect.value = ["6x6", "8x8", "10x10", "12x12"].includes(curSize) ? curSize : "8x8";

    document.querySelectorAll("[data-board-dim]").forEach(btn => {
      const dim = parseInt(btn.dataset.boardDim, 10);
      btn.classList.toggle("active", dim === level.board.rows);
    });

    // Populate challenge types dropdown
    if (chTypeSelect) {
      chTypeSelect.innerHTML = "";
      CONSTANTS.CHALLENGE_TYPES.forEach(ct => {
        const opt = document.createElement("option");
        opt.value = ct.type;
        opt.textContent = ct.label;
        if (level.challenge && level.challenge.type === ct.type) opt.selected = true;
        chTypeSelect.appendChild(opt);
      });
    }

    const currentCh = level.challenge || { type: "CAPTURE_COUNT", target: 1, moveLimit: 2 };
    const chDef = CONSTANTS.CHALLENGE_TYPES.find(c => c.type === currentCh.type) || CONSTANTS.CHALLENGE_TYPES[0];

    if (chTargetRow) {
      chTargetRow.style.display = chDef.hasTarget ? "flex" : "none";
    }
    if (chTargetInput) chTargetInput.value = currentCh.target !== undefined ? currentCh.target : 1;
    if (chMoveLimit) chMoveLimit.value = currentCh.moveLimit !== undefined ? currentCh.moveLimit : 3;

    this.renderRobotMovesList(level);
  }

  renderRobotMovesList(level) {
    const listEl = document.getElementById("robotMovesList");
    if (!listEl) return;
    const moves = (level && level.robotMoves) || [];
    listEl.innerHTML = "";
    if (moves.length === 0) {
      listEl.innerHTML = `<div style="font-size:11px; color:var(--text-muted);">None (Robot uses AI defense)</div>`;
      return;
    }
    moves.forEach((m, idx) => {
      const row = document.createElement("div");
      row.className = "robot-move-item";
      row.innerHTML = `
        <span>#${idx + 1}: <b>${m.from[0]}-${m.from[1]}</b> → <b>${m.to[0]}-${m.to[1]}</b></span>
        <button class="btn btn-icon btn-sm btn-danger" title="Remove" style="padding:2px 6px;">×</button>
      `;
      row.querySelector("button").addEventListener("click", () => {
        level.robotMoves.splice(idx, 1);
        this.renderRobotMovesList(level);
        this.requestAutoSave();
      });
      listEl.appendChild(row);
    });
  }

  runValidation(level) {
    const res = ValidationManager.validate(level);
    const box = document.getElementById("validationAlert");
    if (!box) return;

    if (res.errors.length > 0) {
      box.className = "validation-item error";
      box.innerHTML = `${UI_ICONS.error}<span><b>Error:</b> ${res.errors[0].message}</span>`;
    } else if (res.warnings.length > 0) {
      box.className = "validation-item warning";
      box.innerHTML = `${UI_ICONS.alert}<span><b>Note:</b> ${res.warnings[0].message}</span>`;
    } else {
      box.className = "validation-item success";
      box.innerHTML = `${UI_ICONS.check}<span>Level configuration is ready.</span>`;
    }
  }

  updateStatus() {
    const level = this.getActiveLevel();
    if (!level) return;

    const idEl = document.getElementById("statusLevelId");
    const dimsEl = document.getElementById("statusDims");
    const redEl = document.getElementById("statusRedCount");
    const blackEl = document.getElementById("statusBlackCount");
    const turnEl = document.getElementById("statusFirstTurn");
    const diffEl = document.getElementById("statusDifficulty");

    const squares = level.board.squares || [];
    const redCount = squares.filter(s => s.piece && s.piece.startsWith("RED")).length;
    const blackCount = squares.filter(s => s.piece && s.piece.startsWith("BLACK")).length;

    if (idEl) idEl.textContent = level.levelId;
    if (dimsEl) dimsEl.textContent = `${level.board.rows}×${level.board.columns}`;
    if (redEl) redEl.textContent = `${redCount} Red`;
    if (blackEl) blackEl.textContent = `${blackCount} Black`;
    if (turnEl) turnEl.textContent = level.firstTurn === 1 ? "Robot First" : "Player First";
    if (diffEl) diffEl.textContent = level.difficulty;
  }

  /**
   * LIVE PREVIEW / PLAY MODE
   */
  openPreviewMode() {
    const level = this.getActiveLevel();
    if (!level) return;

    this.isPreviewActive = true;
    const modal = document.getElementById("previewModal");
    if (modal) modal.classList.add("active");

    const rows = level.board.rows;
    const cols = level.board.columns;
    const initialSquares = CheckersEngine.cloneBoard(level.board.squares);

    const redCount = initialSquares.filter(s => s.piece && s.piece.startsWith("RED")).length;
    const blackCount = initialSquares.filter(s => s.piece && s.piece.startsWith("BLACK")).length;

    const startsWithOpponent = level.firstTurn === 1;

    this.previewState = {
      level: StorageManager.cleanInternalLevel(level),
      board: initialSquares,
      boardRows: rows,
      boardCols: cols,
      turn: startsWithOpponent ? "BLACK" : "RED",
      movesTaken: 0,
      robotMovesTaken: 0,
      capturesByRed: 0,
      kingsMadeByRed: 0,
      kingsCapturedByRed: 0,
      initialPiecesRed: redCount,
      initialPiecesBlack: blackCount,
      currentPiecesRed: redCount,
      currentPiecesBlack: blackCount,
      winner: null,
      selectedSquare: null,
      legalMoves: []
    };

    this.previewHistory = [];
    this.renderPreviewBoard();
    this.updatePreviewHUD();

    if (startsWithOpponent) {
      setTimeout(() => this.executeOpponentTurn(), 450);
    }
  }

  closePreviewMode() {
    this.isPreviewActive = false;
    const modal = document.getElementById("previewModal");
    if (modal) modal.classList.remove("active");
    this.renderBoard(this.getActiveLevel());
  }

  renderPreviewBoard() {
    const boardEl = document.getElementById("previewCheckersBoard");
    if (!boardEl || !this.previewState) return;

    const rows = this.previewState.boardRows;
    const cols = this.previewState.boardCols;

    boardEl.style.gridTemplateRows = `repeat(${rows}, 56px)`;
    boardEl.style.gridTemplateColumns = `repeat(${cols}, 56px)`;
    boardEl.innerHTML = "";

    const pieceMap = CheckersEngine.getPieceMap(this.previewState.board);

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const isPlayable = CheckersEngine.isPlayable(r, c);
        const sq = document.createElement("div");
        sq.className = `board-square ${isPlayable ? "sq-dark" : "sq-light"}`;

        if (this.previewState.selectedSquare && this.previewState.selectedSquare.row === r && this.previewState.selectedSquare.col === c) {
          sq.classList.add("sq-selected");
        }

        const legalMove = this.previewState.legalMoves.find(m => m.to.row === r && m.to.column === c);
        if (legalMove) {
          if (legalMove.captured && legalMove.captured.length > 0) sq.classList.add("sq-legal-capture");
          else sq.classList.add("sq-legal-move");
        }

        const key = `${r},${c}`;
        if (pieceMap.has(key)) {
          sq.innerHTML = SVG_PIECES[pieceMap.get(key)] || "";
        }

        sq.addEventListener("click", () => this.handlePreviewSquareClick(r, c));
        boardEl.appendChild(sq);
      }
    }
  }

  handlePreviewSquareClick(r, c) {
    if (!this.previewState || this.previewState.winner) return;
    if (this.previewState.turn !== "RED") {
      this.showToast("Opponent's turn.", "info");
      return;
    }

    const key = `${r},${c}`;
    const pieceMap = CheckersEngine.getPieceMap(this.previewState.board);

    if (this.previewState.selectedSquare) {
      const startR = this.previewState.selectedSquare.row;
      const startC = this.previewState.selectedSquare.col;

      if (startR === r && startC === c) {
        this.previewState.selectedSquare = null;
        this.previewState.legalMoves = [];
        this.renderPreviewBoard();
        return;
      }

      const match = this.previewState.legalMoves.find(m => m.to.row === r && m.to.column === c);
      if (match) {
        this.executePreviewMove(match);
        return;
      }

      if (pieceMap.has(key) && pieceMap.get(key).startsWith("RED")) {
        this.selectPreviewSquare(r, c, pieceMap.get(key));
        return;
      }

      this.previewState.selectedSquare = null;
      this.previewState.legalMoves = [];
      this.renderPreviewBoard();
    } else {
      if (pieceMap.has(key) && pieceMap.get(key).startsWith("RED")) {
        this.selectPreviewSquare(r, c, pieceMap.get(key));
      }
    }
  }

  selectPreviewSquare(r, c, piece) {
    this.previewState.selectedSquare = { row: r, col: c };
    const allMoves = CheckersEngine.getAllLegalMoves(this.previewState.board, this.previewState.boardRows, this.previewState.boardCols, "RED");
    this.previewState.legalMoves = allMoves.filter(m => m.from.row === r && m.from.column === c);
    this.renderPreviewBoard();
  }

  executePreviewMove(move) {
    this.previewHistory.push(JSON.parse(JSON.stringify(this.previewState)));

    const applied = CheckersEngine.applyMove(this.previewState.board, move, this.previewState.boardRows);
    this.previewState.board = applied.newSquares;

    if (move.player === "RED") {
      this.previewState.capturesByRed += move.captured.length;
      if (applied.isPromotion) this.previewState.kingsMadeByRed++;
      for (const cap of move.captured) {
        if (CheckersEngine.isKing(cap.piece)) this.previewState.kingsCapturedByRed++;
      }
      this.previewState.movesTaken++;
    } else {
      this.previewState.robotMovesTaken = (this.previewState.robotMovesTaken || 0) + 1;
    }

    this.previewState.currentPiecesRed = this.previewState.board.filter(s => s.piece && s.piece.startsWith("RED")).length;
    this.previewState.currentPiecesBlack = this.previewState.board.filter(s => s.piece && s.piece.startsWith("BLACK")).length;

    const nextTurn = (move.player === "RED") ? "BLACK" : "RED";
    this.previewState.turn = nextTurn;
    this.previewState.selectedSquare = null;
    this.previewState.legalMoves = [];

    const gameCheck = CheckersEngine.evaluateGameState(this.previewState.board, this.previewState.boardRows, nextTurn);
    if (gameCheck.winner) this.previewState.winner = gameCheck.winner;

    this.renderPreviewBoard();
    this.updatePreviewHUD();

    const evalRes = ChallengeEvaluator.evaluate(this.previewState.level.challenge, this.previewState);
    if (evalRes.satisfied) {
      this.showPreviewResultBanner(true, "Goal Completed! Victory!");
      return;
    } else if (evalRes.failed) {
      this.showPreviewResultBanner(false, evalRes.failReason || "Failed.");
      return;
    }

    // Opponent counter move
    if (this.previewState.turn === "BLACK" && !this.previewState.winner) {
      setTimeout(() => this.executeOpponentTurn(), 500);
    }
  }

  executeOpponentTurn() {
    if (!this.previewState || this.previewState.winner) return;

    let chosenMove = null;
    const scriptedList = (this.previewState.level && this.previewState.level.robotMoves) || [];
    const scripted = scriptedList[this.previewState.robotMovesTaken || 0];
    if (scripted) {
      const legalMoves = CheckersEngine.getAllLegalMoves(
        this.previewState.board,
        this.previewState.boardRows,
        this.previewState.boardCols,
        "BLACK"
      );
      chosenMove = legalMoves.find(m =>
        m.from.column === scripted.from[0] &&
        m.from.row === scripted.from[1] &&
        m.to.column === scripted.to[0] &&
        m.to.row === scripted.to[1]
      ) || null;
    }
    if (!chosenMove) {
      chosenMove = CheckersEngine.getBestAIMove(this.previewState.board, this.previewState.boardRows, "BLACK");
    }
    if (chosenMove) {
      this.executePreviewMove(chosenMove);
    } else {
      this.previewState.winner = "RED";
      this.updatePreviewHUD();
      const evalRes = ChallengeEvaluator.evaluate(this.previewState.level.challenge, this.previewState);
      if (evalRes.satisfied) this.showPreviewResultBanner(true, "Victory! Opponent blocked.");
      else this.showPreviewResultBanner(false, "Draw / Stalemate");
    }
  }

  updatePreviewHUD() {
    if (!this.previewState) return;

    const titleEl = document.getElementById("previewLevelTitle");
    const diffEl = document.getElementById("previewDifficultyBadge");
    const descEl = document.getElementById("previewChallengeDesc");
    const movesEl = document.getElementById("previewMovesCount");
    const progressFill = document.getElementById("previewProgressFill");

    const challenge = this.previewState.level.challenge;
    const chDef = CONSTANTS.CHALLENGE_TYPES.find(c => c.type === (challenge && challenge.type)) || {};

    if (titleEl) titleEl.textContent = this.previewState.level.levelId;
    if (diffEl) {
      diffEl.textContent = this.previewState.level.difficulty;
      diffEl.className = `badge badge-${this.previewState.level.difficulty.toLowerCase()}`;
    }
    if (descEl) descEl.textContent = chDef.label || "Solve puzzle";

    const maxMoves = challenge ? (challenge.moveLimit || 0) : 0;
    if (movesEl) {
      movesEl.textContent = maxMoves > 0 ? `Move ${this.previewState.movesTaken} / ${maxMoves}` : `Moves: ${this.previewState.movesTaken}`;
    }

    const evalRes = ChallengeEvaluator.evaluate(challenge, this.previewState);
    if (progressFill) progressFill.style.width = `${Math.round(evalRes.progress * 100)}%`;
  }

  showPreviewResultBanner(isVictory, message) {
    const banner = document.getElementById("previewResultBanner");
    if (!banner) return;
    banner.style.display = "flex";
    banner.className = `preview-result-banner ${isVictory ? "victory" : "defeat"}`;
    banner.innerHTML = `
      <div style="font-size:36px;">${isVictory ? '🏆' : '💀'}</div>
      <h2 style="font-size:18px; color:${isVictory ? 'var(--accent-success)' : 'var(--accent-danger)'};">${isVictory ? 'VICTORY!' : 'FAILED'}</h2>
      <p style="font-size:12px; color:var(--text-secondary); max-width:280px;">${message}</p>
      <div style="display:flex; gap:8px; margin-top:6px;">
        <button class="btn btn-primary" id="previewRetryBtn">Retry</button>
        <button class="btn" id="previewExitResultBtn">Back to Editor</button>
      </div>
    `;

    document.getElementById("previewRetryBtn").addEventListener("click", () => {
      banner.style.display = "none";
      this.openPreviewMode();
    });

    document.getElementById("previewExitResultBtn").addEventListener("click", () => {
      banner.style.display = "none";
      this.closePreviewMode();
    });
  }

  undoPreviewMove() {
    if (this.previewHistory.length === 0) return;
    this.previewState = this.previewHistory.pop();
    const banner = document.getElementById("previewResultBanner");
    if (banner) banner.style.display = "none";
    this.renderPreviewBoard();
    this.updatePreviewHUD();
    this.showToast("Undid move in preview", "info");
  }

  showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    const icon = type === "success" ? UI_ICONS.check : (type === "error" ? UI_ICONS.error : UI_ICONS.info);
    toast.innerHTML = `${icon}<span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(20px)";
      setTimeout(() => toast.remove(), 250);
    }, 2400);
  }

  /**
   * BIND DOM EVENTS
   */
  bindEvents() {
    // Toolbar buttons
    document.getElementById("btnNewLevel").addEventListener("click", () => this.openNewLevelModal());

    const btnNewFileSidebar = document.getElementById("btnNewFileSidebar");
    if (btnNewFileSidebar) {
      btnNewFileSidebar.addEventListener("click", () => this.openNewLevelModal());
    }

    const closeNewModal = () => {
      const m = document.getElementById("newLevelModal");
      if (m) m.classList.remove("active");
    };
    const btnCloseNew = document.getElementById("closeNewLevelModal");
    if (btnCloseNew) btnCloseNew.addEventListener("click", closeNewModal);
    const btnCancelNew = document.getElementById("btnCancelNewLevel");
    if (btnCancelNew) btnCancelNew.addEventListener("click", closeNewModal);

    const newFileInput = document.getElementById("newLevelFileNameInput");
    const newIdInput = document.getElementById("newLevelIdInput");
    if (newFileInput && newIdInput) {
      newIdInput.addEventListener("input", () => {
        newIdInput.dataset.manual = "true";
      });
      newFileInput.addEventListener("input", () => {
        if (newIdInput.dataset.manual !== "true") {
          newIdInput.value = newFileInput.value.replace(/\.json$/i, "");
        }
      });
    }

    const btnCreateOnly = document.getElementById("btnCreateLevelOnly");
    if (btnCreateOnly) btnCreateOnly.addEventListener("click", () => this.createNewLevelFromModal(false));

    const btnCreateDownload = document.getElementById("btnCreateAndDownload");
    if (btnCreateDownload) btnCreateDownload.addEventListener("click", () => this.createNewLevelFromModal(true));
    document.getElementById("btnUndo").addEventListener("click", () => {
      const prev = this.history.undo(this.getActiveLevel());
      if (prev) {
        const active = this.getActiveLevel();
        Object.assign(active, prev);
        this.loadLevelIntoEditor(active);
        this.requestAutoSave();
        this.showToast("Undo", "info");
      }
    });

    document.getElementById("btnRedo").addEventListener("click", () => {
      const next = this.history.redo(this.getActiveLevel());
      if (next) {
        const active = this.getActiveLevel();
        Object.assign(active, next);
        this.loadLevelIntoEditor(active);
        this.requestAutoSave();
        this.showToast("Redo", "info");
      }
    });

    document.getElementById("btnSave").addEventListener("click", async () => {
      await this.saveToStorage(true);
      this.showToast("Saved", "success");
    });

    document.getElementById("btnPreview").addEventListener("click", () => this.openPreviewMode());

    document.getElementById("btnCopyJson").addEventListener("click", () => this.copyJson());

    document.getElementById("btnExport").addEventListener("click", () => {
      ImportExportManager.exportLevel(this.getActiveLevel());
      this.showToast(`Exported ${this.getActiveLevel().levelId}.json`, "success");
    });

    // Folder browser controls
    const btnSelectFolder = document.getElementById("btnSelectFolder");
    if (btnSelectFolder) {
      btnSelectFolder.addEventListener("click", () => this.selectFolder());
    }

    const folderPicker = document.getElementById("folderPickerInput");
    if (folderPicker) {
      folderPicker.addEventListener("change", (e) => {
        if (e.target.files && e.target.files.length > 0) {
          this.loadFileList(e.target.files);
        }
      });
    }

    const folderSearch = document.getElementById("folderSearchInput");
    if (folderSearch) {
      folderSearch.addEventListener("input", (e) => {
        this.folderSearchQuery = e.target.value;
        this.renderFolderList();
      });
    }

    // Piece tools
    document.querySelectorAll(".tool-btn[data-tool]").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".tool-btn[data-tool]").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        this.activeTool = btn.dataset.tool;
        this.selectedSquare = null;
        this.legalMovesForSelected = [];
        this.renderBoard(this.getActiveLevel());
      });
    });

    // Quick board actions
    document.getElementById("btnFlipBoard").addEventListener("click", () => this.flipBoard());
    document.getElementById("btnRotateBoard").addEventListener("click", () => this.rotateBoard());
    document.getElementById("btnClearAll").addEventListener("click", () => this.clearBoard("ALL"));
    document.getElementById("btnClearRed").addEventListener("click", () => this.clearBoard("RED"));
    document.getElementById("btnClearBlack").addEventListener("click", () => this.clearBoard("BLACK"));
    document.getElementById("btnRandomSetup").addEventListener("click", () => this.randomSetup());

    // Sizing buttons
    document.querySelectorAll("[data-board-dim]").forEach(btn => {
      btn.addEventListener("click", () => {
        const dim = parseInt(btn.dataset.boardDim, 10);
        this.changeBoardDimensions(dim, dim);
      });
    });

    // Inspector inputs
    const idInput = document.getElementById("propLevelId");
    if (idInput) {
      idInput.addEventListener("input", (e) => {
        const lvl = this.getActiveLevel();
        lvl.levelId = e.target.value;
        this.updateStatus();
        this.runValidation(lvl);
        this.requestAutoSave();
      });
    }

    const diffSelect = document.getElementById("propDifficulty");
    if (diffSelect) {
      diffSelect.addEventListener("change", (e) => {
        const lvl = this.getActiveLevel();
        lvl.difficulty = e.target.value;
        this.updateStatus();
        this.requestAutoSave();
      });
    }

    const sizeSelect = document.getElementById("propBoardSize");
    if (sizeSelect) {
      sizeSelect.addEventListener("change", (e) => {
        const [r, c] = e.target.value.split("x").map(Number);
        this.changeBoardDimensions(r, c);
      });
    }

    const firstTurnSelect = document.getElementById("propFirstTurn");
    if (firstTurnSelect) {
      firstTurnSelect.addEventListener("change", (e) => {
        const lvl = this.getActiveLevel();
        lvl.firstTurn = parseInt(e.target.value, 10) === 1 ? 1 : 0;
        this.updateStatus();
        this.requestAutoSave();
      });
    }

    const chTypeSelect = document.getElementById("challengeTypeSelect");
    if (chTypeSelect) {
      chTypeSelect.addEventListener("change", (e) => {
        const lvl = this.getActiveLevel();
        lvl.challenge = lvl.challenge || {};
        lvl.challenge.type = e.target.value;

        const def = CONSTANTS.CHALLENGE_TYPES.find(c => c.type === e.target.value) || {};
        lvl.challenge.target = def.defaultTarget !== undefined ? def.defaultTarget : 1;
        lvl.challenge.moveLimit = def.defaultMoves !== undefined ? def.defaultMoves : 3;

        this.populateInspector(lvl);
        this.runValidation(lvl);
        this.requestAutoSave();
      });
    }

    const chTargetInput = document.getElementById("challengeTargetInput");
    if (chTargetInput) {
      chTargetInput.addEventListener("input", (e) => {
        const lvl = this.getActiveLevel();
        lvl.challenge = lvl.challenge || {};
        lvl.challenge.target = parseInt(e.target.value, 10) || 1;
        this.runValidation(lvl);
        this.requestAutoSave();
      });
    }

    const chMoveLimit = document.getElementById("challengeMoveLimitInput");
    if (chMoveLimit) {
      chMoveLimit.addEventListener("input", (e) => {
        const lvl = this.getActiveLevel();
        lvl.challenge = lvl.challenge || {};
        lvl.challenge.moveLimit = parseInt(e.target.value, 10) || 1;
        this.requestAutoSave();
      });
    }

    const btnPickRobotMove = document.getElementById("btnPickRobotMove");
    if (btnPickRobotMove) {
      btnPickRobotMove.addEventListener("click", () => {
        this.isPickingRobotMove = !this.isPickingRobotMove;
        this.robotMoveFrom = null;
        this.selectedSquare = null;
        btnPickRobotMove.classList.toggle("robot-move-pick-active", this.isPickingRobotMove);
        this.renderBoard(this.getActiveLevel());
        if (this.isPickingRobotMove) {
          this.showToast("Click the Robot piece (From) on the board", "info");
        }
      });
    }

    const btnClearRobotMoves = document.getElementById("btnClearRobotMoves");
    if (btnClearRobotMoves) {
      btnClearRobotMoves.addEventListener("click", () => {
        const lvl = this.getActiveLevel();
        lvl.robotMoves = [];
        this.isPickingRobotMove = false;
        this.robotMoveFrom = null;
        if (btnPickRobotMove) btnPickRobotMove.classList.remove("robot-move-pick-active");
        this.renderRobotMovesList(lvl);
        this.requestAutoSave();
        this.showToast("Cleared scripted Robot moves", "info");
      });
    }

    // Preview modal controls
    document.getElementById("closePreviewBtn").addEventListener("click", () => this.closePreviewMode());
    document.getElementById("previewResetBtn").addEventListener("click", () => this.openPreviewMode());
    document.getElementById("previewUndoBtn").addEventListener("click", () => this.undoPreviewMove());

    // Import JSON
    document.getElementById("btnImportJSON").addEventListener("click", () => {
      document.getElementById("importModal").classList.add("active");
    });

    document.getElementById("closeImportModal").addEventListener("click", () => {
      document.getElementById("importModal").classList.remove("active");
    });

    document.getElementById("btnExecuteImport").addEventListener("click", () => {
      const text = document.getElementById("importTextarea").value;
      this.executeImport(text);
    });

    const fileInput = document.getElementById("importFileInput");
    if (fileInput) {
      fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (event) => {
            document.getElementById("importTextarea").value = event.target.result;
          };
          reader.readAsText(file);
        }
      });
    }

    // Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA" || e.target.tagName === "SELECT") return;

      if ((e.ctrlKey || e.metaKey) && e.key === "z") {
        e.preventDefault();
        if (e.shiftKey) document.getElementById("btnRedo").click();
        else document.getElementById("btnUndo").click();
      } else if ((e.ctrlKey || e.metaKey) && e.key === "y") {
        e.preventDefault();
        document.getElementById("btnRedo").click();
      } else if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        document.getElementById("btnSave").click();
      } else if ((e.ctrlKey || e.metaKey) && e.key === "p") {
        e.preventDefault();
        if (this.isPreviewActive) this.closePreviewMode();
        else this.openPreviewMode();
      } else if (e.key === "Escape") {
        if (this.isPreviewActive) this.closePreviewMode();
        document.querySelectorAll(".modal-overlay").forEach(m => m.classList.remove("active"));
      }
    });
  }

  executeImport(jsonText) {
    const res = ImportExportManager.parseImportJSON(jsonText);
    if (!res.success || !res.levels || res.levels.length === 0) {
      alert(res.error || "No valid level found in JSON.");
      return;
    }

    this.history.push(this.getActiveLevel());
    this.activeFileIndex = -1;
    this.currentLevel = StorageManager.cleanInternalLevel(res.levels[0]);
    this.selectedSquare = null;
    this.legalMovesForSelected = [];

    this.renderFolderList();
    this.loadLevelIntoEditor(this.currentLevel);
    this.requestAutoSave();

    document.getElementById("importModal").classList.remove("active");
    this.showToast(`Loaded level ${this.currentLevel.levelId}`, "success");
  }
}
'''
