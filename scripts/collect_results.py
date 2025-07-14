#!/usr/bin/env python3
"""
Script para coletar e processar resultados de todas as simulações
"""

import json
import os
import re
import statistics
from datetime import datetime
from pathlib import Path

def parse_log_file(log_file):
    """Extrai métricas dos arquivos de log"""
    if not os.path.exists(log_file):
        return {}
    
    with open(log_file, 'r') as f:
        content = f.read()
    
    results = {}
    
    # Padrões para extrair métricas
    patterns = {
        'requests_total': r'Requests:\s*(\d+)',
        'success_rate': r'Success Rate:\s*([\d.]+)%',
        'avg_response_time': r'Avg Response Time:\s*([\d.]+)s',
        'contracts_created': r'Contracts Created:\s*(\d+)',
        'provider_utilization': r'Provider Utilization:\s*([\d.]+)',
        'total_earnings': r'Total Earnings:\s*\$?([\d.]+)',
        'network_corruptions': r'Network Corruptions:\s*(\d+)',
        'simulation_duration': r'Simulation completed in\s*([\d.]+)\s*seconds'
    }
    
    for metric, pattern in patterns.items():
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            try:
                results[metric] = float(match.group(1))
            except ValueError:
                results[metric] = match.group(1)
    
    return results

def collect_json_results():
    """Coleta resultados de arquivos JSON gerados pelas simulações"""
    json_files = [
        'enhanced_cloud_storage_results.json',
        'monte_carlo_results.json',
        'simulation_summary.json'
    ]
    
    json_results = {}
    
    for json_file in json_files:
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    json_results[json_file] = data
            except json.JSONDecodeError:
                print(f"⚠️ Erro ao ler {json_file}")
    
    return json_results

def aggregate_results():
    """Agrega todos os resultados das simulações"""
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    
    # Coleta resultados dos logs
    log_results = {
        'enhanced': parse_log_file(f"{results_dir}/enhanced_output.log"),
        'demo': parse_log_file(f"{results_dir}/demo_output.log"),
        'balanced': parse_log_file(f"{results_dir}/balanced_output.log"),
        'spade': parse_log_file(f"{results_dir}/spade_output.log")
    }
    
    # Coleta resultados JSON
    json_results = collect_json_results()
    
    # Calcula estatísticas agregadas
    all_success_rates = []
    all_response_times = []
    all_utilizations = []
    all_earnings = []
    
    for sim_name, sim_results in log_results.items():
        if 'success_rate' in sim_results:
            all_success_rates.append(sim_results['success_rate'])
        if 'avg_response_time' in sim_results:
            all_response_times.append(sim_results['avg_response_time'])
        if 'provider_utilization' in sim_results:
            all_utilizations.append(sim_results['provider_utilization'])
        if 'total_earnings' in sim_results:
            all_earnings.append(sim_results['total_earnings'])
    
    # Estatísticas agregadas
    aggregated_stats = {
        'success_rate': {
            'mean': statistics.mean(all_success_rates) if all_success_rates else 0,
            'std': statistics.stdev(all_success_rates) if len(all_success_rates) > 1 else 0,
            'min': min(all_success_rates) if all_success_rates else 0,
            'max': max(all_success_rates) if all_success_rates else 0
        },
        'response_time': {
            'mean': statistics.mean(all_response_times) if all_response_times else 0,
            'std': statistics.stdev(all_response_times) if len(all_response_times) > 1 else 0,
            'min': min(all_response_times) if all_response_times else 0,
            'max': max(all_response_times) if all_response_times else 0
        },
        'utilization': {
            'mean': statistics.mean(all_utilizations) if all_utilizations else 0,
            'std': statistics.stdev(all_utilizations) if len(all_utilizations) > 1 else 0,
            'min': min(all_utilizations) if all_utilizations else 0,
            'max': max(all_utilizations) if all_utilizations else 0
        },
        'earnings': {
            'total': sum(all_earnings) if all_earnings else 0,
            'mean': statistics.mean(all_earnings) if all_earnings else 0,
            'std': statistics.stdev(all_earnings) if len(all_earnings) > 1 else 0
        }
    }
    
    # Resultado final
    final_results = {
        'collection_timestamp': datetime.now().isoformat(),
        'individual_simulations': log_results,
        'json_results': json_results,
        'aggregated_statistics': aggregated_stats,
        'summary': {
            'total_simulations': len([r for r in log_results.values() if r]),
            'successful_simulations': len([r for r in log_results.values() if r and 'success_rate' in r]),
            'avg_success_rate': aggregated_stats['success_rate']['mean'],
            'avg_response_time': aggregated_stats['response_time']['mean'],
            'total_economic_value': aggregated_stats['earnings']['total']
        }
    }
    
    # Salva resultados agregados
    output_file = f"{results_dir}/aggregated_results.json"
    with open(output_file, 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"📊 Resultados coletados e salvos em: {output_file}")
    print(f"✅ {final_results['summary']['successful_simulations']} simulações processadas com sucesso")
    print(f"📈 Taxa de sucesso média: {final_results['summary']['avg_success_rate']:.2f}%")
    print(f"⏱️ Tempo de resposta médio: {final_results['summary']['avg_response_time']:.3f}s")
    print(f"💰 Valor econômico total: ${final_results['summary']['total_economic_value']:.2f}")
    
    return final_results

if __name__ == "__main__":
    results = aggregate_results()
