# IF722 – Small LLMs with Multi-Agent Post-Processing for Alloy Test Generation

> Projeto da disciplina IF722 – Engenharia de Software Baseada em Evidências  
> Universidade Federal de Pernambuco (UFPE)  
> Forked from [haslab/Alloy-LLM-Testing](https://github.com/haslab/Alloy-LLM-Testing)

## Resumo

Este projeto estende o trabalho "Validating Formal Specifications with LLM-generated Test Cases" (FM26) ao investigar se modelos de linguagem menores e mais baratos — especificamente o **Gemini 2.0 Flash** — conseguem gerar casos de teste Alloy com qualidade comparável ao GPT-5, quando assistidos por um pipeline **multi-agente com pós-processamento sintático**.

## Escopo

O artigo base demonstrou que LLMs grandes (GPT-5) geram test cases Alloy com até 96% de validade usando few-shot prompting. Este projeto questiona: **é possível obter resultados similares com modelos menores e mais baratos, adicionando um agente de correção sintática automática?**

## Perguntas de Pesquisa

- **RQ1:** O pós-processamento sintático reduz significativamente os erros de sintaxe gerados pelo Gemini 2.0 Flash?
- **RQ2:** Com pós-processamento, o Gemini 2.0 Flash consegue detectar especificações incorretas em nível similar ao GPT-5?
- **RQ3:** Qual é a relação custo-benefício entre usar GPT-5 direto vs Gemini 2.0 Flash + pós-processamento?

## Arquitetura Multi-Agente

```
Requisito (NL)
│
▼
┌─────────────────┐
│ Agente 1 │ → Chama Gemini 2.0 Flash e gera rascunho dos test cases Alloy
│ Generator │
└────────┬────────┘
│
▼
┌─────────────────┐
│ Agente 2 │ → Aplica regras de correção sintática (scope, run, none, etc.)
│ Post-Processor │
└────────┬────────┘
│
▼
┌─────────────────┐
│ Agente 3 │ → Executa Alloy Analyzer, coleta métricas e decide retry
│ Validator │
└─────────────────┘
```

## Estrutura do Repositório

```
├── README.md
├── SCOPE.md
├── src/
│ ├── agents/
│ │ ├── agent_generator.py # Agente 1: geração via Gemini 2.0 Flash
│ │ ├── agent_postprocessor.py # Agente 2: correção sintática
│ │ └── agent_validator.py # Agente 3: validação com Alloy Analyzer
│ ├── pipeline.py # Orquestrador dos 3 agentes
│ └── config.py # Configurações gerais
├── prompts/
│ └── prompt_few_gemini.txt # Prompt few-shot adaptado para Gemini
├── data/
│ ├── inputs/ # Requisitos e modelos Alloy do benchmark
│ ├── raw/ # Saídas brutas do Gemini
│ └── processed/ # Métricas processadas
├── analysis/ # Scripts de análise herdados do artigo
├── execute/ # Scripts de execução herdados do artigo
├── prepare/ # Scripts de preparação herdados do artigo
├── Dockerfile
├── requirements.txt
└── alloytools.jar
```


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