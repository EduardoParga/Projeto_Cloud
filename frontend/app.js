// B3 Frontend - Dados REAIS
const API_BASE_URL = 'https://func-b3-test.azurewebsites.net/api';
let chart = null;

// Aguardar DOM carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 App B3 Iniciado!');
    init();
});

async function init() {
    try {
        await carregarAtivos();
        setupEventListeners();
    } catch (error) {
        console.error('❌ Erro na inicialização:', error);
    }
}

function setupEventListeners() {
    const consultarBtn = document.getElementById('consultarBtn');
    const ativoSelect = document.getElementById('ativoSelect');
    
    if (consultarBtn) {
        consultarBtn.addEventListener('click', consultarAtivo);
    }
    
    if (ativoSelect) {
        ativoSelect.addEventListener('change', function() {
            if (this.value) {
                consultarAtivo();
            }
        });
    }
}

async function carregarAtivos() {
    console.log('📡 Carregando ativos...');
    
    const select = document.getElementById('ativoSelect');
    if (!select) {
        console.error('❌ Element ativoSelect não encontrado');
        return;
    }
    
    select.innerHTML = '<option value="">⏳ Carregando...</option>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/ativos`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Ativos recebidos:', data);
        
        // Limpar select
        select.innerHTML = '<option value="">Selecione um ativo...</option>';
        
        // Adicionar ativos
        if (data.ativos && Array.isArray(data.ativos)) {
            data.ativos.forEach(ativo => {
                const option = document.createElement('option');
                option.value = ativo;
                option.textContent = ativo;
                select.appendChild(option);
            });
            
            console.log(`✅ ${data.ativos.length} ativos carregados!`);
            
            // Adicionar feedback visual
            const container = select.parentNode;
            let feedback = container.querySelector('.loading-feedback');
            if (feedback) feedback.remove();
            
            feedback = document.createElement('small');
            feedback.className = 'loading-feedback text-success';
            feedback.innerHTML = `✅ ${data.ativos.length} ativos carregados da B3`;
            container.appendChild(feedback);
            
        } else {
            throw new Error('Dados inválidos recebidos');
        }
        
    } catch (error) {
        console.error('❌ Erro:', error);
        
        select.innerHTML = '<option value="">❌ Erro ao carregar</option>';
        
        // Fallback com ativos conhecidos
        const ativos = ['ABEV3', 'BBDC4', 'GGBR4', 'ITUB4', 'MGLU3', 'PETR4', 'VALE3', 'WEGE3'];
        ativos.forEach(ativo => {
            const option = document.createElement('option');
            option.value = ativo;
            option.textContent = ativo + ' (cache)';
            select.appendChild(option);
        });
        
        console.log('🔄 Fallback aplicado');
    }
}

async function consultarAtivo() {
    const ativo = document.getElementById('ativoSelect').value;
    
    if (!ativo) {
        alert('Selecione um ativo primeiro!');
        return;
    }
    
    console.log(`📊 Consultando ${ativo}...`);
    mostrarLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/dados?ativo=${ativo}`);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Dados recebidos:', data);
        
        if (data.status === 'success' && data.ativo) {
            // Converter para o formato esperado pela interface
            atualizarInterface({
                simbolo: data.ativo,
                cotacoes: [{
                    simbolo: data.ativo,
                    preco_abertura: data.preco_abertura,
                    preco_maximo: data.preco_maximo,
                    preco_minimo: data.preco_minimo,
                    preco_fechamento: data.preco_fechamento,
                    volume: data.volume,
                    data_negociacao: data.data_negociacao,
                    variacao_percentual: data.variacao_percentual
                }],
                total: 1,
                fonte: data.fonte
            });
        } else {
            throw new Error(data.error || 'Nenhum dado retornado');
        }
        
    } catch (error) {
        console.error('❌ Erro:', error);
        alert(`Erro ao buscar dados para ${ativo}: ${error.message}`);
    } finally {
        mostrarLoading(false);
    }
}

function atualizarInterface(data) {
    console.log('🔄 Atualizando interface:', data);
    
    // Atualizar resumo
    atualizarResumo(data);
    
    // Atualizar gráfico
    atualizarGrafico(data);
    
    // Atualizar tabela
    atualizarTabela(data);
}

function atualizarResumo(data) {
    const card = document.getElementById('resumoCard');
    if (!card) return;
    
    const cotacao = data.cotacoes[0];
    
    card.innerHTML = `
        <h6 class="fw-bold text-primary">📊 ${data.simbolo} - DADOS B3</h6>
        <small class="text-success">✅ Fonte: ${data.fonte || 'Azure Functions'}</small>
        <hr>
        <div class="row g-2">
            <div class="col-6">
                <small class="text-muted">Abertura:</small>
                <div class="fw-bold">R$ ${cotacao.preco_abertura}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Fechamento:</small>
                <div class="fw-bold">R$ ${cotacao.preco_fechamento}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Máxima:</small>
                <div class="fw-bold text-success">R$ ${cotacao.preco_maximo}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Mínima:</small>
                <div class="fw-bold text-danger">R$ ${cotacao.preco_minimo}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Volume:</small>
                <div class="fw-bold text-info">${parseInt(cotacao.volume).toLocaleString('pt-BR')}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Variação:</small>
                <div class="fw-bold ${cotacao.variacao_percentual >= 0 ? 'text-success' : 'text-danger'}">
                    ${cotacao.variacao_percentual >= 0 ? '+' : ''}${cotacao.variacao_percentual}%
                </div>
            </div>
        </div>
        <div class="mt-2 p-2 bg-light rounded">
            <small class="text-muted">Data: ${cotacao.data_negociacao}</small>
        </div>
    `;
}

function atualizarGrafico(data) {
    const ctx = document.getElementById('cotacoesChart');
    if (!ctx) return;
    
    const context = ctx.getContext('2d');
    
    if (chart) {
        chart.destroy();
    }
    
    const cotacao = data.cotacoes[0];
    
    chart = new Chart(context, {
        type: 'bar',
        data: {
            labels: ['Abertura', 'Mínimo', 'Máximo', 'Fechamento'],
            datasets: [{
                label: `${data.simbolo} - Cotação (R$)`,
                data: [
                    parseFloat(cotacao.preco_abertura),
                    parseFloat(cotacao.preco_minimo),
                    parseFloat(cotacao.preco_maximo),
                    parseFloat(cotacao.preco_fechamento)
                ],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(255, 206, 86, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `📊 ${data.simbolo} - Cotação Real B3`,
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
    
    // Esconder mensagem "sem dados"
    const noDataDiv = document.getElementById('noDataMessage');
    if (noDataDiv) {
        noDataDiv.style.display = 'none';
    }
}

function atualizarTabela(data) {
    const tbody = document.getElementById('cotacoesTableBody');
    if (!tbody) return;
    
    const cotacao = data.cotacoes[0];
    
    tbody.innerHTML = `
        <tr>
            <td><strong>${cotacao.data_negociacao}</strong></td>
            <td class="text-success">R$ ${parseFloat(cotacao.preco_abertura).toFixed(2)}</td>
            <td class="text-danger">R$ ${parseFloat(cotacao.preco_minimo).toFixed(2)}</td>
            <td class="text-info">R$ ${parseFloat(cotacao.preco_maximo).toFixed(2)}</td>
            <td class="text-warning">R$ ${parseFloat(cotacao.preco_fechamento).toFixed(2)}</td>
            <td class="fw-bold">${parseInt(cotacao.volume).toLocaleString('pt-BR')}</td>
        </tr>
        <tr>
            <td colspan="6" class="text-center bg-light">
                <small class="text-muted">Fonte: ${data.fonte || 'Azure Functions'}</small>
            </td>
        </tr>
    `;
}

function mostrarLoading(show) {
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');
    const btn = document.getElementById('consultarBtn');
    
    if (show) {
        if (btnText) btnText.classList.add('d-none');
        if (btnLoading) btnLoading.classList.remove('d-none');
        if (btn) btn.disabled = true;
    } else {
        if (btnText) btnText.classList.remove('d-none');
        if (btnLoading) btnLoading.classList.add('d-none');
        if (btn) btn.disabled = false;
    }
}

console.log('✅ Script carregado!');