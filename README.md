# Decentralized Cloud Storage Network Simulation

Este projeto implementa uma simulação abrangente de um Sistema Multi-Agente para Armazenamento em Nuvem Descentralizado. A simulação serve como validação preliminar da arquitetura do sistema, analisando comportamento sob diferentes condições, especialmente na presença de falhas.

## 🎯 Objetivos do Projeto

- **Validação de Arquitetura**: Testar viabilidade de sistema descentralizado
- **Análise de Robustez**: Avaliar comportamento com falhas e latência
- **Estudo Econômico**: Analisar dinâmicas de mercado e preços
- **Pesquisa Acadêmica**: Fornecer base para estudos em sistemas distribuídos

## 📋 Características Principais

### Componentes do Sistema

1. **Três Tipos de Agentes:**
   - **Buyer Agents**: Solicitam armazenamento periodicamente
   - **Storage Provider Agents**: Oferecem espaço com preços dinâmicos  
   - **Intermediary Network Agent**: Medeia comunicação e seleção

2. **Funcionalidades Avançadas:**
   - **Capacidade Real**: Provedores têm espaço finito alocado dinamicamente
   - **Contratos Temporários**: Duração determinada com liberação automática
   - **Latência Simulada**: Delays realísticos de rede (50ms-500ms)
   - **Sistema de Reputação**: Avaliação dinâmica de provedores
   - **Preços Dinâmicos**: Ajuste automático baseado em utilização
   - **Análise Monte Carlo**: Validação estatística multi-iteração

3. **Robustez e Falhas:**
   - Falhas aleatórias de provedores (configurável)
   - Corrupção de contratos na rede
   - Timeouts e indisponibilidade
   - Recuperação automática de falhas

4. **Métricas Abrangentes:**
   - Taxa de sucesso/falha de requisições
   - Tempos de resposta com análise estatística
   - Utilização e reputação de provedores
   - Eficiência econômica do sistema
   - Estatísticas de rede e corrupção

## 🚀 Execução Completa com Makefile

### Pré-requisitos

- Python 3.8+
- Make (GNU Make)
- Git
- Opcionalmente: pdflatex para compilação de PDF

### Execução Automática Completa

```bash
# Executa tudo: testes, coleta resultados, gera gráficos e relatório
make all

# Execução rápida (apenas essencial)
make quick

# Ver todas as opções disponíveis
make help
```

### Execução Step-by-Step

```bash
# 1. Configurar ambiente
make setup

# 2. Instalar dependências
make install

# 3. Executar todas as simulações
make run-all

# 4. Coletar e processar resultados
make collect-results

# 5. Gerar gráficos
make generate-graphs

# 6. Criar relatório LaTeX
make create-report

# 7. Compilar PDF (se disponível)
make compile-pdf
```

### Simulações Individuais

```bash
# Simulação principal (recomendado)
make run-enhanced

# Teste balanceado
make run-balanced

# Demonstração completa
make run-demo

# Versão SPADE (requer XMPP)
make run-spade
```

## 📊 Resultados e Análises

Após a execução, os seguintes arquivos são gerados:

### Resultados Brutos
- `results/aggregated_results.json` - Dados consolidados
- `results/*_output.log` - Logs detalhados de cada simulação

### Visualizações
- `results/performance_comparison.png` - Comparação entre simulações
- `results/statistical_analysis.png` - Análise estatística
- `results/economic_analysis.png` - Análise econômica

### Relatórios
- `results/simulation_report.tex` - Relatório LaTeX completo
- `results/report_[timestamp]/` - Pasta com relatório timestamped
- `CODE_ANALYSIS.md` - Análise detalhada do código

## 📈 Interpretação dos Resultados

### Métricas Principais

1. **Taxa de Sucesso**: Porcentagem de requisições atendidas com sucesso
2. **Tempo de Resposta**: Latência média para processamento de requisições
3. **Utilização de Provedores**: Eficiência no uso dos recursos disponíveis
4. **Valor Econômico**: Total de transações financeiras processadas
5. **Robustez**: Capacidade de operação com falhas simuladas

### Análise Estatística

- **Médias e Desvios**: Consistência entre execuções
- **Distribuições**: Padrões de comportamento do sistema
- **Correlações**: Relações entre métricas diferentes
- **Outliers**: Identificação de comportamentos atípicos

## 🔧 Configuração e Personalização

### Parâmetros Principais

```python
# No arquivo enhanced_cloud_storage.py
SIMULATION_CONFIG = {
    'iterations': 3,              # Número de iterações Monte Carlo
    'duration_per_iteration': 30, # Duração de cada simulação (segundos)
    'num_buyers': 2,             # Número de compradores
    'num_providers': 3,          # Número de provedores
    'corruption_probability': 0.02, # Taxa de corrupção da rede
    'failure_probability': 0.05     # Taxa de falha dos provedores
}
```

### Personalização de Agentes

```python
# Configuração de compradores
buyer_config = {
    'request_interval': (3.0, 6.0),  # Intervalo entre requisições
    'budget_per_hour': 25.0,         # Orçamento por hora
    'space_range': (10, 100)         # Faixa de espaço solicitado (GB)
}

# Configuração de provedores  
provider_config = {
    'total_space_gb': 150,           # Capacidade total
    'base_price_per_gb_hour': 0.4,   # Preço base
    'failure_probability': 0.05       # Probabilidade de falha
}
```

## 🧪 Validação e Testes

### Tipos de Teste

1. **Teste Balanceado** (`balanced_test.py`):
   - Parâmetros equilibrados oferta/demanda
   - Validação de funcionamento básico
   - Duração curta para testes rápidos

2. **Demo Completo** (`demo.py`):
   - Demonstração de todas as funcionalidades
   - Explicações educacionais
   - Cenários variados de teste

3. **Simulação Enhanced** (`enhanced_cloud_storage.py`):
   - Análise Monte Carlo completa
   - Métricas abrangentes
   - Configuração avançada

4. **Versão SPADE** (`cloud_storage_spade.py`):
   - Implementação com framework SPADE
   - Comunicação real via XMPP
   - Validação de arquitetura alternativa

### Cenários de Teste

- **Carga Normal**: Operação em condições ideais
- **Alta Demanda**: Teste com muitas requisições simultâneas
- **Falhas de Rede**: Simulação de problemas de conectividade
- **Falhas de Provedores**: Teste de robustez com indisponibilidades
- **Preços Dinâmicos**: Validação de ajustes automáticos de preço

## � Estrutura do Código

### Arquivos Principais

```
SMA_Simulation/
├── enhanced_cloud_storage.py  # Simulação principal
├── balanced_test.py          # Teste balanceado
├── demo.py                   # Demonstração completa
├── cloud_storage_spade.py    # Versão SPADE
├── Makefile                  # Automação completa
├── requirements.txt          # Dependências Python
└── scripts/                  # Scripts de suporte
    ├── collect_results.py    # Coleta de resultados
    ├── generate_graphs.py    # Geração de gráficos
    ├── create_latex_report.py # Relatório LaTeX
    └── analyze_code.py       # Análise de código
```

### Classes Principais

- `BuyerAgent`: Agente comprador de armazenamento
- `StorageProviderAgent`: Agente provedor de armazenamento  
- `IntermediaryNetworkAgent`: Agente mediador de rede
- `SimulationMetrics`: Coleta de métricas estatísticas
- `MessageBus`: Sistema de comunicação entre agentes

## 🔬 Aplicações de Pesquisa

Este sistema pode ser usado para estudar:

- **Sistemas Distribuídos**: Consenso, tolerância a falhas, escalabilidade
- **Economia Digital**: Mercados dinâmicos, formação de preços
- **Sistemas Multi-Agente**: Cooperação, negociação, emergência
- **Redes P2P**: Topologias, roteamento, incentivos
- **Blockchain**: Aplicações descentralizadas, smart contracts

## 📖 Documentação Adicional

### Para Desenvolvedores
- `CODE_ANALYSIS.md`: Análise detalhada da arquitetura
- Comentários inline no código fonte
- Docstrings em todas as funções principais

### Para Pesquisadores
- Relatório LaTeX gerado automaticamente
- Dados em formato JSON para análise externa
- Gráficos em alta resolução para publicações

### Para Usuários
- Este README com instruções completas
- Logs detalhados de execução
- Exemplos de configuração
source .venv/bin/activate
python cloud_storage_spade.py
```

# Run interactive demo
python demo.py

# Run quick test
python balanced_test.py

## 📊 Simulation Results

The simulation generates several output files:

- **`monte_carlo_results_TIMESTAMP.json`**: Detailed raw results data
- **`simulation_report_TIMESTAMP.txt`**: Human-readable summary report
- **Console logs**: Real-time simulation progress and events

### Key Metrics Tracked

1. **Performance Metrics:**
   - Request success rate (%)
   - Average response time (seconds)
   - Standard deviation of response times

2. **System Utilization:**
   - Provider space utilization
   - Contract completion rates
   - Economic efficiency

3. **Robustness Metrics:**
   - Network corruption incidents
   - Provider failure frequency
   - System resilience under stress

4. **Economic Metrics:**
   - Total economic value generated
   - Provider earnings distribution
   - Buyer spending patterns

## 🔧 Configuration

### Simulation Parameters

You can modify the simulation by adjusting parameters in the main function:

```python
asyncio.run(run_monte_carlo_simulation(
    iterations=5,              # Number of Monte Carlo runs
    duration_per_iteration=60, # Seconds per simulation
    num_buyers=3,             # Number of buyer agents
    num_providers=4           # Number of provider agents
))
```

### Agent Configuration

#### Buyer Agents:
- **Request interval**: Time between storage requests (2-8 seconds)
- **Budget**: Maximum spending per hour ($15-40)
- **Storage needs**: 5-50 GB per request
- **Contract duration**: 0.5-6 hours

#### Provider Agents:
- **Total capacity**: 100-300 GB per provider
- **Base pricing**: $0.3-0.9 per GB/hour
- **Failure probability**: 2-12% random failure rate
- **Dynamic pricing**: Adjusts based on utilization (50-200% of base price)

#### Network Agent:
- **Corruption probability**: 3-5% contract corruption rate
- **Provider selection**: Reputation-weighted algorithm
- **Timeout handling**: 30-60 second timeouts

## 📈 Understanding the Results

### Example Output:
```
🎯 SUCCESS RATE:
   Mean: 87.3% ± 4.2%
   Range: 82.1% - 92.5%

⏱️ RESPONSE TIME:
   Mean: 1.45s ± 0.23s
   Range: 1.18s - 1.78s

💾 PROVIDER UTILIZATION:
   Mean: 0.68 ± 0.12
   Range: 0.52 - 0.84

💰 ECONOMIC EFFICIENCY:
   Mean: 94.2% ± 2.1%
   Range: 91.8% - 96.7%
```

### Interpretation:

- **Success Rate > 85%**: Good system reliability
- **Response Time < 2s**: Acceptable performance  
- **Utilization 0.6-0.8**: Efficient resource usage
- **Economic Efficiency > 90%**: Minimal value loss in transactions

## 🔍 Architecture Details

### Communication Flow:
1. **Buyer** → **Network**: Storage request with requirements
2. **Network** → **Provider**: Allocation request (after provider selection)
3. **Provider** → **Network**: Accept/reject response
4. **Network** → **Buyer**: Final contract confirmation

### Provider Selection Algorithm:
- **Reputation weight (40%)**: Historical success rate
- **Price weight (30%)**: Competitive pricing
- **Availability weight (20%)**: Current space availability  
- **Success rate weight (10%)**: Recent performance

### Reputation System:
- **Initial reputation**: 5.0 (neutral)
- **Success**: +2% reputation (max 10.0)
- **Failure**: -2% reputation (min 0.1)
- **Minimum threshold**: 1.0 for consideration