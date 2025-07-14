#!/usr/bin/env python3
"""
Script para gerar gráficos e visualizações dos resultados das simulações
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
import os

# Configuração do estilo
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_results():
    """Carrega os resultados agregados"""
    results_file = "results/aggregated_results.json"
    if not os.path.exists(results_file):
        print("⚠️ Arquivo de resultados não encontrado. Execute collect_results.py primeiro.")
        return None
    
    with open(results_file, 'r') as f:
        return json.load(f)

def create_performance_comparison_chart(results):
    """Cria gráfico de comparação de performance entre simulações"""
    simulations = results['individual_simulations']
    
    # Preparar dados
    sim_names = []
    success_rates = []
    response_times = []
    utilizations = []
    
    for name, data in simulations.items():
        if data:  # Se tem dados
            sim_names.append(name.capitalize())
            success_rates.append(data.get('success_rate', 0))
            response_times.append(data.get('avg_response_time', 0))
            utilizations.append(data.get('provider_utilization', 0))
    
    # Criar figura com subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Comparação de Performance entre Simulações', fontsize=16, fontweight='bold')
    
    # Taxa de Sucesso
    axes[0, 0].bar(sim_names, success_rates, color='green', alpha=0.7)
    axes[0, 0].set_title('Taxa de Sucesso (%)')
    axes[0, 0].set_ylabel('Percentage')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Tempo de Resposta
    axes[0, 1].bar(sim_names, response_times, color='blue', alpha=0.7)
    axes[0, 1].set_title('Tempo de Resposta Médio (s)')
    axes[0, 1].set_ylabel('Seconds')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # Utilização dos Provedores
    axes[1, 0].bar(sim_names, utilizations, color='orange', alpha=0.7)
    axes[1, 0].set_title('Utilização dos Provedores')
    axes[1, 0].set_ylabel('Utilization Ratio')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Resumo Comparativo
    metrics = ['Success Rate', 'Response Time', 'Utilization']
    data_matrix = np.array([success_rates, response_times, utilizations]).T
    
    # Normalizar dados para comparação
    data_normalized = (data_matrix - data_matrix.min(axis=0)) / (data_matrix.max(axis=0) - data_matrix.min(axis=0))
    
    im = axes[1, 1].imshow(data_normalized, cmap='viridis', aspect='auto')
    axes[1, 1].set_xticks(range(len(metrics)))
    axes[1, 1].set_xticklabels(metrics)
    axes[1, 1].set_yticks(range(len(sim_names)))
    axes[1, 1].set_yticklabels(sim_names)
    axes[1, 1].set_title('Heatmap Normalizado de Métricas')
    
    # Adicionar colorbar
    plt.colorbar(im, ax=axes[1, 1])
    
    plt.tight_layout()
    plt.savefig('results/performance_comparison.png', dpi=300, bbox_inches='tight')
    print("📊 Gráfico de comparação salvo: results/performance_comparison.png")

def create_statistical_analysis_chart(results):
    """Cria gráficos de análise estatística"""
    stats = results['aggregated_statistics']
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análise Estatística das Simulações', fontsize=16, fontweight='bold')
    
    # Box plot de métricas
    metrics_data = []
    metrics_labels = []
    
    for metric_name in ['success_rate', 'response_time', 'utilization']:
        if metric_name in stats:
            metric_stats = stats[metric_name]
            # Simular distribuição baseada nas estatísticas
            mean = metric_stats['mean']
            std = metric_stats['std']
            simulated_data = np.random.normal(mean, std, 100) if std > 0 else [mean] * 100
            metrics_data.append(simulated_data)
            metrics_labels.append(metric_name.replace('_', ' ').title())
    
    axes[0, 0].boxplot(metrics_data, labels=metrics_labels)
    axes[0, 0].set_title('Distribuição das Métricas')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Barras de erro
    means = [stats[m]['mean'] for m in ['success_rate', 'response_time', 'utilization'] if m in stats]
    stds = [stats[m]['std'] for m in ['success_rate', 'response_time', 'utilization'] if m in stats]
    
    x_pos = np.arange(len(metrics_labels))
    axes[0, 1].bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7)
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(metrics_labels, rotation=45)
    axes[0, 1].set_title('Médias com Desvio Padrão')
    
    # Distribuição de ganhos
    if 'earnings' in stats:
        earnings_stats = stats['earnings']
        earnings_data = np.random.gamma(2, earnings_stats['mean']/2, 100) if earnings_stats['mean'] > 0 else [0] * 100
        axes[1, 0].hist(earnings_data, bins=20, alpha=0.7, color='green')
        axes[1, 0].set_title('Distribuição de Ganhos Econômicos')
        axes[1, 0].set_xlabel('Earnings ($)')
        axes[1, 0].set_ylabel('Frequency')
    
    # Radar chart das métricas
    categories = []
    values = []
    
    for metric in ['success_rate', 'response_time', 'utilization']:
        if metric in stats and stats[metric]['mean'] > 0:
            categories.append(metric.replace('_', ' ').title())
            # Normalizar valores para o radar (0-1)
            if metric == 'response_time':
                # Para tempo de resposta, menor é melhor
                values.append(1 / (1 + stats[metric]['mean']))
            else:
                values.append(stats[metric]['mean'] / 100 if stats[metric]['mean'] <= 100 else stats[metric]['mean'] / max(stats[metric]['mean'], 1))
    
    if categories:
        # Fechar o polígono
        categories += [categories[0]]
        values += [values[0]]
        
        angles = np.linspace(0, 2 * np.pi, len(categories))
        
        axes[1, 1].plot(angles, values, 'o-', linewidth=2)
        axes[1, 1].fill(angles, values, alpha=0.25)
        axes[1, 1].set_xticks(angles[:-1])
        axes[1, 1].set_xticklabels(categories[:-1])
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].set_title('Radar de Performance Normalizada')
        axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('results/statistical_analysis.png', dpi=300, bbox_inches='tight')
    print("📈 Gráfico de análise estatística salvo: results/statistical_analysis.png")

def create_economic_analysis_chart(results):
    """Cria gráficos de análise econômica"""
    simulations = results['individual_simulations']
    
    # Extrair dados econômicos
    sim_names = []
    earnings = []
    utilizations = []
    efficiency = []
    
    for name, data in simulations.items():
        if data and 'total_earnings' in data and 'provider_utilization' in data:
            sim_names.append(name.capitalize())
            earnings.append(data['total_earnings'])
            utilizations.append(data['provider_utilization'])
            # Eficiência como ganhos por unidade de utilização
            eff = data['total_earnings'] / max(data['provider_utilization'], 0.01)
            efficiency.append(eff)
    
    if not sim_names:
        print("⚠️ Dados econômicos insuficientes para gráficos")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Análise Econômica das Simulações', fontsize=16, fontweight='bold')
    
    # Ganhos por simulação
    bars1 = axes[0, 0].bar(sim_names, earnings, color='darkgreen', alpha=0.7)
    axes[0, 0].set_title('Ganhos Totais por Simulação')
    axes[0, 0].set_ylabel('Earnings ($)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars1, earnings):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(earnings)*0.01,
                       f'${value:.2f}', ha='center', va='bottom')
    
    # Relação Utilização vs Ganhos
    if len(utilizations) > 1:
        axes[0, 1].scatter(utilizations, earnings, s=100, alpha=0.7)
        for i, name in enumerate(sim_names):
            axes[0, 1].annotate(name, (utilizations[i], earnings[i]), 
                               xytext=(5, 5), textcoords='offset points')
        
        # Linha de tendência
        if len(utilizations) > 2:
            z = np.polyfit(utilizations, earnings, 1)
            p = np.poly1d(z)
            axes[0, 1].plot(utilizations, p(utilizations), "r--", alpha=0.8)
        
        axes[0, 1].set_xlabel('Provider Utilization')
        axes[0, 1].set_ylabel('Total Earnings ($)')
        axes[0, 1].set_title('Correlação Utilização vs Ganhos')
    
    # Eficiência econômica
    bars2 = axes[1, 0].bar(sim_names, efficiency, color='gold', alpha=0.7)
    axes[1, 0].set_title('Eficiência Econômica ($/Utilização)')
    axes[1, 0].set_ylabel('Efficiency ($/unit)')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Adicionar valores nas barras
    for bar, value in zip(bars2, efficiency):
        axes[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(efficiency)*0.01,
                       f'${value:.2f}', ha='center', va='bottom')
    
    # Comparativo multi-métrica
    metrics_df = pd.DataFrame({
        'Simulation': sim_names,
        'Earnings': earnings,
        'Utilization': utilizations,
        'Efficiency': efficiency
    })
    
    # Normalizar para comparação visual
    metrics_norm = metrics_df.copy()
    for col in ['Earnings', 'Utilization', 'Efficiency']:
        metrics_norm[col] = (metrics_norm[col] - metrics_norm[col].min()) / (metrics_norm[col].max() - metrics_norm[col].min())
    
    x = np.arange(len(sim_names))
    width = 0.25
    
    axes[1, 1].bar(x - width, metrics_norm['Earnings'], width, label='Earnings (norm)', alpha=0.8)
    axes[1, 1].bar(x, metrics_norm['Utilization'], width, label='Utilization (norm)', alpha=0.8)
    axes[1, 1].bar(x + width, metrics_norm['Efficiency'], width, label='Efficiency (norm)', alpha=0.8)
    
    axes[1, 1].set_xlabel('Simulações')
    axes[1, 1].set_ylabel('Valores Normalizados')
    axes[1, 1].set_title('Comparativo de Métricas Econômicas')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(sim_names, rotation=45)
    axes[1, 1].legend()
    
    plt.tight_layout()
    plt.savefig('results/economic_analysis.png', dpi=300, bbox_inches='tight')
    print("💰 Gráfico de análise econômica salvo: results/economic_analysis.png")

def generate_all_graphs():
    """Gera todos os gráficos"""
    print("📈 Gerando gráficos das simulações...")
    
    # Carregar resultados
    results = load_results()
    if not results:
        return
    
    # Criar diretório de resultados se não existir
    os.makedirs('results', exist_ok=True)
    
    # Gerar gráficos
    try:
        create_performance_comparison_chart(results)
        create_statistical_analysis_chart(results)
        create_economic_analysis_chart(results)
        
        print("✅ Todos os gráficos foram gerados com sucesso!")
        print("📁 Gráficos salvos em: results/")
        
    except Exception as e:
        print(f"❌ Erro ao gerar gráficos: {e}")

if __name__ == "__main__":
    generate_all_graphs()
