const COMMON_TAGS = [
  "backend",
  "frontend",
  "api",
  "bug",
  "feature",
  "docs",
  "test",
  "release",
  "design",
  "research",
  "urgent",
  "ops",
];

const API_MAX_PAGE_SIZE = 100;

const state = {
  tasks: [],
  catalogTasks: [],
  total: 0,
  currentPage: 1,
  pageSize: 8,
  selectedTaskId: null,
  selectedTask: null,
  selectedTree: null,
  health: null,
  cacheStatus: "--",
  mode: "create",
  availableTagStats: [],
  customTags: [],
  formSelectedTags: [],
  liveClockTimer: null,
  filters: {
    search: "",
    status: "",
    priority: "",
    tag: "",
    sortBy: "created_at",
    order: "desc",
  },
};

const elements = {
  refreshButton: document.querySelector("#refresh-dashboard"),
  serviceStatus: document.querySelector("#service-status"),
  serviceMeta: document.querySelector("#service-meta"),
  statsGrid: document.querySelector("#stats-grid"),
  formTitle: document.querySelector("#form-title"),
  taskForm: document.querySelector("#task-form"),
  titleInput: document.querySelector("#task-title"),
  descriptionInput: document.querySelector("#task-description"),
  statusInput: document.querySelector("#task-status"),
  priorityInput: document.querySelector("#task-priority"),
  tagSelector: document.querySelector("#tag-selector"),
  selectedTags: document.querySelector("#selected-tags"),
  newTagInput: document.querySelector("#new-tag-input"),
  addNewTagButton: document.querySelector("#add-new-tag"),
  submitButton: document.querySelector("#submit-button"),
  cancelEditButton: document.querySelector("#cancel-edit"),
  resetFormButton: document.querySelector("#reset-form"),
  searchInput: document.querySelector("#search-input"),
  filterStatus: document.querySelector("#filter-status"),
  filterPriority: document.querySelector("#filter-priority"),
  filterTags: document.querySelector("#filter-tags"),
  sortBy: document.querySelector("#sort-by"),
  sortOrder: document.querySelector("#sort-order"),
  cacheIndicator: document.querySelector("#cache-indicator"),
  taskBoard: document.querySelector("#task-board"),
  pageIndicator: document.querySelector("#page-indicator"),
  prevPage: document.querySelector("#prev-page"),
  nextPage: document.querySelector("#next-page"),
  detailEmpty: document.querySelector("#detail-empty"),
  detailContent: document.querySelector("#detail-content"),
  detailTitle: document.querySelector("#detail-title"),
  detailDescription: document.querySelector("#detail-description"),
  detailMeta: document.querySelector("#detail-meta"),
  detailTags: document.querySelector("#detail-tags"),
  dependencySelect: document.querySelector("#dependency-select"),
  addDependencyButton: document.querySelector("#add-dependency"),
  directDependencies: document.querySelector("#direct-dependencies"),
  dependencyTree: document.querySelector("#dependency-tree"),
  toastZone: document.querySelector("#toast-zone"),
};

document.addEventListener("DOMContentLoaded", () => {
  bindEvents();
  initializeDashboard();
});

function bindEvents() {
  elements.refreshButton.addEventListener("click", async () => {
    await Promise.all([loadHealth(), refreshAllData()]);
    showToast("首页数据和服务信息已刷新。", "success");
  });

  elements.taskForm.addEventListener("submit", handleTaskSubmit);
  elements.cancelEditButton.addEventListener("click", resetTaskForm);
  elements.resetFormButton.addEventListener("click", resetTaskForm);

  elements.addNewTagButton.addEventListener("click", handleAddCustomTag);
  elements.newTagInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleAddCustomTag();
    }
  });

  elements.tagSelector.addEventListener("click", (event) => {
    event.preventDefault();
    const button = event.target.closest("[data-form-tag]");
    if (!button) {
      return;
    }

    toggleFormTag(button.dataset.formTag);
  });

  elements.selectedTags.addEventListener("click", (event) => {
    event.preventDefault();
    const button = event.target.closest("[data-remove-form-tag]");
    if (!button) {
      return;
    }

    toggleFormTag(button.dataset.removeFormTag);
  });

  elements.filterTags.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-filter-tag]");
    if (!button) {
      return;
    }

    const selectedTag = button.dataset.filterTag || "";
    state.filters.tag = state.filters.tag === selectedTag ? "" : selectedTag;
    state.currentPage = 1;
    renderFilterTags();
    await loadTasks();
  });

  const debouncedFetch = debounce(async () => {
    state.currentPage = 1;
    await loadTasks();
  }, 280);

  elements.searchInput.addEventListener("input", async (event) => {
    state.filters.search = event.target.value;
    debouncedFetch();
  });

  elements.filterStatus.addEventListener("change", async (event) => {
    state.filters.status = event.target.value;
    state.currentPage = 1;
    await loadTasks();
  });

  elements.filterPriority.addEventListener("change", async (event) => {
    state.filters.priority = event.target.value;
    state.currentPage = 1;
    await loadTasks();
  });

  elements.sortBy.addEventListener("change", async (event) => {
    state.filters.sortBy = event.target.value;
    state.currentPage = 1;
    await loadTasks();
  });

  elements.sortOrder.addEventListener("change", async (event) => {
    state.filters.order = event.target.value;
    state.currentPage = 1;
    await loadTasks();
  });

  elements.prevPage.addEventListener("click", async () => {
    if (state.currentPage <= 1) {
      return;
    }
    state.currentPage -= 1;
    await loadTasks();
  });

  elements.nextPage.addEventListener("click", async () => {
    const totalPages = Math.max(1, Math.ceil(state.total / state.pageSize));
    if (state.currentPage >= totalPages) {
      return;
    }
    state.currentPage += 1;
    await loadTasks();
  });

  elements.taskBoard.addEventListener("click", async (event) => {
    const actionButton = event.target.closest("[data-action]");
    const card = event.target.closest("[data-task-id]");
    if (!card) {
      return;
    }

    const taskId = card.dataset.taskId;
    if (!taskId) {
      return;
    }

    if (!actionButton) {
      await selectTask(taskId);
      return;
    }

    const action = actionButton.dataset.action;
    if (action === "edit") {
      await selectTask(taskId, { populateForm: true });
      return;
    }

    if (action === "advance") {
      await advanceTaskStatus(taskId);
      return;
    }

    if (action === "delete") {
      await deleteTask(taskId);
    }
  });

  elements.addDependencyButton.addEventListener("click", async () => {
    const dependencyId = elements.dependencySelect.value;
    if (!state.selectedTaskId || !dependencyId) {
      showToast("请先选择当前任务和要绑定的依赖任务。", "error");
      return;
    }

    try {
      await apiRequest(`/api/tasks/${state.selectedTaskId}/dependencies/${dependencyId}`, {
        method: "POST",
      });
      showToast("依赖关系已添加。", "success");
      await refreshAllData({ keepSelection: true });
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    }
  });

  elements.directDependencies.addEventListener("click", async (event) => {
    const removeButton = event.target.closest("[data-remove-dependency]");
    if (!removeButton || !state.selectedTaskId) {
      return;
    }

    const dependencyId = removeButton.dataset.removeDependency;
    if (!dependencyId) {
      return;
    }

    try {
      await apiRequest(`/api/tasks/${state.selectedTaskId}/dependencies/${dependencyId}`, {
        method: "DELETE",
      });
      showToast("依赖关系已移除。", "success");
      await refreshAllData({ keepSelection: true });
    } catch (error) {
      showToast(getErrorMessage(error), "error");
    }
  });
}

async function initializeDashboard() {
  startLiveClock();
  await Promise.all([loadHealth(), refreshAllData()]);
}

async function refreshAllData(options = {}) {
  await loadCatalogTasks();
  await loadTasks(options);
}

function startLiveClock() {
  if (state.liveClockTimer) {
    return;
  }

  updateLiveClockDisplay();
  state.liveClockTimer = window.setInterval(updateLiveClockDisplay, 1000);
}

function updateLiveClockDisplay() {
  const liveClock = document.querySelector("#live-clock-value");
  if (!liveClock) {
    return;
  }

  liveClock.textContent = formatDateTime(new Date().toISOString());
}

async function loadHealth() {
  try {
    const { payload } = await fetchJson("/health");
    state.health = payload;
    renderHealth();
  } catch (error) {
    elements.serviceStatus.textContent = "服务状态未知";
    showToast("健康检查读取失败。", "error");
  }
}

async function loadCatalogTasks() {
  try {
    const result = await fetchTaskCollection("/api/tasks", {
      sort_by: "created_at",
      order: "desc",
    });
    state.catalogTasks = result.items;
    state.availableTagStats = buildTagStats(state.catalogTasks, state.customTags);
    renderStats();
    renderTagSelector();
    renderSelectedTags();
    renderFilterTags();
  } catch (error) {
    state.catalogTasks = [];
    state.availableTagStats = buildTagStats([], state.customTags);
    renderStats();
    renderTagSelector();
    renderSelectedTags();
    renderFilterTags();
    showToast(getErrorMessage(error), "error");
  }
}

async function loadTasks(options = {}) {
  const keepSelection = options.keepSelection ?? true;

  try {
    const searchKeyword = state.filters.search.trim();
    const result = searchKeyword ? await searchTasks(searchKeyword) : await listTasks();
    state.tasks = result.items;
    state.total = result.total;
    state.cacheStatus = result.cacheStatus || "--";
    renderStats();
    renderBoard();
    renderPagination();
    renderCacheStatus();

    if (state.selectedTaskId) {
      const selectedTaskStillExists = state.catalogTasks.some((task) => task.id === state.selectedTaskId);
      if (!selectedTaskStillExists) {
        clearSelection();
      } else if (keepSelection) {
        await selectTask(state.selectedTaskId);
      }
    }
  } catch (error) {
    showToast(getErrorMessage(error), "error");
  }
}

async function listTasks() {
  const params = new URLSearchParams({
    page: String(state.currentPage),
    page_size: String(state.pageSize),
    sort_by: state.filters.sortBy,
    order: state.filters.order,
  });

  if (state.filters.status) {
    params.set("status", state.filters.status);
  }
  if (state.filters.priority) {
    params.set("priority", state.filters.priority);
  }
  if (state.filters.tag) {
    params.append("tags", state.filters.tag);
  }

  const { response, payload } = await fetchJson(`/api/tasks?${params.toString()}`);

  return {
    items: payload.items || [],
    total: payload.total || 0,
    cacheStatus: response.headers.get("X-Cache"),
  };
}

async function searchTasks(keyword) {
  const { items: allItems, cacheStatus } = await fetchTaskCollection("/api/tasks/search", {
    q: keyword,
  });

  const filteredTasks = applyLocalFilters(allItems);
  const total = filteredTasks.length;
  const start = (state.currentPage - 1) * state.pageSize;
  const items = filteredTasks.slice(start, start + state.pageSize);

  return {
    items,
    total,
    cacheStatus,
  };
}

function applyLocalFilters(items) {
  let filtered = [...items];

  if (state.filters.status) {
    filtered = filtered.filter((task) => task.status === state.filters.status);
  }
  if (state.filters.priority) {
    filtered = filtered.filter((task) => task.priority === state.filters.priority);
  }
  if (state.filters.tag) {
    const selectedTag = state.filters.tag.toLowerCase();
    filtered = filtered.filter((task) =>
      (task.tags || []).some((tag) => tag.toLowerCase() === selectedTag),
    );
  }

  filtered.sort((left, right) => compareTasks(left, right, state.filters.sortBy, state.filters.order));
  return filtered;
}

function compareTasks(left, right, sortBy, order) {
  const direction = order === "asc" ? 1 : -1;
  const priorityRank = { low: 1, medium: 2, high: 3 };
  const statusRank = { pending: 1, in_progress: 2, completed: 3 };

  let leftValue = left.created_at;
  let rightValue = right.created_at;

  if (sortBy === "priority") {
    leftValue = priorityRank[left.priority] || 0;
    rightValue = priorityRank[right.priority] || 0;
  } else if (sortBy === "status") {
    leftValue = statusRank[left.status] || 0;
    rightValue = statusRank[right.status] || 0;
  }

  if (leftValue < rightValue) {
    return -1 * direction;
  }
  if (leftValue > rightValue) {
    return 1 * direction;
  }
  return 0;
}

async function selectTask(taskId, options = {}) {
  state.selectedTaskId = taskId;

  try {
    const [detailResult, treeResult] = await Promise.all([
      fetchTaskDetail(taskId),
      fetchDependencyTree(taskId),
    ]);

    state.selectedTask = detailResult.payload;
    state.selectedTree = treeResult.payload;
    renderBoard();
    renderDetailPanel();

    if (options.populateForm) {
      populateFormForEdit(state.selectedTask);
    }
  } catch (error) {
    showToast(getErrorMessage(error), "error");
  }
}

async function fetchTaskDetail(taskId) {
  const { response, payload } = await fetchJson(`/api/tasks/${taskId}`);
  return { payload, cacheStatus: response.headers.get("X-Cache") };
}

async function fetchDependencyTree(taskId) {
  const { response, payload } = await fetchJson(`/api/tasks/${taskId}/dependencies/tree`);
  return { payload, cacheStatus: response.headers.get("X-Cache") };
}

async function handleTaskSubmit(event) {
  event.preventDefault();

  const payload = {
    title: elements.titleInput.value.trim(),
    description: elements.descriptionInput.value.trim() || null,
    status: elements.statusInput.value,
    priority: elements.priorityInput.value,
    tags: [...state.formSelectedTags],
  };

  if (!payload.title) {
    showToast("标题不能为空。", "error");
    return;
  }

  const isEditing = state.mode === "edit" && state.selectedTaskId;

  try {
    const response = await apiRequest(
      isEditing ? `/api/tasks/${state.selectedTaskId}` : "/api/tasks",
      {
        method: isEditing ? "PATCH" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
    );

    showToast(isEditing ? "任务已更新。" : "任务已创建。", "success");
    const selectedId = response.id || state.selectedTaskId;
    await refreshAllData({ keepSelection: false });
    if (selectedId) {
      await selectTask(selectedId);
    }
    resetTaskForm();
  } catch (error) {
    showToast(getErrorMessage(error), "error");
  }
}

function handleAddCustomTag() {
  const tag = normalizeTag(elements.newTagInput.value);
  if (!tag) {
    showToast("请输入有效的新标签名称。", "error");
    return;
  }

  if (!state.formSelectedTags.includes(tag)) {
    state.formSelectedTags.push(tag);
  }

  if (!state.customTags.includes(tag)) {
    state.customTags.push(tag);
  }

  elements.newTagInput.value = "";
  state.availableTagStats = buildTagStats(state.catalogTasks, state.customTags);
  renderTagSelector();
  renderSelectedTags();
  renderFilterTags();
  showToast(`已添加标签「${tag}」。`, "success");
}

function toggleFormTag(tagValue) {
  const tag = normalizeTag(tagValue);
  if (!tag) {
    return;
  }

  if (state.formSelectedTags.includes(tag)) {
    state.formSelectedTags = state.formSelectedTags.filter((item) => item !== tag);
  } else {
    state.formSelectedTags = [...state.formSelectedTags, tag];
  }

  renderTagSelector();
  renderSelectedTags();
}

async function advanceTaskStatus(taskId) {
  const task = state.catalogTasks.find((item) => item.id === taskId);
  if (!task) {
    return;
  }

  const nextStatus =
    task.status === "pending" ? "in_progress" : task.status === "in_progress" ? "completed" : "completed";
  if (nextStatus === task.status) {
    showToast("这个任务已经是完成状态。", "info");
    return;
  }

  try {
    await apiRequest(`/api/tasks/${taskId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: nextStatus }),
    });
    showToast("任务状态已更新。", "success");
    await refreshAllData({ keepSelection: true });
  } catch (error) {
    showToast(getErrorMessage(error), "error");
  }
}

async function deleteTask(taskId) {
  const task = state.catalogTasks.find((item) => item.id === taskId);
  const confirmed = window.confirm(`确认删除任务「${task?.title || taskId}」吗？`);
  if (!confirmed) {
    return;
  }

  try {
    await apiRequest(`/api/tasks/${taskId}`, { method: "DELETE" });
    if (state.selectedTaskId === taskId) {
      clearSelection();
    }
    showToast("任务已删除。", "success");
    await refreshAllData({ keepSelection: true });
  } catch (error) {
    showToast(getErrorMessage(error), "error");
  }
}

function clearSelection() {
  state.selectedTaskId = null;
  state.selectedTask = null;
  state.selectedTree = null;
  renderBoard();
  renderDetailPanel();
  resetTaskForm();
}

function populateFormForEdit(task) {
  state.mode = "edit";
  elements.formTitle.textContent = "编辑任务";
  elements.submitButton.textContent = "保存更新";
  elements.titleInput.value = task.title || "";
  elements.descriptionInput.value = task.description || "";
  elements.statusInput.value = task.status || "pending";
  elements.priorityInput.value = task.priority || "medium";
  state.formSelectedTags = [...(task.tags || [])].map(normalizeTag).filter(Boolean);
  state.formSelectedTags.forEach((tag) => {
    if (!state.customTags.includes(tag)) {
      state.customTags.push(tag);
    }
  });
  state.availableTagStats = buildTagStats(state.catalogTasks, state.customTags);
  renderTagSelector();
  renderSelectedTags();
}

function resetTaskForm() {
  state.mode = "create";
  elements.formTitle.textContent = "创建新任务";
  elements.submitButton.textContent = "保存任务";
  elements.taskForm.reset();
  elements.statusInput.value = "pending";
  elements.priorityInput.value = "medium";
  state.formSelectedTags = [];
  renderTagSelector();
  renderSelectedTags();
}

function renderHealth() {
  const health = state.health;
  if (!health) {
    return;
  }

  elements.serviceStatus.textContent = health.database ? "数据库在线" : "数据库离线";
  elements.serviceStatus.style.background = health.database
    ? "rgba(33, 79, 71, 0.12)"
    : "rgba(208, 103, 61, 0.16)";
  elements.serviceStatus.style.color = health.database ? "var(--forest)" : "var(--accent-deep)";

  const items = [
    { label: "服务名", value: escapeHtml(health.app_name || "-") },
    { label: "版本", value: escapeHtml(health.version || "-") },
    { label: "上次同步", value: escapeHtml(formatDateTime(health.timestamp)) },
    { label: "实时时间", value: `<span id="live-clock-value">${escapeHtml(formatDateTime(new Date().toISOString()))}</span>` },
  ];

  elements.serviceMeta.innerHTML = items
    .map(
      (item) => `
        <div class="service-card">
          <strong>${item.label}</strong>
          <span>${item.value}</span>
        </div>
      `,
    )
    .join("");
}

function renderStats() {
  const tasks = state.catalogTasks;
  const pending = tasks.filter((task) => task.status === "pending").length;
  const inProgress = tasks.filter((task) => task.status === "in_progress").length;
  const completed = tasks.filter((task) => task.status === "completed").length;
  const cards = [
    { label: "任务总数", value: tasks.length },
    { label: "待处理", value: pending },
    { label: "进行中", value: inProgress },
    { label: "已完成", value: completed },
  ];

  elements.statsGrid.innerHTML = cards
    .map(
      (item) => `
        <div class="stat-card">
          <strong>${item.value}</strong>
          <span>${item.label}</span>
        </div>
      `,
    )
    .join("");
}

function renderTagSelector() {
  const tags = getFormTagStats();
  elements.tagSelector.innerHTML = tags
    .map((tag) => {
      const selectedClass = state.formSelectedTags.includes(tag.name) ? "is-selected" : "";
      return `
        <button class="tag-choice ${selectedClass}" type="button" data-form-tag="${escapeHtml(tag.name)}">
          <span class="tag-choice-name">${escapeHtml(tag.name)}</span>
          <span class="tag-choice-count">${tag.count}</span>
        </button>
      `;
    })
    .join("");
}

function renderSelectedTags() {
  if (!state.formSelectedTags.length) {
    elements.selectedTags.innerHTML = `<span class="selected-tags-empty">还没有选择标签。你可以先点选常用标签，也可以添加新的标签。</span>`;
    return;
  }

  elements.selectedTags.innerHTML = state.formSelectedTags
    .map((tag) => {
      const count = getTagCount(tag);
      return `
        <span class="selected-tag-chip">
          <span>${escapeHtml(tag)} · ${count}</span>
          <button type="button" data-remove-form-tag="${escapeHtml(tag)}">×</button>
        </span>
      `;
    })
    .join("");
}

function renderFilterTags() {
  const activeTag = state.filters.tag;
  const usedTags = getFilterTagStats();

  const chips = [
    `
      <button class="tag-choice ${activeTag ? "" : "is-filter-active"}" type="button" data-filter-tag="">
        <span class="tag-choice-name">全部标签</span>
        <span class="tag-choice-count">${state.catalogTasks.length}</span>
      </button>
    `,
  ];

  if (!usedTags.length) {
    chips.push(`<div class="selected-tags-empty">当前还没有可筛选的标签。</div>`);
  } else {
    usedTags.forEach((tag) => {
      const selectedClass = activeTag === tag.name ? "is-filter-active" : "";
      chips.push(`
        <button class="tag-choice ${selectedClass}" type="button" data-filter-tag="${escapeHtml(tag.name)}">
          <span class="tag-choice-name">${escapeHtml(tag.name)}</span>
          <span class="tag-choice-count">${tag.count}</span>
        </button>
      `);
    });
  }

  elements.filterTags.innerHTML = chips.join("");
}

function renderBoard() {
  if (!state.tasks.length) {
    elements.taskBoard.innerHTML = `
      <div class="empty-board">
        当前筛选条件下还没有任务。你可以调整搜索条件，或者直接在上方表单里创建一个新任务。
      </div>
    `;
    return;
  }

  elements.taskBoard.innerHTML = state.tasks
    .map((task) => {
      const statusLabel = statusToLabel(task.status);
      const priorityLabel = priorityToLabel(task.priority);
      const description = task.description ? escapeHtml(task.description) : "这个任务暂时还没有补充说明。";
      const tags = task.tags?.length
        ? task.tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")
        : `<span class="tag">未添加标签</span>`;
      const selectedClass = state.selectedTaskId === task.id ? "is-active" : "";
      const advanceLabel = task.status === "pending" ? "开始处理" : "标记完成";
      const advanceDisabled = task.status === "completed" ? "disabled" : "";

      return `
        <article class="task-card ${selectedClass}" data-task-id="${task.id}">
          <div class="task-top">
            <span class="badge ${task.status}">${statusLabel}</span>
            <span class="badge ${task.priority}">${priorityLabel}</span>
          </div>
          <div>
            <h3>${escapeHtml(task.title)}</h3>
            <p>${description}</p>
          </div>
          <div class="tag-row">${tags}</div>
          <div class="meta-pills">
            <span class="mini-badge ${task.status}">${statusLabel}</span>
            <span class="tag">更新于 ${formatDateTime(task.updated_at, { compact: true })}</span>
          </div>
          <div class="task-actions">
            <button class="mini-button" data-action="edit" type="button">编辑</button>
            <button class="mini-button" data-action="advance" type="button" ${advanceDisabled}>${advanceLabel}</button>
            <button class="mini-button warn" data-action="delete" type="button">删除</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderPagination() {
  const totalPages = Math.max(1, Math.ceil(state.total / state.pageSize));
  elements.pageIndicator.textContent = `第 ${state.currentPage} / ${totalPages} 页`;
  elements.prevPage.disabled = state.currentPage <= 1;
  elements.nextPage.disabled = state.currentPage >= totalPages;
}

function renderCacheStatus() {
  elements.cacheIndicator.textContent = `X-Cache: ${state.cacheStatus || "--"}`;
}

function renderDetailPanel() {
  if (!state.selectedTask || !state.selectedTree) {
    elements.detailEmpty.classList.remove("hidden");
    elements.detailContent.classList.add("hidden");
    return;
  }

  elements.detailEmpty.classList.add("hidden");
  elements.detailContent.classList.remove("hidden");
  elements.detailTitle.textContent = state.selectedTask.title;
  elements.detailDescription.textContent =
    state.selectedTask.description || "这个任务目前还没有补充描述。";

  const metaItems = [
    { label: "当前状态", value: statusToLabel(state.selectedTask.status) },
    { label: "优先级", value: priorityToLabel(state.selectedTask.priority) },
    { label: "创建时间", value: formatDateTime(state.selectedTask.created_at) },
    { label: "更新时间", value: formatDateTime(state.selectedTask.updated_at) },
  ];

  elements.detailMeta.innerHTML = metaItems
    .map(
      (item) => `
        <div class="detail-meta-card">
          <strong>${item.label}</strong>
          <span>${item.value}</span>
        </div>
      `,
    )
    .join("");

  elements.detailTags.innerHTML = (state.selectedTask.tags || []).length
    ? state.selectedTask.tags
        .map((tag) => {
          const count = getTagCount(tag);
          return `<span class="tag">${escapeHtml(tag)} · ${count}</span>`;
        })
        .join("")
    : `<span class="tag">未添加标签</span>`;

  renderDependencySelect();
  renderDirectDependencies();
  renderDependencyTree();
}

function renderDependencySelect() {
  const excludedIds = new Set([state.selectedTaskId]);
  (state.selectedTree.dependencies || []).forEach((dependency) => excludedIds.add(dependency.id));

  const options = state.catalogTasks.filter((task) => !excludedIds.has(task.id));
  elements.dependencySelect.innerHTML = options.length
    ? options
        .map((task) => `<option value="${task.id}">${escapeHtml(task.title)}</option>`)
        .join("")
    : `<option value="">没有可添加的依赖任务</option>`;
}

function renderDirectDependencies() {
  const directDependencies = state.selectedTree.dependencies || [];
  if (!directDependencies.length) {
    elements.directDependencies.innerHTML = `<div class="empty-inline">当前任务没有直接依赖。</div>`;
    return;
  }

  elements.directDependencies.innerHTML = directDependencies
    .map(
      (dependency) => `
        <div class="dependency-chip">
          <span>${escapeHtml(dependency.title)}</span>
          <button type="button" data-remove-dependency="${dependency.id}">移除</button>
        </div>
      `,
    )
    .join("");
}

function renderDependencyTree() {
  const dependencies = state.selectedTree.dependencies || [];
  if (!dependencies.length) {
    elements.dependencyTree.innerHTML = `<div class="empty-inline">当前任务没有依赖树节点。</div>`;
    return;
  }

  elements.dependencyTree.innerHTML = dependencies.map((node) => renderTreeNode(node)).join("");
}

function renderTreeNode(node) {
  const children = node.dependencies || [];
  const childMarkup = children.length
    ? `<div class="tree-node-children">${children.map((child) => renderTreeNode(child)).join("")}</div>`
    : "";

  return `
    <div class="tree-node">
      <div class="tree-node-head">
        <strong>${escapeHtml(node.title)}</strong>
        <span class="mini-badge ${node.status}">${statusToLabel(node.status)}</span>
        <span class="tag">${priorityToLabel(node.priority)}</span>
      </div>
      ${childMarkup}
    </div>
  `;
}

async function apiRequest(url, options = {}) {
  const { payload } = await fetchJson(url, options);
  return payload;
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (response.status === 204) {
    return { response, payload: {} };
  }

  const payload = await response.json();
  if (!response.ok) {
    throw payload;
  }
  return { response, payload };
}

async function fetchTaskCollection(path, baseParams = {}) {
  const items = [];
  let total = 0;
  let page = 1;
  let cacheStatus = "--";

  // Pull all pages while respecting the API limit so dashboard stats stay accurate.
  while (true) {
    const params = new URLSearchParams();

    Object.entries(baseParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        params.set(key, String(value));
      }
    });

    params.set("page", String(page));
    params.set("page_size", String(API_MAX_PAGE_SIZE));

    const { response, payload } = await fetchJson(`${path}?${params.toString()}`);
    const pageItems = payload.items || [];

    items.push(...pageItems);
    total = Number(payload.total || items.length);
    cacheStatus = response.headers.get("X-Cache") || cacheStatus;

    if (!pageItems.length || pageItems.length < API_MAX_PAGE_SIZE || items.length >= total) {
      break;
    }

    page += 1;
  }

  return {
    items,
    total,
    cacheStatus,
  };
}

function buildTagStats(tasks, extraTags = []) {
  const counts = new Map();

  tasks.forEach((task) => {
    (task.tags || []).forEach((tag) => {
      const normalizedTag = normalizeTag(tag);
      if (!normalizedTag) {
        return;
      }
      counts.set(normalizedTag, (counts.get(normalizedTag) || 0) + 1);
    });
  });

  [...COMMON_TAGS, ...extraTags].forEach((tag) => {
    const normalizedTag = normalizeTag(tag);
    if (!normalizedTag) {
      return;
    }
    if (!counts.has(normalizedTag)) {
      counts.set(normalizedTag, 0);
    }
  });

  return [...counts.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((left, right) => {
      if (right.count !== left.count) {
        return right.count - left.count;
      }
      return left.name.localeCompare(right.name, "zh-CN");
    });
}

function getFormTagStats() {
  const tags = state.availableTagStats.length
    ? [...state.availableTagStats]
    : buildTagStats(state.catalogTasks, state.customTags);

  state.formSelectedTags.forEach((tag) => {
    const normalizedTag = normalizeTag(tag);
    if (!normalizedTag) {
      return;
    }
    if (!tags.some((item) => item.name === normalizedTag)) {
      tags.push({ name: normalizedTag, count: 0 });
    }
  });

  return tags.sort((left, right) => {
    if (right.count !== left.count) {
      return right.count - left.count;
    }
    return left.name.localeCompare(right.name, "zh-CN");
  });
}

function getFilterTagStats() {
  const tags = state.availableTagStats.length
    ? [...state.availableTagStats]
    : buildTagStats(state.catalogTasks, state.customTags);

  const activeTag = normalizeTag(state.filters.tag);
  if (activeTag && !tags.some((item) => item.name === activeTag)) {
    tags.push({ name: activeTag, count: 0 });
  }

  return tags.filter((tag) => tag.count > 0 || tag.name === activeTag);
}

function getTagCount(tagName) {
  const normalizedTag = normalizeTag(tagName);
  const found = state.availableTagStats.find((item) => item.name === normalizedTag);
  return found ? found.count : 0;
}

function normalizeTag(value) {
  return String(value || "")
    .trim()
    .replace(/\s+/g, "-")
    .toLowerCase();
}

function statusToLabel(status) {
  return {
    pending: "待处理",
    in_progress: "进行中",
    completed: "已完成",
  }[status] || status;
}

function priorityToLabel(priority) {
  return {
    low: "低优先级",
    medium: "中优先级",
    high: "高优先级",
  }[priority] || priority;
}

function formatDateTime(value, options = {}) {
  if (!value) {
    return "-";
  }

  const formatter = new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    ...(options.compact ? {} : { second: "2-digit" }),
  });
  return formatter.format(new Date(value));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function getErrorMessage(error) {
  if (!error) {
    return "发生了未知错误。";
  }
  if (typeof error === "string") {
    return error;
  }
  if (error.message) {
    return error.message;
  }
  if (error.detail) {
    return typeof error.detail === "string" ? error.detail : "请求失败。";
  }
  return "请求失败。";
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;
  elements.toastZone.appendChild(toast);

  window.setTimeout(() => {
    toast.remove();
  }, 2800);
}

function debounce(callback, wait = 200) {
  let timeoutId = null;
  return (...args) => {
    window.clearTimeout(timeoutId);
    timeoutId = window.setTimeout(() => {
      callback(...args);
    }, wait);
  };
}
