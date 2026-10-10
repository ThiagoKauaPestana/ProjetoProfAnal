const state = { espacos: [], eventos: [], sessoes: [] };

const $ = (selector, scope = document) => scope.querySelector(selector);
const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];

const icons = {
  edit: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m5 16 10.3-10.3 3 3L8 19H5v-3Zm12.4-12.4a1.4 1.4 0 0 1 2 0l1 1a1.4 1.4 0 0 1 0 2l-1 1-3-3 1-1Z"/></svg>',
  trash: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 21a2 2 0 0 1-2-2V6H4V4h5V3h6v1h5v2h-1v13a2 2 0 0 1-2 2H7Zm0-15v13h10V6H7Zm2 2h2v9H9V8Zm4 0h2v9h-2V8Z"/></svg>'
};

function escapeHTML(value = "") {
  return String(value).replace(/[&<>'"]/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
}

function normalizeError(detail) {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map(item => item.msg).join("; ");
  if (detail?.mensagem) return detail.mensagem;
  return "Não foi possível concluir a operação.";
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options.headers || {}) }
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(normalizeError(body.detail));
  }
  return response.status === 204 ? null : response.json();
}

function toast(message, error = false) {
  const element = $("#toast");
  element.textContent = message;
  element.className = `toast show${error ? " error" : ""}`;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => element.className = "toast", 3600);
}

function formatDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", year: "numeric", timeZone: "UTC" }).format(new Date(`${value}T00:00:00Z`));
}

function formatDateTime(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function toInputDateTime(value) {
  if (!value) return "";
  const date = new Date(value);
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

function statusLabel(value) {
  return ({ planejado: "Planejado", em_andamento: "Em andamento", encerrado: "Encerrado", cancelado: "Cancelado" })[value] || value;
}

function statusClass(value) {
  return ({ planejado: "gold", em_andamento: "success", encerrado: "neutral", cancelado: "red" })[value] || "neutral";
}

function entityName(collection, id) {
  return state[collection].find(item => item.id === id)?.nome || `#${id}`;
}

function showView(name) {
  $$(".view").forEach(view => view.classList.toggle("active", view.id === `${name}View`));
  $$(".nav-item").forEach(item => item.classList.toggle("active", item.dataset.view === name));
  $(".sidebar").classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadData() {
  try {
    const [espacos, eventos, sessoes] = await Promise.all([
      api("/espacos"), api("/eventos"), api("/sessoes")
    ]);
    state.espacos = espacos;
    state.eventos = eventos;
    state.sessoes = sessoes;
    renderAll();
  } catch (error) {
    toast(`Erro ao carregar dados: ${error.message}`, true);
  }
}

function renderAll() {
  renderDashboard();
  renderEspacos();
  renderEventos();
  renderSessoes();
  fillRelations();
}

function renderDashboard() {
  $("#countEspacos").textContent = state.espacos.length;
  $("#countAtivos").textContent = `${state.espacos.filter(item => item.ativo).length} ativos`;
  $("#countEventos").textContent = state.eventos.length;
  $("#countSessoes").textContent = state.sessoes.length;
  const now = new Date();
  const upcoming = state.sessoes.filter(item => new Date(item.data_hora_fim) >= now).sort((a, b) => new Date(a.data_hora_inicio) - new Date(b.data_hora_inicio));
  $("#countProximas").textContent = `${upcoming.length} próximas`;
  $("#upcomingList").innerHTML = upcoming.length ? upcoming.slice(0, 5).map(item => {
    const date = new Date(item.data_hora_inicio);
    return `<div class="upcoming-item">
      <span class="date-badge"><strong>${String(date.getDate()).padStart(2, "0")}</strong><small>${date.toLocaleDateString("pt-BR", { month: "short" }).replace(".", "")}</small></span>
      <div class="upcoming-copy"><strong>${escapeHTML(item.titulo)}</strong><span>${escapeHTML(entityName("espacos", item.espaco_id))} · ${escapeHTML(entityName("eventos", item.evento_id))}</span></div>
      <span class="time-pill">${date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}</span>
    </div>`;
  }).join("") : '<div class="empty-state"><strong>Nenhuma sessão futura</strong>Agende uma sessão para vê-la aqui.</div>';
}

function renderEspacos() {
  const term = $("#searchEspacos").value.trim().toLowerCase();
  const rows = state.espacos.filter(item => `${item.nome} ${item.tipo} ${item.localizacao || ""}`.toLowerCase().includes(term));
  $("#espacosTable").innerHTML = rows.length ? rows.map(item => `<tr>
    <td><div class="main-cell"><strong>${escapeHTML(item.nome)}</strong><small>${escapeHTML(item.recursos || "Sem recursos informados")}</small></div></td>
    <td><span class="badge neutral">${escapeHTML(item.tipo)}</span></td>
    <td>${item.capacidade} pessoas</td>
    <td>${escapeHTML(item.localizacao || "—")}</td>
    <td><span class="badge ${item.ativo ? "success" : "neutral"}">${item.ativo ? "Ativo" : "Inativo"}</span></td>
    <td><div class="row-actions"><button class="row-action" data-edit="espaco" data-id="${item.id}" aria-label="Editar espaço">${icons.edit}</button><button class="row-action delete" data-delete="espaco" data-id="${item.id}" aria-label="Excluir espaço">${icons.trash}</button></div></td>
  </tr>`).join("") : emptyRow(6, "Nenhum espaço encontrado");
}

function renderEventos() {
  const term = $("#searchEventos").value.trim().toLowerCase();
  const rows = state.eventos.filter(item => `${item.nome} ${item.descricao || ""} ${item.status}`.toLowerCase().includes(term));
  $("#eventosTable").innerHTML = rows.length ? rows.map(item => `<tr>
    <td><div class="main-cell"><strong>${escapeHTML(item.nome)}</strong><small>${escapeHTML(item.descricao || "Sem descrição")}</small></div></td>
    <td>${formatDate(item.data_inicio)} — ${formatDate(item.data_fim)}</td>
    <td><span class="badge ${statusClass(item.status)}">${escapeHTML(statusLabel(item.status))}</span></td>
    <td><div class="row-actions"><button class="row-action" data-edit="evento" data-id="${item.id}" aria-label="Editar evento">${icons.edit}</button><button class="row-action delete" data-delete="evento" data-id="${item.id}" aria-label="Excluir evento">${icons.trash}</button></div></td>
  </tr>`).join("") : emptyRow(4, "Nenhum evento encontrado");
}

function renderSessoes() {
  const term = $("#searchSessoes").value.trim().toLowerCase();
  const rows = state.sessoes.filter(item => `${item.titulo} ${entityName("eventos", item.evento_id)} ${entityName("espacos", item.espaco_id)}`.toLowerCase().includes(term));
  $("#sessoesTable").innerHTML = rows.length ? rows.sort((a, b) => new Date(a.data_hora_inicio) - new Date(b.data_hora_inicio)).map(item => `<tr>
    <td><div class="main-cell"><strong>${escapeHTML(item.titulo)}</strong><small>${escapeHTML(item.tipo || item.responsavel || "Sessão")}</small></div></td>
    <td>${escapeHTML(entityName("eventos", item.evento_id))}</td>
    <td>${escapeHTML(entityName("espacos", item.espaco_id))}</td>
    <td><div class="main-cell"><strong>${formatDateTime(item.data_hora_inicio)}</strong><small>até ${formatDateTime(item.data_hora_fim)}</small></div></td>
    <td><div class="row-actions"><button class="row-action" data-edit="sessao" data-id="${item.id}" aria-label="Editar sessão">${icons.edit}</button><button class="row-action delete" data-delete="sessao" data-id="${item.id}" aria-label="Excluir sessão">${icons.trash}</button></div></td>
  </tr>`).join("") : emptyRow(5, "Nenhuma sessão encontrada");
}

function emptyRow(columns, message) {
  return `<tr><td colspan="${columns}"><div class="empty-state"><strong>${message}</strong>Use o botão de cadastro para começar.</div></td></tr>`;
}

function fillRelations() {
  const eventSelect = $("#sessaoForm [name='evento_id']");
  const spaceSelect = $("#sessaoForm [name='espaco_id']");
  const eventValue = eventSelect.value;
  const spaceValue = spaceSelect.value;
  eventSelect.innerHTML = '<option value="">Selecione o evento</option>' + state.eventos.map(item => `<option value="${item.id}">${escapeHTML(item.nome)}</option>`).join("");
  spaceSelect.innerHTML = '<option value="">Selecione o espaço</option>' + state.espacos.filter(item => item.ativo).map(item => `<option value="${item.id}">${escapeHTML(item.nome)} (${item.capacidade})</option>`).join("");
  eventSelect.value = eventValue;
  spaceSelect.value = spaceValue;
}

function openEntity(type, id = null) {
  const dialog = $(`#${type}Dialog`);
  const form = $(`#${type}Form`);
  form.reset();
  form.elements.id.value = id || "";
  if (type === "espaco") {
    $("#espacoDialogTitle").textContent = id ? "Editar espaço" : "Novo espaço";
    form.elements.ativo.checked = true;
    if (id) setForm(form, state.espacos.find(item => item.id === id));
  }
  if (type === "evento") {
    $("#eventoDialogTitle").textContent = id ? "Editar evento" : "Novo evento";
    if (id) setForm(form, state.eventos.find(item => item.id === id));
  }
  if (type === "sessao") {
    $("#sessaoDialogTitle").textContent = id ? "Editar sessão" : "Nova sessão";
    fillRelations();
    form.elements.evento_id.disabled = Boolean(id);
    if (id) {
      const item = state.sessoes.find(entry => entry.id === id);
      setForm(form, { ...item, data_hora_inicio: toInputDateTime(item.data_hora_inicio), data_hora_fim: toInputDateTime(item.data_hora_fim) });
    }
  }
  dialog.showModal();
}

function setForm(form, data) {
  Object.entries(data || {}).forEach(([key, value]) => {
    if (!form.elements[key]) return;
    if (form.elements[key].type === "checkbox") form.elements[key].checked = Boolean(value);
    else form.elements[key].value = value ?? "";
  });
}

function formObject(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  return data;
}

async function submitEspaco(form) {
  const data = formObject(form);
  const id = data.id;
  delete data.id;
  data.capacidade = Number(data.capacidade);
  data.ativo = form.elements.ativo.checked;
  await api(id ? `/espacos/${id}` : "/espacos", { method: id ? "PUT" : "POST", body: JSON.stringify(data) });
  return id ? "Espaço atualizado." : "Espaço cadastrado.";
}

async function submitEvento(form) {
  const data = formObject(form);
  const id = data.id;
  delete data.id;
  await api(id ? `/eventos/${id}` : "/eventos", { method: id ? "PUT" : "POST", body: JSON.stringify(data) });
  return id ? "Evento atualizado." : "Evento cadastrado.";
}

async function submitSessao(form) {
  const data = formObject(form);
  const id = data.id;
  delete data.id;
  if (!id) data.evento_id = Number(data.evento_id);
  data.espaco_id = Number(data.espaco_id);
  data.capacidade_prevista = data.capacidade_prevista ? Number(data.capacidade_prevista) : null;
  await api(id ? `/sessoes/${id}` : "/sessoes", { method: id ? "PUT" : "POST", body: JSON.stringify(data) });
  return id ? "Sessão atualizada." : "Sessão agendada.";
}

async function handleForm(event, type, submitter) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  button.textContent = "Salvando...";
  try {
    const message = await submitter(form);
    form.closest("dialog").close();
    await loadData();
    toast(message);
  } catch (error) {
    toast(error.message, true);
  } finally {
    button.disabled = false;
    button.textContent = type === "sessao" ? "Salvar sessão" : type === "evento" ? "Salvar evento" : "Salvar espaço";
  }
}

async function deleteEntity(type, id) {
  const labels = { espaco: "espaço", evento: "evento", sessao: "sessão" };
  const routes = { espaco: "espacos", evento: "eventos", sessao: "sessoes" };
  if (!window.confirm(`Deseja realmente excluir este ${labels[type]}?`)) return;
  try {
    await api(`/${routes[type]}/${id}`, { method: "DELETE" });
    await loadData();
    toast(`${labels[type][0].toUpperCase() + labels[type].slice(1)} excluído.`);
  } catch (error) {
    toast(error.message, true);
  }
}

function setToday() {
  const now = new Date();
  $("#todayWeekday").textContent = now.toLocaleDateString("pt-BR", { weekday: "long" });
  $("#todayDate").textContent = now.toLocaleDateString("pt-BR", { day: "2-digit", month: "long" });
}

document.addEventListener("click", event => {
  const nav = event.target.closest("[data-view]");
  if (nav) showView(nav.dataset.view);
  const jump = event.target.closest("[data-view-jump]");
  if (jump) showView(jump.dataset.viewJump);
  const opener = event.target.closest("[data-open]");
  if (opener) openEntity(opener.dataset.open);
  const editor = event.target.closest("[data-edit]");
  if (editor) openEntity(editor.dataset.edit, Number(editor.dataset.id));
  const deleter = event.target.closest("[data-delete]");
  if (deleter) deleteEntity(deleter.dataset.delete, Number(deleter.dataset.id));
  if (event.target.closest(".close-dialog")) event.target.closest("dialog").close();
});

$("#mobileMenu").addEventListener("click", () => $(".sidebar").classList.toggle("open"));
$("#searchEspacos").addEventListener("input", renderEspacos);
$("#searchEventos").addEventListener("input", renderEventos);
$("#searchSessoes").addEventListener("input", renderSessoes);
$("#espacoForm").addEventListener("submit", event => handleForm(event, "espaco", submitEspaco));
$("#eventoForm").addEventListener("submit", event => handleForm(event, "evento", submitEvento));
$("#sessaoForm").addEventListener("submit", event => handleForm(event, "sessao", submitSessao));

setToday();
loadData();
