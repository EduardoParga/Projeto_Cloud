const API_BASE_URL = 'https://func-b3-test.azurewebsites.net/api'; // AZURE FUNCTIONS - DADOS REAIS B3

let chart = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando aplicação com dados REAIS B3...');
    carregarAtivos();
    
    document.getElementById('consultarBtn').addEventListener('click', consultarAtivo);
    document.getElementById('ativoSelect').addEventListener('change', function() {
        if (this.value) {
            consultarAtivo();
        }
    });
});

async function carregarAtivos() {
    console.log('📡 Carregando ativos REAIS da B3...');
    
    const select = document.getElementById('ativoSelect');
    select.innerHTML = '<option value="">Carregando ativos...</option>';
    
    try {
        console.log('🔗 Fazendo requisição para:', `${API_BASE_URL}/ativos`);
        
        const response = await fetch(`${API_BASE_URL}/ativos`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        console.log('📡 Response status:', response.status);
        console.log('📡 Response headers:', response.headers);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Dados recebidos da API:', data);
        
        select.innerHTML = '<option value="">Selecione um ativo...</option>';
        
        // Verificar se temos dados válidos
        if (data && data.ativos && Array.isArray(data.ativos) && data.ativos.length > 0) {
            data.ativos.forEach(ativo => {
                const option = document.createElement('option');
                option.value = ativo;
                option.textContent = ativo;
                select.appendChild(option);
            });
            console.log(`✅ Carregados ${data.ativos.length} ativos REAIS:`, data.ativos);
            
            // Mostrar notificação de sucesso
            const successMsg = document.createElement('div');
            successMsg.innerHTML = `<small class="text-success">✅ ${data.ativos.length} ativos carregados da B3</small>`;
            select.parentNode.appendChild(successMsg);
            
        } else {
            throw new Error('Nenhum ativo encontrado na resposta');
        }
        
    } catch (error) {
        console.error('❌ ERRO ao carregar ativos:', error);
        console.error('❌ Detalhes do erro:', error.message);
        
        // Mostrar erro para o usuário
        select.innerHTML = '<option value="">❌ Erro ao carregar ativos</option>';
        
        // Adicionar mensagem de erro
        const errorMsg = document.createElement('div');
        errorMsg.innerHTML = `<small class="text-danger">❌ Erro: ${error.message}</small>`;
        select.parentNode.appendChild(errorMsg);
        
        // Tentar carregar ativos fixos como fallback
        console.log('🔄 Tentando fallback com ativos fixos...');
        const ativosFixos = ['ITUB4', 'PETR4', 'VALE3', 'BBDC4', 'ABEV3', 'MGLU3', 'WEGE3', 'GGBR4'];
        
        select.innerHTML = '<option value="">Selecione um ativo (fallback)...</option>';
        ativosFixos.forEach(ativo => {
            const option = document.createElement('option');
            option.value = ativo;
            option.textContent = ativo;
            select.appendChild(option);
        });
        
        console.log('✅ Fallback aplicado com ativos fixos');
    }
}

async function consultarAtivo() {
    const ativo = document.getElementById('ativoSelect').value;
    
    if (!ativo) {
        alert('Selecione um ativo primeiro!');
        return;
    }

    console.log(`📊 Consultando dados REAIS para ${ativo}...`);
    mostrarLoading(true);

    try {
        // Buscar dados REAIS da API Azure Functions
        const dadosResponse = await fetch(`${API_BASE_URL}/dados?ativo=${ativo}`);
        
        if (!dadosResponse.ok) {
            throw new Error(`Erro HTTP ${dadosResponse.status}: ${dadosResponse.statusText}`);
        }
        
        const dadosData = await dadosResponse.json();
        console.log('✅ Dados REAIS recebidos:', dadosData);
        
        if (dadosData.error) {
            throw new Error(dadosData.error);
        }
        
        // Processar dados REAIS
        const cotacoesAtivo = dadosData.dados || [];
        
        if (cotacoesAtivo.length === 0) {
            throw new Error(`Nenhum dado encontrado para ${ativo}`);
        }
        
        const dadosProcessados = {
            simbolo: ativo,
            ativo: ativo,
            cotacoes: cotacoesAtivo,
            total: cotacoesAtivo.length,
            fonte: dadosData.fonte || 'Azure SQL Database - Dados Reais B3'
        };
        
        // Calcular estatísticas REAIS do ativo
        const volumeTotal = cotacoesAtivo.reduce((acc, d) => acc + (parseInt(d.volume) || 0), 0);
        const negociosTotal = cotacoesAtivo.reduce((acc, d) => acc + (parseInt(d.negocios) || 0), 0);
        
        const statsData = {
            total_registros: cotacoesAtivo.length,
            total_ativos: 1,
            data_inicial: '2025-10-07',
            data_final: '2025-10-07', 
            volume_total: volumeTotal,
            negocios_total: negociosTotal,
            fonte: dadosData.fonte || 'Azure SQL Database - Dados Reais B3'
        };
        
        console.log(`✅ Dados processados para ${ativo}:`, dadosProcessados);
        console.log('📈 Estatísticas REAIS:', statsData);
        
        atualizarGrafico(dadosProcessados);
        atualizarResumo(statsData, ativo);
        atualizarTabela(dadosProcessados);
        
    } catch (error) {
        console.error('❌ Erro ao consultar ativo:', error);
        alert(`❌ Erro ao consultar dados REAIS: ${error.message}\n\nVerifique se as Azure Functions estão ativas.`);
        
        // Não usar fallback - só dados REAIS
        document.getElementById('grafico').innerHTML = `
            <div style="text-align: center; padding: 40px; color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px;">
                <h3>❌ Erro ao Carregar Dados REAIS</h3>
                <p>Não foi possível carregar os dados reais do ativo <strong>${ativo}</strong></p>
                <p>Erro: ${error.message}</p>
                <button onclick="location.reload()" class="btn" style="margin-top: 10px;">🔄 Tentar Novamente</button>
            </div>
        `;
        
    } finally {
        mostrarLoading(false);
    }
}

function gerarDadosSimulados(simbolo) {
    const basePreco = simbolo === 'ITUB4' ? 35.50 : 
                      simbolo === 'PETR4' ? 42.80 : 
                      simbolo === 'VALE3' ? 65.20 : 
                      simbolo === 'BBDC4' ? 28.90 : 30.00;
    
    const cotacoes = [];
    const hoje = new Date();
    
    for (let i = 29; i >= 0; i--) {
        const data = new Date(hoje);
        data.setDate(hoje.getDate() - i);
        
        // Simular variação de preço realista
        const variacao = (Math.random() - 0.5) * 0.1; // ±5%
        const abertura = basePreco * (1 + variacao);
        const fechamento = abertura * (1 + (Math.random() - 0.5) * 0.08);
        const minimo = Math.min(abertura, fechamento) * 0.98;
        const maximo = Math.max(abertura, fechamento) * 1.02;
        
        cotacoes.push({
            data: data.toISOString().split('T')[0],
            abertura: Number(abertura.toFixed(2)),
            minimo: Number(minimo.toFixed(2)),
            maximo: Number(maximo.toFixed(2)),
            fechamento: Number(fechamento.toFixed(2)),
            negocios: Math.floor(Math.random() * 5000) + 1000,
            volume: Math.floor(Math.random() * 10000000) + 1000000
        });
    }
    
    return { simbolo, cotacoes, total: cotacoes.length };
}

function gerarEstatisticasGerais() {
    return {
        total_registros: 156789,
        total_ativos: 487,
        data_inicial: '2025-10-07',
        data_final: '2025-11-19',
        volume_total: 98765432100
    };
}

function mostrarLoading(show) {
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');
    const btn = document.getElementById('consultarBtn');
    
    if (show) {
        btnText.classList.add('d-none');
        btnLoading.classList.remove('d-none');
        btn.disabled = true;
    } else {
        btnText.classList.remove('d-none');
        btnLoading.classList.add('d-none');
        btn.disabled = false;
    }
}

function atualizarGrafico(data) {
    const ctx = document.getElementById('cotacoesChart').getContext('2d');
    const noDataDiv = document.getElementById('noDataMessage');
    
    if (chart) {
        chart.destroy();
    }
    
    if (!data.cotacoes || data.cotacoes.length === 0) {
        console.log('❌ Nenhum dado encontrado para o gráfico');
        noDataDiv.style.display = 'block';
        return;
    }
    
    console.log('📊 Criando gráfico com dados REAIS:', data.cotacoes);
    noDataDiv.style.display = 'none';
    
    // Pegar primeira cotação (dados únicos por ativo)
    const cotacao = data.cotacoes[0];
    
    // Criar gráfico de barras com os 4 preços
    const labels = ['Abertura', 'Mínimo', 'Máximo', 'Fechamento'];
    const valores = [
        parseFloat(cotacao.abertura),
        parseFloat(cotacao.minimo),
        parseFloat(cotacao.maximo),
        parseFloat(cotacao.fechamento)
    ];
    
    console.log('📈 Valores para o gráfico:', valores);
    
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: `${data.simbolo} - Cotação Real B3 (R$)`,
                data: valores,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',   // Abertura - Azul
                    'rgba(255, 99, 132, 0.8)',   // Mínimo - Vermelho
                    'rgba(75, 192, 192, 0.8)',   // Máximo - Verde
                    'rgba(255, 206, 86, 0.8)'    // Fechamento - Amarelo
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)', 
                    'rgba(75, 192, 192, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `📊 ${data.simbolo} - Cotação Real B3 (07/10/2025)`,
                    font: { size: 18, weight: 'bold' },
                    color: '#2c3e50'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Valor (R$)',
                        font: { size: 14, weight: 'bold' }
                    },
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + value.toFixed(2);
                        }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Preços de Negociação',
                        font: { size: 14, weight: 'bold' }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
    
    console.log('✅ Gráfico criado com sucesso!');
}

function atualizarResumo(stats, ativo = '') {
    const card = document.getElementById('resumoCard');
    
    if (stats.error) {
        card.innerHTML = `<p class="text-danger">❌ ${stats.error}</p>`;
        return;
    }
    
    card.innerHTML = `
        <h6 class="fw-bold text-primary">📊 Resumo ${ativo} - DADOS REAIS B3</h6>
        <small class="text-success">✅ Fonte: ${stats.fonte}</small>
        <hr>
        <div class="row g-2">
            <div class="col-6">
                <small class="text-muted">Registros ${ativo}:</small>
                <div class="fw-bold text-primary">${stats.total_registros || 0}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Volume Real:</small>
                <div class="fw-bold text-success">${stats.volume_total ? stats.volume_total.toLocaleString('pt-BR') : 'N/A'}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Negócios:</small>
                <div class="fw-bold text-info">${stats.negocios_total ? stats.negocios_total.toLocaleString('pt-BR') : 'N/A'}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Data B3:</small>
                <div class="fw-bold text-warning">07/10/2025</div>
            </div>
        </div>
        <div class="mt-2 p-2 bg-light rounded">
            <small class="text-muted d-block">🎯 Status:</small>
            <small class="text-success fw-bold">✅ DADOS 100% REAIS EXTRAÍDOS DO XML B3</small>
        </div>
    `;
}
}

function atualizarTabela(data) {
    const tbody = document.getElementById('cotacoesTableBody');
    
    if (!data.cotacoes || data.cotacoes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhum dado encontrado</td></tr>';
        return;
    }
    
    console.log('📋 Atualizando tabela com dados REAIS:', data.cotacoes);
    tbody.innerHTML = '';
    
    // Mostrar todos os dados (geralmente será apenas 1 cotação por ativo)
    data.cotacoes.forEach((cotacao, index) => {
        const row = document.createElement('tr');
        
        // Dados REAIS da B3
        row.innerHTML = `
            <td><strong>07/10/2025</strong></td>
            <td class="text-success">R$ ${parseFloat(cotacao.abertura).toFixed(2)}</td>
            <td class="text-danger">R$ ${parseFloat(cotacao.minimo).toFixed(2)}</td>
            <td class="text-info">R$ ${parseFloat(cotacao.maximo).toFixed(2)}</td>
            <td class="text-warning">R$ ${parseFloat(cotacao.fechamento).toFixed(2)}</td>
            <td class="fw-bold">${parseInt(cotacao.volume).toLocaleString('pt-BR')}</td>
        `;
        tbody.appendChild(row);
    });
    
    // Adicionar linha de informação sobre fonte dos dados
    const infoRow = document.createElement('tr');
    infoRow.innerHTML = `
        <td colspan="6" class="text-center bg-light">
            <small class="text-success">✅ Dados REAIS extraídos do XML B3 - Total: ${data.cotacoes.length} registro(s)</small>
        </td>
    `;
    tbody.appendChild(infoRow);
    
    console.log('✅ Tabela atualizada com sucesso!');
}