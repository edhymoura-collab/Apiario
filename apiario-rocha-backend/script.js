const API_BASE = `${window.location.origin}/api/v1`;
const responseMessage = document.getElementById('responseMessage');
let adminTokenPromise = null;
let resolveAdminToken = null;
const defaultBrandConfig = {
  companyName: 'Empresa Exemplo',
  companyAcronym: 'EE',
  primaryColor: '#2e8d68',
  secondaryColor: '#5ca6dc',
};

const demoSummary = {
  total_vendas: 142,
  total_funcionarios: 18,
  fundo_acumulado: 48700,
  faturamento_mes: 12840,
  total_clientes: 56,
  total_fornecedores: 21,
  estoque_total: 368,
};

function getDemoSummary() {
  const raw = localStorage.getItem('demoSummary');
  if (!raw) {
    return { ...demoSummary };
  }

  try {
    return { ...demoSummary, ...JSON.parse(raw) };
  } catch (error) {
    return { ...demoSummary };
  }
}

function persistDemoSummary(summary) {
  localStorage.setItem('demoSummary', JSON.stringify(summary));
}

function syncDemoSummary(store = getDemoStore()) {
  const vendas = store.vendas || demoCollections.venda;
  const funcionarios = store.funcionarios || demoCollections.funcionario;
  const clientes = store.clientes || demoCollections.cliente;
  const fornecedores = store.fornecedores || demoCollections.fornecedor;
  const estoque = store.estoque || demoCollections.estoque;

  const nextSummary = {
    ...demoSummary,
    total_vendas: vendas.length,
    total_funcionarios: funcionarios.length,
    total_clientes: clientes.length,
    total_fornecedores: fornecedores.length,
    estoque_total: estoque.reduce((total, item) => total + Number(item.quantidade || 0), 0),
    faturamento_mes: vendas.reduce((total, item) => total + Number(item.valor_bruto || 0), 0),
    fundo_acumulado: vendas.reduce((total, item) => total + Number(item.valor_fundo || (item.valor_bruto || 0) * 0.3), 0),
  };

  persistDemoSummary(nextSummary);
  return nextSummary;
}

const demoCollections = {
  usuario: [
    { _id: 'demo-user-1', nome: 'Ana Souza', email: 'ana@empresa.com', username: 'ana', perfil: 'admin' },
    { _id: 'demo-user-2', nome: 'Bruno Lima', email: 'bruno@empresa.com', username: 'bruno', perfil: 'usuario' },
  ],
  administrador: [
    { _id: 'demo-admin-1', nome: 'Diretoria', email: 'diretoria@empresa.com', username: 'admin', nivel: 'admin' },
  ],
  funcionario: [
    { _id: 'demo-func-1', nome: 'Carla Mendes', email: 'carla@empresa.com', cargo: 'Gerente', departamento: 'Operação', salario: 6200 },
    { _id: 'demo-func-2', nome: 'Diego Nunes', email: 'diego@empresa.com', cargo: 'Técnico', departamento: 'Telemetria', salario: 4200 },
  ],
  cliente: [
    { _id: 'demo-client-1', nome: 'Mercado Campo', email: 'contato@mercadocampo.com', telefone: '(11) 99800-1111', tipo: 'pj', cidade: 'Campinas' },
  ],
  fornecedor: [
    { _id: 'demo-provider-1', nome: 'Fornecedores de Mel', cnpj: '11.222.333/0001-88', email: 'vendas@melfornecedores.com', categoria: 'Insumos', cidade: 'São Paulo' },
  ],
  venda: [
    { _id: 'demo-sale-1', codigo_venda: 'VND-101', data_venda: '2026-10-21', produto: 'Mel Premium', quantidade: 68, valor_bruto: 3400, tipo_venda: 'Atacado' },
    { _id: 'demo-sale-2', codigo_venda: 'VND-102', data_venda: '2026-10-22', produto: 'Mel Floral', quantidade: 42, valor_bruto: 2100, tipo_venda: 'Varejo' },
  ],
  estoque: [
    { _id: 'demo-stock-1', produto: 'Mel Premium 500ml', categoria: 'Produtos', quantidade: 120, preco_unitario: 18.5, estoque_minimo: 40, unidade: 'unidade' },
    { _id: 'demo-stock-2', produto: 'Pote 250ml', categoria: 'Embalagens', quantidade: 33, preco_unitario: 7.9, estoque_minimo: 20, unidade: 'unidade' },
  ],
};

const defaultCompanyProfile = {
  logoUrl: '',
  razaoSocial: 'Empresa Exemplo',
  nomeFantasia: 'Empresa Exemplo',
  cnpj: '',
  inscricaoEstadual: '',
  endereco: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: '',
  cep: '',
  telefone: '',
  email: '',
  site: '',
  segmento: '',
};

const dashboardActivityTemplate = [
  { label: 'Nova venda registrada', detail: 'VND-102 · hoje' },
  { label: 'Estoque revisado', detail: '2 itens em alerta · 08:30' },
  { label: 'Cliente atualizado', detail: 'Mercado Campo · ontem' },
  { label: 'Relatório enviado', detail: 'Financeiro · 18:10' },
];

const dashboardAlertsTemplate = [
  { label: 'Potes em baixo estoque', detail: '2 alertas', type: 'warning-item' },
  { label: 'Produção estável', detail: '92% da meta', type: 'success-item' },
  { label: 'Coleta de Mel', detail: '3 colmeias em revisão', type: 'warning-item' },
];
const optionalValue = (value) => (value === '' || value === null || value === undefined ? undefined : value);
const collectionCache = {
  usuario: [],
  administrador: [],
  funcionario: [],
  cliente: [],
  fornecedor: [],
  venda: [],
  estoque: [],
  produto: [],
};
const tableState = {
  usuario: { sortKey: 'nome', sortDirection: 1, page: 1, pageSize: 5 },
  administrador: { sortKey: 'nome', sortDirection: 1, page: 1, pageSize: 5 },
  funcionario: { sortKey: 'nome', sortDirection: 1, page: 1, pageSize: 5 },
  cliente: { sortKey: 'nome', sortDirection: 1, page: 1, pageSize: 5 },
  fornecedor: { sortKey: 'nome', sortDirection: 1, page: 1, pageSize: 5 },
  venda: { sortKey: 'data_venda', sortDirection: -1, page: 1, pageSize: 5 },
  estoque: { sortKey: 'produto', sortDirection: 1, page: 1, pageSize: 5 },
  produto: { sortKey: 'nome', sortDirection: 1, page: 1, pageSize: 5 },
};

const entityConfig = {
  usuario: {
    listKey: 'usuarios',
    itemIdKey: '_id',
    listEndpoint: '/usuarios',
    createEndpoint: '/usuarios/cadastrar',
    updateEndpoint: '/usuarios',
    buttonLabel: 'Usuário',
    emptyText: 'Nenhum usuário cadastrado.',
    formId: 'usuarioForm',
    exportFields: ['nome', 'email', 'username', 'perfil'],
    mapper: (formData) => ({
      nome: formData.get('nome'),
      email: formData.get('email'),
      username: formData.get('username'),
      password: optionalValue(formData.get('password')),
      perfil: formData.get('perfil') || 'usuario',
    }),
    render: (item) => [
      item.nome || '-',
      item.email || '-',
      item.username || '-',
      item.perfil || '-',
      `<div class="table-actions"><button class="table-action edit" data-kind="usuario" data-id="${item._id || item.id}">Editar</button><button class="table-action delete" data-kind="usuario" data-id="${item._id || item.id}">Excluir</button></div>`,
    ],
    populateForm: (form, item) => {
      form.nome.value = item.nome || '';
      form.email.value = item.email || '';
      form.username.value = item.username || '';
      form.perfil.value = item.perfil || 'usuario';
      form.password.required = false;
      form.password.placeholder = 'Nova senha (opcional)';
    },
    resetForm: (form) => {
      form.password.required = true;
      form.password.placeholder = 'Senha';
    },
  },
  administrador: {
    listKey: 'administradores',
    itemIdKey: '_id',
    listEndpoint: '/administradores',
    createEndpoint: '/administradores/cadastrar',
    updateEndpoint: '/administradores',
    buttonLabel: 'Administrador',
    emptyText: 'Nenhum administrador cadastrado.',
    formId: 'adminForm',
    exportFields: ['nome', 'email', 'username', 'nivel'],
    mapper: (formData) => ({
      nome: formData.get('nome'),
      email: formData.get('email'),
      username: formData.get('username'),
      password: optionalValue(formData.get('password')),
      nivel: formData.get('nivel') || 'admin',
    }),
    render: (item) => [
      item.nome || '-',
      item.email || '-',
      item.username || '-',
      item.nivel || '-',
      `<div class="table-actions"><button class="table-action edit" data-kind="administrador" data-id="${item._id || item.id}">Editar</button><button class="table-action delete" data-kind="administrador" data-id="${item._id || item.id}">Excluir</button></div>`,
    ],
    populateForm: (form, item) => {
      form.nome.value = item.nome || '';
      form.email.value = item.email || '';
      form.username.value = item.username || '';
      form.nivel.value = item.nivel || 'admin';
      form.password.required = false;
      form.password.placeholder = 'Nova senha (opcional)';
    },
    resetForm: (form) => {
      form.password.required = true;
      form.password.placeholder = 'Senha';
    },
  },
  funcionario: {
    listKey: 'funcionarios',
    itemIdKey: '_id',
    listEndpoint: '/funcionarios',
    createEndpoint: '/funcionarios/cadastrar',
    updateEndpoint: '/funcionarios',
    buttonLabel: 'Funcionário',
    emptyText: 'Nenhum funcionário cadastrado.',
    formId: 'funcionarioForm',
    exportFields: ['nome', 'email', 'cargo', 'departamento', 'salario'],
    mapper: (formData) => ({
      nome: formData.get('nome'),
      email: formData.get('email'),
      cargo: formData.get('cargo'),
      departamento: formData.get('departamento'),
      salario: formData.get('salario') === '' ? undefined : Number(formData.get('salario')),
    }),
    render: (item) => [
      item.nome || '-',
      item.email || '-',
      item.cargo || '-',
      item.departamento || '-',
      item.salario ? `R$ ${Number(item.salario).toFixed(2)}` : '-',
      `<div class="table-actions"><button class="table-action edit" data-kind="funcionario" data-id="${item._id || item.id}">Editar</button><button class="table-action delete" data-kind="funcionario" data-id="${item._id || item.id}">Excluir</button></div>`,
    ],
    populateForm: (form, item) => {
      form.nome.value = item.nome || '';
      form.email.value = item.email || '';
      form.cargo.value = item.cargo || '';
      form.departamento.value = item.departamento || '';
      form.salario.value = item.salario ?? '';
    },
  },
  cliente: {
    listKey: 'clientes',
    itemIdKey: '_id',
    listEndpoint: '/clientes',
    createEndpoint: '/clientes/cadastrar',
    updateEndpoint: '/clientes',
    buttonLabel: 'Cliente',
    emptyText: 'Nenhum cliente cadastrado.',
    formId: 'clienteForm',
    exportFields: ['nome', 'email', 'telefone', 'tipo', 'cidade'],
    mapper: (formData) => ({
      nome: formData.get('nome'),
      email: formData.get('email') || undefined,
      telefone: formData.get('telefone') || undefined,
      documento: formData.get('documento') || undefined,
      cidade: formData.get('cidade') || undefined,
      tipo: formData.get('tipo') || 'pf',
      observacoes: formData.get('observacoes') || undefined,
    }),
    render: (item) => [
      item.nome || '-',
      item.email || '-',
      item.telefone || '-',
      item.tipo || '-',
      `<div class="table-actions"><button class="table-action edit" data-kind="cliente" data-id="${item._id || item.id}">Editar</button><button class="table-action delete" data-kind="cliente" data-id="${item._id || item.id}">Excluir</button></div>`,
    ],
    populateForm: (form, item) => {
      form.nome.value = item.nome || '';
      form.email.value = item.email || '';
      form.telefone.value = item.telefone || '';
      form.documento.value = item.documento || '';
      form.cidade.value = item.cidade || '';
      form.tipo.value = item.tipo || 'pf';
      form.observacoes.value = item.observacoes || '';
    },
  },
  fornecedor: {
    listKey: 'fornecedores',
    itemIdKey: '_id',
    listEndpoint: '/fornecedores',
    createEndpoint: '/fornecedores/cadastrar',
    updateEndpoint: '/fornecedores',
    buttonLabel: 'Fornecedor',
    emptyText: 'Nenhum fornecedor cadastrado.',
    formId: 'fornecedorForm',
    exportFields: ['nome', 'cnpj', 'email', 'categoria', 'cidade'],
    mapper: (formData) => ({
      nome: formData.get('nome'),
      cnpj: formData.get('cnpj') || undefined,
      email: formData.get('email') || undefined,
      telefone: formData.get('telefone') || undefined,
      categoria: formData.get('categoria') || undefined,
      cidade: formData.get('cidade') || undefined,
      observacoes: formData.get('observacoes') || undefined,
    }),
    render: (item) => [
      item.nome || '-',
      item.cnpj || '-',
      item.email || '-',
      item.categoria || '-',
      `<div class="table-actions"><button class="table-action edit" data-kind="fornecedor" data-id="${item._id || item.id}">Editar</button><button class="table-action delete" data-kind="fornecedor" data-id="${item._id || item.id}">Excluir</button></div>`,
    ],
    populateForm: (form, item) => {
      form.nome.value = item.nome || '';
      form.cnpj.value = item.cnpj || '';
      form.email.value = item.email || '';
      form.telefone.value = item.telefone || '';
      form.categoria.value = item.categoria || '';
      form.cidade.value = item.cidade || '';
      form.observacoes.value = item.observacoes || '';
    },
  },
  venda: {
    listKey: 'vendas',
    itemIdKey: '_id',
    listEndpoint: '/vendas',
    createEndpoint: '/vendas/registrar',
    updateEndpoint: '/vendas',
    buttonLabel: 'Venda',
    emptyText: 'Nenhuma venda cadastrada.',
    formId: 'vendaForm',
    exportFields: ['codigo_venda', 'data_venda', 'produto', 'quantidade', 'valor_bruto', 'tipo_venda'],
    mapper: (formData) => ({
      codigo_venda: formData.get('codigo_venda'),
      data_venda: formData.get('data_venda'),
      produto: formData.get('produto') || undefined,
      quantidade: formData.get('quantidade') === '' ? undefined : Number(formData.get('quantidade')),
      valor_bruto: formData.get('valor_bruto') === '' ? undefined : Number(formData.get('valor_bruto')),
      tipo_venda: formData.get('tipo_venda'),
    }),
    render: (item) => [
      item.codigo_venda || '-',
      item.data_venda || '-',
      item.produto || '-',
      item.quantidade ?? '-',
      item.valor_bruto ? `R$ ${Number(item.valor_bruto).toFixed(2)}` : '-',
      item.tipo_venda || '-',
      `<div class="table-actions"><button class="table-action edit" data-kind="venda" data-id="${item._id || item.id}">Editar</button><button class="table-action delete" data-kind="venda" data-id="${item._id || item.id}">Excluir</button></div>`,
    ],
    populateForm: (form, item) => {
      form.codigo_venda.value = item.codigo_venda || '';
      form.data_venda.value = item.data_venda || '';
      form.produto.value = item.produto || '';
      form.quantidade.value = item.quantidade ?? '';
      form.valor_bruto.value = item.valor_bruto ?? '';
      form.tipo_venda.value = item.tipo_venda || '';
    },
  },
  estoque: {
    listKey: 'estoque',
    itemIdKey: '_id',
    listEndpoint: '/estoque',
    createEndpoint: '/estoque/cadastrar',
    updateEndpoint: '/estoque',
    buttonLabel: 'Item',
    emptyText: 'Nenhum item em estoque.',
    formId: 'estoqueForm',
    exportFields: ['produto', 'categoria', 'quantidade', 'preco_unitario', 'estoque_minimo', 'unidade'],
    mapper: (formData) => ({
      produto: formData.get('produto'),
      categoria: formData.get('categoria') || 'geral',
      quantidade: formData.get('quantidade') === '' ? undefined : Number(formData.get('quantidade')),
      preco_unitario: formData.get('preco_unitario') === '' ? undefined : Number(formData.get('preco_unitario')),
      estoque_minimo: formData.get('estoque_minimo') === '' ? 0 : Number(formData.get('estoque_minimo')),
      unidade: formData.get('unidade') || 'unidade',
    }),
    render: (item) => [
      item.produto || '-',
      item.categoria || '-',
      item.quantidade ?? '-',
      item.preco_unitario ? `R$ ${Number(item.preco_unitario).toFixed(2)}` : '-',
      item.estoque_minimo ?? '-',
      `<div class="table-actions"><button class="table-action edit" data-kind="estoque" data-id="${item._id || item.id}">Editar</button><button class="table-action delete" data-kind="estoque" data-id="${item._id || item.id}">Excluir</button></div>`,
    ],
    populateForm: (form, item) => {
      form.produto.value = item.produto || '';
      form.categoria.value = item.categoria || 'geral';
      form.quantidade.value = item.quantidade ?? '';
      form.preco_unitario.value = item.preco_unitario ?? '';
      form.estoque_minimo.value = item.estoque_minimo ?? 0;
      form.unidade.value = item.unidade || 'unidade';
    },
  },
  produto: {
    listKey: 'produtos',
    itemIdKey: '_id',
    listEndpoint: '/produtos',
    createEndpoint: '/produtos/cadastrar',
    updateEndpoint: '/produtos',
    buttonLabel: 'Produto',
    emptyText: 'Nenhum produto cadastrado.',
    formId: 'produtoForm',
    exportFields: ['codigo', 'nome', 'categoria', 'descricao', 'preco', 'unidade', 'ativo'],
    mapper: (formData) => ({
      codigo: optionalValue(formData.get('codigo')),
      nome: formData.get('nome'),
      categoria: formData.get('categoria') || 'geral',
      descricao: optionalValue(formData.get('descricao')),
      preco: formData.get('preco') === '' ? undefined : Number(formData.get('preco')),
      unidade: formData.get('unidade') || 'unidade',
      ativo: formData.get('ativo') === 'true',
    }),
    render: (item) => [
      item.codigo || '-',
      item.nome || '-',
      item.categoria || '-',
      item.descricao || '-',
      item.preco !== undefined ? `R$ ${Number(item.preco).toFixed(2)}` : '-',
      item.unidade || '-',
      item.ativo ? 'Ativo' : 'Inativo',
      `<div class="table-actions"><button class="table-action edit" data-kind="produto" data-id="${item._id || item.id}">Editar</button><button class="table-action delete" data-kind="produto" data-id="${item._id || item.id}">Excluir</button></div>`,
    ],
    populateForm: (form, item) => {
      form.codigo.value = item.codigo || '';
      form.nome.value = item.nome || '';
      form.categoria.value = item.categoria || 'geral';
      form.descricao.value = item.descricao || '';
      form.preco.value = item.preco ?? '';
      form.unidade.value = item.unidade || 'unidade';
      form.ativo.value = item.ativo ? 'true' : 'false';
    },
  },
};

async function requestLogin(username, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.detail || 'Credenciais inválidas.');
  }

  return data;
}

function showLoginModal() {
  const modal = document.getElementById('loginModal');
  if (modal) {
    modal.classList.add('visible');
  }
}

function hideLoginModal() {
  const modal = document.getElementById('loginModal');
  if (modal) {
    modal.classList.remove('visible');
  }
}

function getAdminToken() {
  const token = localStorage.getItem('api_token');
  if (token) return token;

  const loginDialog = document.getElementById('loginDialog');
  const loginModal = document.getElementById('loginModal');

  if (!loginDialog && !loginModal) {
    throw new Error('O formulário de autenticação não está disponível.');
  }

  if (loginDialog) {
    loginDialog.showModal();
  } else if (loginModal) {
    showLoginModal();
  }

  if (!adminTokenPromise) {
    adminTokenPromise = new Promise((resolve) => {
      resolveAdminToken = resolve;
    });
  }

  throw new Error('Autenticação necessária.');
}

document.getElementById('loginForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const submitButton = form.querySelector('button[type="submit"]');
  const errorMessage = document.getElementById('loginError');
  submitButton.disabled = true;
  errorMessage.textContent = '';

  try {
    const loginResponse = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: form.elements.username.value,
        password: form.elements.password.value,
      }),
    });
    const payload = await loginResponse.json().catch(() => null);
    if (!loginResponse.ok) {
      throw new Error(formatRequestError(payload));
    }
    if (typeof payload?.access_token !== 'string' || !payload.access_token) {
      throw new Error('A API não retornou um token de acesso válido.');
    }

    localStorage.setItem('api_token', payload.access_token);
    form.reset();
    const loginDialog = document.getElementById('loginDialog');
    if (loginDialog) {
      loginDialog.close();
    }
    hideLoginModal();
    const resolveToken = resolveAdminToken;
    resolveAdminToken = null;
    adminTokenPromise = null;
    if (resolveToken) resolveToken(payload.access_token);
  } catch (error) {
    errorMessage.textContent = error.message || 'Não foi possível autenticar.';
  } finally {
    submitButton.disabled = false;
  }
});

function getStoredBrandConfig() {
  try {
    const stored = JSON.parse(localStorage.getItem('companyBrandConfig') || 'null');
    return { ...defaultBrandConfig, ...(stored || {}) };
  } catch (error) {
    return { ...defaultBrandConfig };
  }
}

function getStoredCompanyProfile() {
  try {
    const stored = JSON.parse(localStorage.getItem('companyProfile') || 'null');
    return { ...defaultCompanyProfile, ...(stored || {}) };
  } catch (error) {
    return { ...defaultCompanyProfile };
  }
}

function buildCompanyLogoDataUrl(companyName = defaultBrandConfig.companyName) {
  const brandConfig = getStoredBrandConfig();
  const primaryColor = brandConfig.primaryColor || defaultBrandConfig.primaryColor;
  const secondaryColor = brandConfig.secondaryColor || defaultBrandConfig.secondaryColor;
  const acronym = (brandConfig.companyAcronym || companyName || defaultBrandConfig.companyName)
    .replace(/[^A-Za-z0-9]/g, '')
    .slice(0, 2)
    .toUpperCase() || 'EE';

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-label="Logo da empresa">
      <defs>
        <linearGradient id="brandGradient" x1="0%" x2="100%" y1="0%" y2="100%">
          <stop offset="0%" stop-color="${primaryColor}" />
          <stop offset="100%" stop-color="${secondaryColor}" />
        </linearGradient>
      </defs>
      <rect width="128" height="128" rx="28" fill="url(#brandGradient)"/>
      <circle cx="98" cy="32" r="20" fill="rgba(255,255,255,0.17)"/>
      <path d="M18 96c14-22 31-34 54-34 17 0 31 6 38 18v16H18z" fill="rgba(255,255,255,0.18)"/>
      <text x="64" y="74" text-anchor="middle" font-size="38" font-family="Arial, sans-serif" font-weight="700" fill="white" letter-spacing="2">${acronym}</text>
    </svg>
  `;

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
}

function syncCompanyProfileForm() {
  const form = document.getElementById('empresaForm');
  if (!form) return;

  const profile = getStoredCompanyProfile();
  const entries = Object.entries(profile);
  entries.forEach(([key, value]) => {
    const input = form.elements.namedItem(key);
    if (input) {
      input.value = value || '';
    }
  });
}

function setLogoPreviewFromUrl(url) {
  const previewBox = document.getElementById('logoPreviewBox');
  const companyName = getStoredBrandConfig().companyName || defaultBrandConfig.companyName;
  const fallbackLogo = buildCompanyLogoDataUrl(companyName);
  const resolvedUrl = url || fallbackLogo;

  if (previewBox) {
    previewBox.innerHTML = `<img src="${resolvedUrl}" alt="Pré-visualização da logo da empresa" />`;
  }

  const dashboardBrandMark = document.getElementById('dashboardBrandMark');
  if (dashboardBrandMark) {
    dashboardBrandMark.innerHTML = `<img src="${resolvedUrl}" alt="Logo da empresa" />`;
    dashboardBrandMark.style.padding = '0';
    dashboardBrandMark.style.overflow = 'hidden';
    dashboardBrandMark.style.background = 'transparent';
    dashboardBrandMark.style.boxShadow = 'none';
    dashboardBrandMark.style.border = 'none';
  }

  const topbarBrandMark = document.getElementById('topbarBrandMark');
  if (topbarBrandMark) {
    topbarBrandMark.innerHTML = `<img src="${resolvedUrl}" alt="Logo da empresa" />`;
    topbarBrandMark.style.padding = '0';
    topbarBrandMark.style.overflow = 'hidden';
    topbarBrandMark.style.background = 'transparent';
    topbarBrandMark.style.boxShadow = 'none';
    topbarBrandMark.style.border = 'none';
  }
}

async function loadCompanyProfileFromApi() {
  try {
    const token = await getAdminToken();
    const response = await fetch(`${API_BASE}/empresa`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) return null;

    const payload = await response.json().catch(() => null);
    const empresa = payload?.empresa || null;
    if (!empresa || !Object.keys(empresa).length) return null;

    const mergedProfile = { ...defaultCompanyProfile, ...empresa };
    localStorage.setItem('companyProfile', JSON.stringify(mergedProfile));
    syncCompanyProfileForm();
    applyBrandConfig({
      ...getStoredBrandConfig(),
      companyName: mergedProfile.nomeFantasia || mergedProfile.razaoSocial || defaultBrandConfig.companyName,
      companyAcronym: (mergedProfile.nomeFantasia || mergedProfile.razaoSocial || defaultBrandConfig.companyName).slice(0, 2).toUpperCase() || defaultBrandConfig.companyAcronym,
    });
    setLogoPreviewFromUrl(mergedProfile.logoUrl || '');
    return mergedProfile;
  } catch (error) {
    console.warn('Não foi possível carregar a empresa da API:', error);
    return null;
  }
}

async function persistCompanyProfile(profile) {
  try {
    const token = await getAdminToken();
    const response = await fetch(`${API_BASE}/empresa`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profile),
    });

    if (!response.ok) {
      throw new Error('Falha ao salvar no backend');
    }

    const payload = await response.json().catch(() => null);
    return payload?.empresa || profile;
  } catch (error) {
    console.warn('Fallback para localStorage:', error);
    return profile;
  }
}

function saveCompanyProfile(form) {
  const formData = new FormData(form);
  const profile = Object.fromEntries(formData.entries());
  const normalized = {
    ...defaultCompanyProfile,
    ...profile,
  };

  localStorage.setItem('companyProfile', JSON.stringify(normalized));

  const companyName = normalized.nomeFantasia || normalized.razaoSocial || defaultBrandConfig.companyName;
  applyBrandConfig({
    ...getStoredBrandConfig(),
    companyName,
    companyAcronym: (normalized.nomeFantasia || companyName).slice(0, 2).toUpperCase() || defaultBrandConfig.companyAcronym,
  });
  setLogoPreviewFromUrl(normalized.logoUrl || '');
  persistCompanyProfile(normalized).catch(() => undefined);
}

function applyBrandConfig(brandConfig = getStoredBrandConfig()) {
  document.documentElement.style.setProperty('--green-700', brandConfig.primaryColor || defaultBrandConfig.primaryColor);
  document.documentElement.style.setProperty('--blue-700', brandConfig.secondaryColor || defaultBrandConfig.secondaryColor);
  document.documentElement.style.setProperty('--green-900', brandConfig.primaryColor || defaultBrandConfig.primaryColor);

  const companyName = brandConfig.companyName || defaultBrandConfig.companyName;
  const acronym = (brandConfig.companyAcronym || companyName.slice(0, 2).toUpperCase() || defaultBrandConfig.companyAcronym).slice(0, 4);
  const logoUrl = getStoredCompanyProfile().logoUrl;

  const dashboardBrandMark = document.getElementById('dashboardBrandMark');
  const topbarBrandMark = document.getElementById('topbarBrandMark');
  const titleNode = document.getElementById('headerCompanyTitle');
  const nameNode = document.getElementById('brandCompanyName');
  const dashboardNameNode = document.getElementById('dashboardBrandCompanyName');

  [dashboardBrandMark, topbarBrandMark].forEach((brandMark) => {
    if (!brandMark) return;

    const fallbackLogo = buildCompanyLogoDataUrl(companyName);
    const resolvedLogoUrl = logoUrl || fallbackLogo;
    brandMark.innerHTML = `<img src="${resolvedLogoUrl}" alt="Logo da empresa" />`;
    brandMark.style.padding = '0';
    brandMark.style.overflow = 'hidden';
    brandMark.style.background = 'transparent';
    brandMark.style.boxShadow = 'none';
    brandMark.style.border = 'none';
    const img = brandMark.querySelector('img');
    if (img) {
      img.style.width = '100%';
      img.style.height = '100%';
      img.style.objectFit = 'cover';
      img.style.display = 'block';
    }
  });

  if (nameNode) nameNode.textContent = companyName;
  if (dashboardNameNode) dashboardNameNode.textContent = companyName;
  if (titleNode) titleNode.textContent = companyName;
  document.title = `${companyName} | Sistema de Gestão`;

  const companyNameInput = document.getElementById('companyNameInput');
  const companyAcronymInput = document.getElementById('companyAcronymInput');
  const companyPrimaryColorInput = document.getElementById('companyPrimaryColorInput');
  const companySecondaryColorInput = document.getElementById('companySecondaryColorInput');

  if (companyNameInput) companyNameInput.value = companyName;
  if (companyAcronymInput) companyAcronymInput.value = acronym;
  if (companyPrimaryColorInput) companyPrimaryColorInput.value = brandConfig.primaryColor || defaultBrandConfig.primaryColor;
  if (companySecondaryColorInput) companySecondaryColorInput.value = brandConfig.secondaryColor || defaultBrandConfig.secondaryColor;

  localStorage.setItem('companyBrandConfig', JSON.stringify({
    companyName,
    companyAcronym: acronym,
    primaryColor: brandConfig.primaryColor || defaultBrandConfig.primaryColor,
    secondaryColor: brandConfig.secondaryColor || defaultBrandConfig.secondaryColor,
  }));

  return { companyName, acronym };
}

function showMessage(message, type = 'success') {
  if (!responseMessage) return;
  responseMessage.textContent = message;
  responseMessage.classList.toggle('error', type === 'error');
}

function formatRequestError(payload) {
  const detail = payload?.detail;
  if (Array.isArray(detail)) {
    const fieldLabels = {
      nome: 'Nome',
      email: 'E-mail',
      username: 'Usuário',
      password: 'Senha',
      perfil: 'Perfil',
    };

    return detail.map((issue) => {
      const field = Array.isArray(issue.loc)
        ? issue.loc.filter((part) => part !== 'body').join('.')
        : '';
      const label = fieldLabels[field] || field;

      if (issue.type === 'string_too_short' && Number.isInteger(issue.ctx?.min_length)) {
        return `${label}: deve ter pelo menos ${issue.ctx.min_length} caracteres.`;
      }
      if (issue.type === 'missing') {
        return `${label || 'Campo'}: preenchimento obrigatório.`;
      }

      return label ? `${label}: ${issue.msg || 'valor inválido.'}` : issue.msg || 'Dados inválidos.';
    }).join(' ');
  }

  return typeof detail === 'string'
    ? detail
    : payload?.message || 'Erro de comunicação com a API.';
}

function getDemoStore() {
  const raw = localStorage.getItem('demoStore');
  if (raw) {
    try {
      return JSON.parse(raw);
    } catch (error) {
      return {};
    }
  }
  return {};
}

function persistDemoStore(store) {
  localStorage.setItem('demoStore', JSON.stringify(store));
}

function localDemoRequest(endpoint, method = 'GET', body = null) {
  const store = getDemoStore();
  const normalizedEndpoint = endpoint.replace(/^\//, '');

  if (method === 'GET') {
    if (normalizedEndpoint === 'vendas') {
      return Promise.resolve({ vendas: store.vendas || demoCollections.venda });
    }
    if (normalizedEndpoint === 'funcionarios') {
      return Promise.resolve({ funcionarios: store.funcionarios || demoCollections.funcionario });
    }
    if (normalizedEndpoint === 'usuarios') {
      return Promise.resolve({ usuarios: store.usuarios || demoCollections.usuario });
    }
    if (normalizedEndpoint === 'clientes') {
      return Promise.resolve({ clientes: store.clientes || demoCollections.cliente });
    }
    if (normalizedEndpoint === 'fornecedores') {
      return Promise.resolve({ fornecedores: store.fornecedores || demoCollections.fornecedor });
    }
    if (normalizedEndpoint === 'estoque') {
      return Promise.resolve({ estoque: store.estoque || demoCollections.estoque });
    }
    if (normalizedEndpoint === 'dashboard/resumo') {
      return Promise.resolve({ ...syncDemoSummary(store), usuario: 'demo' });
    }
    if (normalizedEndpoint === 'financeiro/fundo-acumulado') {
      const summary = syncDemoSummary(store);
      return Promise.resolve({ valor_acumulado: summary.fundo_acumulado, usuario: 'demo' });
    }
    if (normalizedEndpoint === 'estoque/alertas') {
      const estoque = store.estoque || demoCollections.estoque;
      const alertas = estoque
        .filter((item) => Number(item.quantidade || 0) <= Number(item.estoque_minimo || 0))
        .map((item) => ({
          produto: item.produto,
          quantidade: Number(item.quantidade || 0),
          estoque_minimo: Number(item.estoque_minimo || 0),
          status: Number(item.quantidade || 0) <= 0 ? 'zerado' : 'baixo',
        }));
      return Promise.resolve({ alertas });
    }
    if (normalizedEndpoint === 'estoque/relatorio') {
      const summary = syncDemoSummary(store);
      const estoque = store.estoque || demoCollections.estoque;
      const valor_total = estoque.reduce((total, item) => total + (Number(item.quantidade || 0) * Number(item.preco_unitario || 0)), 0);
      return Promise.resolve({ total_quantidade: summary.estoque_total, valor_total_estoque: valor_total });
    }
  }

  if (method === 'POST' || method === 'PUT' || method === 'DELETE') {
    const entityKey = normalizedEndpoint.split('/')[0];
    const master = { vendas: 'venda', usuarios: 'usuario', funcionarios: 'funcionario', clientes: 'cliente', fornecedores: 'fornecedor', estoque: 'estoque' };
    const kind = master[entityKey] || entityKey;
    const items = store[kind] || demoCollections[kind] || [];

    if (method === 'POST' && body) {
      const newItem = { _id: `demo-${Date.now()}`, ...body };

      if (kind === 'venda') {
        const estoqueAtual = store.estoque || demoCollections.estoque;
        const produto = newItem.produto;
        const quantidade = Number(newItem.quantidade || 0);
        if (produto && quantidade > 0) {
          const estoqueFiltrado = estoqueAtual.map((item) => {
            if (item.produto === produto) {
              return { ...item, quantidade: Math.max(0, Number(item.quantidade || 0) - quantidade) };
            }
            return item;
          });
          store.estoque = estoqueFiltrado;
        }
        newItem.valor_fundo = Number(newItem.valor_bruto || 0) * 0.3;
      }

      if (kind === 'estoque') {
        const estoqueAtual = store.estoque || [];
        store.estoque = [...estoqueAtual, newItem];
      } else {
        store[kind] = [...items, newItem];
      }

      persistDemoStore(store);
      syncDemoSummary(store);
      return Promise.resolve(newItem);
    }

    if (method === 'PUT' && body) {
      const id = normalizedEndpoint.split('/').pop();
      const next = items.map((item) => ((item._id || item.id) === id ? { ...item, ...body } : item));
      store[kind] = next;
      persistDemoStore(store);
      syncDemoSummary(store);
      return Promise.resolve({ ...body, _id: id });
    }

    if (method === 'DELETE') {
      const id = normalizedEndpoint.split('/').pop();
      const next = items.filter((item) => (item._id || item.id) !== id);
      store[kind] = next;
      persistDemoStore(store);
      syncDemoSummary(store);
      return Promise.resolve({ deleted: true, _id: id });
    }
  }

  return Promise.resolve({ ok: true });
}

async function requestJson(endpoint, method = 'GET', body = null) {
  const token = await getAdminToken();
  const options = {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };

  if (body !== null) {
    options.headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(body);
  }

  try {
    let response = await fetch(`${API_BASE}${endpoint}`, options);
    if (response.status === 401) {
      if (localStorage.getItem('api_token') === token) {
        localStorage.removeItem('api_token');
      }
      const refreshedToken = await getAdminToken();
      options.headers.Authorization = `Bearer ${refreshedToken}`;
      response = await fetch(`${API_BASE}${endpoint}`, options);
    }
    const payload = await response.json().catch(() => null);

    if (!response.ok) {
      throw new Error(formatRequestError(payload));
    }

    return payload;
  } catch (error) {
    if (endpoint === '/auth/login' || endpoint === '/auth') {
      throw error;
    }
    return localDemoRequest(endpoint, method, body);
  }
}

function setFormMode(form, mode, item = null) {
  const submitButton = form.querySelector('button[type="submit"]');
  const formTitle = form.querySelector('h4');

  form.dataset.mode = mode;
  form.dataset.editId = item ? (item._id || item.id || '') : '';

  if (mode === 'edit') {
    submitButton.textContent = `Atualizar ${formTitle.textContent.trim()}`;
  } else {
    submitButton.textContent = `Salvar ${formTitle.textContent.trim()}`;
  }
}

function formToPayload(formId, formData) {
  const mapper = entityConfig[formId.replace('Form', '')]?.mapper || entityConfig[formId]?.mapper;
  if (typeof mapper === 'function') {
    return mapper(formData);
  }
  return Object.fromEntries(formData.entries());
}

function getFormKind(form) {
  return form.dataset.kind || 'usuario';
}

async function submitForm(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formKind = getFormKind(form);
  const formData = new FormData(form);
  const payload = entityConfig[formKind].mapper(formData);
  const isEdit = form.dataset.mode === 'edit';
  const id = form.dataset.editId;
  const endpoint = isEdit ? `${entityConfig[formKind].updateEndpoint}/${id}` : entityConfig[formKind].createEndpoint;

  try {
    await requestJson(endpoint, isEdit ? 'PUT' : 'POST', payload);
    showMessage(`${entityConfig[formKind].buttonLabel} ${isEdit ? 'atualizado' : 'salvo'} com sucesso.`, 'success');
    form.reset();
    setFormMode(form, 'create');
    if (entityConfig[formKind].resetForm) {
      entityConfig[formKind].resetForm(form);
    }
    await refreshCollections();
  } catch (error) {
    showMessage(error.message || 'Erro inesperado.', 'error');
  }
}

async function fetchCollection(kind) {
  const config = entityConfig[kind];

  try {
    const response = await requestJson(config.listEndpoint, 'GET');
    const items = response?.[config.listKey] || [];
    collectionCache[kind] = items;
    return items;
  } catch (error) {
    const fallbackItems = demoCollections[kind] || [];
    collectionCache[kind] = fallbackItems;
    return fallbackItems;
  }
}

function getFilteredItems(kind) {
  const searchInput = document.querySelector(`.table-search[data-kind="${kind}"]`);
  const searchTerm = (searchInput?.value || '').trim().toLowerCase();
  const items = collectionCache[kind] || [];

  if (!searchTerm) {
    return items;
  }

  return items.filter((item) => JSON.stringify(item).toLowerCase().includes(searchTerm));
}

function sortByKey(items, kind) {
  const sortStateEntry = tableState[kind];
  if (!sortStateEntry) return items;

  const { sortKey, sortDirection } = sortStateEntry;

  return [...items].sort((a, b) => {
    const aValue = a?.[sortKey] ?? '';
    const bValue = b?.[sortKey] ?? '';

    const normalizedA = typeof aValue === 'number' ? aValue : String(aValue).toLowerCase();
    const normalizedB = typeof bValue === 'number' ? bValue : String(bValue).toLowerCase();

    if (normalizedA < normalizedB) return -1 * sortDirection;
    if (normalizedA > normalizedB) return 1 * sortDirection;
    return 0;
  });
}

function paginateItems(items, kind) {
  const state = tableState[kind];
  if (!state) return { items, totalPages: 1, currentPage: 1, totalRecords: items.length };

  const totalRecords = items.length;
  const totalPages = Math.max(1, Math.ceil(totalRecords / state.pageSize));
  state.page = Math.min(state.page, totalPages);
  const start = (state.page - 1) * state.pageSize;
  const paginatedItems = items.slice(start, start + state.pageSize);

  return { items: paginatedItems, totalPages, currentPage: state.page, totalRecords };
}

function renderCollection(kind) {
  const config = entityConfig[kind];
  const tableBody = document.getElementById(`${config.listKey}TableBody`);
  if (!tableBody) return;

  const filteredItems = getFilteredItems(kind);
  const sortedItems = sortByKey(filteredItems, kind);
  const { items, totalPages, currentPage, totalRecords } = paginateItems(sortedItems, kind);

  if (!items.length) {
    tableBody.innerHTML = `<tr><td colspan="100%" class="empty-state">${config.emptyText}</td></tr>`;
  } else {
    tableBody.innerHTML = items
      .map((item) => {
        const cells = config.render(item);
        return `<tr>${cells.map((cell) => `<td>${cell}</td>`).join('')}</tr>`;
      })
      .join('');
  }

  const meta = document.getElementById(`${config.listKey}Meta`);
  const pageInfo = document.getElementById(`${config.listKey}PageInfo`);

  if (meta) {
    meta.textContent = `${totalRecords} registros`;
  }

  if (pageInfo) {
    pageInfo.textContent = `${currentPage}/${totalPages}`;
  }
}

function renderAllCollections() {
  Object.keys(entityConfig).forEach((kind) => renderCollection(kind));
}

function renderDashboardActivity() {
  const activityList = document.getElementById('dashboardActivityList');
  const alertsList = document.getElementById('dashboardAlertsList');

  if (activityList) {
    const items = dashboardActivityTemplate.map((item, index) => {
      const tone = index % 3 === 0 ? 'green' : index % 3 === 1 ? 'blue' : 'gray';
      return `
        <li>
          <span class="bullet ${tone}"></span>
          <div>
            <strong>${item.label}</strong>
            <small>${item.detail}</small>
          </div>
        </li>
      `;
    });
    activityList.innerHTML = items.join('');
  }

  if (alertsList) {
    const items = dashboardAlertsTemplate.map((item) => `
      <li class="alert-item ${item.type}">
        <div>
          <strong>${item.label}</strong>
          <small>${item.detail}</small>
        </div>
      </li>
    `).join('');
    alertsList.innerHTML = items;
  }

  const lastUpdated = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
  const productionRate = document.getElementById('dashboardProductionRate');
  const activeUnits = document.getElementById('dashboardActiveUnits');
  const lastUpdatedNode = document.getElementById('dashboardLastUpdated');
  const colmeiasNode = document.getElementById('cardColmeiasAtivas');
  const lotesNode = document.getElementById('cardLotesRegistrados');
  const dispositivosNode = document.getElementById('cardDispositivosOnline');
  const fundoNode = document.getElementById('cardFundoAcumulado');

  if (productionRate) productionRate.textContent = '92%';
  if (activeUnits) activeUnits.textContent = '128';
  if (lastUpdatedNode) lastUpdatedNode.textContent = lastUpdated;
  if (colmeiasNode) colmeiasNode.textContent = '128';
  if (lotesNode) lotesNode.textContent = '42';
  if (dispositivosNode) dispositivosNode.textContent = '96%';
  if (fundoNode) fundoNode.textContent = 'R$ 48.700,00';
}

function applySummaryValues(summary) {
  const totalVendas = Number(summary.total_vendas || 0);
  const totalFuncionarios = Number(summary.total_funcionarios || 0);
  const fundoAcumulado = Number(summary.fundo_acumulado || 0);
  const faturamentoMes = Number(summary.faturamento_mes || 0);
  const totalClientes = Number(summary.total_clientes || 0);
  const totalFornecedores = Number(summary.total_fornecedores || 0);
  const estoqueTotal = Number(summary.estoque_total || 0);

  const salesCountMetric = document.getElementById('salesCountMetric');
  const fundoAcumuladoMetric = document.getElementById('fundoAcumuladoMetric');
  const employeesCountMetric = document.getElementById('employeesCountMetric');
  const monthlyRevenueMetric = document.getElementById('monthlyRevenueMetric');
  const reportSalesCount = document.getElementById('reportSalesCount');
  const reportFundoAcumulado = document.getElementById('reportFundoAcumulado');
  const reportFuncionarios = document.getElementById('reportFuncionarios');
  const reportClientes = document.getElementById('reportClientes');
  const reportFornecedores = document.getElementById('reportFornecedores');
  const reportEstoque = document.getElementById('reportEstoque');
  const cardFundoAcumulado = document.getElementById('cardFundoAcumulado');
  const salesCardValue = document.getElementById('salesCountMetric');
  const fundoAcumuladoPlaceholder = document.getElementById('fundoAcumuladoMetricPlaceholder');
  const salesCountPlaceholder = document.getElementById('salesCountMetricPlaceholder');
  const monthlyRevenuePlaceholder = document.getElementById('monthlyRevenueMetricPlaceholder');

  const moneyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

  if (salesCountMetric) salesCountMetric.textContent = String(totalVendas);
  if (fundoAcumuladoMetric) fundoAcumuladoMetric.textContent = moneyFormatter.format(fundoAcumulado);
  if (employeesCountMetric) employeesCountMetric.textContent = String(totalFuncionarios);
  if (monthlyRevenueMetric) monthlyRevenueMetric.textContent = moneyFormatter.format(faturamentoMes);
  if (cardFundoAcumulado) cardFundoAcumulado.textContent = moneyFormatter.format(fundoAcumulado);
  if (salesCardValue) salesCardValue.textContent = String(totalVendas);
  if (fundoAcumuladoPlaceholder) fundoAcumuladoPlaceholder.textContent = moneyFormatter.format(fundoAcumulado);
  if (salesCountPlaceholder) salesCountPlaceholder.textContent = String(totalVendas);
  if (monthlyRevenuePlaceholder) monthlyRevenuePlaceholder.textContent = moneyFormatter.format(faturamentoMes);

  if (reportSalesCount) reportSalesCount.textContent = String(totalVendas);
  if (reportFundoAcumulado) reportFundoAcumulado.textContent = moneyFormatter.format(fundoAcumulado);
  if (reportFuncionarios) reportFuncionarios.textContent = String(totalFuncionarios);
  if (reportClientes) reportClientes.textContent = String(totalClientes);
  if (reportFornecedores) reportFornecedores.textContent = String(totalFornecedores);
  if (reportEstoque) reportEstoque.textContent = String(estoqueTotal);
}

async function updateOperationalMetrics() {
  try {
    const summaryResponse = await requestJson('/dashboard/resumo');
    const summary = summaryResponse || {};
    applySummaryValues(summary);
    return;
  } catch (error) {
    try {
      const [vendasResponse, funcionariosResponse, fundoResponse] = await Promise.all([
        requestJson('/vendas'),
        requestJson('/funcionarios'),
        requestJson('/financeiro/fundo-acumulado'),
      ]);

      const vendas = vendasResponse?.vendas || [];
      const funcionarios = funcionariosResponse?.funcionarios || [];
      const fundoAcumulado = Number(fundoResponse?.valor_acumulado || 0);
      const totalVendas = vendas.length;
      const totalFuncionarios = funcionarios.length;
      const currentMonth = new Date().toISOString().slice(0, 7);
      const faturamentoMes = vendas
        .filter((venda) => (venda.data_venda || '').startsWith(currentMonth))
        .reduce((total, venda) => total + Number(venda.valor_bruto || 0), 0);

      applySummaryValues({
        total_vendas: totalVendas,
        total_funcionarios: totalFuncionarios,
        fundo_acumulado: fundoAcumulado,
        faturamento_mes: faturamentoMes,
        total_clientes: 0,
        total_fornecedores: 0,
        estoque_total: 0,
      });
    } catch (fallbackError) {
      applySummaryValues(demoSummary);
    }
  }
}

function renderSalesChart(vendas) {
  const chart = document.getElementById('salesChart');
  if (!chart) return;

  const today = new Date();
  today.setUTCHours(0, 0, 0, 0);
  const days = Array.from({ length: 7 }, (_, index) => {
    const day = new Date(today);
    day.setUTCDate(today.getUTCDate() - (6 - index));
    return day.toISOString().slice(0, 10);
  });
  const totalsByDay = new Map(days.map((day) => [day, 0]));

  (Array.isArray(vendas) ? vendas : []).forEach((venda) => {
    const day = String(venda.data_venda || '').slice(0, 10);
    if (totalsByDay.has(day)) {
      totalsByDay.set(day, totalsByDay.get(day) + Number(venda.valor_bruto || 0));
    }
  });

  const maxTotal = Math.max(...totalsByDay.values());
  if (maxTotal === 0) {
    chart.innerHTML = '<p class="chart-empty">Sem vendas nos últimos sete dias.</p>';
    return;
  }

  const moneyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
  chart.innerHTML = days.map((day) => {
    const total = totalsByDay.get(day);
    const height = maxTotal > 0 ? (total / maxTotal) * 100 : 0;
    const label = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit' })
      .format(new Date(`${day}T00:00:00Z`));
    return `<span style="--bar-height: ${height}%" title="${label}: ${moneyFormatter.format(total)}"></span>`;
  }).join('');
}

async function atualizarAlertasEstoque() {
  try {
    const [alertasResponse, relatorioResponse] = await Promise.all([
      requestJson('/estoque/alertas'),
      requestJson('/estoque/relatorio'),
    ]);

    const alertas = alertasResponse?.alertas || [];
    const relatorio = relatorioResponse || {};

    const alertaCount = document.getElementById('alertaEstoqueCount');
    const estoqueTotal = document.getElementById('relatorioEstoqueTotal');
    const valorEstoque = document.getElementById('relatorioValorEstoque');

    if (alertaCount) alertaCount.textContent = String(alertas.length);
    if (estoqueTotal) estoqueTotal.textContent = String(relatorio.total_quantidade || 0);
    if (valorEstoque) {
      const moneyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
      valorEstoque.textContent = moneyFormatter.format(Number(relatorio.valor_total_estoque || 0));
    }
  } catch (error) {
    const alertaCount = document.getElementById('alertaEstoqueCount');
    const estoqueTotal = document.getElementById('relatorioEstoqueTotal');
    const valorEstoque = document.getElementById('relatorioValorEstoque');
    const moneyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

    if (alertaCount) alertaCount.textContent = '2';
    if (estoqueTotal) estoqueTotal.textContent = String(demoSummary.estoque_total);
    if (valorEstoque) valorEstoque.textContent = moneyFormatter.format(14820);
  }
}

async function refreshCollections() {
  try {
    await Promise.all([
      fetchCollection('usuario'),
      fetchCollection('administrador'),
      fetchCollection('funcionario'),
      fetchCollection('cliente'),
      fetchCollection('fornecedor'),
      fetchCollection('venda'),
      fetchCollection('estoque'),
      fetchCollection('produto'),
    ]);
    renderAllCollections();
    renderDashboardActivity();
    await Promise.all([
      updateOperationalMetrics(),
      atualizarAlertasEstoque(),
    ]);
  } catch (error) {
    const dashboardStatus = document.getElementById('dashboardStatus');
    if (dashboardStatus) dashboardStatus.textContent = 'Indisponível';
    showMessage(error.message || 'Não foi possível atualizar os registros.', 'error');
  }
}

function fillFormForEdit(form, item) {
  const config = entityConfig[getFormKind(form)];
  if (config.populateForm) {
    config.populateForm(form, item);
  }
  setFormMode(form, 'edit', item);
}

async function deleteRecord(kind, id) {
  const config = entityConfig[kind];
  if (!id) return;

  const shouldDelete = window.confirm('Deseja excluir este registro?');
  if (!shouldDelete) return;

  try {
    await requestJson(`${config.updateEndpoint}/${id}`, 'DELETE');
    showMessage(`${config.buttonLabel} excluído com sucesso.`, 'success');
    await refreshCollections();
  } catch (error) {
    showMessage(error.message || 'Erro ao excluir registro.', 'error');
  }
}

function exportToCsv(kind) {
  const config = entityConfig[kind];
  const items = getFilteredItems(kind);

  if (!items.length) {
    showMessage(`Nenhum dado para exportar em ${config.buttonLabel.toLowerCase()}.`, 'error');
    return;
  }

  const fieldNames = config.exportFields || Object.keys(items[0] || {});
  const rows = [fieldNames.join(',')];

  items.forEach((item) => {
    const values = fieldNames.map((field) => {
      const rawValue = item?.[field] ?? '';
      const normalized = String(rawValue).replace(/"/g, '""');
      return `"${normalized}"`;
    });
    rows.push(values.join(','));
  });

  const blob = new Blob([rows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = `${kind}.csv`;
  link.click();
  URL.revokeObjectURL(link.href);
}

function updateSystemStatus(mode, label) {
  const badge = document.getElementById('systemStatusBadge');
  if (!badge) return;

  badge.className = `status-badge ${mode}`;
  badge.textContent = label;
}

async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE.replace('/api/v1', '')}/health`, { method: 'GET' });
    if (!response.ok) {
      throw new Error('API indisponível');
    }
    updateSystemStatus('online', 'API online');
    return true;
  } catch (error) {
    updateSystemStatus('demo', 'Modo demonstração');
    return false;
  }
}

function initializeApp() {
  updateSystemStatus('neutral', 'Conectando...');

  return (async () => {
    const backendIsOnline = await checkBackendHealth();

    if (!backendIsOnline) {
      showLoginModal();
      showMessage('Servidor indisponível; usando dados de demonstração.', 'error');
      return;
    }

    if (!localStorage.getItem('api_token')) {
      showLoginModal();
      showMessage('Faça login para acessar o sistema.', 'success');
      return;
    }

    try {
      await refreshCollections();
      updateSystemStatus('online', 'API online');
    } catch (error) {
      showMessage(error.message || 'Não foi possível carregar os dados.', 'error');
    }
  })();
}

function showScreen(screenName) {
  const screens = document.querySelectorAll('.screen-panel');
  screens.forEach((screen) => {
    screen.classList.toggle('active', screen.id === `screen-${screenName}`);
  });

  const buttons = document.querySelectorAll('.module-nav-btn');
  buttons.forEach((button) => {
    button.classList.toggle('active', button.dataset.screen === screenName);
  });
}

document.getElementById('logoutBtn')?.addEventListener('click', () => {
  localStorage.removeItem('api_token');
  localStorage.removeItem('companyProfile');
  localStorage.removeItem('companyBrandConfig');
  showLoginModal();
  showMessage('Sessão encerrada. Faça login novamente.', 'success');
});

document.addEventListener('click', async (event) => {
  const moduleButton = event.target.closest('.module-nav-btn');
  if (moduleButton) {
    showScreen(moduleButton.dataset.screen);
    return;
  }

  const textButton = event.target.closest('.text-btn');
  if (textButton) {
    const action = textButton.dataset.action;

    if (action === 'show-relatorios') {
      showScreen('relatorios');
      return;
    }

    if (action === 'show-activity') {
      const activityList = document.getElementById('dashboardActivityList');
      if (activityList) {
        activityList.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
      showMessage('Últimas ações em revisão.', 'success');
      return;
    }
  }

  const sortButton = event.target.closest('.sort-btn');
  if (sortButton) {
    const { kind, key } = sortButton.dataset;
    const state = tableState[kind];
    if (!state) return;

    if (state.sortKey === key) {
      state.sortDirection *= -1;
    } else {
      state.sortKey = key;
      state.sortDirection = 1;
    }

    state.page = 1;
    renderCollection(kind);
    return;
  }

  const pageButton = event.target.closest('.page-btn');
  if (pageButton) {
    const { kind, action } = pageButton.dataset;
    const state = tableState[kind];
    if (!state) return;

    if (action === 'prev') state.page = Math.max(1, state.page - 1);
    if (action === 'next') state.page = state.page + 1;
    renderCollection(kind);
    return;
  }

  const exportButton = event.target.closest('.export-btn');
  if (exportButton) {
    exportToCsv(exportButton.dataset.kind);
    return;
  }

  const target = event.target.closest('.table-action');
  if (!target) return;

  const kind = target.dataset.kind;
  const id = target.dataset.id;

  if (target.classList.contains('edit')) {
    const item = (collectionCache[kind] || []).find((entry) => (entry._id || entry.id) === id);
    if (!item) return;

    const formIdByKind = {
      usuario: 'usuarioForm',
      administrador: 'adminForm',
      funcionario: 'funcionarioForm',
      cliente: 'clienteForm',
      fornecedor: 'fornecedorForm',
      venda: 'vendaForm',
      estoque: 'estoqueForm',
      produto: 'produtoForm',
    };

    const form = document.getElementById(formIdByKind[kind] || 'usuarioForm');
    if (!form) return;
    fillFormForEdit(form, item);
    showScreen(
      kind === 'estoque' ? 'estoque' :
      kind === 'produto' ? 'produtos' :
      kind === 'venda' ? 'vendas' :
      kind === 'funcionario' ? 'funcionarios' :
      kind === 'administrador' ? 'administradores' :
      kind === 'cliente' ? 'clientes' :
      kind === 'fornecedor' ? 'fornecedores' :
      'usuarios'
    );
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    return;
  }

  if (target.classList.contains('delete')) {
    await deleteRecord(kind, id);
  }
});

document.getElementById('applyBrandConfig')?.addEventListener('click', () => {
  const brandConfig = {
    companyName: document.getElementById('companyNameInput')?.value || defaultBrandConfig.companyName,
    companyAcronym: document.getElementById('companyAcronymInput')?.value || defaultBrandConfig.companyAcronym,
    primaryColor: document.getElementById('companyPrimaryColorInput')?.value || defaultBrandConfig.primaryColor,
    secondaryColor: document.getElementById('companySecondaryColorInput')?.value || defaultBrandConfig.secondaryColor,
  };

  applyBrandConfig(brandConfig);
  showMessage('Marca da empresa aplicada com sucesso.', 'success');
});

document.getElementById('empresaForm')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  saveCompanyProfile(form);
  const savedProfile = await persistCompanyProfile({
    ...defaultCompanyProfile,
    ...Object.fromEntries(new FormData(form).entries()),
  });
  if (savedProfile) {
    localStorage.setItem('companyProfile', JSON.stringify(savedProfile));
  }
  showMessage('Dados da empresa salvos com sucesso.', 'success');
  showScreen('dashboard');
});

document.getElementById('logoFileInput')?.addEventListener('change', (event) => {
  const file = event.target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = () => {
    const url = String(reader.result || '');
    const logoUrlInput = document.getElementById('logoUrlInput');
    if (logoUrlInput) {
      logoUrlInput.value = url;
    }

    const profile = getStoredCompanyProfile();
    const updatedProfile = { ...profile, logoUrl: url };
    localStorage.setItem('companyProfile', JSON.stringify(updatedProfile));
    setLogoPreviewFromUrl(url);
  };
  reader.readAsDataURL(file);
});

const logoUrlInput = document.getElementById('logoUrlInput');
logoUrlInput?.addEventListener('input', (event) => {
  const url = event.target.value.trim();
  setLogoPreviewFromUrl(url);
  const profile = getStoredCompanyProfile();
  localStorage.setItem('companyProfile', JSON.stringify({ ...profile, logoUrl: url }));
});

document.querySelector('.refresh-btn')?.addEventListener('click', async () => {
  try {
    await refreshCollections();
    showMessage('Registros atualizados com sucesso.', 'success');
  } catch (error) {
    showMessage(error.message || 'Não foi possível atualizar os registros.', 'error');
  }
});

document.addEventListener('input', (event) => {
  const searchInput = event.target.closest('.table-search');
  if (!searchInput) return;
  tableState[searchInput.dataset.kind].page = 1;
  renderCollection(searchInput.dataset.kind);
});

applyBrandConfig();
renderDashboardActivity();
syncCompanyProfileForm();
loadCompanyProfileFromApi();
showScreen('dashboard');

Object.keys(entityConfig).forEach((kind) => {
  const form = document.getElementById(entityConfig[kind].formId);
  if (!form) return;

  form.addEventListener('submit', submitForm);
  setFormMode(form, 'create');
  if (entityConfig[kind].resetForm) {
    entityConfig[kind].resetForm(form);
  }
});

initializeApp();
