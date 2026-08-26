"""Embedded offline user interface for the Claude Chat Exporter."""

HTML: str = r"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="dark">
  <title>Claude Chat Exporter</title>
  <style>
    :root {
      --bg: #0b0c0d;
      --surface: #111315;
      --surface-raised: #17191c;
      --surface-soft: #1c1e21;
      --border: rgba(255, 255, 255, 0.085);
      --border-strong: rgba(255, 255, 255, 0.15);
      --text: #f4f1eb;
      --muted: #9b9d9d;
      --muted-2: #929493;
      --orange: #e28752;
      --orange-soft: rgba(226, 135, 82, 0.13);
      --green: #83b28a;
      --green-soft: rgba(131, 178, 138, 0.12);
      --danger: #e47d78;
      --shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
      --radius: 14px;
      --radius-sm: 9px;
      --topbar: 70px;
      --selection-bar: 92px;
      font-family: "Segoe UI Variable", "Segoe UI", system-ui, -apple-system, sans-serif;
      font-synthesis: none;
    }

    * { box-sizing: border-box; }

    html, body {
      width: 100%;
      min-width: 980px;
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: var(--bg);
      color: var(--text);
    }

    body {
      background:
        radial-gradient(circle at 9% 0%, rgba(226, 135, 82, 0.055), transparent 29%),
        radial-gradient(circle at 88% 8%, rgba(131, 178, 138, 0.04), transparent 25%),
        var(--bg);
      font-size: 14px;
      line-height: 1.45;
      -webkit-font-smoothing: antialiased;
    }

    button, input, select { font: inherit; }

    button { color: inherit; }

    button:focus-visible,
    input:focus-visible,
    select:focus-visible,
    [tabindex]:focus-visible {
      outline: 2px solid rgba(226, 135, 82, 0.9);
      outline-offset: 2px;
    }

    ::selection { background: rgba(226, 135, 82, 0.32); }

    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
      border: 3px solid transparent;
      border-radius: 10px;
      background: rgba(255, 255, 255, 0.15);
      background-clip: padding-box;
    }
    ::-webkit-scrollbar-thumb:hover { background-color: rgba(255, 255, 255, 0.24); }

    .hidden { display: none !important; }

    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }

    .app {
      width: 100%;
      height: 100%;
      isolation: isolate;
    }

    .topbar {
      position: relative;
      z-index: 20;
      height: var(--topbar);
      padding: 0 26px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      background: rgba(11, 12, 13, 0.9);
      backdrop-filter: blur(18px);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      min-width: 0;
    }

    .brand-mark {
      width: 34px;
      height: 34px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(226, 135, 82, 0.25);
      border-radius: 10px;
      background: linear-gradient(145deg, rgba(226, 135, 82, 0.18), rgba(226, 135, 82, 0.05));
      color: var(--orange);
      box-shadow: inset 0 1px 0 rgba(255,255,255,.08);
    }

    .brand-mark svg { width: 19px; height: 19px; }

    .brand-name {
      font-size: 15px;
      font-weight: 670;
      letter-spacing: -0.01em;
    }

    .brand-version {
      margin-left: 2px;
      color: var(--muted-2);
      font-size: 11px;
      font-weight: 600;
      letter-spacing: .07em;
      text-transform: uppercase;
    }

    .topbar-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .privacy-badge {
      height: 34px;
      padding: 0 12px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid rgba(131, 178, 138, 0.23);
      border-radius: 999px;
      background: var(--green-soft);
      color: #b6d5bb;
      cursor: pointer;
    }

    .privacy-badge:hover { border-color: rgba(131, 178, 138, 0.42); background: rgba(131,178,138,.16); }

    .legal-button {
      height: 34px;
      padding: 0 9px;
      border: 1px solid transparent;
      border-radius: 8px;
      background: transparent;
      color: var(--muted-2);
      font-size: 11px;
      cursor: pointer;
    }

    .legal-button:hover { border-color: var(--border); background: rgba(255,255,255,.035); color: var(--muted); }

    .privacy-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 0 4px rgba(131, 178, 138, 0.1);
    }

    .top-source-button {
      height: 36px;
      padding: 0 13px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      border: 1px solid var(--border);
      border-radius: 9px;
      background: rgba(255,255,255,.025);
      cursor: pointer;
    }

    .top-source-button:hover { border-color: var(--border-strong); background: rgba(255,255,255,.05); }
    .top-source-button svg { width: 16px; height: 16px; color: var(--muted); }

    .loading-view,
    .empty-view {
      height: calc(100vh - var(--topbar));
      display: grid;
      place-items: center;
      padding: 34px;
    }

    .loading-card,
    .empty-card {
      width: min(560px, 80vw);
      text-align: center;
    }

    .loading-orbit {
      width: 52px;
      height: 52px;
      position: relative;
      margin: 0 auto 22px;
      border: 1px solid var(--border);
      border-radius: 50%;
    }

    .loading-orbit::before {
      content: "";
      position: absolute;
      inset: 7px;
      border: 2px solid transparent;
      border-top-color: var(--orange);
      border-right-color: rgba(226,135,82,.25);
      border-radius: 50%;
      animation: spin .85s linear infinite;
    }

    .loading-orbit::after {
      content: "";
      position: absolute;
      inset: 20px;
      border-radius: 50%;
      background: var(--orange);
      box-shadow: 0 0 18px rgba(226,135,82,.38);
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    .loading-title { margin: 0 0 7px; font-size: 18px; font-weight: 650; }
    .loading-copy { margin: 0; color: var(--muted); }

    .empty-visual {
      width: 82px;
      height: 82px;
      margin: 0 auto 24px;
      position: relative;
      display: grid;
      place-items: center;
      border: 1px solid var(--border);
      border-radius: 22px;
      background: linear-gradient(145deg, rgba(255,255,255,.045), rgba(255,255,255,.015));
      color: var(--orange);
      box-shadow: var(--shadow);
    }

    .empty-visual::before {
      content: "";
      position: absolute;
      width: 24px;
      height: 24px;
      right: -8px;
      bottom: -7px;
      border: 5px solid var(--bg);
      border-radius: 50%;
      background: var(--green);
    }

    .empty-visual svg { width: 38px; height: 38px; }

    .empty-title {
      margin: 0 0 10px;
      font-size: 26px;
      line-height: 1.2;
      letter-spacing: -.025em;
    }

    .empty-copy {
      max-width: 480px;
      margin: 0 auto 22px;
      color: var(--muted);
      font-size: 15px;
      line-height: 1.6;
    }

    .primary-button,
    .secondary-button,
    .ghost-button,
    .icon-button {
      border: 0;
      cursor: pointer;
      transition: background .14s ease, border-color .14s ease, color .14s ease, transform .14s ease;
    }

    .primary-button {
      min-height: 42px;
      padding: 0 17px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 9px;
      border: 1px solid #ec9662;
      border-radius: 10px;
      background: linear-gradient(180deg, #e9925d, #d97843);
      color: #1d120c;
      font-weight: 690;
      box-shadow: 0 7px 22px rgba(218, 119, 66, 0.17), inset 0 1px rgba(255,255,255,.3);
    }

    .primary-button:hover:not(:disabled) { transform: translateY(-1px); background: linear-gradient(180deg, #efa06e, #df7f49); }

    .secondary-button {
      min-height: 42px;
      padding: 0 16px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 9px;
      border: 1px solid var(--border-strong);
      border-radius: 10px;
      background: rgba(255,255,255,.055);
      color: var(--text);
      font-weight: 620;
    }

    .secondary-button:hover:not(:disabled) { background: rgba(255,255,255,.09); border-color: rgba(255,255,255,.22); }

    button:disabled { opacity: .42; cursor: default; transform: none !important; }
    .button-spinner { width: 14px; height: 14px; border: 2px solid currentColor; border-right-color: transparent; border-radius: 50%; animation: spin .7s linear infinite; }

    .empty-note {
      margin-top: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 7px;
      color: var(--muted-2);
      font-size: 12px;
    }

    .empty-note svg { width: 14px; height: 14px; color: var(--green); }

    .workspace {
      height: calc(100vh - var(--topbar));
      min-height: 0;
      display: grid;
      grid-template-rows: minmax(0, 1fr) var(--selection-bar);
    }

    .work-grid {
      min-height: 0;
      display: grid;
      grid-template-columns: clamp(365px, 35vw, 455px) minmax(0, 1fr);
    }

    .library {
      min-height: 0;
      display: flex;
      flex-direction: column;
      border-right: 1px solid var(--border);
      background: rgba(16, 18, 20, 0.78);
    }

    .library-head {
      padding: 18px 18px 14px;
      border-bottom: 1px solid var(--border);
    }

    .source-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
    }

    .source-info { min-width: 0; }

    .eyebrow {
      margin: 0 0 3px;
      color: var(--muted-2);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: .105em;
      text-transform: uppercase;
    }

    .source-name {
      max-width: 280px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 14px;
      font-weight: 640;
    }

    .icon-button {
      width: 32px;
      height: 32px;
      flex: 0 0 auto;
      display: grid;
      place-items: center;
      border: 1px solid transparent;
      border-radius: 8px;
      background: transparent;
      color: var(--muted);
    }

    .icon-button:hover { border-color: var(--border); background: rgba(255,255,255,.045); color: var(--text); }
    .icon-button svg { width: 16px; height: 16px; }

    .search-wrap { position: relative; }

    .search-icon {
      width: 17px;
      height: 17px;
      position: absolute;
      left: 12px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--muted-2);
      pointer-events: none;
    }

    .search-input {
      width: 100%;
      height: 42px;
      padding: 0 72px 0 39px;
      border: 1px solid var(--border);
      border-radius: 10px;
      outline: 0;
      background: rgba(0,0,0,.22);
      color: var(--text);
      transition: border-color .14s ease, box-shadow .14s ease, background .14s ease;
    }

    .search-input::placeholder { color: #6f7272; }
    .search-input:focus { border-color: rgba(226,135,82,.58); background: rgba(0,0,0,.32); box-shadow: 0 0 0 3px rgba(226,135,82,.08); }

    .key-hint {
      position: absolute;
      right: 9px;
      top: 50%;
      transform: translateY(-50%);
      padding: 2px 6px;
      border: 1px solid var(--border);
      border-radius: 5px;
      color: var(--muted-2);
      background: rgba(255,255,255,.035);
      font-size: 10px;
      pointer-events: none;
    }

    .clear-search {
      width: 26px;
      height: 26px;
      position: absolute;
      top: 8px;
      right: 42px;
      display: grid;
      place-items: center;
      border: 0;
      border-radius: 6px;
      background: transparent;
      color: var(--muted);
      cursor: pointer;
    }
    .clear-search:hover { background: rgba(255,255,255,.07); color: var(--text); }
    .clear-search svg { width: 13px; height: 13px; }

    .filter-row {
      margin-top: 11px;
      display: flex;
      align-items: center;
      gap: 7px;
      overflow: hidden;
    }

    .filter-chip {
      height: 29px;
      padding: 0 10px;
      flex: 0 0 auto;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: transparent;
      color: var(--muted);
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
    }

    .filter-chip:hover { border-color: var(--border-strong); color: var(--text); }
    .filter-chip.active { border-color: rgba(226,135,82,.33); background: var(--orange-soft); color: #efb18c; }

    .sort-select {
      height: 29px;
      min-width: 0;
      margin-left: auto;
      padding: 0 25px 0 9px;
      border: 1px solid var(--border);
      border-radius: 8px;
      outline: 0;
      background: #151719;
      color: var(--muted);
      font-size: 11px;
      cursor: pointer;
    }

    .list-toolbar {
      height: 43px;
      padding: 0 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      border-bottom: 1px solid var(--border);
    }

    .select-all-label {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      cursor: pointer;
      user-select: none;
    }

    input[type="checkbox"] {
      width: 16px;
      height: 16px;
      margin: 0;
      accent-color: var(--orange);
      cursor: pointer;
    }

    .results-count {
      display: flex;
      align-items: center;
      gap: 7px;
      color: var(--muted-2);
      font-size: 11px;
      white-space: nowrap;
    }

    .mini-spinner { width: 12px; height: 12px; border: 2px solid rgba(255,255,255,.18); border-top-color: var(--orange); border-radius: 50%; animation: spin .7s linear infinite; }

    .chat-list {
      min-height: 0;
      flex: 1 1 auto;
      overflow-y: auto;
      padding: 8px;
      overscroll-behavior: contain;
    }

    .chat-card {
      position: relative;
      padding: 12px 12px 11px 40px;
      border: 1px solid transparent;
      border-radius: 11px;
      cursor: pointer;
      user-select: none;
      transition: border-color .13s ease, background .13s ease;
    }

    .chat-card + .chat-card { margin-top: 3px; }
    .chat-card:hover { background: rgba(255,255,255,.035); }
    .chat-card.active { border-color: var(--border); background: rgba(255,255,255,.045); }
    .chat-card.selected { background: rgba(226,135,82,.055); }
    .chat-card.active.selected { border-color: rgba(226,135,82,.24); background: rgba(226,135,82,.08); }

    .card-checkbox {
      position: absolute;
      left: 9px;
      top: 11px;
      width: 24px;
      height: 24px;
      border-radius: 5px;
      background: transparent;
      pointer-events: auto;
      cursor: pointer;
    }
    .card-checkbox::before {
      content: "";
      position: absolute;
      left: 4px;
      top: 4px;
      width: 14px;
      height: 14px;
      border: 1px solid #777a79;
      border-radius: 3px;
      background: #222426;
      transition: border-color .13s ease, background .13s ease;
    }
    .card-checkbox:hover::before { border-color: #a9abaa; }
    .chat-card.selected .card-checkbox::before {
      border-color: var(--orange);
      background: var(--orange);
    }
    .chat-card.selected .card-checkbox::after {
      content: "";
      position: absolute;
      left: 9px;
      top: 5px;
      width: 5px;
      height: 9px;
      border: solid #171412;
      border-width: 0 2px 2px 0;
      transform: rotate(45deg);
    }

    .card-title-row {
      display: flex;
      align-items: center;
      gap: 7px;
      min-width: 0;
    }

    .card-title {
      min-width: 0;
      flex: 1 1 auto;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      color: #e9e7e2;
      font-size: 13px;
      font-weight: 630;
    }

    .tech-dot {
      width: 6px;
      height: 6px;
      flex: 0 0 auto;
      border-radius: 50%;
      background: var(--orange);
      box-shadow: 0 0 0 3px rgba(226,135,82,.1);
    }

    .card-summary {
      height: 34px;
      margin: 5px 0 8px;
      overflow: hidden;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      color: var(--muted);
      font-size: 11.5px;
      line-height: 17px;
    }

    .card-meta {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted-2);
      font-size: 10.5px;
    }

    .meta-item { display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; }
    .meta-item svg { width: 12px; height: 12px; }
    .card-meta .meta-date { margin-left: auto; overflow: hidden; text-overflow: ellipsis; }

    .load-more-wrap {
      flex: 0 0 auto;
      padding: 0 8px 8px;
    }
    .load-more {
      width: 100%;
      height: 38px;
      margin: 0;
      border: 1px solid var(--border);
      border-radius: 9px;
      background: rgba(255,255,255,.025);
      color: var(--muted);
      cursor: pointer;
    }
    .load-more:hover { background: rgba(255,255,255,.05); color: var(--text); }

    .no-results {
      min-height: 260px;
      padding: 36px 20px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      color: var(--muted);
    }
    .no-results-icon { width: 44px; height: 44px; margin-bottom: 13px; display: grid; place-items: center; border: 1px solid var(--border); border-radius: 13px; color: var(--muted-2); }
    .no-results-icon svg { width: 20px; height: 20px; }
    .no-results-title { margin: 0 0 5px; color: #d8d6d1; font-weight: 620; }
    .no-results-copy { margin: 0; max-width: 280px; font-size: 12px; }

    .preview {
      min-width: 0;
      min-height: 0;
      display: flex;
      flex-direction: column;
      background: rgba(12, 13, 14, 0.56);
    }

    .preview-head {
      min-height: 78px;
      padding: 15px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      border-bottom: 1px solid var(--border);
    }

    .preview-heading { min-width: 0; }
    .preview-title {
      max-width: min(600px, 45vw);
      margin: 0 0 5px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 17px;
      font-weight: 660;
      letter-spacing: -.015em;
    }

    .preview-subtitle { color: var(--muted); font-size: 11.5px; }

    .preview-status {
      flex: 0 0 auto;
      display: inline-flex;
      align-items: center;
      gap: 7px;
      padding: 5px 9px;
      border: 1px solid var(--border);
      border-radius: 999px;
      color: var(--muted);
      font-size: 10.5px;
    }

    .preview-status-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); }

    .preview-body {
      min-height: 0;
      position: relative;
      flex: 1 1 auto;
      overflow: hidden;
    }

    .preview-empty {
      height: 100%;
      display: grid;
      place-items: center;
      padding: 30px;
      text-align: center;
      color: var(--muted);
    }

    .preview-empty-inner { max-width: 370px; }
    .preview-empty-mark {
      width: 58px;
      height: 58px;
      margin: 0 auto 17px;
      display: grid;
      place-items: center;
      border: 1px solid var(--border);
      border-radius: 17px;
      background: rgba(255,255,255,.022);
      color: var(--muted-2);
    }
    .preview-empty-mark svg { width: 26px; height: 26px; }
    .preview-empty h2 { margin: 0 0 7px; color: #d9d7d1; font-size: 16px; }
    .preview-empty p { margin: 0; font-size: 12.5px; line-height: 1.6; }

    .preview-loading {
      height: 100%;
      padding: 24px;
    }

    .skeleton-line {
      height: 12px;
      margin-bottom: 12px;
      border-radius: 5px;
      background: linear-gradient(90deg, rgba(255,255,255,.035), rgba(255,255,255,.075), rgba(255,255,255,.035));
      background-size: 240% 100%;
      animation: shimmer 1.35s ease-in-out infinite;
    }
    .skeleton-line:nth-child(3n) { width: 73%; }
    .skeleton-line:nth-child(5n) { width: 88%; }
    @keyframes shimmer { to { background-position: -240% 0; } }

    .preview-content {
      height: 100%;
      overflow: auto;
      overscroll-behavior: contain;
    }

    .preview-notice {
      margin: 16px 20px 0;
      padding: 10px 12px;
      display: flex;
      align-items: flex-start;
      gap: 9px;
      border: 1px solid rgba(226,135,82,.21);
      border-radius: 9px;
      background: rgba(226,135,82,.07);
      color: #d9aa8d;
      font-size: 11.5px;
    }
    .preview-notice svg { width: 15px; height: 15px; flex: 0 0 auto; margin-top: 1px; }

    .preview-warnings { margin: 10px 20px 0; display: grid; gap: 6px; }
    .preview-warning { color: #d6b792; font-size: 11px; }

    .preview-text {
      margin: 0;
      padding: 22px 24px 70px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      color: #d8d7d3;
      font: 12.5px/1.68 "Cascadia Code", "SFMono-Regular", Consolas, monospace;
      tab-size: 2;
    }

    .selection-bar {
      position: relative;
      z-index: 15;
      min-width: 0;
      padding: 11px 18px;
      display: grid;
      grid-template-columns: minmax(200px, 1fr) minmax(215px, 270px) auto;
      align-items: center;
      gap: 16px;
      border-top: 1px solid var(--border-strong);
      background: rgba(19, 21, 23, 0.96);
      box-shadow: 0 -18px 44px rgba(0,0,0,.24);
      backdrop-filter: blur(18px);
    }

    .selection-summary { min-width: 0; display: flex; align-items: center; gap: 13px; }

    .selection-count {
      width: 36px;
      height: 36px;
      flex: 0 0 auto;
      display: grid;
      place-items: center;
      border: 1px solid rgba(226,135,82,.24);
      border-radius: 10px;
      background: var(--orange-soft);
      color: #efad86;
      font-size: 13px;
      font-weight: 720;
    }

    .selection-copy { min-width: 0; }
    .selection-label { margin: 0 0 2px; font-size: 12px; font-weight: 650; }
    .selection-meta { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted-2); font-size: 10.5px; }
    .clear-selection { margin-left: 4px; padding: 3px 0; border: 0; background: transparent; color: var(--orange); font-size: 10.5px; cursor: pointer; }
    .clear-selection:hover { color: #f1a678; text-decoration: underline; }

    .output-options {
      min-width: 0;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 5px 7px;
      align-items: center;
    }

    .format-select {
      width: 100%;
      height: 35px;
      padding: 0 29px 0 10px;
      border: 1px solid var(--border);
      border-radius: 8px;
      outline: 0;
      background: #17191b;
      color: #dedbd5;
      font-size: 11.5px;
      cursor: pointer;
    }

    .folder-button {
      min-width: 0;
      padding: 0;
      overflow: hidden;
      border: 0;
      background: transparent;
      color: var(--muted-2);
      text-align: left;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 10px;
      cursor: pointer;
    }
    .folder-button:hover { color: var(--muted); }
    .folder-reveal { width: 28px; height: 28px; grid-row: 1 / span 2; grid-column: 2; }

    .selection-actions { display: flex; align-items: center; gap: 9px; }
    .selection-actions .secondary-button,
    .selection-actions .primary-button { min-height: 42px; white-space: nowrap; }
    .selection-actions svg { width: 16px; height: 16px; }

    .toast-region {
      position: fixed;
      z-index: 80;
      top: 82px;
      right: 18px;
      width: min(380px, 34vw);
      display: grid;
      gap: 9px;
      pointer-events: none;
    }

    .toast {
      padding: 12px 13px;
      display: grid;
      grid-template-columns: 23px 1fr auto;
      align-items: center;
      gap: 9px;
      border: 1px solid var(--border-strong);
      border-radius: 11px;
      background: rgba(29,31,33,.97);
      color: #e4e1dc;
      box-shadow: 0 15px 45px rgba(0,0,0,.35);
      pointer-events: auto;
      animation: toast-in .2s ease-out;
    }
    @keyframes toast-in { from { opacity: 0; transform: translateY(-6px); } }
    .toast-icon { width: 22px; height: 22px; display: grid; place-items: center; border-radius: 50%; background: var(--green-soft); color: var(--green); font-size: 12px; font-weight: 800; }
    .toast.error .toast-icon { background: rgba(228,125,120,.12); color: var(--danger); }
    .toast.info .toast-icon { background: var(--orange-soft); color: var(--orange); }
    .toast-message { font-size: 12px; line-height: 1.4; }
    .toast-action { padding: 4px 7px; border: 0; border-radius: 6px; background: transparent; color: #ef9d6b; font-size: 11px; cursor: pointer; }
    .toast-action:hover { background: var(--orange-soft); }

    .modal-layer {
      position: fixed;
      z-index: 100;
      inset: 0;
      padding: 30px;
      display: grid;
      place-items: center;
      background: rgba(3,4,5,.72);
      backdrop-filter: blur(8px);
      animation: fade-in .14s ease-out;
    }
    @keyframes fade-in { from { opacity: 0; } }

    .modal {
      width: min(510px, 80vw);
      max-height: min(680px, 85vh);
      overflow: auto;
      padding: 23px;
      border: 1px solid var(--border-strong);
      border-radius: 16px;
      background: #17191b;
      box-shadow: var(--shadow);
    }

    .modal-mark {
      width: 38px;
      height: 38px;
      margin-bottom: 17px;
      display: grid;
      place-items: center;
      border: 1px solid rgba(226,135,82,.22);
      border-radius: 11px;
      background: var(--orange-soft);
      color: var(--orange);
    }
    .modal-mark svg { width: 19px; height: 19px; }
    .modal-eyebrow { margin: 0 0 5px; color: var(--orange); font-size: 10px; font-weight: 720; letter-spacing: .1em; text-transform: uppercase; }
    .modal-title { margin: 0 0 10px; font-size: 20px; line-height: 1.25; letter-spacing: -.02em; }
    .modal-body { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.6; }
    .modal-facts { margin: 17px 0 0; padding: 0; list-style: none; display: grid; gap: 8px; }
    .modal-facts li { position: relative; padding: 9px 10px 9px 28px; border: 1px solid var(--border); border-radius: 9px; background: rgba(0,0,0,.13); color: #c9c7c1; font-size: 11.5px; }
    .modal-facts li::before { content: "\2713"; position: absolute; left: 10px; top: 9px; color: var(--green); font-weight: 800; }
    .modal-actions { margin-top: 22px; display: flex; justify-content: flex-end; gap: 9px; }
    .modal.modal-wide { width: min(800px, 88vw); }
    .modal-legal {
      max-height: min(460px, 54vh);
      margin: 17px 0 0;
      padding: 14px;
      overflow: auto;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: rgba(0,0,0,.2);
      color: #c9c7c1;
      font: 10.5px/1.55 ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      user-select: text;
    }

    @media (max-width: 1120px) {
      .work-grid { grid-template-columns: 385px minmax(0, 1fr); }
      .selection-bar { grid-template-columns: minmax(180px, 1fr) 220px auto; gap: 11px; padding-inline: 13px; }
      .selection-actions .secondary-button, .selection-actions .primary-button { padding-inline: 12px; font-size: 12px; }
      .selection-meta { max-width: 210px; }
    }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior: auto !important; animation-duration: .001ms !important; animation-iteration-count: 1 !important; transition-duration: .001ms !important; }
    }
  </style>
</head>
<body>
  <div id="app" class="app" aria-busy="true">
    <header class="topbar">
      <div class="brand" aria-label="Claude Chat Exporter">
        <div class="brand-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 4.8h8.5A3.5 3.5 0 0 1 18 8.3v5.2a3.5 3.5 0 0 1-3.5 3.5H10l-4 3v-3.4a3.5 3.5 0 0 1-3-3.5V8.3A3.5 3.5 0 0 1 6.5 4.8Z"/>
            <path d="M8 9h5.8M8 12.5h3.8"/>
          </svg>
        </div>
        <div>
          <span class="brand-name">Claude Chat Exporter</span>
          <span class="brand-version">Desktop</span>
        </div>
      </div>
      <div class="topbar-actions">
        <button id="legalButton" class="legal-button" type="button" aria-label="Projekt- und Drittanbieter-Lizenzen anzeigen">Lizenzen</button>
        <button id="privacyBadge" class="privacy-badge" type="button" aria-label="Informationen zum lokalen Datenschutz anzeigen">
          <span class="privacy-dot" aria-hidden="true"></span>
          <span>100 % lokal</span>
        </button>
        <button id="topSourceButton" class="top-source-button hidden" type="button" aria-label="Anderen Claude-Export öffnen">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 6.5h6l2 2H20a1.5 1.5 0 0 1 1.5 1.5v7.5A2.5 2.5 0 0 1 19 20H5a2.5 2.5 0 0 1-2.5-2.5V8A1.5 1.5 0 0 1 4 6.5Z"/><path d="M3.5 10h18"/></svg>
          <span>Export wechseln</span>
        </button>
      </div>
    </header>

    <main>
      <section id="loadingView" class="loading-view" aria-live="polite">
        <div class="loading-card">
          <div class="loading-orbit" aria-hidden="true"></div>
          <h1 id="loadingTitle" class="loading-title">Claude-Daten werden vorbereitet</h1>
          <p id="loadingCopy" class="loading-copy">Alles bleibt auf diesem Computer.</p>
        </div>
      </section>

      <section id="emptyView" class="empty-view hidden" aria-labelledby="emptyTitle">
        <div class="empty-card">
          <div class="empty-visual" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4.8h10.7A3.3 3.3 0 0 1 18 8.1v5.2a3.3 3.3 0 0 1-3.3 3.3H10l-5 3.2v-3.7a3.2 3.2 0 0 1-2.3-3V8.1A3.3 3.3 0 0 1 6 4.8Z"/><path d="M8 9.2h5M8 12.3h3.5"/></svg>
          </div>
          <h1 id="emptyTitle" class="empty-title">Deine Claude-Chats. Bereit für ChatGPT.</h1>
          <p id="emptyCopy" class="empty-copy">Wähle die <strong>conversations.json</strong> aus deinem Claude-Datenexport. Danach kannst du jeden Chat sofort kopieren oder als eigene Datei exportieren.</p>
          <button id="chooseSourceButton" class="primary-button" type="button">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 6.5h6l2 2H20a1.5 1.5 0 0 1 1.5 1.5v7.5A2.5 2.5 0 0 1 19 20H5a2.5 2.5 0 0 1-2.5-2.5V8A1.5 1.5 0 0 1 4 6.5Z"/><path d="M3.5 10h18"/></svg>
            <span>Claude-Export auswählen</span>
          </button>
          <div class="empty-note">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-3.5 8-10V5l-8-3-8 3v7c0 6.5 8 10 8 10Z"/><path d="m9 12 2 2 4-5"/></svg>
            Kein Upload · kein Konto · keine Cloud
          </div>
        </div>
      </section>

      <section id="workspace" class="workspace hidden" aria-label="Claude-Konversationen">
        <div class="work-grid">
          <aside class="library" aria-label="Chatbibliothek">
            <div class="library-head">
              <div class="source-row">
                <div class="source-info">
                  <p class="eyebrow">Datenquelle</p>
                  <div id="sourceName" class="source-name">conversations.json</div>
                </div>
                <button id="changeSourceButton" class="icon-button" type="button" aria-label="Anderen Claude-Export auswählen" title="Export wechseln">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3.5 6.5h6l2 2H20a1.5 1.5 0 0 1 1.5 1.5v7.5A2.5 2.5 0 0 1 19 20H5a2.5 2.5 0 0 1-2.5-2.5V8A1.5 1.5 0 0 1 4 6.5Z"/><path d="M3.5 10h18"/></svg>
                </button>
              </div>
              <div class="search-wrap">
                <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>
                <input id="searchInput" class="search-input" type="search" autocomplete="off" spellcheck="false" placeholder="Titel und Inhalt durchsuchen …" aria-label="Chats durchsuchen">
                <button id="clearSearch" class="clear-search hidden" type="button" aria-label="Suche löschen">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m7 7 10 10M17 7 7 17"/></svg>
                </button>
                <span class="key-hint" aria-hidden="true">Ctrl F</span>
              </div>
              <div class="filter-row" aria-label="Chatfilter">
                <button class="filter-chip" type="button" data-filter="attachments" aria-pressed="false">Anhänge</button>
                <button class="filter-chip" type="button" data-filter="files" aria-pressed="false">Dateien</button>
                <button class="filter-chip" type="button" data-filter="technical" aria-pressed="false">Technisch</button>
                <button class="filter-chip" type="button" data-filter="exclude_empty" aria-pressed="false">Leere aus</button>
                <select id="sortSelect" class="sort-select" aria-label="Chats sortieren">
                  <option value="updated_desc">Zuletzt geändert</option>
                  <option value="created_desc">Neueste zuerst</option>
                  <option value="created_asc">Älteste zuerst</option>
                  <option value="title_asc">Titel A–Z</option>
                  <option value="messages_desc">Meiste Nachrichten</option>
                </select>
              </div>
            </div>
            <div class="list-toolbar">
              <label class="select-all-label">
                <input id="selectAllFiltered" type="checkbox" aria-label="Alle gefilterten Chats auswählen">
                <span>Alle gefilterten wählen</span>
              </label>
              <div class="results-count" aria-live="polite">
                <span id="searchSpinner" class="mini-spinner hidden" aria-hidden="true"></span>
                <span id="resultCount">0 Chats</span>
              </div>
            </div>
            <p id="chatListHelp" class="sr-only">Enter öffnet den Chat. Leertaste wählt ihn für den Export. Umschalt plus Leertaste wählt einen Bereich.</p>
            <div id="chatList" class="chat-list" role="listbox" aria-multiselectable="true" aria-label="Gefundene Chats" aria-describedby="chatListHelp"></div>
            <div id="loadMoreContainer" class="load-more-wrap"></div>
          </aside>

          <section class="preview" aria-label="Chatvorschau">
            <header class="preview-head">
              <div class="preview-heading">
                <p class="eyebrow">Vorschau</p>
                <h2 id="previewTitle" class="preview-title">Chat auswählen</h2>
                <div id="previewSubtitle" class="preview-subtitle">Die Vorschau entspricht dem gewählten Exportformat.</div>
              </div>
              <div id="previewStatus" class="preview-status hidden">
                <span class="preview-status-dot" aria-hidden="true"></span>
                <span id="previewStatusText">Vollständige Vorschau</span>
              </div>
            </header>
            <div class="preview-body">
              <div id="previewEmpty" class="preview-empty">
                <div class="preview-empty-inner">
                  <div class="preview-empty-mark" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 3v-3.5A2 2 0 0 1 3 16V6a2 2 0 0 1 2-2Z"/><path d="M8 9h8M8 13h5"/></svg>
                  </div>
                  <h2>Wähle links einen Chat</h2>
                  <p>Ein Klick öffnet die Vorschau. Über das Hakenfeld wählst du Chats für den Export.</p>
                </div>
              </div>
              <div id="previewLoading" class="preview-loading hidden" aria-label="Vorschau wird geladen">
                <div class="skeleton-line"></div><div class="skeleton-line"></div><div class="skeleton-line"></div><div class="skeleton-line"></div><div class="skeleton-line"></div><div class="skeleton-line"></div><div class="skeleton-line"></div><div class="skeleton-line"></div><div class="skeleton-line"></div>
              </div>
              <div id="previewContent" class="preview-content hidden">
                <div id="previewTruncated" class="preview-notice hidden">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 9v4M12 17h.01"/><path d="M10.3 3.6 2.4 17.2A2 2 0 0 0 4.1 20h15.8a2 2 0 0 0 1.7-2.8L13.7 3.6a2 2 0 0 0-3.4 0Z"/></svg>
                  <span id="previewTruncatedText">Diese Vorschau ist gekürzt. Kopie und Export werden gegenüber dem gewählten Format nicht zusätzlich gekürzt.</span>
                </div>
                <div id="previewWarnings" class="preview-warnings"></div>
                <pre id="previewText" class="preview-text"></pre>
              </div>
            </div>
          </section>
        </div>

        <footer class="selection-bar" aria-label="Exportauswahl">
          <div class="selection-summary">
            <div id="selectionCount" class="selection-count" aria-hidden="true">0</div>
            <div class="selection-copy">
              <p id="selectionLabel" class="selection-label">Noch nichts ausgewählt</p>
              <div id="selectionMeta" class="selection-meta">Über die Hakenfelder oder „Alle gefilterten wählen“ auswählen</div>
              <button id="clearSelection" class="clear-selection hidden" type="button">Auswahl aufheben</button>
            </div>
          </div>

          <div class="output-options">
            <select id="formatSelect" class="format-select" aria-label="Exportformat">
              <option value="chatgpt_markdown">ChatGPT Markdown · empfohlen</option>
              <option value="complete_markdown">Vollständiges Markdown</option>
              <option value="raw_json">Original-Rohdaten (JSON)</option>
            </select>
            <button id="revealFolderButton" class="icon-button folder-reveal" type="button" aria-label="Ausgabeordner im Explorer öffnen" title="Im Explorer öffnen">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9"/><path d="M18 13v5a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h5"/></svg>
            </button>
            <button id="folderButton" class="folder-button" type="button" aria-label="Ausgabeordner ändern">Ausgabeordner wählen</button>
          </div>

          <div class="selection-actions">
            <button id="copyButton" class="secondary-button" type="button" disabled title="Kopiert den aktuell geöffneten Chat">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/></svg>
              <span>Für ChatGPT kopieren</span>
            </button>
            <button id="exportButton" class="primary-button" type="button" disabled title="Ctrl+E">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12M7 10l5 5 5-5"/><path d="M5 21h14"/></svg>
              <span>Exportieren</span>
            </button>
          </div>
        </footer>
      </section>
    </main>

    <div id="toastRegion" class="toast-region" aria-live="polite" aria-atomic="false"></div>

    <div id="modalLayer" class="modal-layer hidden" role="presentation">
      <section id="modalDialog" class="modal" role="dialog" aria-modal="true" aria-labelledby="modalTitle" aria-describedby="modalBody">
        <div class="modal-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/></svg>
        </div>
        <p id="modalEyebrow" class="modal-eyebrow">Hinweis</p>
        <h2 id="modalTitle" class="modal-title">Bevor du fortfährst</h2>
        <p id="modalBody" class="modal-body"></p>
        <ul id="modalFacts" class="modal-facts"></ul>
        <pre id="modalLegal" class="modal-legal hidden" tabindex="0"></pre>
        <div class="modal-actions">
          <button id="modalCancel" class="secondary-button" type="button">Abbrechen</button>
          <button id="modalConfirm" class="primary-button" type="button">Fortfahren</button>
        </div>
      </section>
    </div>
  </div>

  <script>
    (() => {
      "use strict";

      const $ = (id) => document.getElementById(id);
      const dom = {
        app: $("app"), loadingView: $("loadingView"), loadingTitle: $("loadingTitle"), loadingCopy: $("loadingCopy"),
        emptyView: $("emptyView"), emptyTitle: $("emptyTitle"), emptyCopy: $("emptyCopy"), workspace: $("workspace"),
        topSourceButton: $("topSourceButton"), chooseSourceButton: $("chooseSourceButton"), changeSourceButton: $("changeSourceButton"),
        privacyBadge: $("privacyBadge"), legalButton: $("legalButton"), sourceName: $("sourceName"), searchInput: $("searchInput"), clearSearch: $("clearSearch"),
        sortSelect: $("sortSelect"), selectAllFiltered: $("selectAllFiltered"), resultCount: $("resultCount"),
        searchSpinner: $("searchSpinner"), chatList: $("chatList"), loadMoreContainer: $("loadMoreContainer"), previewTitle: $("previewTitle"), previewSubtitle: $("previewSubtitle"),
        previewStatus: $("previewStatus"), previewStatusText: $("previewStatusText"), previewEmpty: $("previewEmpty"),
        previewLoading: $("previewLoading"), previewContent: $("previewContent"), previewText: $("previewText"),
        previewTruncated: $("previewTruncated"), previewTruncatedText: $("previewTruncatedText"), previewWarnings: $("previewWarnings"),
        selectionCount: $("selectionCount"), selectionLabel: $("selectionLabel"), selectionMeta: $("selectionMeta"),
        clearSelection: $("clearSelection"), formatSelect: $("formatSelect"), folderButton: $("folderButton"),
        revealFolderButton: $("revealFolderButton"), copyButton: $("copyButton"), exportButton: $("exportButton"),
        toastRegion: $("toastRegion"), modalLayer: $("modalLayer"), modalDialog: $("modalDialog"), modalEyebrow: $("modalEyebrow"),
        modalTitle: $("modalTitle"), modalBody: $("modalBody"), modalFacts: $("modalFacts"),
        modalLegal: $("modalLegal"), modalCancel: $("modalCancel"), modalConfirm: $("modalConfirm")
      };

      const VALID_FORMATS = new Set(["chatgpt_markdown", "complete_markdown", "raw_json"]);
      const VALID_SORTS = new Set(["updated_desc", "created_desc", "created_asc", "title_asc", "messages_desc"]);
      const PAGE_SIZE = 140;
      const filters = { attachments: false, files: false, technical: false, exclude_empty: false };
      const state = {
        booted: false,
        loaded: false,
        sourceName: "",
        sourcePath: "",
        exportFolder: "",
        all: [],
        byId: new Map(),
        filtered: [],
        selected: new Set(),
        activeUuid: null,
        lastSelectionIndex: -1,
        visibleLimit: PAGE_SIZE,
        format: "chatgpt_markdown",
        searchSequence: 0,
        previewSequence: 0,
        previewData: null,
        selectionSize: null,
        selectionSizeSequence: 0,
        modalConfirmAction: null,
        modalCancelAction: null,
        modalLastFocus: null
      };

      const icons = {
        messages: () => makeSvg("M5 5h14a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H9l-5 3v-3.5A2 2 0 0 1 3 15V7a2 2 0 0 1 2-2Z"),
        paperclip: () => makeSvg("m20 11.5-8.3 8.3a5 5 0 0 1-7.1-7.1l9-9a3.5 3.5 0 0 1 5 5l-9 9a2 2 0 0 1-2.9-2.8l8.3-8.3"),
        branch: () => makeSvg("M6 3v12a4 4 0 0 0 4 4h8M6 7h5a4 4 0 0 1 4 4v8M3 6l3 3 3-3M12 16l3 3 3-3"),
        calendar: () => makeSvg("M6 3v3M18 3v3M4 8h16M5 5h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2Z")
      };

      function makeSvg(pathData) {
        const ns = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(ns, "svg");
        svg.setAttribute("viewBox", "0 0 24 24");
        svg.setAttribute("fill", "none");
        svg.setAttribute("stroke", "currentColor");
        svg.setAttribute("stroke-width", "1.8");
        svg.setAttribute("stroke-linecap", "round");
        svg.setAttribute("stroke-linejoin", "round");
        svg.setAttribute("aria-hidden", "true");
        const path = document.createElementNS(ns, "path");
        path.setAttribute("d", pathData);
        svg.appendChild(path);
        return svg;
      }

      function text(value, fallback = "") {
        if (value === null || value === undefined) return fallback;
        return String(value);
      }

      function number(value) {
        const parsed = Number(value);
        return Number.isFinite(parsed) ? parsed : 0;
      }

      function formatNumber(value) {
        return new Intl.NumberFormat("de-DE").format(number(value));
      }

      function compactNumber(value) {
        const amount = number(value);
        if (amount < 1000) return formatNumber(amount);
        return new Intl.NumberFormat("de-DE", { notation: "compact", maximumFractionDigits: 1 }).format(amount);
      }

      function formatDate(value) {
        if (!value) return "Datum unbekannt";
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return "Datum unbekannt";
        return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "short", year: "numeric" }).format(date);
      }

      function formatBytesFromChars(chars) {
        const bytes = Math.max(0, number(chars) * 1.45);
        if (bytes < 1024) return Math.round(bytes) + " B";
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(bytes > 10240 ? 0 : 1).replace(".", ",") + " KB";
        return (bytes / (1024 * 1024)).toFixed(bytes > 10 * 1024 * 1024 ? 0 : 1).replace(".", ",") + " MB";
      }

      function plural(count, singular, pluralForm) {
        return count === 1 ? singular : pluralForm;
      }

      async function apiCall(method, ...args) {
        const api = window.pywebview && window.pywebview.api;
        if (!api || typeof api[method] !== "function") {
          throw new Error("Die lokale Programm-Schnittstelle ist noch nicht bereit.");
        }
        return await api[method](...args);
      }

      function showView(name) {
        dom.loadingView.classList.toggle("hidden", name !== "loading");
        dom.emptyView.classList.toggle("hidden", name !== "empty");
        dom.workspace.classList.toggle("hidden", name !== "workspace");
        dom.topSourceButton.classList.toggle("hidden", name !== "workspace");
        dom.app.setAttribute("aria-busy", name === "loading" ? "true" : "false");
      }

      function setLoading(title, copy) {
        dom.loadingTitle.textContent = title;
        dom.loadingCopy.textContent = copy;
        showView("loading");
      }

      function setButtonBusy(button, busy, label) {
        if (!button.dataset.defaultLabel) {
          const span = button.querySelector("span:last-child");
          button.dataset.defaultLabel = span ? span.textContent : button.textContent;
        }
        const labelSpan = button.querySelector("span:last-child");
        button.disabled = busy;
        if (labelSpan) labelSpan.textContent = busy ? label : button.dataset.defaultLabel;
      }

      function toast(message, type = "success", actionLabel = "", action = null) {
        const item = document.createElement("div");
        item.className = "toast " + type;
        item.setAttribute("role", type === "error" ? "alert" : "status");

        const icon = document.createElement("div");
        icon.className = "toast-icon";
        icon.textContent = type === "error" ? "!" : (type === "info" ? "i" : "✓");
        const copy = document.createElement("div");
        copy.className = "toast-message";
        copy.textContent = text(message, "Fertig.");

        item.appendChild(icon);
        item.appendChild(copy);
        if (actionLabel && typeof action === "function") {
          const button = document.createElement("button");
          button.type = "button";
          button.className = "toast-action";
          button.textContent = actionLabel;
          button.addEventListener("click", () => { action(); item.remove(); });
          item.appendChild(button);
        }
        dom.toastRegion.appendChild(item);
        window.setTimeout(() => item.remove(), actionLabel ? 8000 : 5200);
      }

      function openModal(options) {
        state.modalLastFocus = document.activeElement;
        state.modalConfirmAction = typeof options.onConfirm === "function" ? options.onConfirm : null;
        state.modalCancelAction = typeof options.onCancel === "function" ? options.onCancel : null;
        dom.modalEyebrow.textContent = options.eyebrow || "Hinweis";
        dom.modalTitle.textContent = options.title || "Bevor du fortfährst";
        dom.modalBody.textContent = options.body || "";
        dom.modalFacts.replaceChildren();
        (options.facts || []).forEach((fact) => {
          const li = document.createElement("li");
          li.textContent = text(fact);
          dom.modalFacts.appendChild(li);
        });
        const legalText = typeof options.legalText === "string" ? options.legalText : "";
        dom.modalLegal.textContent = legalText;
        dom.modalLegal.classList.toggle("hidden", !legalText);
        dom.modalDialog.classList.toggle("modal-wide", Boolean(legalText));
        dom.modalCancel.textContent = options.cancelText || "Abbrechen";
        dom.modalConfirm.textContent = options.confirmText || "Fortfahren";
        dom.modalCancel.classList.toggle("hidden", Boolean(options.hideCancel));
        dom.modalLayer.classList.remove("hidden");
        window.setTimeout(() => dom.modalConfirm.focus(), 0);
      }

      function closeModal(confirmed) {
        if (dom.modalLayer.classList.contains("hidden")) return;
        const action = confirmed ? state.modalConfirmAction : state.modalCancelAction;
        dom.modalLayer.classList.add("hidden");
        state.modalConfirmAction = null;
        state.modalCancelAction = null;
        const focusTarget = state.modalLastFocus;
        state.modalLastFocus = null;
        if (focusTarget && typeof focusTarget.focus === "function") focusTarget.focus();
        if (action) Promise.resolve().then(action);
      }

      function currentFilters() {
        return {
          attachments: filters.attachments,
          files: filters.files,
          technical: filters.technical,
          exclude_empty: filters.exclude_empty
        };
      }

      function normalizeFormatSizes(value) {
        const result = {};
        VALID_FORMATS.forEach((format) => {
          const entry = value && value[format];
          if (entry && Number.isFinite(Number(entry.chars)) && Number.isFinite(Number(entry.tokens))) {
            result[format] = { chars: number(entry.chars), tokens: number(entry.tokens) };
          }
        });
        return result;
      }

      function normalizeConversations(items) {
        if (!Array.isArray(items)) return [];
        return items.filter((item) => item && item.uuid).map((item) => ({
          uuid: text(item.uuid),
          title: text(item.title, "Unbenannter Chat"),
          summary: text(item.summary),
          created_at: item.created_at,
          updated_at: item.updated_at,
          message_count: number(item.message_count),
          attachment_count: number(item.attachment_count),
          file_count: number(item.file_count),
          branch_count: number(item.branch_count),
          char_count: number(item.char_count),
          estimated_tokens: number(item.estimated_tokens),
          format_sizes: normalizeFormatSizes(item.format_sizes),
          has_technical: Boolean(item.has_technical),
          is_empty: Boolean(item.is_empty)
        }));
      }

      function applySnapshot(snapshot) {
        if (!snapshot || snapshot.ok === false) {
          throw new Error(text(snapshot && snapshot.error, "Der Claude-Export konnte nicht gelesen werden."));
        }
        state.loaded = Boolean(snapshot.loaded);
        state.sourceName = text(snapshot.source_name, "conversations.json");
        state.sourcePath = text(snapshot.source_path);
        state.exportFolder = text(snapshot.export_folder);
        state.all = normalizeConversations(snapshot.conversations);
        state.filtered = state.all.slice();
        state.byId = new Map(state.all.map((item) => [item.uuid, item]));
        state.selected.clear();
        state.activeUuid = null;
        state.lastSelectionIndex = -1;
        state.visibleLimit = PAGE_SIZE;
        state.previewData = null;
        state.selectionSize = null;
        state.selectionSizeSequence += 1;

        const settings = snapshot.settings || {};
        const savedFormat = settings.last_format || settings.format;
        if (VALID_FORMATS.has(savedFormat)) state.format = savedFormat;
        if (VALID_SORTS.has(settings.sort)) dom.sortSelect.value = settings.sort;
        dom.formatSelect.value = state.format;
        dom.sourceName.textContent = state.sourceName;
        dom.sourceName.title = state.sourcePath || state.sourceName;
        renderFolder();
        (Array.isArray(snapshot.warnings) ? snapshot.warnings : []).forEach((warning) => {
          toast(text(warning), "error");
        });

        if (!state.loaded || state.all.length === 0) {
          dom.emptyTitle.textContent = state.loaded ? "Keine Konversationen gefunden" : "Deine Claude-Chats. Bereit für ChatGPT.";
          dom.emptyCopy.textContent = state.loaded
            ? "Diese Datei enthält keine exportierbaren Chats. Wähle eine andere conversations.json aus deinem Claude-Datenexport."
            : "Wähle die conversations.json aus deinem Claude-Datenexport. Danach kannst du jeden Chat sofort kopieren oder als eigene Datei exportieren.";
          showView("empty");
          return;
        }

        showView("workspace");
        state.activeUuid = state.filtered[0] ? state.filtered[0].uuid : null;
        renderList();
        renderSelection();
        if (state.activeUuid) requestPreview(state.activeUuid, false);
      }

      function renderFolder() {
        const folder = state.exportFolder;
        dom.folderButton.textContent = folder || "Ausgabeordner wählen";
        dom.folderButton.title = folder || "Ordner für exportierte Dateien wählen";
        dom.revealFolderButton.disabled = !folder;
      }

      function makeMeta(iconFactory, value, className = "") {
        const span = document.createElement("span");
        span.className = "meta-item" + (className ? " " + className : "");
        span.appendChild(iconFactory());
        const copy = document.createElement("span");
        copy.textContent = value;
        span.appendChild(copy);
        return span;
      }

      function renderList() {
        const previousScroll = dom.chatList.scrollTop;
        dom.chatList.replaceChildren();
        dom.loadMoreContainer.replaceChildren();
        dom.resultCount.textContent = formatNumber(state.filtered.length) + " " + plural(state.filtered.length, "Chat", "Chats");

        if (state.filtered.length === 0) {
          const empty = document.createElement("div");
          empty.className = "no-results";
          empty.setAttribute("role", "option");
          empty.setAttribute("aria-disabled", "true");
          const mark = document.createElement("div");
          mark.className = "no-results-icon";
          mark.appendChild(makeSvg("M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14ZM20 20l-4-4"));
          const title = document.createElement("p");
          title.className = "no-results-title";
          title.textContent = "Keine passenden Chats";
          const copy = document.createElement("p");
          copy.className = "no-results-copy";
          copy.textContent = "Passe Suche oder Filter an – deine Daten bleiben unverändert.";
          empty.append(mark, title, copy);
          dom.chatList.appendChild(empty);
          updateSelectAll();
          return;
        }

        const fragment = document.createDocumentFragment();
        const visible = state.filtered.slice(0, state.visibleLimit);
        const activeIsVisible = visible.some((item) => item.uuid === state.activeUuid);
        const rovingUuid = activeIsVisible ? state.activeUuid : (visible[0] ? visible[0].uuid : null);
        visible.forEach((item, index) => {
          const card = document.createElement("article");
          card.className = "chat-card";
          card.setAttribute("role", "option");
          card.setAttribute("tabindex", rovingUuid === item.uuid ? "0" : "-1");
          card.setAttribute("aria-label", item.title + " öffnen");
          card.setAttribute("aria-selected", state.selected.has(item.uuid) ? "true" : "false");
          if (state.activeUuid === item.uuid) card.setAttribute("aria-current", "true");
          card.dataset.uuid = item.uuid;
          card.classList.toggle("selected", state.selected.has(item.uuid));
          card.classList.toggle("active", state.activeUuid === item.uuid);

          const checkbox = document.createElement("span");
          checkbox.className = "card-checkbox";
          checkbox.setAttribute("aria-hidden", "true");
          checkbox.title = state.selected.has(item.uuid) ? "Auswahl aufheben" : "Für Export auswählen";
          checkbox.addEventListener("click", (event) => {
            event.stopPropagation();
            changeSelection(item.uuid, index, !state.selected.has(item.uuid), event.shiftKey, false);
          });

          const titleRow = document.createElement("div");
          titleRow.className = "card-title-row";
          const title = document.createElement("div");
          title.className = "card-title";
          title.textContent = item.title || "Unbenannter Chat";
          title.title = item.title || "Unbenannter Chat";
          titleRow.appendChild(title);
          if (item.has_technical) {
            const dot = document.createElement("span");
            dot.className = "tech-dot";
            dot.title = "Enthält technische Daten";
            dot.setAttribute("aria-label", "Enthält technische Daten");
            titleRow.appendChild(dot);
          }

          const summary = document.createElement("p");
          summary.className = "card-summary";
          summary.textContent = item.summary || (item.is_empty ? "Leere Konversation" : "Keine Textvorschau verfügbar");

          const meta = document.createElement("div");
          meta.className = "card-meta";
          meta.appendChild(makeMeta(icons.messages, compactNumber(item.message_count)));
          if (item.attachment_count > 0) meta.appendChild(makeMeta(icons.paperclip, compactNumber(item.attachment_count)));
          if (item.branch_count > 0) meta.appendChild(makeMeta(icons.branch, compactNumber(item.branch_count)));
          meta.appendChild(makeMeta(icons.calendar, formatDate(item.updated_at || item.created_at), "meta-date"));

          card.append(checkbox, titleRow, summary, meta);
          card.addEventListener("click", () => {
            activateChat(item.uuid, true);
          });
          card.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              activateChat(item.uuid, true);
              return;
            }
            if (event.key === " ") {
              event.preventDefault();
              changeSelection(item.uuid, index, !state.selected.has(item.uuid), event.shiftKey, true);
              return;
            }
            const keyTarget = event.key === "ArrowDown" ? index + 1
              : event.key === "ArrowUp" ? index - 1
              : event.key === "Home" ? 0
              : event.key === "End" ? state.filtered.length - 1
              : -1;
            if (keyTarget >= 0 && keyTarget < state.filtered.length) {
              event.preventDefault();
              if (keyTarget >= state.visibleLimit) {
                state.visibleLimit = Math.min(state.filtered.length, Math.max(keyTarget + 1, state.visibleLimit + PAGE_SIZE));
              }
              const targetItem = state.filtered[keyTarget];
              activateChat(targetItem.uuid, true);
            }
          });
          fragment.appendChild(card);
        });

        if (visible.length < state.filtered.length) {
          const more = document.createElement("button");
          more.type = "button";
          more.className = "load-more";
          const remaining = state.filtered.length - visible.length;
          more.textContent = "Weitere " + formatNumber(Math.min(PAGE_SIZE, remaining)) + " Chats anzeigen";
          more.addEventListener("click", () => {
            const nextIndex = visible.length;
            state.visibleLimit = Math.min(state.filtered.length, state.visibleLimit + PAGE_SIZE);
            const targetItem = state.filtered[nextIndex];
            if (targetItem) {
              activateChat(targetItem.uuid, true);
            } else {
              renderList();
            }
          });
          dom.loadMoreContainer.appendChild(more);
        }

        dom.chatList.appendChild(fragment);
        dom.chatList.scrollTop = previousScroll;
        updateSelectAll();
      }

      function focusChatCard(uuid) {
        const card = Array.from(dom.chatList.querySelectorAll("[data-uuid]")).find((entry) => entry.dataset.uuid === uuid);
        if (card) card.focus();
      }

      function activateChat(uuid, restoreFocus = false) {
        const previewIsCurrent = state.activeUuid === uuid
          && state.previewData
          && state.previewData.uuid === uuid
          && state.previewData.format === state.format;
        state.activeUuid = uuid;
        if (!previewIsCurrent) requestPreview(uuid, false);
        renderList();
        if (restoreFocus) focusChatCard(uuid);
      }

      function changeSelection(uuid, index, checked, shiftRange, restoreFocus = false) {
        const previousSelection = new Set(state.selected);
        if (shiftRange && state.lastSelectionIndex >= 0 && state.filtered.length) {
          const start = Math.min(state.lastSelectionIndex, index);
          const end = Math.max(state.lastSelectionIndex, index);
          for (let i = start; i <= end; i += 1) {
            const item = state.filtered[i];
            if (!item) continue;
            if (checked) state.selected.add(item.uuid); else state.selected.delete(item.uuid);
          }
        } else {
          if (checked) state.selected.add(uuid); else state.selected.delete(uuid);
        }
        const selectionChanged = previousSelection.size !== state.selected.size
          || Array.from(state.selected).some((selectedUuid) => !previousSelection.has(selectedUuid));
        if (selectionChanged) state.lastSelectionIndex = index;
        renderList();
        if (selectionChanged) queueSelectionSize();
        if (restoreFocus) focusChatCard(uuid);
      }

      function updateSelectAll() {
        const total = state.filtered.length;
        const selected = state.filtered.reduce((sum, item) => sum + (state.selected.has(item.uuid) ? 1 : 0), 0);
        dom.selectAllFiltered.checked = total > 0 && selected === total;
        dom.selectAllFiltered.indeterminate = selected > 0 && selected < total;
        dom.selectAllFiltered.disabled = total === 0;
      }

      function selectedItems() {
        const items = [];
        state.selected.forEach((uuid) => {
          const item = state.byId.get(uuid);
          if (item) items.push(item);
        });
        return items;
      }

      function selectionKey() {
        return state.format + "|" + Array.from(state.selected).sort().join("|");
      }

      function exactSelectionSize() {
        const value = state.selectionSize;
        return value && value.key === selectionKey() ? value : null;
      }

      let selectionSizeTimer = null;
      function queueSelectionSize() {
        window.clearTimeout(selectionSizeTimer);
        state.selectionSize = null;
        state.selectionSizeSequence += 1;
        const items = selectedItems();
        if (!items.length) {
          renderSelection();
          return;
        }
        const previewMatchesSingle = (
          items.length === 1
          && items[0].uuid === state.activeUuid
          && state.previewData
          && state.previewData.uuid === state.activeUuid
          && state.previewData.format === state.format
        );
        if (previewMatchesSingle) {
          state.selectionSize = {
            key: selectionKey(),
            count: 1,
            chars: number(state.previewData.total_chars),
            tokens: number(state.previewData.estimated_tokens)
          };
          renderSelection();
          return;
        }
        const waitingForSinglePreview = items.length === 1 && items[0].uuid === state.activeUuid;
        if (!waitingForSinglePreview) {
          selectionSizeTimer = window.setTimeout(refreshSelectionSize, 80);
        }
        renderSelection();
      }

      async function refreshSelectionSize() {
        const uuids = Array.from(state.selected);
        if (!uuids.length) return;
        const key = selectionKey();
        const sequence = ++state.selectionSizeSequence;
        try {
          const result = await apiCall("get_sizes", uuids, state.format);
          if (sequence !== state.selectionSizeSequence || key !== selectionKey()) return;
          if (!result || result.ok === false) throw new Error(text(result && result.error, "Größe konnte nicht berechnet werden."));
          state.selectionSize = {
            key: key,
            count: number(result.count),
            chars: number(result.total_chars),
            tokens: number(result.estimated_tokens)
          };
          renderSelection();
        } catch (error) {
          if (sequence === state.selectionSizeSequence) {
            state.selectionSize = null;
            renderSelection();
            toast(text(error.message, error), "error");
          }
        }
      }

      function renderSelection() {
        const items = selectedItems();
        const count = items.length;
        const exact = exactSelectionSize();
        const estimate = exact || sizeInfo("export");
        const chars = estimate.chars;
        const tokens = estimate.tokens;
        const pending = count > 0 && !exact;
        const previewReady = Boolean(
          state.activeUuid
          && state.previewData
          && state.previewData.uuid === state.activeUuid
          && state.previewData.format === state.format
        );
        dom.selectionCount.textContent = compactNumber(count);
        dom.selectionLabel.textContent = count === 0
          ? "Noch nichts ausgewählt"
          : formatNumber(count) + " " + plural(count, "Chat ausgewählt", "Chats ausgewählt");
        dom.selectionMeta.textContent = count === 0
          ? "Über die Hakenfelder oder „Alle gefilterten wählen“ auswählen"
          : pending
            ? "Vollständige Größe wird berechnet …"
            : "ca. " + compactNumber(tokens) + " Tokens · " + formatBytesFromChars(chars);
        dom.clearSelection.classList.toggle("hidden", count === 0);
        dom.exportButton.disabled = count === 0 || pending;
        dom.copyButton.disabled = !state.activeUuid || !previewReady;
        dom.exportButton.title = pending ? "Die vollständige Exportgröße wird gerade berechnet" : "";
        dom.copyButton.title = !state.activeUuid
          ? "Öffne zuerst einen Chat"
          : !previewReady
            ? "Die vollständige Chatgröße wird gerade berechnet"
            : (count > 1 ? "Kopiert den aktuell geöffneten Chat; Exportieren speichert die gesamte Auswahl" : "Kopiert den aktuell geöffneten Chat");
        updateSelectAll();
      }


      function showPreviewState(name) {
        dom.previewEmpty.classList.toggle("hidden", name !== "empty");
        dom.previewLoading.classList.toggle("hidden", name !== "loading");
        dom.previewContent.classList.toggle("hidden", name !== "content");
      }

      async function requestPreview(uuid, scrollToTop = true) {
        const item = state.byId.get(uuid) || state.filtered.find((entry) => entry.uuid === uuid);
        if (!item) {
          showPreviewState("empty");
          return;
        }
        state.activeUuid = uuid;
        state.previewData = null;
        dom.previewTitle.textContent = item.title || "Unbenannter Chat";
        dom.previewTitle.title = item.title || "Unbenannter Chat";
        const initialSize = estimateItems([item]);
        dom.previewSubtitle.textContent = formatNumber(item.message_count) + " " + plural(item.message_count, "Nachricht", "Nachrichten")
          + " · ca. " + compactNumber(initialSize.tokens) + " Tokens · " + formatDate(item.created_at);
        dom.previewStatus.classList.add("hidden");
        showPreviewState("loading");
        const sequence = ++state.previewSequence;
        renderSelection();

        try {
          const result = await apiCall("get_preview", uuid, state.format);
          if (sequence !== state.previewSequence) return;
          if (!result || result.ok === false || (result.error && !result.text)) throw new Error(text(result && result.error, "Vorschau konnte nicht geladen werden."));
          state.previewData = { ...result, uuid: uuid, format: state.format };
          if (state.selected.size === 1 && state.selected.has(uuid)) {
            state.selectionSize = {
              key: selectionKey(),
              count: 1,
              chars: number(result.total_chars),
              tokens: number(result.estimated_tokens)
            };
          }
          dom.previewSubtitle.textContent = formatNumber(item.message_count) + " " + plural(item.message_count, "Nachricht", "Nachrichten")
            + " · ca. " + compactNumber(result.estimated_tokens) + " Tokens · " + formatDate(item.created_at);
          dom.previewText.textContent = text(result.text);
          dom.previewTruncated.classList.toggle("hidden", !result.truncated);
          if (result.truncated) {
            dom.previewTruncatedText.textContent = "Die Vorschau zeigt nur einen Ausschnitt von " + formatNumber(result.total_chars) + " Zeichen. Kopie und Export werden gegenüber dem gewählten Format nicht zusätzlich gekürzt.";
          }
          dom.previewWarnings.replaceChildren();
          (Array.isArray(result.warnings) ? result.warnings : []).forEach((warning) => {
            const row = document.createElement("div");
            row.className = "preview-warning";
            row.textContent = "Hinweis: " + text(warning);
            dom.previewWarnings.appendChild(row);
          });
          dom.previewStatusText.textContent = result.truncated ? "Vorschau gekürzt" : "Vollständige Vorschau";
          dom.previewStatus.classList.remove("hidden");
          showPreviewState("content");
          if (scrollToTop) dom.previewContent.scrollTop = 0;
          renderSelection();
        } catch (error) {
          if (sequence !== state.previewSequence) return;
          dom.previewText.textContent = "Die Vorschau konnte nicht geladen werden.\n\n" + text(error.message, error);
          dom.previewTruncated.classList.add("hidden");
          dom.previewWarnings.replaceChildren();
          showPreviewState("content");
          toast(text(error.message, error), "error");
        }
      }

      let searchTimer = null;
      function queueSearch(immediate = false) {
        window.clearTimeout(searchTimer);
        searchTimer = window.setTimeout(runSearch, immediate ? 0 : 180);
      }

      async function runSearch() {
        if (!state.loaded) return;
        const sequence = ++state.searchSequence;
        dom.searchSpinner.classList.remove("hidden");
        dom.clearSearch.classList.toggle("hidden", !dom.searchInput.value);
        try {
          const result = await apiCall("search", dom.searchInput.value.trim(), currentFilters(), dom.sortSelect.value);
          if (sequence !== state.searchSequence) return;
          const items = normalizeConversations(Array.isArray(result) ? result : (result && result.conversations));
          state.filtered = items;
          items.forEach((item) => {
            state.byId.set(item.uuid, item);
          });
          state.visibleLimit = PAGE_SIZE;
          state.lastSelectionIndex = -1;
          renderList();
          renderSelection();
        } catch (error) {
          if (sequence === state.searchSequence) toast("Suche fehlgeschlagen: " + text(error.message, error), "error");
        } finally {
          if (sequence === state.searchSequence) dom.searchSpinner.classList.add("hidden");
        }
      }

      async function chooseSource() {
        setLoading("Claude-Export wird eingelesen", "Große Exporte können einen Moment dauern.");
        try {
          const snapshot = await apiCall("choose_source");
          if (snapshot && snapshot.cancelled) {
            showView(state.loaded ? "workspace" : "empty");
            return;
          }
          applySnapshot(snapshot);
          if (state.loaded && state.all.length) toast(formatNumber(state.all.length) + " Chats geladen.");
        } catch (error) {
          showView(state.loaded ? "workspace" : "empty");
          toast(text(error.message, error), "error");
        }
      }

      function commitFormat(next) {
        state.format = next;
        state.previewData = null;
        state.selectionSize = null;
        state.selectionSizeSequence += 1;
        dom.formatSelect.value = next;
        renderSelection();
        if (state.activeUuid) requestPreview(state.activeUuid);
        queueSelectionSize();
      }

      function onFormatChange() {
        const next = dom.formatSelect.value;
        const previous = state.format;
        if (!VALID_FORMATS.has(next)) {
          dom.formatSelect.value = previous;
          return;
        }
        if (next === "chatgpt_markdown") {
          commitFormat(next);
          return;
        }

        const raw = next === "raw_json";
        openModal({
          eyebrow: "Vollständiger technischer Export",
          title: raw ? "Originaldaten wirklich verwenden?" : "Technische Details einschließen?",
          body: raw
            ? "JSON bewahrt die ursprüngliche Datenstruktur nahezu unverändert. Für das Einfügen in ChatGPT ist das empfohlene Markdown meist deutlich lesbarer und kompakter."
            : "Dieses Format nimmt zusätzlich Thinking-Blöcke, Tool-Aufrufe und -Ergebnisse, interne Prompts, technische Metadaten und vorhandene Verzweigungen auf. Dadurch kann die Datei erheblich größer werden.",
          facts: raw
            ? ["Gut für Archivierung und spätere Weiterverarbeitung", "Kann interne IDs, Zeitstempel und technische Felder enthalten", "Benötigt häufig deutlich mehr Kontext in ChatGPT"]
            : ["Thinking-, Tool- und Prompt-Blöcke werden vollständig ergänzt", "Technische Metadaten und Branch-Informationen bleiben erhalten", "Für sehr große Chats entstehen größere Dateien"],
          cancelText: "Empfohlenes Format behalten",
          confirmText: raw ? "JSON verwenden" : "Vollständig verwenden",
          onConfirm: () => commitFormat(next),
          onCancel: () => { dom.formatSelect.value = previous; }
        });
      }

      function formatFactor() {
        return state.format === "chatgpt_markdown" ? 1.57 : (state.format === "complete_markdown" ? 17.4 : 17.7);
      }

      function estimateItems(items) {
        const exact = items.map((item) => item.format_sizes && item.format_sizes[state.format]);
        if (exact.every((entry) => entry && Number.isFinite(entry.chars) && Number.isFinite(entry.tokens))) {
          return {
            count: items.length,
            chars: exact.reduce((sum, entry) => sum + entry.chars, 0),
            tokens: exact.reduce((sum, entry) => sum + entry.tokens, 0)
          };
        }
        const factor = formatFactor();
        return {
          count: items.length,
          chars: Math.round(items.reduce((sum, item) => sum + number(item.char_count), 0) * factor),
          tokens: Math.round(items.reduce((sum, item) => sum + number(item.estimated_tokens), 0) * factor)
        };
      }


      function sizeInfo(kind) {
        if (kind === "export") {
          const exact = exactSelectionSize();
          if (exact) return exact;
        }
        const items = kind === "copy"
          ? (state.byId.get(state.activeUuid) ? [state.byId.get(state.activeUuid)] : [])
          : selectedItems();
        const exactPreviewMatches = (
          state.previewData
          && state.previewData.uuid === state.activeUuid
          && state.previewData.format === state.format
          && number(state.previewData.total_chars) > 0
          && items.length === 1
          && items[0].uuid === state.activeUuid
        );
        if (exactPreviewMatches) {
          return {
            count: 1,
            chars: number(state.previewData.total_chars),
            tokens: number(state.previewData.estimated_tokens)
          };
        }
        return estimateItems(items);
      }


      function afterSizeConfirmation(kind, action) {
        const info = sizeInfo(kind);
        const isLarge = info.tokens >= 100000 || info.chars >= 500000 || (kind === "export" && info.count >= 100);
        if (!isLarge) {
          action();
          return;
        }
        openModal({
          eyebrow: "Großer Umfang",
          title: kind === "copy" ? "Dieser Chat ist sehr groß" : "Diese Auswahl ist sehr groß",
          body: kind === "copy"
            ? "Die Kopie kann das Kontextlimit eines einzelnen ChatGPT-Chats überschreiten. Gegenüber dem gewählten Exportformat wird sie nicht zusätzlich gekürzt."
            : "Der Export kann je nach Größe einige Sekunden dauern. Jede Konversation wird gegenüber dem gewählten Format ohne zusätzliche Kürzung in eine eigene Datei geschrieben.",
          facts: [formatNumber(info.count) + " " + plural(info.count, "Chat", "Chats"), "ca. " + formatNumber(info.tokens) + " Tokens", "geschätzte Textgröße: " + formatBytesFromChars(info.chars)],
          cancelText: "Zurück",
          confirmText: kind === "copy" ? "Trotzdem kopieren" : "Trotzdem exportieren",
          onConfirm: action
        });
      }

      async function copyActive() {
        if (!state.activeUuid) {
          toast("Öffne zuerst einen Chat.", "info");
          return;
        }
        setButtonBusy(dom.copyButton, true, "Wird kopiert …");
        try {
          const result = await apiCall("copy_selected", state.activeUuid, state.format);
          if (!result || result.ok === false) throw new Error(text(result && result.error, "Kopieren fehlgeschlagen."));
          const suffix = result.estimated_tokens ? " · ca. " + compactNumber(result.estimated_tokens) + " Tokens" : "";
          toast(formatNumber(result.chars) + " Zeichen für ChatGPT kopiert" + suffix + ".");
        } catch (error) {
          toast(text(error.message, error), "error");
        } finally {
          setButtonBusy(dom.copyButton, false, "");
          renderSelection();
        }
      }

      async function exportSelected() {
        const uuids = Array.from(state.selected);
        if (!uuids.length) {
          toast("Wähle mindestens einen Chat aus.", "info");
          return;
        }
        setButtonBusy(dom.exportButton, true, "Export läuft …");
        try {
          const result = await apiCall("export_selected", uuids, state.format);
          if (!result || result.ok === false) throw new Error(text(result && result.error, "Export fehlgeschlagen."));
          if (result.folder) {
            state.exportFolder = text(result.folder);
            renderFolder();
          }
          const count = number(result.count) || uuids.length;
          toast(formatNumber(count) + " " + plural(count, "Chat exportiert", "Chats exportiert") + ".", "success", "Ordner öffnen", revealFolder);
          if (Array.isArray(result.warnings) && result.warnings.length) {
            toast(result.warnings.map(text).join(" "), "info");
          }
        } catch (error) {
          toast(text(error.message, error), "error");
        } finally {
          setButtonBusy(dom.exportButton, false, "");
          renderSelection();
        }
      }

      async function chooseExportFolder() {
        try {
          const result = await apiCall("choose_export_folder");
          if (result && result.ok && result.folder) {
            state.exportFolder = text(result.folder);
            renderFolder();
            toast("Ausgabeordner aktualisiert.");
          } else if (result && result.error) {
            throw new Error(text(result.error));
          }
        } catch (error) {
          toast(text(error.message, error), "error");
        }
      }

      async function revealFolder() {
        if (!state.exportFolder) {
          chooseExportFolder();
          return;
        }
        try {
          const result = await apiCall("reveal_export_folder");
          if (!result || result.ok === false) throw new Error(text(result && result.error, "Ordner konnte nicht geöffnet werden."));
        } catch (error) {
          toast(text(error.message, error), "error");
        }
      }

      async function showLegalNotices() {
        try {
          const result = await apiCall("get_legal_notices");
          if (!result || result.ok === false) {
            throw new Error(text(result && result.error, "Lizenzhinweise konnten nicht geladen werden."));
          }
          openModal({
            eyebrow: "Open Source",
            title: "Lizenzen und Drittanbieterhinweise",
            body: "Der Projektcode steht unter MIT. Die folgenden Texte gehören zu den in dieser EXE enthaltenen Komponenten.",
            legalText: text(result.text),
            confirmText: "Schließen",
            hideCancel: true
          });
        } catch (error) {
          toast(text(error.message, error), "error");
        }
      }

      function bindEvents() {
        dom.chooseSourceButton.addEventListener("click", chooseSource);
        dom.changeSourceButton.addEventListener("click", chooseSource);
        dom.topSourceButton.addEventListener("click", chooseSource);
        dom.clearSearch.addEventListener("click", () => {
          dom.searchInput.value = "";
          dom.clearSearch.classList.add("hidden");
          dom.searchInput.focus();
          queueSearch(true);
        });
        dom.searchInput.addEventListener("input", () => {
          dom.clearSearch.classList.toggle("hidden", !dom.searchInput.value);
          queueSearch();
        });
        dom.sortSelect.addEventListener("change", () => queueSearch(true));
        document.querySelectorAll("[data-filter]").forEach((button) => {
          button.addEventListener("click", () => {
            const key = button.dataset.filter;
            filters[key] = !filters[key];
            button.classList.toggle("active", filters[key]);
            button.setAttribute("aria-pressed", filters[key] ? "true" : "false");
            queueSearch(true);
          });
        });
        dom.selectAllFiltered.addEventListener("change", () => {
          const shouldSelect = dom.selectAllFiltered.checked;
          state.filtered.forEach((item) => {
            if (shouldSelect) state.selected.add(item.uuid); else state.selected.delete(item.uuid);
          });
          state.lastSelectionIndex = -1;
          renderList();
          queueSelectionSize();
        });
        dom.clearSelection.addEventListener("click", () => {
          state.selected.clear();
          state.lastSelectionIndex = -1;
          renderList();
          queueSelectionSize();
        });
        dom.formatSelect.addEventListener("change", onFormatChange);
        dom.folderButton.addEventListener("click", chooseExportFolder);
        dom.revealFolderButton.addEventListener("click", revealFolder);
        dom.copyButton.addEventListener("click", () => afterSizeConfirmation("copy", copyActive));
        dom.exportButton.addEventListener("click", () => afterSizeConfirmation("export", exportSelected));
        dom.legalButton.addEventListener("click", showLegalNotices);
        dom.privacyBadge.addEventListener("click", () => openModal({
          eyebrow: "100 % lokal",
          title: "Deine Gespräche verlassen diesen Computer nicht",
          body: "Der Exporter liest, durchsucht, kopiert und speichert deine Claude-Daten ausschließlich lokal. Es gibt keinen Upload und keine Verbindung zu einem fremden Server.",
          facts: ["Keine Anmeldung erforderlich", "Keine Cloud-Verarbeitung", "Du bestimmst Quelle und Ausgabeordner"],
          confirmText: "Verstanden",
          hideCancel: true
        }));
        dom.modalCancel.addEventListener("click", () => closeModal(false));
        dom.modalConfirm.addEventListener("click", () => closeModal(true));
        dom.modalLayer.addEventListener("mousedown", (event) => {
          if (event.target === dom.modalLayer) closeModal(false);
        });
        dom.modalLayer.addEventListener("keydown", (event) => {
          if (event.key === "Escape") {
            event.preventDefault();
            closeModal(false);
            return;
          }
          if (event.key !== "Tab") return;
          const focusable = Array.from(dom.modalLayer.querySelectorAll("[tabindex='0']:not(.hidden), button:not(.hidden):not(:disabled)"));
          if (!focusable.length) return;
          const first = focusable[0];
          const last = focusable[focusable.length - 1];
          if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
          else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
        });
        document.addEventListener("keydown", (event) => {
          const modifier = event.ctrlKey || event.metaKey;
          if (!dom.modalLayer.classList.contains("hidden")) {
            if (modifier && ["f", "e"].includes(event.key.toLowerCase())) event.preventDefault();
            return;
          }
          if (modifier && event.key.toLowerCase() === "f") {
            event.preventDefault();
            if (!dom.workspace.classList.contains("hidden")) {
              dom.searchInput.focus();
              dom.searchInput.select();
            }
          }
          if (modifier && event.key.toLowerCase() === "e") {
            event.preventDefault();
            if (!dom.exportButton.disabled) afterSizeConfirmation("export", exportSelected);
          }
        });
      }

      async function bootstrap() {
        if (state.booted) return;
        state.booted = true;
        bindEvents();
        setLoading("Claude-Daten werden vorbereitet", "Alles bleibt auf diesem Computer.");
        try {
          const snapshot = await apiCall("initialize");
          applySnapshot(snapshot);
        } catch (error) {
          dom.emptyTitle.textContent = "Programm konnte nicht gestartet werden";
          dom.emptyCopy.textContent = text(error.message, error) + " Starte das Programm erneut oder wähle den Export manuell.";
          showView("empty");
          toast(text(error.message, error), "error");
        }
      }

      window.addEventListener("pywebviewready", bootstrap, { once: true });
      if (window.pywebview && window.pywebview.api) window.setTimeout(bootstrap, 0);
    })();
  </script>
</body>
</html>
"""
