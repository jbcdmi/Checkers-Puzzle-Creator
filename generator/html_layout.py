# generator/html_layout.py

def get_html_layout(css_content, js_engine, js_managers, js_ui, svg_pieces_json, ui_icons_json):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Checkers Level Creator</title>
  <style>
{css_content}
  </style>
</head>
<body>

  <!-- TOP TOOLBAR -->
  <header class="app-toolbar">
    <div class="brand-section">
      <div class="brand-logo">
        <svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/><path d="M7 7h4v4H7zm6 0h4v4h-4zm-6 6h4v4H7zm6 0h4v4h-4z"/></svg>
        <span>CHECKERS CREATOR</span>
      </div>
      <span class="brand-badge">Simple Studio</span>
    </div>

    <div class="toolbar-actions">
      <button class="btn btn-primary" id="btnNewLevel">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
        New Level
      </button>

      <div class="toolbar-divider"></div>

      <button class="btn btn-icon" id="btnUndo" title="Undo (Ctrl+Z)">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/></svg>
      </button>
      <button class="btn btn-icon" id="btnRedo" title="Redo (Ctrl+Y)">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M18.4 10.6C16.55 8.99 14.15 8 11.5 8c-4.65 0-8.58 3.03-9.96 7.22L3.9 16c1.05-3.19 4.05-5.5 7.6-5.5 1.95 0 3.73.72 5.12 1.88L13 16h9V7l-3.6 3.6z"/></svg>
      </button>

      <div class="toolbar-divider"></div>

      <button class="btn btn-success" id="btnPreview" title="Playtest Level in Preview Mode (Ctrl+P)">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
        Preview / Play
      </button>

      <button class="btn" id="btnSave" title="Save All Work (Ctrl+S)">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M17 3H5c-1.1 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>
        Save
      </button>

      <button class="btn" id="btnCopyJson" title="Copy Level JSON to Clipboard">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>
        Copy JSON
      </button>

      <button class="btn" id="btnExport" title="Export Current Level as JSON">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
        Export JSON
      </button>
    </div>
  </header>

  <!-- MAIN WORKSPACE -->
  <main class="app-workspace">

    <!-- LEFT SIDEBAR: FOLDER LEVEL BROWSER -->
    <aside class="sidebar-left">
      <div class="sidebar-header">
        <div class="sidebar-title-row">
          <span class="sidebar-title">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M10 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z"/></svg>
            Folder Levels
          </span>
          <span class="level-id-badge" id="folderCountBadge">0 files</span>
        </div>

        <div style="display:flex; gap:6px;">
          <button class="btn btn-primary" id="btnSelectFolder" style="flex:1; justify-content:center;">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/></svg>
            Select Folder
          </button>
          <button class="btn" id="btnNewFileSidebar" title="Create New Level File">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 14h-3v3h-2v-3H8v-2h3v-3h2v3h3v2zm-3-7V3.5L18.5 9H13z"/></svg>
            New File
          </button>
        </div>
        <input type="file" id="folderPickerInput" webkitdirectory directory multiple style="display:none;" />

        <div class="folder-path-pill" id="folderNameDisplay" title="No folder selected">No folder selected</div>

        <div class="search-box">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
          <input type="text" class="search-input" id="folderSearchInput" placeholder="Filter files in folder..." />
        </div>
      </div>

      <!-- FOLDER FILE LIST -->
      <div class="level-list-container" id="folderFileList">
        <!-- Injected via JavaScript -->
      </div>

      <!-- SIDEBAR FOOTER -->
      <div class="sidebar-footer">
        <button class="btn btn-sm" id="btnImportJSON" style="width:100%; justify-content:center;">
          <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z"/></svg>
          Import / Paste JSON
        </button>
      </div>
    </aside>

    <!-- CENTER PANEL: INTERACTIVE CHECKERS BOARD -->
    <section class="center-panel">

      <!-- BOARD TOOLBAR -->
      <div class="board-toolbar">
        <div class="board-tools-group">
          <!-- RED NORMAL -->
          <button class="tool-btn active" data-tool="RED_NORMAL" title="Place Red Normal Piece">
            <span class="tool-piece-preview">
              <svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="#e02424" stroke="#7f1d1d" stroke-width="6"/><circle cx="50" cy="50" r="24" fill="#b91c1c"/></svg>
            </span>
            <span>Red</span>
          </button>

          <!-- RED KING -->
          <button class="tool-btn" data-tool="RED_KING" title="Place Red King Piece">
            <span class="tool-piece-preview">
              <svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="#e02424" stroke="#7f1d1d" stroke-width="6"/><path d="M30 63 L70 63 L67 43 L50 53 L33 43 Z" fill="#fbbf24"/></svg>
            </span>
            <span>Red King</span>
          </button>

          <!-- BLACK NORMAL -->
          <button class="tool-btn" data-tool="BLACK_NORMAL" title="Place Black Normal Piece">
            <span class="tool-piece-preview">
              <svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="#1e293b" stroke="#090d16" stroke-width="6"/><circle cx="50" cy="50" r="24" fill="#0f172a"/></svg>
            </span>
            <span>Black</span>
          </button>

          <!-- BLACK KING -->
          <button class="tool-btn" data-tool="BLACK_KING" title="Place Black King Piece">
            <span class="tool-piece-preview">
              <svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="42" fill="#1e293b" stroke="#090d16" stroke-width="6"/><path d="M30 63 L70 63 L67 43 L50 53 L33 43 Z" fill="#fbbf24"/></svg>
            </span>
            <span>Black King</span>
          </button>

          <!-- ERASER -->
          <button class="tool-btn" data-tool="ERASER" title="Eraser: Remove Piece on Click">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M15.14 3c-.4 0-.8.15-1.11.45l-9.58 9.58c-.62.62-.62 1.61 0 2.23l5.29 5.29c.61.62 1.6.62 2.22 0l9.58-9.58c.62-.62.62-1.61 0-2.23L16.25 3.45c-.31-.3-.71-.45-1.11-.45zM4.22 15.58l4.49-4.49 4.2 4.2-4.49 4.49-4.2-4.2z"/></svg>
            <span>Eraser</span>
          </button>

          <!-- MOVE / SELECT -->
          <button class="tool-btn" data-tool="MOVE" title="Select and Move Pieces">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M10 9h4V6h3l-5-5-5 5h3v3zm-1 1H6V7l-5 5 5 5v-3h3v-4zm14 2l-5-5v3h-3v4h3v3l5-5zm-9 3h-4v3H7l5 5 5-5h-3v-3z"/></svg>
            <span>Move</span>
          </button>
        </div>

        <!-- QUICK SIZING -->
        <div class="board-tools-group">
          <span style="font-size:11px; font-weight:600; color:var(--text-muted); padding-left:4px;">Size:</span>
          <button class="tool-btn" data-board-dim="6">6×6</button>
          <button class="tool-btn" data-board-dim="8">8×8</button>
          <button class="tool-btn" data-board-dim="10">10×10</button>
          <button class="tool-btn" data-board-dim="12">12×12</button>
        </div>

        <!-- QUICK ACTIONS -->
        <div class="board-quick-actions">
          <button class="btn btn-icon btn-sm" id="btnFlipBoard" title="Flip Board 180°">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M15 21h2v-2h-2v2zm4-12h2V7h-2v2zM3 5v14c0 1.1.9 2 2 2h4v-2H5V5h4V3H5c-1.1 0-2 .9-2 2zm16-2v2h2c0-1.1-.9-2-2-2zm-8 20h2V1h-2v22zm8-6h2v-2h-2v2zM15 5h2V3h-2v2zm4 8h2v-2h-2v2z"/></svg>
          </button>
          <button class="btn btn-icon btn-sm" id="btnRotateBoard" title="Rotate Board 90°">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M7.11 8.53L5.7 7.11C4.8 8.27 4.24 9.61 4.07 11h2.02c.14-.87.49-1.72 1.02-2.47zM6.09 13H4.07c.17 1.39.72 2.73 1.62 3.89l1.41-1.42c-.52-.75-.87-1.59-1.01-2.47zm1.01 5.32c1.16.9 2.51 1.44 3.9 1.61V17.9c-.87-.15-1.71-.49-2.46-1.03L7.1 18.32zM13 4.07V1L8.45 5.55 13 10V6.09c3.37 0 6.09 2.72 6.09 6.09s-2.72 6.09-6.09 6.09v2.02c4.49 0 8.11-3.62 8.11-8.11s-3.62-8.02-8.11-8.02z"/></svg>
          </button>
          <button class="btn btn-sm" id="btnRandomSetup" title="Generate Random Valid Position">Random</button>
          <button class="btn btn-sm btn-danger" id="btnClearRed" title="Clear Red Pieces">Clear Red</button>
          <button class="btn btn-sm btn-danger" id="btnClearBlack" title="Clear Black Pieces">Clear Black</button>
          <button class="btn btn-sm btn-danger" id="btnClearAll" title="Clear Board">Clear All</button>
        </div>
      </div>

      <!-- BOARD STAGE -->
      <div class="board-stage">
        <div class="board-outer-frame" id="boardOuterFrame">
          <div class="board-coords-top" id="boardCoordsTop"></div>
          <div class="board-inner-row">
            <div class="board-coords-left" id="boardCoordsLeft"></div>
            <div class="checkers-board" id="checkersBoard"></div>
            <div class="board-coords-right" id="boardCoordsRight"></div>
          </div>
          <div class="board-coords-bottom" id="boardCoordsBottom"></div>
        </div>
      </div>
    </section>

    <!-- RIGHT SIDEBAR: SIMPLE LEVEL INSPECTOR -->
    <aside class="sidebar-right">
      <div class="sidebar-header" style="border-bottom: 1px solid var(--border-subtle);">
        <span class="sidebar-title">Level Settings</span>
      </div>

      <div class="tab-content">
        <div class="config-card">
          <div class="form-group">
            <label class="form-label">Level ID</label>
            <input type="text" class="form-input" id="propLevelId" placeholder="e.g. CHK_001" />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Difficulty</label>
              <select class="form-select" id="propDifficulty">
                <option value="BEGINNER">Beginner</option>
                <option value="INTERMEDIATE">Intermediate</option>
                <option value="ADVANCED">Advanced</option>
                <option value="EXPERT">Expert</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Board Size</label>
              <select class="form-select" id="propBoardSize">
                <option value="6x6">6 × 6</option>
                <option value="8x8">8 × 8</option>
                <option value="10x10">10 × 10</option>
                <option value="12x12">12 × 12</option>
              </select>
            </div>
          </div>

          <div class="form-group" style="margin-top:8px;">
            <label class="form-label">First Turn</label>
            <select class="form-select" id="propFirstTurn">
              <option value="0" selected>Player First (0)</option>
              <option value="1">Robot First (1)</option>
            </select>
          </div>
        </div>

        <!-- CHALLENGE GOAL -->
        <div class="config-card">
          <div class="config-card-header">Challenge Goal</div>
          <div class="form-group">
            <label class="form-label">Goal Type</label>
            <select class="form-select" id="challengeTypeSelect"></select>
          </div>

          <div class="form-row" id="challengeTargetRow">
            <div class="form-group">
              <label class="form-label">Target Count</label>
              <input type="number" class="form-input" id="challengeTargetInput" value="1" min="1" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Move Limit</label>
            <input type="number" class="form-input" id="challengeMoveLimitInput" value="3" min="1" />
          </div>
        </div>

        <!-- SCRIPTED ROBOT MOVES -->
        <div class="config-card">
          <div class="config-card-header" style="display:flex; align-items:center; justify-content:space-between;">
            <span>Robot Moves (Optional)</span>
            <div style="display:flex; gap:4px;">
              <button class="btn btn-sm" id="btnPickRobotMove" title="Click From and To squares on the board">Pick on Board</button>
              <button class="btn btn-sm btn-danger" id="btnClearRobotMoves" title="Clear all scripted robot moves">Clear</button>
            </div>
          </div>
          <div id="robotMovesList" style="display:flex; flex-direction:column; gap:6px; margin-top:6px;"></div>
        </div>

        <!-- VALIDATION STATUS ALERT -->
        <div id="validationAlert" class="validation-item success">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
          <span>Level configuration is ready.</span>
        </div>
      </div>
    </aside>

  </main>

  <!-- BOTTOM STATUS BAR -->
  <footer class="app-statusbar">
    <div class="status-group">
      <div class="status-item">
        <span class="status-indicator" id="statusIndicator"></span>
        <span id="statusSaveText">Saved</span>
      </div>
      <div class="status-item">Level: <b id="statusLevelId" style="color:var(--text-primary); margin-left:3px;">CHK_001</b></div>
      <div class="status-item">Board: <b id="statusDims" style="color:var(--text-primary); margin-left:3px;">8×8</b></div>
    </div>

    <div class="status-group">
      <div class="status-item"><b id="statusRedCount" style="color:var(--accent-danger);">0 Red</b></div>
      <div class="status-item"><b id="statusBlackCount" style="color:#94a3b8;">0 Black</b></div>
      <div class="status-item"><span id="statusFirstTurn">Player First</span></div>
      <div class="status-item"><span id="statusDifficulty">BEGINNER</span></div>
    </div>
  </footer>

  <!-- LIVE PUZZLE PREVIEW MODAL -->
  <div class="modal-overlay" id="previewModal">
    <div class="modal-dialog preview-modal-dialog">
      <div class="modal-header">
        <div class="modal-title">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>
          <span id="previewLevelTitle">Level Preview</span>
          <span class="badge badge-beginner" id="previewDifficultyBadge">BEGINNER</span>
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
          <button class="btn btn-sm" id="previewUndoBtn" title="Undo Move">Undo</button>
          <button class="btn btn-sm" id="previewResetBtn" title="Restart Puzzle">Restart</button>
          <button class="btn btn-sm btn-danger" id="closePreviewBtn">Exit</button>
        </div>
      </div>

      <div class="preview-hud">
        <div class="preview-objective-box">
          <span class="preview-objective-title">Goal</span>
          <span class="preview-objective-desc" id="previewChallengeDesc">Capture Pieces</span>
        </div>

        <div style="display:flex; align-items:center; gap:16px;">
          <div style="display:flex; flex-direction:column; gap:4px;">
            <div class="progress-bar-container">
              <div class="progress-bar-fill" id="previewProgressFill" style="width:0%;"></div>
            </div>
          </div>
          <span style="font-size:12px; font-weight:700;" id="previewMovesCount">Moves: 0</span>
        </div>
      </div>

      <div class="preview-stage-container">
        <div class="checkers-board" id="previewCheckersBoard"></div>
        <div class="preview-result-banner" id="previewResultBanner" style="display:none;"></div>
      </div>
    </div>
  </div>

  <!-- IMPORT JSON MODAL -->
  <div class="modal-overlay" id="importModal">
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z"/></svg>
          Import JSON Levels
        </div>
        <button class="btn btn-icon btn-sm" id="closeImportModal">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label class="form-label">Select JSON File</label>
          <input type="file" id="importFileInput" accept=".json" class="form-input" />
        </div>
        <div class="form-group">
          <label class="form-label">Or Paste JSON Data</label>
          <textarea class="form-textarea" id="importTextarea" style="min-height:160px; font-family:var(--font-mono); font-size:11px;" placeholder="Paste single level or levels array JSON..."></textarea>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary" id="btnExecuteImport">Import</button>
      </div>
    </div>
  </div>

  <!-- NEW LEVEL / NEW FILE MODAL -->
  <div class="modal-overlay" id="newLevelModal">
    <div class="modal-dialog">
      <div class="modal-header">
        <div class="modal-title">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 14h-3v3h-2v-3H8v-2h3v-3h2v3h3v2zm-3-7V3.5L18.5 9H13z"/></svg>
          Create New Level / File
        </div>
        <button class="btn btn-icon btn-sm" id="closeNewLevelModal">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
        </button>
      </div>
      <div class="modal-body">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">File Name</label>
            <input type="text" class="form-input" id="newLevelFileNameInput" placeholder="e.g. 1.json" />
          </div>
          <div class="form-group">
            <label class="form-label">Level ID</label>
            <input type="text" class="form-input" id="newLevelIdInput" placeholder="e.g. 1" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Difficulty</label>
            <select class="form-select" id="newLevelDifficultySelect">
              <option value="BEGINNER">Beginner</option>
              <option value="INTERMEDIATE">Intermediate</option>
              <option value="ADVANCED">Advanced</option>
              <option value="EXPERT">Expert</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Board Size</label>
            <select class="form-select" id="newLevelBoardSizeSelect">
              <option value="6">6 × 6</option>
              <option value="8" selected>8 × 8</option>
              <option value="10">10 × 10</option>
              <option value="12">12 × 12</option>
            </select>
          </div>
        </div>
        <div class="folder-path-pill" id="newLevelModalHint" style="white-space:normal; line-height:1.4;">
          Creates a new level and optionally saves a new .json file.
        </div>
      </div>
      <div class="modal-footer" style="display:flex; justify-content:flex-end; gap:8px;">
        <button class="btn" id="btnCancelNewLevel">Cancel</button>
        <button class="btn btn-primary" id="btnCreateLevelOnly">Create Level</button>
        <button class="btn btn-success" id="btnCreateAndDownload">Create &amp; Download .json</button>
      </div>
    </div>
  </div>

  <!-- TOAST CONTAINER -->
  <div class="toast-container" id="toastContainer"></div>

  <!-- JAVASCRIPT RUNTIME -->
  <script>
    const SVG_PIECES = {svg_pieces_json};
    const UI_ICONS = {ui_icons_json};

{js_engine}

{js_managers}

{js_ui}

    window.addEventListener("DOMContentLoaded", () => {{
      window.app = new UIManager();
      window.app.init();
    }});
  </script>
</body>
</html>
'''
