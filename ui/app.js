const state = {
  folder: "",
  parser: "pyverilog",
  tops: [],
  modules: [],
  selectedModule: null,
  graph: null,
};

const folderInput = document.getElementById("folderInput");
const parserSelect = document.getElementById("parserSelect");
const loadBtn = document.getElementById("loadBtn");
const refreshBtn = document.getElementById("refreshBtn");
const statusBadge = document.getElementById("statusBadge");
const topList = document.getElementById("topList");
const moduleList = document.getElementById("moduleList");
const graphTag = document.getElementById("graphTag");
const graphStats = document.getElementById("graphStats");
const graphPreview = document.getElementById("graphPreview");
const inspector = document.getElementById("inspector");

function setStatus(text, kind) {
  statusBadge.textContent = text;
  statusBadge.className = `status ${kind}`;
}

async function apiRequest(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.detail || `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return payload;
}

function countByKind(items) {
  const counts = {};
  for (const item of items) {
    const key = item.kind || "unknown";
    counts[key] = (counts[key] || 0) + 1;
  }
  return counts;
}

function renderList(container, values, onClick) {
  container.innerHTML = "";

  if (!values.length) {
    const li = document.createElement("li");
    li.textContent = "(none)";
    li.style.color = "#8ea2b1";
    container.appendChild(li);
    return;
  }

  for (const value of values) {
    const li = document.createElement("li");
    const button = document.createElement("button");
    button.textContent = value;
    button.className = value === state.selectedModule ? "active" : "";
    button.addEventListener("click", () => onClick(value));
    li.appendChild(button);
    container.appendChild(li);
  }
}

function renderInspector(summary) {
  inspector.innerHTML = `
    <div><span class="k">Loaded folder:</span><br>${summary.loaded_folder || "-"}</div>
    <div style="margin-top:10px;"><span class="k">Parser:</span> ${summary.parser_backend || "-"}</div>
    <div><span class="k">Files:</span> ${summary.file_count ?? 0}</div>
    <div><span class="k">Modules:</span> ${summary.module_count ?? 0}</div>
    <div><span class="k">Top candidates:</span> ${summary.top_candidates?.join(", ") || "(none)"}</div>
    <div style="margin-top:10px;"><span class="k">Selected module:</span> ${state.selectedModule || "(none)"}</div>
    <div style="margin-top:12px;"><span class="k">Reminder:</span> total node count includes modules, instances, ports, and nets.</div>
  `;
}

function renderGraphStats(nodeCounts, edgeCounts) {
  const nodeKinds = [
    { key: "module", label: "module nodes" },
    { key: "instance", label: "instance nodes" },
    { key: "port", label: "port nodes" },
    { key: "net", label: "net nodes" },
  ];

  const edgeKinds = [
    { key: "hierarchy", label: "hierarchy edges" },
    { key: "signal", label: "signal edges" },
  ];

  const totalNodes = Object.values(nodeCounts).reduce((acc, value) => acc + value, 0);
  const totalEdges = Object.values(edgeCounts).reduce((acc, value) => acc + value, 0);

  const pills = [
    `<span class="stat-pill"><strong>Total nodes</strong>${totalNodes}</span>`,
    `<span class="stat-pill"><strong>Total edges</strong>${totalEdges}</span>`,
  ];

  for (const kind of nodeKinds) {
    pills.push(
      `<span class="stat-pill ${kind.key}"><strong>${kind.label}</strong>${nodeCounts[kind.key] || 0}</span>`
    );
  }

  for (const kind of edgeKinds) {
    pills.push(
      `<span class="stat-pill ${kind.key}"><strong>${kind.label}</strong>${edgeCounts[kind.key] || 0}</span>`
    );
  }

  graphStats.classList.remove("empty");
  graphStats.innerHTML = pills.join("");
}

function clearGraphStats() {
  graphStats.classList.add("empty");
  graphStats.innerHTML = "<p>Load a module graph to see a node/edge breakdown.</p>";
}

function renderGraph(graph) {
  if (!graph) {
    graphTag.textContent = "No graph loaded";
    graphPreview.textContent = "";
    clearGraphStats();
    return;
  }

  const nodeCounts = countByKind(graph.nodes || []);
  const edgeCounts = countByKind(graph.edges || []);

  graphTag.textContent = `Top: ${graph.top_module} | Nodes: ${graph.nodes.length} | Edges: ${graph.edges.length}`;
  renderGraphStats(nodeCounts, edgeCounts);

  const preview = {
    schema_version: graph.schema_version,
    top_module: graph.top_module,
    interpretation: {
      note: "Node total includes module + instance + port + net nodes, not only instances.",
      instance_nodes: nodeCounts.instance || 0,
      total_nodes: graph.nodes.length,
    },
    node_kind_counts: nodeCounts,
    edge_kind_counts: edgeCounts,
    sample_nodes: (graph.nodes || []).slice(0, 6),
    sample_edges: (graph.edges || []).slice(0, 6),
  };

  graphPreview.textContent = JSON.stringify(preview, null, 2);
}

async function loadGraph(moduleName) {
  state.selectedModule = moduleName;
  renderList(topList, state.tops, loadGraph);
  renderList(moduleList, state.modules, loadGraph);

  const graph = await apiRequest(`/api/project/graph/${encodeURIComponent(moduleName)}`);
  state.graph = graph;
  renderGraph(graph);
}

async function refreshProject() {
  const topsPayload = await apiRequest("/api/project/tops");
  const modulesPayload = await apiRequest("/api/project/modules");

  state.tops = topsPayload.top_candidates || [];
  state.modules = modulesPayload.modules || [];

  renderList(topList, state.tops, loadGraph);
  renderList(moduleList, state.modules, loadGraph);

  if (state.selectedModule && state.modules.includes(state.selectedModule)) {
    await loadGraph(state.selectedModule);
    return;
  }

  if (state.tops.length === 1) {
    await loadGraph(state.tops[0]);
    return;
  }

  renderGraph(null);
}

async function handleLoad() {
  const folder = folderInput.value.trim();
  if (!folder) {
    setStatus("Need folder path", "error");
    return;
  }

  state.folder = folder;
  state.parser = parserSelect.value;

  try {
    setStatus("Loading...", "busy");
    const summary = await apiRequest("/api/project/load", {
      method: "POST",
      body: JSON.stringify({ folder: state.folder, parser_backend: state.parser }),
    });

    renderInspector(summary);
    await refreshProject();
    setStatus("Project loaded", "ok");
  } catch (error) {
    setStatus("Load failed", "error");
    inspector.innerHTML = `<p>${error.message}</p>`;
    renderGraph(null);
  }
}

loadBtn.addEventListener("click", handleLoad);
refreshBtn.addEventListener("click", async () => {
  try {
    setStatus("Refreshing...", "busy");
    await refreshProject();
    setStatus("Refreshed", "ok");
  } catch (error) {
    setStatus("Refresh failed", "error");
    inspector.innerHTML = `<p>${error.message}</p>`;
  }
});

folderInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    handleLoad();
  }
});

clearGraphStats();

(async function init() {
  try {
    const health = await apiRequest("/api/health");
    if (health.status === "ok") {
      setStatus("API ready", "ok");
    }
  } catch {
    setStatus("API unavailable", "error");
  }
})();
