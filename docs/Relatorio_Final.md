# Relatório Final: Automação de Casos de Teste em Alloy via Pipeline Multi-Agente com LLMs Menores

## 1. Introdução e Motivação
A linguagem de especificação formal Alloy é extremamente poderosa para validar propriedades estruturais e comportamentais de sistemas de software. No entanto, criar casos de teste (comandos `run` e `expect`) é uma tarefa complexa que exige domínio rigoroso de lógica de primeira ordem e cálculo relacional. 

Embora LLMs massivos, como o GPT-4/GPT-5, tenham demonstrado alta precisão na geração desses testes, seus custos financeiros e lentidão de inferência inviabilizam o uso contínuo em larga escala. A motivação deste projeto foi investigar a eficácia de **LLMs menores e altamente eficientes** — especificamente o modelo **Gemini 2.5 Flash** — na automação da geração de testes para o benchmark Alloy4Fun.

## 2. Arquitetura do Pipeline Multi-Agente
A solução foi orquestrada utilizando Python, integrando as bibliotecas do Google GenAI para a inferência e o `jpype` para a validação via `alloytools.jar` (JVM). A arquitetura é composta por agentes interconectados:

### 2.1. Agente 1: Generator (LLM)
O primeiro agente recebe o modelo base Alloy e o requisito em linguagem natural. Utilizamos a técnica de **Few-Shot Prompting**, guiando o modelo a gerar as instâncias. Ele também é capaz de aceitar contexto de execuções anteriores falhas (ver Seção 2.4).

### 2.2. Agente 2: Post-Processor (Algoritmo Simbólico)
O principal obstáculo de LLMs pequenos é a consistência sintática: eles frequentemente violam regras estritas ou replicam `sig` originais. O segundo agente atua como um corretor heurístico (via expressões regulares) para **higienizar** as saídas geradas.

### 2.3. Agente 3: Validator (JPype / Alloy Analyzer)
O terceiro agente submete os códigos ao motor Java subjacente do Kodkod/Alloy, conferindo falhas de sintaxe e consistência.

### 2.4. Módulo de Self-Reflection (Reflexão com Estado)
Foi implementado, no nível do orquestrador interativo (`pipeline.py`), um laço de feedback em tempo de execução (*Stateful Retries*). Nele, caso o Agente 3 detecte uma falha de sintaxe ou de consistência, o erro logado pela máquina virtual Java (`raw_output`) e o código gerado defeituoso são reintroduzidos dinamicamente ao Agente 1 (Generator) na tentativa subsequente. O modelo menor é assim instruído a realizar **Auto-Correção** baseada em rastreios de compilador:
> *"In your previous attempt, you generated this code: [...] But the Alloy Analyzer returned the following error: [...]. Please fix the syntax or structural errors..."*

Isso transforma inferências diretas e heurísticas em ciclos interativos de refinamento formal, técnica que se torna exequível em alta escala e tempo real somente devido à enorme rapidez e ao baixo custo da família Flash.

## 3. Metodologia Experimental
Foi utilizado o dataset originado da plataforma web **Alloy4Fun**.
- **Abordagem:** Execução em *batch* por meio do módulo `src/run_experiment.py`.
- **Prevenção contra Limites:** Implementação de mecanismos de *retry* em falhas (típicos de sobrecarga de API) e injeção de atrasos sistemáticos (`time.sleep`) para conformidade à cota de chamadas do Google AI Studio.
- **Avaliação:** Comparação com o modelo acadêmico base (*GPT-5*).

## 4. Resultados e Discussão
1. **Taxa de Parsing e Sintaxe:** Observou-se que modelos menores tendem a ser criativos com as nomenclaturas, refletindo em um número elevado de *Syntax Errors* na abordagem Zero/Few-shot (apenas 29.15% de compilação válida frente aos 98.84% do GPT-5).
2. **Custo-Benefício:** Em compensação, enquanto a rodada de testes do GPT-5 custou **US$ 3.56**, a rodada completa com o Gemini 2.5 Flash custou apenas **US$ 0.01**. Essa diferença de custo na ordem de 350x torna a técnica de **Self-Reflection** (Seção 2.4) financeiramente suportável.
3. **Métricas Raw vs. Processed (Paridade de Resultados):**
   Durante a avaliação automatizada (`run_experiment.py`), os resultados das métricas brutas e processadas se mostraram numericamente equivalentes. 
   
   > [!NOTE]
   > **Explicação Técnica:** Isso ocorre porque o avaliador oficial da ferramenta acadêmica utiliza expressões regulares estruturadas para extrair apenas os blocos `run {...}`, descartando de antemão tudo o que estiver fora desse escopo. No entanto, em um pipeline em produção real, a versão "Raw" quebraria com erros de "Duplicate Signature".

## 5. Conclusão
A arquitetura Multi-Agente, combinada com estratégias de Self-Reflection, mitiga as fraquezas dos modelos compactos em tarefas determinísticas (como sintaxe formal). Acoplar um LLM de alta velocidade (Flash) a um validador pós-processamento barato constrói a base ideal para um framework de testes automatizados iterativos, escaláveis e incrivelmente econômicos.
