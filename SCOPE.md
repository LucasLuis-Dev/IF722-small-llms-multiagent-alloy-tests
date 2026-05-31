# Escopo do Projeto

## Contexto

O artigo "Validating Formal Specifications with LLM-generated Test Cases" (FM26) avaliou o uso de LLMs para gerar casos de teste Alloy automaticamente a partir de requisitos em linguagem natural. O melhor resultado foi obtido com GPT-5 usando few-shot prompting: 96% de validade e detecção de até 93.57% das especificações incorretas.

## Hipótese

Um modelo menor e mais barato (Gemini 2.0 Flash) combinado com um agente de pós-processamento sintático pode atingir resultados comparáveis ao GPT-5, com custo significativamente menor.

## Benchmark

- Dataset: Alloy4Fun (mesmo do artigo original)
- Métricas mantidas do artigo: Syntax, Consistent, Valid, Missed (wrong specs)
- Prompt base: few-shot (melhor resultado no artigo original)

## Modelos Avaliados

| Modelo | Papel | Custo (input/output por 1M tokens) |
|--------|-------|--------------------------------------|
| GPT-5 | Baseline (resultados do artigo) | — |
| Gemini 2.0 Flash | Modelo experimental | $0.10 / $0.40 |

## Regras de Pós-Processamento (Agente 2)

1. Corrigir declarações `sig` sem fechamento de chaves
2. Padronizar formato do comando `run` (adicionar `for N` quando ausente)
3. Substituir referências `none` sem tipagem para `none -> none` quando necessário
4. Remover linhas duplicadas de `pred` ou `fact`
5. Garantir que o bloco de teste termine com exatamente um comando `run`

## Métricas do Experimento

| Métrica | Descrição |
|---------|-----------|
| Syntax (%) | % de test cases sintaticamente corretos |
| Syntax após PP (%) | % após pós-processamento do Agente 2 |
| Consistent (%) | % de test cases com instância satisfatível |
| Valid (%) | % completamente válidos (syntax + consistent) |
| Missed (%) | % de especificações incorretas não detectadas |
| Custo ($) | Custo total de API para o experimento |

## Cronograma

| Semana | Atividade |
|--------|-----------|
| 1 | Configuração do ambiente, integração com Gemini API |
| 2 | Implementação do Agente 1 (Generator) |
| 3 | Implementação do Agente 2 (Post-Processor) |
| 4 | Implementação do Agente 3 (Validator) e pipeline |
| 5 | Execução do experimento e coleta de dados |
| 6 | Análise dos resultados e comparação com baseline |
| 7 | Escrita do relatório final e apresentação |