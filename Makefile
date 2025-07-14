# Makefile para Simulação Multi-Agente de Armazenamento em Nuvem
# Executa todos os testes, coleta resultados e gera relatórios completos

# Configurações
PYTHON = python3
VENV_DIR = .venv
RESULTS_DIR = results
TIMESTAMP = $(shell date +%Y%m%d_%H%M%S)
REPORT_DIR = $(RESULTS_DIR)/report_$(TIMESTAMP)

# Scripts de simulação
SIMULATIONS = enhanced_cloud_storage.py demo.py balanced_test.py cloud_storage_spade.py

# Arquivos de resultado
RESULT_FILES = $(RESULTS_DIR)/enhanced_results.json \
               $(RESULTS_DIR)/demo_results.json \
               $(RESULTS_DIR)/balanced_results.json \
               $(RESULTS_DIR)/spade_results.json

# Arquivos de gráficos
GRAPH_FILES = $(RESULTS_DIR)/performance_graphs.png \
              $(RESULTS_DIR)/comparison_graphs.png \
              $(RESULTS_DIR)/statistical_analysis.png

.PHONY: all setup install run-all run-enhanced run-demo run-balanced run-spade \
        collect-results generate-graphs create-report clean help

# Target principal - executa tudo
all: setup install run-all collect-results generate-graphs create-report
	@echo "🎉 Simulação completa finalizada!"
	@echo "📁 Resultados disponíveis em: $(REPORT_DIR)"
	@echo "📄 Relatório LaTeX: $(REPORT_DIR)/simulation_report.tex"
	@echo "📊 Gráficos: $(RESULTS_DIR)/"

# Configuração do ambiente
setup:
	@echo "🔧 Configurando ambiente..."
	@mkdir -p $(RESULTS_DIR)
	@mkdir -p $(REPORT_DIR)
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "📦 Criando ambiente virtual..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi

# Instalação de dependências
install: setup
	@echo "📥 Instalando dependências..."
	@$(VENV_DIR)/bin/pip install --upgrade pip
	@$(VENV_DIR)/bin/pip install -r requirements.txt
	@$(VENV_DIR)/bin/pip install matplotlib seaborn pandas numpy scipy
	@$(VENV_DIR)/bin/pip install jinja2 # Para geração de relatórios

# Executa todas as simulações
run-all: run-enhanced run-demo run-balanced run-spade
	@echo "✅ Todas as simulações concluídas!"

# Simulação enhanced (principal)
run-enhanced:
	@echo "🚀 Executando simulação enhanced..."
	@$(VENV_DIR)/bin/python enhanced_cloud_storage.py > $(RESULTS_DIR)/enhanced_output.log 2>&1
	@echo "✅ Simulação enhanced concluída"

# Simulação demo
run-demo:
	@echo "🎬 Executando demo..."
	@$(VENV_DIR)/bin/python demo.py > $(RESULTS_DIR)/demo_output.log 2>&1
	@echo "✅ Demo concluído"

# Teste balanceado
run-balanced:
	@echo "⚖️ Executando teste balanceado..."
	@$(VENV_DIR)/bin/python balanced_test.py > $(RESULTS_DIR)/balanced_output.log 2>&1
	@echo "✅ Teste balanceado concluído"

# Simulação SPADE (pode falhar se não tiver XMPP)
run-spade:
	@echo "🌐 Tentando executar simulação SPADE..."
	@timeout 60 $(VENV_DIR)/bin/python cloud_storage_spade.py > $(RESULTS_DIR)/spade_output.log 2>&1 || \
		echo "⚠️ Simulação SPADE não concluída (normal se não houver servidor XMPP)"

# Coleta e processa resultados
collect-results:
	@echo "📊 Coletando resultados..."
	@$(VENV_DIR)/bin/python scripts/collect_results.py

# Gera gráficos
generate-graphs: collect-results
	@echo "📈 Gerando gráficos..."
	@$(VENV_DIR)/bin/python scripts/generate_graphs.py

# Cria relatório final em LaTeX
create-report: generate-graphs
	@echo "📝 Criando relatório LaTeX..."
	@$(VENV_DIR)/bin/python scripts/create_latex_report.py
	@cp $(RESULTS_DIR)/simulation_report.tex $(REPORT_DIR)/
	@cp -r $(RESULTS_DIR)/*.png $(REPORT_DIR)/ 2>/dev/null || true
	@echo "📄 Relatório criado: $(REPORT_DIR)/simulation_report.tex"

# Compila PDF do relatório (se pdflatex estiver disponível)
compile-pdf: create-report
	@echo "🔧 Tentando compilar PDF..."
	@if command -v pdflatex >/dev/null 2>&1; then \
		cd $(REPORT_DIR) && pdflatex simulation_report.tex; \
		echo "📄 PDF gerado: $(REPORT_DIR)/simulation_report.pdf"; \
	else \
		echo "⚠️ pdflatex não encontrado. Instale TeXLive para gerar PDF."; \
	fi

# Limpeza
clean:
	@echo "🧹 Limpando arquivos temporários..."
	@rm -rf $(RESULTS_DIR)
	@rm -rf __pycache__
	@rm -rf *.pyc
	@find . -name "*.log" -delete
	@echo "✅ Limpeza concluída"

# Limpeza completa (incluindo venv)
clean-all: clean
	@echo "🧹 Limpeza completa..."
	@rm -rf $(VENV_DIR)
	@echo "✅ Limpeza completa concluída"

# Execução rápida (apenas testes essenciais)
quick: setup install run-enhanced run-balanced collect-results
	@echo "⚡ Execução rápida concluída!"

# Ajuda
help:
	@echo "🆘 Comandos disponíveis:"
	@echo "  make all          - Executa simulação completa"
	@echo "  make quick        - Execução rápida (essencial)"
	@echo "  make setup        - Configura ambiente"
	@echo "  make install      - Instala dependências"
	@echo "  make run-all      - Executa todas as simulações"
	@echo "  make run-enhanced - Executa simulação principal"
	@echo "  make run-demo     - Executa demo"
	@echo "  make run-balanced - Executa teste balanceado"
	@echo "  make run-spade    - Executa simulação SPADE"
	@echo "  make collect-results - Coleta resultados"
	@echo "  make generate-graphs - Gera gráficos"
	@echo "  make create-report   - Cria relatório LaTeX"
	@echo "  make compile-pdf     - Compila PDF (requer pdflatex)"
	@echo "  make clean        - Remove arquivos temporários"
	@echo "  make clean-all    - Limpeza completa"
	@echo "  make help         - Mostra esta ajuda"

# Target padrão
.DEFAULT_GOAL := help
