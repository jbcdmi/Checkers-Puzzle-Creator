# generator/svg_icons.py

SVG_PIECES = {
    "RED_NORMAL": '''<svg viewBox="0 0 100 100" class="checkers-piece piece-red-normal">
  <defs>
    <radialGradient id="redNormalGrad" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#ff6b6b"/>
      <stop offset="45%" stop-color="#e02424"/>
      <stop offset="85%" stop-color="#991b1b"/>
      <stop offset="100%" stop-color="#580e0e"/>
    </radialGradient>
    <filter id="pieceShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>
  <circle cx="50" cy="50" r="44" fill="url(#redNormalGrad)" stroke="#7f1d1d" stroke-width="2.5" filter="url(#pieceShadow)"/>
  <circle cx="50" cy="50" r="34" fill="none" stroke="#f87171" stroke-width="1.8" stroke-dasharray="none" opacity="0.6"/>
  <circle cx="50" cy="50" r="24" fill="#b91c1c" stroke="#7f1d1d" stroke-width="1.5"/>
  <circle cx="50" cy="50" r="14" fill="none" stroke="#fca5a5" stroke-width="1.2" opacity="0.5"/>
</svg>''',

    "RED_KING": '''<svg viewBox="0 0 100 100" class="checkers-piece piece-red-king">
  <defs>
    <radialGradient id="redKingGrad" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#ff6b6b"/>
      <stop offset="45%" stop-color="#e02424"/>
      <stop offset="85%" stop-color="#991b1b"/>
      <stop offset="100%" stop-color="#580e0e"/>
    </radialGradient>
    <linearGradient id="goldCrownGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#fef08a"/>
      <stop offset="50%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#b45309"/>
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="44" fill="url(#redKingGrad)" stroke="#7f1d1d" stroke-width="2.5" filter="url(#pieceShadow)"/>
  <circle cx="50" cy="50" r="34" fill="none" stroke="#f87171" stroke-width="1.8" opacity="0.6"/>
  <circle cx="50" cy="50" r="26" fill="#991b1b" stroke="#f59e0b" stroke-width="1.8"/>
  <!-- King Crown Emboss -->
  <g transform="translate(0, -2)">
    <path d="M30 63 L70 63 L67 43 L50 53 L33 43 Z" fill="url(#goldCrownGrad)" stroke="#78350f" stroke-width="1.5"/>
    <circle cx="33" cy="41" r="2.5" fill="#fef08a" stroke="#78350f" stroke-width="1"/>
    <circle cx="50" cy="51" r="2.5" fill="#fef08a" stroke="#78350f" stroke-width="1"/>
    <circle cx="67" cy="41" r="2.5" fill="#fef08a" stroke="#78350f" stroke-width="1"/>
    <rect x="33" y="61" width="34" height="4" rx="2" fill="#d97706"/>
  </g>
</svg>''',

    "BLACK_NORMAL": '''<svg viewBox="0 0 100 100" class="checkers-piece piece-black-normal">
  <defs>
    <radialGradient id="blackNormalGrad" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#475569"/>
      <stop offset="45%" stop-color="#1e293b"/>
      <stop offset="85%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#020617"/>
    </radialGradient>
  </defs>
  <circle cx="50" cy="50" r="44" fill="url(#blackNormalGrad)" stroke="#090d16" stroke-width="2.5" filter="url(#pieceShadow)"/>
  <circle cx="50" cy="50" r="34" fill="none" stroke="#64748b" stroke-width="1.8" opacity="0.6"/>
  <circle cx="50" cy="50" r="24" fill="#1e293b" stroke="#090d16" stroke-width="1.5"/>
  <circle cx="50" cy="50" r="14" fill="none" stroke="#94a3b8" stroke-width="1.2" opacity="0.5"/>
</svg>''',

    "BLACK_KING": '''<svg viewBox="0 0 100 100" class="checkers-piece piece-black-king">
  <defs>
    <radialGradient id="blackKingGrad" cx="35%" cy="35%" r="65%">
      <stop offset="0%" stop-color="#475569"/>
      <stop offset="45%" stop-color="#1e293b"/>
      <stop offset="85%" stop-color="#0f172a"/>
      <stop offset="100%" stop-color="#020617"/>
    </radialGradient>
  </defs>
  <circle cx="50" cy="50" r="44" fill="url(#blackKingGrad)" stroke="#090d16" stroke-width="2.5" filter="url(#pieceShadow)"/>
  <circle cx="50" cy="50" r="34" fill="none" stroke="#64748b" stroke-width="1.8" opacity="0.6"/>
  <circle cx="50" cy="50" r="26" fill="#0f172a" stroke="#f59e0b" stroke-width="1.8"/>
  <!-- King Crown Emboss -->
  <g transform="translate(0, -2)">
    <path d="M30 63 L70 63 L67 43 L50 53 L33 43 Z" fill="url(#goldCrownGrad)" stroke="#78350f" stroke-width="1.5"/>
    <circle cx="33" cy="41" r="2.5" fill="#fef08a" stroke="#78350f" stroke-width="1"/>
    <circle cx="50" cy="51" r="2.5" fill="#fef08a" stroke="#78350f" stroke-width="1"/>
    <circle cx="67" cy="41" r="2.5" fill="#fef08a" stroke="#78350f" stroke-width="1"/>
    <rect x="33" y="61" width="34" height="4" rx="2" fill="#d97706"/>
  </g>
</svg>'''
}

UI_ICONS = {
    "crown": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/></svg>''',
    "undo": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12.5 8c-2.65 0-5.05.99-6.9 2.6L2 7v9h9l-3.62-3.62c1.39-1.16 3.16-1.88 5.12-1.88 3.54 0 6.55 2.31 7.6 5.5l2.37-.78C21.08 11.03 17.15 8 12.5 8z"/></svg>''',
    "redo": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M18.4 10.6C16.55 8.99 14.15 8 11.5 8c-4.65 0-8.58 3.03-9.96 7.22L3.9 16c1.05-3.19 4.05-5.5 7.6-5.5 1.95 0 3.73.72 5.12 1.88L13 16h9V7l-3.6 3.6z"/></svg>''',
    "save": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>''',
    "export": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>''',
    "import": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M9 16h6v-6h4l-7-7-7 7h4v6zm-4 2h14v2H5v-2z"/></svg>''',
    "play": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>''',
    "check": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>''',
    "alert": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/></svg>''',
    "error": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>''',
    "trash": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>''',
    "duplicate": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>''',
    "plus": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>''',
    "search": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>''',
    "flip": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M15 21h2v-2h-2v2zm4-12h2V7h-2v2zM3 5v14c0 1.1.9 2 2 2h4v-2H5V5h4V3H5c-1.1 0-2 .9-2 2zm16-2v2h2c0-1.1-.9-2-2-2zm-8 20h2V1h-2v22zm8-6h2v-2h-2v2zM15 5h2V3h-2v2zm4 8h2v-2h-2v2z"/></svg>''',
    "rotate": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M7.11 8.53L5.7 7.11C4.8 8.27 4.24 9.61 4.07 11h2.02c.14-.87.49-1.72 1.02-2.47zM6.09 13H4.07c.17 1.39.72 2.73 1.62 3.89l1.41-1.42c-.52-.75-.87-1.59-1.01-2.47zm1.01 5.32c1.16.9 2.51 1.44 3.9 1.61V17.9c-.87-.15-1.71-.49-2.46-1.03L7.1 18.32zM13 4.07V1L8.45 5.55 13 10V6.09c3.37 0 6.09 2.72 6.09 6.09s-2.72 6.09-6.09 6.09v2.02c4.49 0 8.11-3.62 8.11-8.11s-3.62-8.02-8.11-8.02z"/></svg>''',
    "eraser": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M15.14 3c-.4 0-.8.15-1.11.45l-9.58 9.58c-.62.62-.62 1.61 0 2.23l5.29 5.29c.61.62 1.6.62 2.22 0l9.58-9.58c.62-.62.62-1.61 0-2.23L16.25 3.45c-.31-.3-.71-.45-1.11-.45zM4.22 15.58l4.49-4.49 4.2 4.2-4.49 4.49-4.2-4.2z"/></svg>''',
    "move": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M10 9h4V6h3l-5-5-5 5h3v3zm-1 1H6V7l-5 5 5 5v-3h3v-4zm14 2l-5-5v3h-3v4h3v3l5-5zm-9 3h-4v3H7l5 5 5-5h-3v-3z"/></svg>''',
    "shuffle": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/></svg>''',
    "reset": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>''',
    "hint": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z"/></svg>''',
    "info": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>''',
    "close": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>''',
    "record": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><circle cx="12" cy="12" r="8"/></svg>''',
    "help": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 16h-2v-2h2v2zm1.07-7.75l-.9.92C12.45 11.9 12 12.5 12 14h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H7c0-2.76 2.24-5 5-5s5 2.24 5 5c0 .88-.36 1.68-.93 2.25z"/></svg>''',
    "template": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/></svg>''',
    "filter": '''<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><path d="M10 18h4v-2h-4v2zM3 6v2h18V6H3zm3 7h12v-2H6v2z"/></svg>'''
}

