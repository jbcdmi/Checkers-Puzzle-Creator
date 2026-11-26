# generator/css_styles.py

CSS_CONTENT = '''
:root {
  --bg-app: #0f1117;
  --bg-sidebar: #161b22;
  --bg-panel: #1b2028;
  --bg-card: #21262d;
  --bg-card-hover: #29313d;
  --bg-input: #0d1117;
  --bg-active: #30363d;
  
  --border-subtle: #272d37;
  --border-focus: #58a6ff;
  --border-light: #363e4d;
  
  --text-primary: #f0f6fc;
  --text-secondary: #8b949e;
  --text-muted: #5c6570;
  --text-light: #ffffff;
  
  --accent-primary: #6366f1;
  --accent-primary-hover: #4f46e5;
  --accent-danger: #ea3943;
  --accent-danger-hover: #dc2626;
  --accent-success: #238636;
  --accent-success-hover: #2ea043;
  --accent-warning: #f59e0b;
  --accent-info: #388bfd;
  --accent-gold: #fbbf24;
  
  --board-dark-sq: #2d3748;
  --board-light-sq: #cbd5e1;
  --board-frame: #181d24;
  --board-frame-border: #3b4252;
  
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.4);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.5);
  --shadow-lg: 0 10px 25px rgba(0,0,0,0.6);
  
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 10px;
  --radius-full: 9999px;
  
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: var(--font-family);
  background-color: var(--bg-app);
  color: var(--text-primary);
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  user-select: none;
  font-size: 13px;
}

/* Scrollbars */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: var(--border-subtle);
  border-radius: var(--radius-sm);
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}

/* TOP TOOLBAR */
.app-toolbar {
  height: 52px;
  background-color: var(--bg-sidebar);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 20;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  font-size: 15px;
  letter-spacing: 0.5px;
  color: var(--text-primary);
}

.brand-logo svg {
  color: var(--accent-primary);
}

.brand-badge {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(6, 182, 212, 0.2));
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.4);
  padding: 2px 7px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-divider {
  width: 1px;
  height: 22px;
  background-color: var(--border-subtle);
  margin: 0 4px;
}

/* BUTTONS */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid var(--border-subtle);
  background-color: var(--bg-card);
  color: var(--text-primary);
  transition: all 0.15s ease;
  white-space: nowrap;
}

.btn:hover {
  background-color: var(--bg-card-hover);
  border-color: var(--border-light);
}

.btn:active {
  transform: translateY(1px);
}

.btn-primary {
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.btn-primary:hover {
  background-color: var(--accent-primary-hover);
  border-color: var(--accent-primary-hover);
}

.btn-success {
  background-color: var(--accent-success);
  border-color: var(--accent-success);
  color: #ffffff;
}

.btn-success:hover {
  background-color: var(--accent-success-hover);
  border-color: var(--accent-success-hover);
}

.btn-danger {
  background-color: rgba(234, 57, 67, 0.15);
  border-color: rgba(234, 57, 67, 0.4);
  color: #f87171;
}

.btn-danger:hover {
  background-color: var(--accent-danger);
  border-color: var(--accent-danger);
  color: #ffffff;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}

.btn-icon {
  padding: 6px;
  border-radius: var(--radius-md);
}

/* MAIN LAYOUT */
.app-workspace {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* LEFT SIDEBAR - LEVEL LIBRARY */
.sidebar-left {
  width: 270px;
  min-width: 240px;
  background-color: var(--bg-sidebar);
  border-right: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10;
}

.sidebar-header {
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box svg {
  position: absolute;
  left: 10px;
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 7px 10px 7px 32px;
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-size: 12px;
  outline: none;
}

.search-input:focus {
  border-color: var(--border-focus);
}

.folder-path-pill {
  font-size: 11px;
  color: var(--text-secondary);
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 5px 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-name-sub {
  font-size: 10px;
  font-family: var(--font-mono);
  color: var(--text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.filter-row {
  display: flex;
  gap: 6px;
}

.select-filter {
  flex: 1;
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  padding: 5px 8px;
  border-radius: var(--radius-md);
  font-size: 11px;
  outline: none;
}

.select-filter:focus {
  border-color: var(--border-focus);
  color: var(--text-primary);
}

/* LEVEL LIST */
.level-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.level-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.15s ease;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.level-card:hover {
  background-color: var(--bg-card-hover);
  border-color: var(--border-light);
}

.level-card.active {
  border-color: var(--accent-primary);
  background-color: rgba(99, 102, 241, 0.1);
  box-shadow: 0 0 0 1px var(--accent-primary);
}

.level-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.level-id-badge {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 700;
  padding: 2px 6px;
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
}

.badge {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  text-transform: uppercase;
}

.badge-beginner {
  background-color: rgba(35, 134, 54, 0.2);
  color: #4ade80;
  border: 1px solid rgba(35, 134, 54, 0.4);
}

.badge-intermediate {
  background-color: rgba(56, 139, 253, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(56, 139, 253, 0.4);
}

.badge-advanced {
  background-color: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.badge-expert {
  background-color: rgba(234, 57, 67, 0.2);
  color: #f87171;
  border: 1px solid rgba(234, 57, 67, 0.4);
}

.level-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sidebar-footer {
  padding: 10px 14px;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-sidebar);
}

/* CENTER PANEL - BOARD EDITOR */
.center-panel {
  flex: 1;
  background-color: var(--bg-app);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* BOARD TOOLBAR */
.board-toolbar {
  padding: 8px 16px;
  background-color: var(--bg-panel);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.board-tools-group {
  display: flex;
  align-items: center;
  gap: 4px;
  background-color: var(--bg-card);
  padding: 3px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.tool-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 9px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.15s ease;
}

.tool-btn:hover {
  background-color: var(--bg-card-hover);
  color: var(--text-primary);
}

.tool-btn.active {
  background-color: var(--bg-active);
  color: var(--text-primary);
  border-color: var(--border-light);
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.tool-piece-preview {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tool-piece-preview svg {
  width: 100%;
  height: 100%;
}

.board-quick-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* BOARD STAGE */
.board-stage {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  overflow: auto;
  position: relative;
  background: radial-gradient(circle at center, #181d25 0%, #0d1015 100%);
}

.board-outer-frame {
  display: flex;
  flex-direction: column;
  background-color: var(--board-frame);
  border: 2px solid var(--board-frame-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255,255,255,0.05);
  padding: 12px;
  position: relative;
  transition: transform 0.3s ease;
}

.board-coords-top, .board-coords-bottom {
  display: flex;
  height: 20px;
  margin-left: 20px;
  margin-right: 20px;
}

.board-coords-left, .board-coords-right {
  display: flex;
  flex-direction: column;
  width: 20px;
}

.coord-label {
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
}

.board-inner-row {
  display: flex;
}

/* THE CHECKERS BOARD GRID */
.checkers-board {
  display: grid;
  background-color: var(--board-dark-sq);
  border: 2px solid #1a202c;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.board-square {
  width: 60px;
  height: 60px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.sq-coord-hint {
  position: absolute;
  top: 2px;
  left: 4px;
  font-size: 9px;
  font-family: var(--font-mono);
  font-weight: 600;
  opacity: 0.45;
  pointer-events: none;
  z-index: 1;
}

.sq-dark .sq-coord-hint {
  color: #cbd5e1;
}

.sq-light .sq-coord-hint {
  color: #334155;
}

.robot-move-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 5px 8px;
  font-size: 11px;
  font-family: var(--font-mono);
}

.btn.robot-move-pick-active {
  background-color: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #ffffff;
}

.sq-dark {
  background-color: var(--board-dark-sq);
}

.sq-light {
  background-color: var(--board-light-sq);
  cursor: not-allowed;
}

.sq-dark:hover {
  filter: brightness(1.15);
}

.sq-selected {
  box-shadow: inset 0 0 0 3px var(--accent-gold);
}

.sq-legal-move::before {
  content: "";
  position: absolute;
  width: 18px;
  height: 18px;
  background-color: rgba(34, 197, 94, 0.7);
  border-radius: 50%;
  pointer-events: none;
  box-shadow: 0 0 10px rgba(34, 197, 94, 0.9);
}

.sq-legal-capture::before {
  content: "";
  position: absolute;
  width: 32px;
  height: 32px;
  border: 3px solid rgba(239, 68, 68, 0.9);
  border-radius: 50%;
  pointer-events: none;
  box-shadow: 0 0 12px rgba(239, 68, 68, 0.9);
}

.sq-drag-over {
  box-shadow: inset 0 0 0 3px var(--accent-info) !important;
}

/* PIECES */
.checkers-piece {
  width: 86%;
  height: 86%;
  display: block;
  cursor: grab;
  transition: transform 0.15s ease;
  z-index: 2;
}

.checkers-piece:hover {
  transform: scale(1.05);
}

.checkers-piece:active {
  cursor: grabbing;
}

/* RIGHT SIDEBAR - SIMPLE INSPECTOR */
.sidebar-right {
  width: 290px;
  min-width: 260px;
  background-color: var(--bg-sidebar);
  border-left: 1px solid var(--border-subtle);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10;
}

.tab-content {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* FORM ELEMENTS */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input, .form-select, .form-textarea {
  background-color: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  padding: 7px 10px;
  font-size: 12px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s ease;
}

.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: var(--border-focus);
}

.form-row {
  display: flex;
  gap: 8px;
}

.form-row > * {
  flex: 1;
}

/* CARDS IN SIDEBAR */
.config-card {
  background-color: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-subtle);
  padding-bottom: 6px;
  font-weight: 600;
  font-size: 12px;
  color: var(--text-primary);
}

/* VALIDATION ALERT */
.validation-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  font-size: 12px;
}

.validation-item.error {
  background-color: rgba(234, 57, 67, 0.1);
  border-color: rgba(234, 57, 67, 0.3);
  color: #fca5a5;
}

.validation-item.warning {
  background-color: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.3);
  color: #fde047;
}

.validation-item.success {
  background-color: rgba(35, 134, 54, 0.1);
  border-color: rgba(35, 134, 54, 0.3);
  color: #86efac;
}

/* BOTTOM STATUS BAR */
.app-statusbar {
  height: 32px;
  background-color: var(--bg-sidebar);
  border-top: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  font-size: 11px;
  color: var(--text-secondary);
  z-index: 20;
}

.status-group {
  display: flex;
  align-items: center;
  gap: 14px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.status-indicator {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background-color: var(--accent-success);
}

.status-indicator.saving {
  background-color: var(--accent-warning);
}

/* MODALS */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.modal-overlay.active {
  opacity: 1;
  pointer-events: auto;
}

.modal-dialog {
  background-color: var(--bg-panel);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 560px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: var(--bg-card);
}

.modal-title {
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-footer {
  padding: 10px 16px;
  border-top: 1px solid var(--border-subtle);
  background-color: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

/* LIVE PREVIEW MODAL SPECIFICS */
.preview-modal-dialog {
  width: 90vw;
  max-width: 960px;
  height: 85vh;
}

.preview-hud {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background-color: var(--bg-sidebar);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  margin: 10px 16px 0 16px;
}

.preview-objective-title {
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 600;
}

.preview-objective-desc {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-bar-container {
  width: 140px;
  height: 6px;
  background-color: var(--bg-input);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: var(--accent-primary);
  transition: width 0.3s ease;
}

.preview-stage-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.preview-result-banner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(15, 17, 23, 0.95);
  border: 2px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 20px 30px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.8);
  z-index: 50;
}

.preview-result-banner.victory { border-color: var(--accent-success); }
.preview-result-banner.defeat { border-color: var(--accent-danger); }

/* TOAST */
.toast-container {
  position: fixed;
  bottom: 42px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 2000;
  pointer-events: none;
}

.toast {
  background-color: var(--bg-card);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-lg);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  pointer-events: auto;
}

.toast-success { border-left: 3px solid var(--accent-success); }
.toast-error { border-left: 3px solid var(--accent-danger); }
.toast-info { border-left: 3px solid var(--accent-info); }
'''
