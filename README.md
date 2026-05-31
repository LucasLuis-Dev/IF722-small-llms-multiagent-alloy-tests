# IF722 – Small LLMs with Multi-Agent Post-Processing for Alloy Test Generation

> Projeto da disciplina IF722 – Engenharia de Software Baseada em Evidências  
> Universidade Federal de Pernambuco (UFPE)  
> Forked from [haslab/Alloy-LLM-Testing](https://github.com/haslab/Alloy-LLM-Testing)

## Resumo

Este projeto estende o trabalho "Validating Formal Specifications with LLM-generated Test Cases" (FM26) ao investigar se modelos de linguagem menores e mais baratos — especificamente o **Gemini 2.5 Flash** — conseguem gerar casos de teste Alloy com qualidade comparável ao GPT-5, quando assistidos por um pipeline **multi-agente com pós-processamento sintático**.

## Escopo

O artigo base demonstrou que LLMs grandes (GPT-5) geram test cases Alloy com até 96% de validade usando few-shot prompting. Este projeto questiona: **é possível obter resultados similares com modelos menores e mais baratos, adicionando um agente de correção sintática automática?**

## Perguntas de Pesquisa

- **RQ1:** O pós-processamento sintático reduz significativamente os erros de sintaxe gerados pelo Gemini 2.5 Flash?
- **RQ2:** Com pós-processamento, o Gemini 2.5 Flash consegue detectar especificações incorretas em nível similar ao GPT-5?
- **RQ3:** Qual é a relação custo-benefício entre usar GPT-5 direto vs Gemini 2.5 Flash + pós-processamento?

## Arquitetura Multi-Agente

```
NL Requirement
│
▼
┌─────────────────┐
│    Agent 1      │ → Calls Gemini 2.5 Flash and generates draft Alloy test cases
│   Generator     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Agent 2      │ → Applies syntax correction rules (scope, run, none, etc.)
│ Post-Processor  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Agent 3      │ → Runs Alloy Analyzer, collects metrics and decides retry
│   Validator     │
└─────────────────┘
```

## Estrutura do Repositório

```
├── README.md
├── SCOPE.md
├── docs/
│   ├── Relatorio_Final.md     # Relatório detalhado do projeto
│   ├── Apresentacao.md        # Roteiro slide-a-slide da apresentação
│   └── images/                # Imagens dos resultados
├── src/
│   ├── agents/
│   │   ├── agent_generator.py      # Agente 1: geração via Gemini 2.5 Flash
│   │   ├── agent_postprocessor.py  # Agente 2: correção sintática
│   │   └── agent_validator.py      # Agente 3: validação com Alloy Analyzer
│   ├── pipeline.py                 # Orquestrador dos 3 agentes
│   └── config.py                   # Configurações gerais
├── prompts/
│   └── prompt_few_gemini.txt       # Prompt few-shot adaptado para Gemini
├── data/
│   ├── inputs/                     # Requisitos e modelos Alloy do benchmark
│   ├── raw/                        # Saídas brutas do Gemini
│   └── processed/                  # Métricas processadas
├── analysis/                       # Scripts de análise herdados do artigo
├── execute/                        # Scripts de execução herdados do artigo
├── prepare/                        # Scripts de preparação herdados do artigo
├── Dockerfile
├── requirements.txt
└── alloytools.jar
```

## Resultados

O experimento foi executado avaliando o modelo **Gemini 2.5 Flash** (com e sem o pipeline multi-agente de pós-processamento) em comparação ao baseline do **GPT-5**.

Os resultados obtidos a partir do notebook de análise consolidaram as seguintes métricas de desempenho:

### Tabelas Comparativas de Performance

#### Métricas Absolutas
![Tabela de Métricas Absolutas](docs/images/results_table1.png)

#### Métricas Relativas (%)
![Tabela de Métricas Relativas](docs/images/results_table2.png)

### Gráficos Comparativos

#### Desempenho na Geração de Instâncias (Syntax %, Consistent %, Valid %)
![Gráfico de Geração de Instâncias](docs/images/results_chart1.png)

#### Taxa de Especificações Incorretas Não Detectadas (Missed %) - Menor é Melhor
![Gráfico de Missed Specifications](docs/images/results_chart2.png)


## Como Reproduzir

### Sem Docker
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=sua_chave_aqui
python src/pipeline.py
```

### Com Docker
```bash
docker build -t alloy-multiagent .
docker run -e GEMINI_API_KEY=sua_chave alloy-multiagent
```

## Baseline

Os resultados do GPT-5 usados como baseline são provenientes do artigo original, disponíveis em [haslab/Alloy-LLM-Testing](https://github.com/haslab/Alloy-LLM-Testing).

## Equipe

| Nome | Login UFPE |
|------|-----------|
| Lucas Luis de Souza | lls4 |
| Antonio Apolinario | aab2 |
| Monyque Gabrieli | mgbl |
| Lucas de Holanda | lhl |