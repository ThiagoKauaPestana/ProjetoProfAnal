
const API_BASE = window.AUDITORIO_API_BASE || '';

const config = {
  espacos: {
    title: 'Espaços',
    desc: 'Cadastre e organize salas e auditórios.',
    fields: [
      ['nome', 'Nome do espaço', 'text', true],
      ['capacidade', 'Capacidade', 'number', true],
      ['localizacao', 'Localização', 'text', false],
      ['descricao', 'Descrição', 'textarea', false]
    ]
  },

  eventos: {
    title: 'Eventos',
    desc: 'Organize a programação dos seus eventos.',
    fields: [
      ['nome', 'Nome do evento', 'text', true],
      ['descricao', 'Descrição', 'textarea', false],
      ['data_inicio', 'Data de início', 'datetime-local', false],
      ['data_fim', 'Data de término', 'datetime-local', false]
    ]
  },

  sessoes: {
    title: 'Sessões',
    desc: 'Agende atividades e evite conflitos de horários.',
    fields: [
      ['nome', 'Nome da sessão', 'text', true],
      ['evento_id', 'Evento', 'select-eventos', true],
      ['espaco_id', 'Espaço', 'select-espacos', true],
      ['inicio', 'Início', 'datetime-local', true],
      ['fim', 'Término', 'datetime-local', true]
    ]
  }
};

let page = 'dashboard';
let records = { espacos: [], eventos: [], sessoes: [] };
let editing = null;

const $ = id => document.getElementById(id);

function toast(message) {
  $('toast').textContent = message;
  $('toast').style.display = 'block';

  clearTimeout(window.toastTimer);
  window.toastTimer = setTimeout(() => {
    $('toast').style.display = 'none';
  }, 4500);
}

async function request(path, options = {}) {
  const response = await fetch(API_BASE + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });

  let data;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    let message = typeof data?.detail === 'string'
      ? data.detail
      : JSON.stringify(data?.detail || data || response.statusText);

    if (response.status === 409) {
      message = 'Conflito de horário: este espaço já possui uma sessão nesse período.';
    }

    throw Error(message);
  }

  return data;
}

function listFrom(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

async function loadAll() {
  const checks = await Promise.allSettled(
    Object.keys(config).map(async key => {
      records[key] = listFrom(await request('/' + key));
      $('count-' + key).textContent = records[key].length;
    })
  );

  const ok = checks.some(x => x.status === 'fulfilled');

  $('api-status').textContent = ok
    ? 'API conectada'
    : 'API indisponível';

  document.querySelector('.status-dot')
    .classList.toggle('online', ok);

  if (page !== 'dashboard') renderTable();

  if (!ok) {
    toast('Não foi possível conectar à API.');
  }
}

function navigate(to) {
  page = to;

  document.querySelectorAll('.nav').forEach(button => {
    button.classList.toggle(
      'active',
      button.dataset.page === to
    );
  });

  $('dashboard').classList.toggle('hidden', to !== 'dashboard');
  $('listing').classList.toggle('hidden', to === 'dashboard');

  $('page-title').textContent =
    to === 'dashboard' ? 'Visão geral' : config[to].title;

  $('page-subtitle').textContent =
    to === 'dashboard'
      ? 'Gerencie seus espaços e eventos em um só lugar.'
      : config[to].desc;

  if (to !== 'dashboard') {
    $('list-title').textContent =
      'Gerenciar ' + config[to].title.toLowerCase();

    $('list-desc').textContent = config[to].desc;
    $('search').value = '';
    renderTable();
  }
}

function idOf(obj) {
  return obj.id ?? obj[page.slice(0, -1) + '_id'];
}

function renderTable() {
  const arr = records[page] || [];
  const q = $('search').value.toLowerCase();

  const filtered = arr.filter(item =>
    JSON.stringify(item).toLowerCase().includes(q)
  );

  let keys = [...new Set(
    arr.flatMap(item => Object.keys(item))
  )].slice(0, 6);

  if (!keys.length) {
    keys = config[page].fields.map(f => f[0]).slice(0, 5);
  }

  $('thead').replaceChildren();
  $('tbody').replaceChildren();

  const header = document.createElement('tr');

  [...keys, 'Ações'].forEach(key => {
    const th = document.createElement('th');
    th.textContent = key.replaceAll('_', ' ');
    header.append(th);
  });

  $('thead').append(header);

  filtered.forEach(obj => {
    const tr = document.createElement('tr');

    keys.forEach(key => {
      const td = document.createElement('td');
      td.textContent = obj[key] == null
        ? '—'
        : String(obj[key]);
      tr.append(td);
    });

    const actions = document.createElement('td');

    const edit = document.createElement('button');
    edit.className = 'action';
    edit.textContent = 'Editar';
    edit.onclick = () => openForm(obj);

    const del = document.createElement('button');
    del.className = 'action delete';
    del.textContent = 'Excluir';
    del.onclick = () => remove(obj);

    actions.append(edit, del);
    tr.append(actions);
    $('tbody').append(tr);
  });

  $('list-empty').classList.toggle(
    'hidden',
    filtered.length !== 0
  );
}

async function openForm(obj = null) {
  editing = obj;
  const current = page;

  $('modal-title').textContent =
    (obj ? 'Editar ' : 'Novo cadastro: ') +
    config[current].title.toLowerCase();

  $('form-fields').replaceChildren();

  for (const [key, label, type, required] of config[current].fields) {
    const div = document.createElement('div');
    div.className = 'field';

    const lab = document.createElement('label');
    lab.textContent = label;
    lab.htmlFor = 'f-' + key;

    let input;

    if (type.startsWith('select-')) {
      input = document.createElement('select');
      const relation = type.slice(7);

      const blank = document.createElement('option');
      blank.value = '';
      blank.textContent = 'Selecione...';
      input.append(blank);

      if (!records[relation].length) {
        try {
          records[relation] = listFrom(
            await request('/' + relation)
          );
        } catch (error) {
          console.error(error);
        }
      }

      records[relation].forEach(record => {
        const option = document.createElement('option');
        option.value = record.id ?? '';
        option.textContent =
          record.nome ?? record.titulo ?? `#${record.id}`;
        input.append(option);
      });

    } else if (type === 'textarea') {
      input = document.createElement('textarea');

    } else {
      input = document.createElement('input');
      input.type = type;
    }

    input.id = 'f-' + key;
    input.name = key;
    input.required = required;

    if (obj?.[key] != null) {
      let value = String(obj[key]);

      if (type === 'datetime-local') {
        value = value.slice(0, 16);
      }

      input.value = value;
    }

    div.append(lab, input);
    $('form-fields').append(div);
  }

  $('modal').showModal();
}

async function remove(obj) {
  const id = idOf(obj);

  if (id == null) {
    toast('Registro sem identificador.');
    return;
  }

  if (!confirm('Deseja realmente excluir este registro?')) {
    return;
  }

  try {
    await request('/' + page + '/' + id, {
      method: 'DELETE'
    });

    toast('Registro excluído.');
    await loadAll();

  } catch (error) {
    toast(error.message);
  }
}

$('entry-form').onsubmit = async event => {
  event.preventDefault();

  const body = {};

  for (const [key, , type] of config[page].fields) {
    const value = $('f-' + key).value;

    if (!value) continue;

    if (type === 'number' || type.startsWith('select-')) {
      body[key] = Number(value);
    } else if (type === 'datetime-local') {
      body[key] = new Date(value).toISOString();
    } else {
      body[key] = value;
    }
  }

  const id = editing && idOf(editing);

  try {
    await request('/' + page + (editing ? '/' + id : ''), {
      method: editing ? 'PUT' : 'POST',
      body: JSON.stringify(body)
    });

    $('modal').close();
    toast('Cadastro salvo com sucesso.');
    await loadAll();

  } catch (error) {
    toast(error.message);
  }
};

document.querySelectorAll('[data-page]').forEach(button => {
  button.onclick = () => navigate(button.dataset.page);
});

document.querySelectorAll('[data-go]').forEach(button => {
  button.onclick = () => navigate(button.dataset.go);
});

$('new-session').onclick = () => {
  navigate('sessoes');
  openForm();
};

$('add').onclick = () => openForm();
$('refresh').onclick = loadAll;
$('search').oninput = renderTable;

$('close').onclick = () => $('modal').close();
$('cancel').onclick = () => $('modal').close();

$('today').textContent = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: 'long',
  year: 'numeric'
}).format(new Date());

loadAll();

