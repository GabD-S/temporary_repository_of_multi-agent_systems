#!/usr/bin/env python3
"""
Análise detalhada do código da simulação multi-agente
"""

import ast
import os
from pathlib import Path

def analyze_code_structure():
    """Analisa a estrutura do código fonte"""
    
    files_to_analyze = [
        'enhanced_cloud_storage.py',
        'balanced_test.py', 
        'demo.py',
        'cloud_storage_spade.py'
    ]
    
    analysis = {
        'total_lines': 0,
        'total_functions': 0,
        'total_classes': 0,
        'files': {}
    }
    
    for filename in files_to_analyze:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = len(content.splitlines())
            analysis['total_lines'] += lines
            
            try:
                tree = ast.parse(content)
                
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                
                analysis['total_functions'] += len(functions)
                analysis['total_classes'] += len(classes)
                
                analysis['files'][filename] = {
                    'lines': lines,
                    'functions': len(functions),
                    'classes': len(classes),
                    'function_names': [f.name for f in functions],
                    'class_names': [c.name for c in classes]
                }
                
            except SyntaxError:
                analysis['files'][filename] = {
                    'lines': lines,
                    'error': 'Syntax error in parsing'
                }
    
    return analysis

def generate_code_documentation():
    """Gera documentação detalhada do código"""
    
    analysis = analyze_code_structure()
    
    doc = f"""
# ANÁLISE DETALHADA DO CÓDIGO - SISTEMA MULTI-AGENTE

## Resumo Estatístico
- **Total de linhas de código**: {analysis['total_lines']:,}
- **Total de funções**: {analysis['total_functions']}
- **Total de classes**: {analysis['total_classes']}
- **Arquivos analisados**: {len(analysis['files'])}

## Descrição Detalhada dos Componentes

### 1. enhanced_cloud_storage.py - NÚCLEO DO SISTEMA

Este é o arquivo principal que implementa toda a lógica da simulação multi-agente.

#### Componentes Principais:

**Classes de Dados:**
- `StorageRequest`: Estrutura para requisições de armazenamento
- `StorageContract`: Representa contratos entre compradores e provedores  
- `ProviderInfo`: Informações dos provedores mantidas pela rede

**Classe de Métricas:**
- `SimulationMetrics`: Coleta abrangente de métricas para análise Monte Carlo
  - Métricas de requisições (taxa de sucesso, tempo de resposta)
  - Métricas de contratos (criação, duração, valores)
  - Métricas de provedores (utilização, reputação, ganhos)
  - Métricas de rede (corrupções, latência)

**Sistema de Comunicação:**
- `MessageBus`: Simula comunicação entre agentes com latência realística
  - Implementa delays de rede (50ms-500ms)
  - Suporte a múltiplos mailboxes por agente
  - Contagem de mensagens para análise

**Agentes do Sistema:**

1. **BuyerAgent (Agente Comprador)**
   - Gera requisições periódicas de armazenamento
   - Gerencia orçamento e preferências
   - Avalia propostas dos provedores
   - Implementa comportamento de negociação

2. **StorageProviderAgent (Agente Provedor)**
   - Gerencia capacidade real de armazenamento
   - Implementa preços dinâmicos baseados em utilização
   - Sistema de reputação baseado em performance
   - Simulação de falhas aleatórias
   - Liberação automática de espaço ao fim dos contratos

3. **IntermediaryNetworkAgent (Agente de Rede)**
   - Intermedia comunicação entre compradores e provedores
   - Mantém registro de provedores disponíveis
   - Implementa algoritmos de seleção de provedores
   - Simula corrupção de contratos

#### Funcionalidades Avançadas:

**Gestão de Capacidade Real:**
- Provedores têm espaço finito que é alocado dinamicamente
- Contratos têm duração determinada com liberação automática
- Verificação de disponibilidade em tempo real

**Sistema de Reputação:**
- Reputação baseada em taxa de sucesso histórica
- Influencia na seleção de provedores
- Atualização contínua baseada em performance

**Preços Dinâmicos:**
- Ajuste automático baseado na utilização atual
- Fator de multiplicação quando utilização é alta
- Simulação de mercado dinâmico

**Análise Monte Carlo:**
- Execução de múltiplas iterações com parâmetros variados
- Coleta de estatísticas agregadas
- Geração de relatórios detalhados

### 2. balanced_test.py - TESTE EQUILIBRADO

Implementa um teste focado com parâmetros balanceados:

```python
# Configuração balanceada
providers = 2 (150GB cada, preço base $0.4/GB/h)
buyers = 2 (orçamento $25/h cada)
duração = 15 segundos
```

**Objetivo:** Validar funcionamento básico com parâmetros equilibrados onde oferta e demanda estão balanceadas.

### 3. demo.py - DEMONSTRAÇÃO COMPLETA

Script de demonstração que:
- Mostra todas as funcionalidades do sistema
- Executa análise Monte Carlo completa
- Demonstra diferentes cenários de teste
- Inclui explicações educacionais

**Funcionalidades demonstradas:**
- Capacidade real de armazenamento
- Contratos com duração
- Latência de rede
- Sistema de reputação
- Preços dinâmicos
- Propagação de erros

### 4. cloud_storage_spade.py - VERSÃO SPADE

Implementação alternativa usando o framework SPADE:
- Agentes baseados em XMPP
- Comportamentos síncronos e assíncronos
- Templates de mensagens
- Integração com servidor XMPP

**Diferenças principais:**
- Comunicação real via XMPP vs. MessageBus simulado
- Comportamentos explícitos vs. métodos async
- Maior complexidade de configuração

## Arquitetura do Sistema

### Fluxo de Execução:

1. **Inicialização:**
   - Criação do MessageBus
   - Inicialização dos agentes (rede, provedores, compradores)
   - Configuração de parâmetros iniciais

2. **Operação:**
   - Compradores geram requisições periódicas
   - Rede recebe requisições e consulta provedores
   - Provedores avaliam capacidade e fazem propostas
   - Rede seleciona melhor provedor e cria contratos
   - Contratos são executados com duração determinada
   - Métricas são coletadas continuamente

3. **Finalização:**
   - Parada coordenada de todos os agentes
   - Coleta de métricas finais
   - Geração de relatórios

### Padrões de Design Utilizados:

- **Observer Pattern**: Métricas globais observam eventos dos agentes
- **Mediator Pattern**: Agente de rede medeia comunicação
- **State Pattern**: Contratos têm estados (pending, active, completed, failed)
- **Strategy Pattern**: Diferentes estratégias de seleção de provedores

### Aspectos de Engenharia de Software:

- **Modularidade**: Código bem separado em classes e módulos
- **Testabilidade**: Parâmetros configuráveis facilitam testes
- **Escalabilidade**: Arquitetura suporta muitos agentes
- **Robustez**: Tratamento de erros e timeouts
- **Observabilidade**: Logging detalhado e métricas

## Considerações de Performance

- **Assíncrono**: Uso extensivo de async/await para concorrência
- **Eficiência de Memória**: Estruturas de dados otimizadas
- **Coleta de Métricas**: Mínimo overhead na coleta de dados
- **Simulação de Rede**: Latência controlada via asyncio.sleep()

## Limitações e Melhorias Futuras

**Limitações atuais:**
- Simulação vs. implementação real
- Número limitado de agentes para testes
- Algoritmos de seleção básicos

**Melhorias propostas:**
- Algoritmos de consensus distribuído
- Machine learning para predição
- Integração com blockchain
- Testes de estresse com milhares de agentes
"""
    
    # Adicionar detalhes específicos por arquivo
    for filename, file_info in analysis['files'].items():
        if 'error' not in file_info:
            doc += f"""

### Detalhes do arquivo {filename}:
- **Linhas de código**: {file_info['lines']:,}
- **Funções**: {file_info['functions']} 
- **Classes**: {file_info['classes']}
"""
            if file_info['class_names']:
                doc += f"- **Classes**: {', '.join(file_info['class_names'])}\n"
            
            if file_info['function_names']:
                # Mostrar apenas algumas funções principais para não ser muito verbose
                main_functions = file_info['function_names'][:10]
                doc += f"- **Principais funções**: {', '.join(main_functions)}\n"
                if len(file_info['function_names']) > 10:
                    doc += f"  (e mais {len(file_info['function_names']) - 10} funções)\n"
    
    return doc

if __name__ == "__main__":
    documentation = generate_code_documentation()
    
    with open('CODE_ANALYSIS.md', 'w', encoding='utf-8') as f:
        f.write(documentation)
    
    print("📚 Análise do código salva em: CODE_ANALYSIS.md")
    print(f"📊 {analyze_code_structure()['total_lines']:,} linhas de código analisadas")
