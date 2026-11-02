/* Sprint 3 v2 — inscrições, autenticação e gestão visual integrada à API. */
const sprint3 = { user: null, authMode: 'login', minhas: [], filtro: {}, catalogo: [] };
const s3 = selector => document.querySelector(selector);
const safe = value => escapeHTML(value ?? '');
const ativo = i => i.status === 'confirmada' || i.status === 'lista_espera';
const rotulo = status => ({ confirmada: 'Confirmada', lista_espera: 'Fila de espera', cancelada: 'Cancelada' })[status] || status;
window.canOrganize = () => sprint3.user?.papel === 'organizador';
const isParticipant = () => sprint3.user?.papel === 'participante';
function updateIdentity() {
  const organizer = window.canOrganize();
  document.querySelectorAll('.organizer-only').forEach(el => { el.hidden = !organizer; });
  document.querySelectorAll('.participant-only').forEach(el => { el.hidden = !isParticipant(); });
  s3('#sessionName').textContent = sprint3.user?.nome || 'Visitante';
  s3('#authButton').textContent = sprint3.user ? 'Sair' : 'Entrar / Cadastrar';
  const current = document.querySelector('.view.active');
  if (!current || current.hidden) showView('catalogo');
}
async function restoreSession() {
  if (sessionStorage.getItem('g15_token')) {
    try { sprint3.user = await api('/auth/me'); }
    catch { sessionStorage.removeItem('g15_token'); sprint3.user = null; }
  }
  updateIdentity();
  await refreshRegistrations();
}
function setAuthMode(mode) {
  sprint3.authMode = mode;
  const register = mode === 'registro';
  s3('#authTitle').textContent = register ? 'Criar conta de participante' : 'Entrar';
  s3('#authNameField').hidden = !register;
  s3('#authForm [name=nome]').required = register;
  s3('#toggleAuthMode').textContent = register ? 'Já tenho conta' : 'Criar conta';
  s3('#submitAuth').textContent = register ? 'Cadastrar' : 'Entrar';
}
s3('#authButton').addEventListener('click', async () => {
  if (sprint3.user) {
    sessionStorage.removeItem('g15_token'); sprint3.user = null; sprint3.minhas = [];
    updateIdentity(); renderCatalog(); showView('catalogo'); toast('Sessão encerrada.');
  } else { setAuthMode('login'); s3('#authDialog').showModal(); }
});
s3('#toggleAuthMode').addEventListener('click', () => setAuthMode(sprint3.authMode === 'login' ? 'registro' : 'login'));
s3('#authForm').addEventListener('submit', async event => {
  event.preventDefault(); const form = event.currentTarget;
  const button = s3('#submitAuth'); button.disabled = true;
  try {
    const payload = { email: form.elements.email.value.trim(), senha: form.elements.senha.value };
    if (sprint3.authMode === 'registro') {
      await api('/auth/registro', { method: 'POST', body: JSON.stringify({ ...payload, nome: form.elements.nome.value.trim() }) });
    }
    const response = await api('/auth/login', { method: 'POST', body: JSON.stringify(payload) });
    sessionStorage.setItem('g15_token', response.access_token);
    sprint3.user = response.usuario; form.reset(); s3('#authDialog').close(); updateIdentity();
    await loadData(); await refreshRegistrations(); showView(isParticipant() ? 'catalogo' : 'dashboard');
    toast(`Bem-vindo(a), ${sprint3.user.nome}!`);
  } catch (error) { toast(error.message, true); }
  finally { button.disabled = false; }
});
function populateSelects() {
  for (const name of ['#catalogFilters [name=evento_id]', '#managementFilters [name=evento_id]']) {
    const el = s3(name); const previous = el.value;
    el.innerHTML = `<option value="">${name.startsWith('#catalog') ? 'Todos os eventos' : 'Selecione um evento'}</option>` +
      state.eventos.map(e => `<option value="${e.id}">${safe(e.nome)}</option>`).join('');
    el.value = previous;
  }
  const el = s3('#managementFilters [name=sessao_id]'); const prev = el.value;
  const selected = s3('#managementFilters [name=evento_id]').value;
  el.innerHTML = '<option value="">Todas as sessões</option>' + state.sessoes.filter(i => !selected || String(i.evento_id) === selected).map(i => `<option value="${i.id}">${safe(i.titulo)}</option>`).join('');
  el.value = prev;
}
async function loadCatalog() {
  const params = new URLSearchParams();
  for (const [key, val] of Object.entries(sprint3.filtro)) { if (val !== '' && val !== false && val != null) params.set(key, val); }
  try { sprint3.catalogo = await api(`/sessoes${params.size ? '?' + params : ''}`); renderCatalog(); }
  catch (error) { toast(error.message, true); }
}
function renderCatalog() {
  const items = sprint3.catalogo;
  s3('#catalogCount').textContent = `(${items.length})`;
  const mine = new Map(sprint3.minhas.filter(ativo).map(i => [i.sessao_id, i]));
  s3('#catalogList').innerHTML = items.length ? items.map(item => {
    const own = mine.get(item.id), available = item.vagas_disponiveis;
    const ended = new Date(item.data_hora_inicio) <= new Date();
    const button = !sprint3.user ? '<button class="primary-button" data-login-required>Entre para se inscrever</button>'
      : !isParticipant() ? '<span class="s3-muted">Inscrições disponíveis para participantes</span>'
      : own ? `<button class="secondary-button" data-cancel-session="${item.id}">Cancelar inscrição</button>`
      : ended ? '<button class="secondary-button" disabled>Sessão iniciada</button>'
      : `<button class="primary-button" data-enroll="${item.id}">${available > 0 ? 'Reservar vaga' : 'Entrar na fila de espera'}</button>`;
    return `<article class="session-card"><div class="s3-card-top"><span class="badge ${available > 0 ? 'success' : 'gold'}">${available} vaga(s) livre(s)</span><span>${item.lista_espera} na espera</span></div>
      <h3>${safe(item.titulo)}</h3><p>${safe(item.descricao || item.tipo || 'Atividade acadêmica')}</p>
      <p><strong>Evento:</strong> ${safe(item.evento_nome)} · <strong>Local:</strong> ${safe(item.espaco_nome)}</p>
      <p><strong>Horário:</strong> ${formatDateTime(item.data_hora_inicio)} · ${item.capacidade_total} lugares</p>
      ${own ? `<p class="s3-status">Sua inscrição: ${rotulo(own.status)}${own.posicao_fila ? ` (posição ${own.posicao_fila})` : ''}</p>` : ''}
      ${button}</article>`;
  }).join('') : '<p>Nenhuma sessão encontrada. Experimente outros filtros.</p>';
}
async function refreshRegistrations() {
  if (!sprint3.user) { sprint3.minhas = []; renderCatalog(); return; }
  try {
    sprint3.minhas = await api('/inscricoes/minhas?incluir_canceladas=true');
    renderMine(); renderCatalog();
  } catch (error) { toast(`Não foi possível carregar inscrições: ${error.message}`, true); }
}
function renderMine() {
  const canceled = s3('#includeCanceled').checked;
  const list = sprint3.minhas.filter(item => canceled || ativo(item));
  s3('#myRegistrations').innerHTML = list.length ? list.map(item => `<article class="session-card">
    <span class="badge ${item.status === 'confirmada' ? 'success' : item.status === 'cancelada' ? 'neutral' : 'gold'}">${rotulo(item.status)}</span>
    <h3>${safe(item.sessao.titulo)}</h3><p>${safe(item.sessao.evento_nome)} · ${safe(item.sessao.espaco_nome)}</p>
    <p>${formatDateTime(item.sessao.data_hora_inicio)}</p>
    ${item.posicao_fila ? `<p><strong>Posição na fila: ${item.posicao_fila}</strong></p>` : ''}
    ${ativo(item) ? `<button class="secondary-button" data-cancel-id="${item.id}">Cancelar inscrição</button>` : ''}
    </article>`).join('') : '<p>Nenhuma inscrição para exibir. Explore o catálogo e reserve uma vaga.</p>';
}
async function registrationAction(path, method) {
  if (!confirm(method === 'DELETE' ? 'Deseja cancelar esta inscrição?' : 'Confirma sua inscrição na sessão?')) return;
  try {
    const result = await api(path, { method });
    const message = method === 'POST' ? result.status === 'confirmada' ? 'Inscrição confirmada!' : `Você entrou na fila de espera (posição ${result.posicao_fila}).`
      : result.promovidas_total ? `Inscrição cancelada. ${result.promovidas_total} pessoa(s) promovida(s) da fila.` : 'Inscrição cancelada.';
    await loadCatalog(); await refreshRegistrations();
    if (window.canOrganize()) await loadManagement();
    toast(message);
  } catch (error) { toast(error.message, true); }
}
s3('#catalogFilters').addEventListener('submit', event => {
  event.preventDefault(); const form = new FormData(event.currentTarget);
  sprint3.filtro = Object.fromEntries(form.entries()); sprint3.filtro.apenas_com_vagas = event.currentTarget.elements.apenas_com_vagas.checked;
  loadCatalog();
});
s3('#clearFilters').addEventListener('click', () => { s3('#catalogFilters').reset(); sprint3.filtro = {}; loadCatalog(); });
s3('#includeCanceled').addEventListener('change', renderMine);
s3('#managementFilters [name=evento_id]').addEventListener('change', populateSelects);
s3('#managementFilters').addEventListener('submit', event => { event.preventDefault(); loadManagement(); });
async function loadManagement() {
  if (!window.canOrganize()) return;
  const f = s3('#managementFilters').elements;
  if (!f.evento_id.value) { s3('#managementResults').textContent = 'Selecione um evento.'; return; }
  const params = new URLSearchParams();
  if (f.status.value) params.set('status', f.status.value);
  if (f.sessao_id.value) params.set('sessao_id', f.sessao_id.value);
  if (f.incluir_canceladas.checked || f.status.value === 'cancelada') params.set('incluir_canceladas', 'true');
  try {
    const data = await api(`/eventos/${f.evento_id.value}/inscricoes?${params}`);
    s3('#managementResults').innerHTML = data.length ? `<table><thead><tr><th>Participante</th><th>Sessão</th><th>Status</th><th>Fila</th><th>Ações</th></tr></thead><tbody>${data.map(item => `<tr><td>${safe(item.usuario.nome)}<small>${safe(item.usuario.email)}</small></td><td>${safe(item.sessao.titulo)}</td><td>${rotulo(item.status)}</td><td>${item.posicao_fila || '—'}</td><td>${ativo(item) ? `<button class="secondary-button" data-cancel-id="${item.id}">Cancelar</button>` : '—'}</td></tr>`).join('')}</tbody></table>` : '<p>Nenhuma inscrição encontrada.</p>';
  } catch (error) { toast(error.message, true); }
}
document.addEventListener('click', event => {
  const login = event.target.closest('[data-login-required]');
  if (login) { setAuthMode('login'); s3('#authDialog').showModal(); }
  const enroll = event.target.closest('[data-enroll]');
  if (enroll) registrationAction(`/sessoes/${enroll.dataset.enroll}/inscricao`, 'POST');
  const cancel = event.target.closest('[data-cancel-session]');
  if (cancel) registrationAction(`/sessoes/${cancel.dataset.cancelSession}/inscricao`, 'DELETE');
  const cancelId = event.target.closest('[data-cancel-id]');
  if (cancelId) registrationAction(`/inscricoes/${cancelId.dataset.cancelId}`, 'DELETE');
});
const originalRenderAll = renderAll;
renderAll = function () { originalRenderAll(); populateSelects(); if (!Object.keys(sprint3.filtro).length) sprint3.catalogo = state.sessoes; renderCatalog(); };
restoreSession().then(() => { showView(window.canOrganize() ? 'dashboard' : 'catalogo'); });
