# Plano Experimental — Detalhamento do Escopo

## Contexto

O artigo de referência demonstrou que o GPT-5 com few-shot prompting alcança ~96% de taxa de testes válidos na geração de casos de teste para especificações formais Alloy. Contudo, o uso do GPT-5 tem custo elevado e depende de API proprietária.

Modelos menores (open-source ou versões "mini") cometem mais erros sintáticos na geração de código Alloy — principalmente em padrões específicos como `R none` ao invés de `R none -> none`. Esses erros são sistemáticos e previsíveis.

Nossa hipótese é que um agente de pós-processamento determinístico, aplicado após a saída do LLM menor, pode corrigir a maioria desses erros e aproximar a taxa de testes válidos à do modelo maior, com custo significativamente menor.

***

## Modelos Avaliados

| Modelo | Tipo | Motivo |
|--------|------|--------|
| GPT-5 (referência) | Proprietário grande | Baseline do artigo original |
| GPT-4o-mini | Proprietário pequeno | Amplamente acessível, baixo custo |
| Llama 3.1 8B (via Ollama) | Open-source local | Gratuito, reprodutível sem API |

***

## Regras de Pós-Processamento (Agente 2)

Baseadas nas causas de erro identificadas no artigo de referência:

1. **Correção de relações vazias**: `R none` → `R none -> none` (para relações binárias)
2. **Inserção de scope ausente**: detectar comandos `run` sem `for N X` e inferir scope padrão
3. **Correção de expect**: garantir que testes positivos usem `expect 1` e negativos `expect 0`
4. **Normalização de `some disj`**: verificar que todos os quantificadores usam o padrão `some disj`
5. **Limpeza de blocos malformados**: detectar e remover comandos `run` incompletos ou sem corpo

***

## Métricas de Avaliação

Seguindo exatamente o artigo de referência:

| Métrica | Descrição |
|---------|-----------|
| **Tests** | Total de casos de teste gerados |
| **Syntax** | Casos sintaticamente corretos (após pós-processamento) |
| **Consistent** | Casos que produzem uma instância no Alloy Analyzer |
| **Previous** | Casos que satisfazem todos os requisitos anteriores |
| **Valid** | Casos que concordam com o oráculo (requisito correto) |
| **Cost** | Custo real de chamada à API do LLM |

Métricas adicionais deste projeto:
- **Syntax (antes do PP)** — para medir o ganho do pós-processamento isolado
- **Syntax (depois do PP)** — taxa após correção automática
- **Delta PP** — diferença entre antes e depois do pós-processamento

***

## Cronograma Sugerido

| Semana | Atividade |
|--------|-----------|
| 1 | Fork do repositório base, setup do ambiente Docker/Ollama |
| 2 | Implementar Agente 1 (Generator) com GPT-4o-mini e Llama |
| 3 | Implementar Agente 2 (Post-processor) com as regras acima |
| 4 | Implementar Agente 3 (Validator) e pipeline completo |
| 5 | Executar experimentos e coletar dados |
| 6 | Análise, geração de tabelas/gráficos e escrita do relatório |
| 7 | Preparação da apresentação |