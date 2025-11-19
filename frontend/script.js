const API_BASE_URL = 'https://app-b3-backend123-e2bcc3hrg7c4aggh.westus-01.azurewebsites.net/api'; // AZURE


let chart = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando aplicação...');
    carregarAtivos();
    
    document.getElementById('consultarBtn').addEventListener('click', consultarAtivo);
    document.getElementById('ativoSelect').addEventListener('change', function() {
        if (this.value) {
            consultarAtivo();
        }
    });
});

async function carregarAtivos() {
    console.log('Carregando ativos...');
    try {
        const response = await fetch(`${API_BASE_URL}/ativos`);
        const data = await response.json();
        
        console.log('Ativos recebidos:', data);
        
        const select = document.getElementById('ativoSelect');
        select.innerHTML = '<option value="">Selecione um ativo...</option>';
        
        if (data.ativos && data.ativos.length > 0) {
            data.ativos.forEach(ativo => {
                const option = document.createElement('option');
                option.value = ativo;
                option.textContent = ativo;
                select.appendChild(option);
            });
        } else {
            select.innerHTML = '<option value="">Nenhum ativo encontrado</option>';
        }
    } catch (error) {
        console.error('Erro ao carregar ativos:', error);
        document.getElementById('ativoSelect').innerHTML = '<option value="">Erro ao carregar ativos</option>';
    }
}

async function consultarAtivo() {
    const ativo = document.getElementById('ativoSelect').value;
    const days = document.getElementById('periodSelect').value;
    
    if (!ativo) {
        alert('Selecione um ativo primeiro!');
        return;
    }

    mostrarLoading(true);

    try {
        console.log(`Consultando ativo: ${ativo} - Período: ${days} dias`);
        
        // Carregar cotações e resumo em paralelo
        const [cotacoesResponse, resumoResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/cotacoes/${ativo}?days=${days}`),
            fetch(`${API_BASE_URL}/resumo/${ativo}`)
        ]);
        
        const cotacoesData = await cotacoesResponse.json();
        const resumoData = await resumoResponse.json();
        
        console.log('Dados recebidos:', { cotacoesData, resumoData });
        
        if (cotacoesData.error) {
            throw new Error(cotacoesData.error);
        }
        
        atualizarGrafico(cotacoesData);
        atualizarResumo(resumoData);
        atualizarTabela(cotacoesData);
        
    } catch (error) {
        console.error('Erro ao consultar ativo:', error);
        alert(`Erro ao consultar dados: ${error.message}`);
    } finally {
        mostrarLoading(false);
    }
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
        noDataDiv.style.display = 'block';
        return;
    }
    
    noDataDiv.style.display = 'none';
    
    // Ordenar por data (mais antigo primeiro para o gráfico)
    data.cotacoes.sort((a, b) => new Date(a.data) - new Date(b.data));
    
    const labels = data.cotacoes.map(c => new Date(c.data).toLocaleDateString('pt-BR'));
    const fechamentos = data.cotacoes.map(c => c.fechamento);
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${data.ativo} - Preço de Fechamento`,
                data: fechamentos,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `Cotações de ${data.ativo} - Últimos ${data.cotacoes.length} registros`,
                    font: { size: 16 }
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
                        text: 'Preço (R$)',
                        font: { size: 14 }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Data',
                        font: { size: 14 }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

function atualizarResumo(resumo) {
    const card = document.getElementById('resumoCard');
    
    if (resumo.error) {
        card.innerHTML = `<p class="text-danger">❌ ${resumo.error}</p>`;
        return;
    }
    
    card.innerHTML = `
        <h6 class="fw-bold text-primary">${resumo.ativo}</h6>
        <hr>
        <div class="row g-2">
            <div class="col-6">
                <small class="text-muted">Total Registros:</small>
                <div class="fw-bold">${resumo.total_registros || 0}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Preço Médio:</small>
                <div class="fw-bold text-info">R$ ${resumo.preco_medio ? resumo.preco_medio.toFixed(2) : 'N/A'}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Menor Preço:</small>
                <div class="fw-bold text-success">R$ ${resumo.menor_preco ? resumo.menor_preco.toFixed(2) : 'N/A'}</div>
            </div>
            <div class="col-6">
                <small class="text-muted">Maior Preço:</small>
                <div class="fw-bold text-danger">R$ ${resumo.maior_preco ? resumo.maior_preco.toFixed(2) : 'N/A'}</div>
            </div>
            <div class="col-12">
                <small class="text-muted">Volume Total:</small>
                <div class="fw-bold">${resumo.volume_total ? resumo.volume_total.toLocaleString('pt-BR') : 'N/A'}</div>
            </div>
            <div class="col-12">
                <small class="text-muted">Última Data:</small>
                <div class="fw-bold">${resumo.ultima_data ? new Date(resumo.ultima_data).toLocaleDateString('pt-BR') : 'N/A'}</div>
            </div>
        </div>
    `;
}

function atualizarTabela(data) {
    const tbody = document.getElementById('cotacoesTableBody');
    
    if (!data.cotacoes || data.cotacoes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nenhum dado encontrado</td></tr>';
        return;
    }
    
    // Ordenar por data (mais recente primeiro para a tabela)
    data.cotacoes.sort((a, b) => new Date(b.data) - new Date(a.data));
    
    tbody.innerHTML = '';
    
    data.cotacoes.slice(0, 20).forEach(cotacao => { // Mostrar apenas 20 mais recentes
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(cotacao.data).toLocaleDateString('pt-BR')}</td>
            <td>R$ ${cotacao.abertura ? cotacao.abertura.toFixed(2) : '-'}</td>
            <td>R$ ${cotacao.fechamento ? cotacao.fechamento.toFixed(2) : '-'}</td>
            <td>R$ ${cotacao.minimo ? cotacao.minimo.toFixed(2) : '-'}</td>
            <td>R$ ${cotacao.maximo ? cotacao.maximo.toFixed(2) : '-'}</td>
            <td>${cotacao.volume ? cotacao.volume.toLocaleString('pt-BR') : '-'}</td>
        `;
        tbody.appendChild(row);
    });
    
    if (data.cotacoes.length > 20) {
        const row = document.createElement('tr');
        row.innerHTML = `<td colspan="6" class="text-center text-muted">... e mais ${data.cotacoes.length - 20} registros</td>`;
        tbody.appendChild(row);
    }
}