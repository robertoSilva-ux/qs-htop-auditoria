# Auditoria de Qualidade de Software — htop

Relatórios e artefatos da auditoria de qualidade de software aplicada ao **htop**, projeto de código aberto, como parte do Trabalho Prático em Grupo (P2) da disciplina de **Qualidade de Software** — TADS, IFRS Campus Rio Grande, 2026.2.

**Autor:** Roberto Fabiano Cunha da Silva
**Professor:** Me. Juan Carlos Quevedo Weimar

## Objeto de estudo

| Item | Valor |
|---|---|
| Projeto | [htop](https://github.com/htop-dev/htop) — monitor de processos interativo para terminal |
| Commit analisado | [`8ff043d`](https://github.com/htop-dev/htop/commit/8ff043d2429b0bb5a8c093d1442c3a1534603381) (20/09/2026) |
| Fork auditado | [robertoSilva-ux/htop](https://github.com/robertoSilva-ux/htop) |
| Ferramenta de análise estática | SonarQube Cloud (SonarCloud), com base de compilação (`compile_commands.json`) e *taint analysis* |

O mesmo commit é usado nos dois milestones, para que os números sejam comparáveis entre si.

## Conteúdo

| Arquivo | Entrega | O que traz |
|---|---|---|
| [`docs/M1-htop-mapeamento-processos.pdf`](docs/M1-htop-mapeamento-processos.pdf) | Milestone 1 | Mapeamento de processos aderente à ISO/IEC 12207, diagnóstico de maturidade (MR-MPS-SW / CMMI) e registro de não-conformidades |
| [`docs/M2-htop-plano-de-metricas.docx`](docs/M2-htop-plano-de-metricas.docx) | Milestone 2 | Versão editável do plano de métricas + relatório de análise estática |
| [`docs/M2-htop-plano-metricas-iso25010.pdf`](docs/M2-htop-plano-metricas-iso25010.pdf) | Milestone 2 | Plano de métricas de produto (ISO/IEC 25010) e relatório de análise estática, com a tabela de aderência ao enunciado |
| [`docs/M2-htop-plano-metricas-iso25010.md`](docs/M2-htop-plano-metricas-iso25010.md) | — | Fonte em Markdown do relatório |
| [`testes/ct02_htoprc_fora_da_faixa.py`](testes/ct02_htoprc_fora_da_faixa.py) | Milestone 2 | Caso de teste executável CT-02 (ver abaixo) |
| [`testes/ct02-saida.txt`](testes/ct02-saida.txt) | Milestone 2 | Saída registrada da execução do caso |

## Números principais do Milestone 2

- **37.458** linhas de código (ncloc) medidas em 293 arquivos; 86 dos 132 arquivos `.c` compilados em Linux
- **73 issues** abertas: 42 BLOCKER, 21 MAJOR, 10 MINOR
- **12 vulnerabilidades BLOCKER de injeção** (*taint analysis*), concentradas em **5 arquivos** — todos dentro do recorte de risco que o Milestone 1 isolou por Pareto
- Ratings: confiabilidade **E**, segurança **E**, manutenibilidade **A**
- Quality Gate **ERROR** (2 de 6 condições), dívida técnica de **645 min**, duplicação de **6,8%**
- Cobertura de testes: a CI publica **0%**; medida nesta auditoria, **37,5% de linhas / 23,5% de ramos** — um piso, não o valor da suíte oficial

## Caso de teste executável (CT-02)

O projeto **tem** suíte de testes (`test_spec.lua`, 687 linhas, `busted` + `rote`), mas ela não pôde ser executada nesta auditoria: o `rote` não tem versão publicada para Lua 5.5 — `luarocks install rote` responde `No results matching query were found for Lua 5.5`. Sem essa biblioteca, o `test_spec.lua` falha já no `require("rote")` da linha 13.

Para não deixar o eixo de testabilidade apenas no papel, um caso foi implementado como teste executável: **CT-02 — `htoprc` com campo fora da faixa** (análise de valor limite, fronteira inválida superior), derivado da seção 6 do relatório.

O teste executa o binário real num pty de 24×80 (o mesmo par da suíte oficial, `RoteTerm(24, 80)`), com `HOME` temporário contendo o `htoprc` hostil, captura a tela e compara a assinatura de interface com uma execução de controle de configuração válida. Se as assinaturas coincidem, o índice inválido não foi aplicado.

### Como rodar

Pré-requisitos: Linux, Python 3.8+ e um binário do htop compilado a partir do commit `8ff043d`.

```bash
git clone https://github.com/robertoSilva-ux/htop.git
cd htop && git checkout 8ff043d
./autogen.sh && ./configure && make          # requer ncurses-devel

python3 testes/ct02_htoprc_fora_da_faixa.py ./htop
```

Saída esperada (a registrada em `testes/ct02-saida.txt`):

```
CT-02 — htoprc com campo fora da faixa (BVA, limite superior + 1)
  configuração inválida : fields=0 999        -> saída 0
  configuração válida   : fields=0 48 49 ...  -> saída 0
  marcadores na tela    : 15 de 15
  [PASS] htop sobe com o valor inválido (não aborta)
  [PASS] encerra normalmente com 'q' (código 0)
  [PASS] não termina por sinal (sem crash/segfault)
  [PASS] interface desenhada: medidores, tarefas, carga e barra de funções
  [PASS] colunas em uso são as padrão (índice 999 ignorado)
  [PASS] htoprc preservado (não corrompido na leitura)
  RESULTADO: PASSOU (6 de 6 checagens)
```

Controle negativo — o mesmo teste apontado para um binário que não é o htop reprova:

```bash
python3 testes/ct02_htoprc_fora_da_faixa.py /bin/true   # 2 FAIL, código de saída 1
```

## Limitações declaradas

- A suíte oficial do projeto não foi executada (dependência `rote` indisponível para Lua 5.5). O número de cobertura apresentado vem de navegação dirigida em pty e é um **piso**.
- 46 arquivos das camadas de plataforma (`darwin/`, `*bsd/`, `solaris/`, `pcp/`) não são compilados em Linux e ficam fora das métricas de complexidade e defeito.
- As 12 vulnerabilidades são achados de análise estática de fluxo de dados; exigem confirmação por execução, proposta na seção 6 do relatório.

## Uso

Material acadêmico, produzido para avaliação da disciplina. O código auditado pertence ao projeto htop e permanece sob a licença GPL-2.0 do projeto original.
