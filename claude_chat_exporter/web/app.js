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
