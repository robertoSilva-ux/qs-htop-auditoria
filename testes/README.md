# Casos de teste executáveis

Um dos seis casos especificados no relatório do Milestone 2 foi implementado como teste executável, para que o eixo de testabilidade não ficasse apenas no papel.

## `ct02_htoprc_fora_da_faixa.py`

**Caso:** CT-02 — `htoprc` com campo fora da faixa.
**Técnica:** análise de valor limite (BVA), fronteira inválida superior.
**Derivação:** seção 6 do relatório (`docs/M2-htop-plano-metricas-iso25010.pdf`).

| | |
|---|---|
| **Pré-condição** | `~/.config/htop/htoprc` com `fields=0 999` |
| **Ação** | executar o `htop` e encerrar com `q` |
| **Resultado esperado** | o valor inválido é ignorado, o htop sobe com as colunas padrão e encerra normalmente |
| **Critério de falha** | aborto, término por sinal, ausência de interface, ou uso de configuração diferente da de controle |

### Por que diferencial e não leitura do arquivo

O htop **não regrava** o `htoprc` quando nada muda na configuração — verificado em três fluxos (`q` direto, `F2`+`Esc`, `F9`+`Esc`): o arquivo volta idêntico. Portanto não é possível provar "o valor foi descartado" lendo o arquivo depois da execução.

A verificação adotada é comportamental: o teste roda **duas vezes** — com `fields=0 999` e com uma configuração válida — e compara a assinatura de 15 elementos de interface capturada do pty (medidores, `Tasks:`, `Load average`, `Uptime:`, barra `F1`–`F10`, coluna `PID`). Assinaturas iguais entre os dois casos significam que o índice inválido não foi aplicado.

### Como rodar

```bash
python3 ct02_htoprc_fora_da_faixa.py /caminho/para/o/binario/htop
```

- Requisitos: Linux, Python 3.8+ (só biblioteca padrão), binário do htop compilado do commit `8ff043d`.
- Sem argumento, o script procura `~/.hermes/cache/scratch/qs-m2/htop/htop` — caminho usado na auditoria.
- Código de saída: `0` se passar, `1` se falhar.
- O script cria o `htoprc` num `HOME` temporário: **não toca** na configuração do usuário.
- Define `GCOV_PREFIX` para um diretório temporário, para que um binário compilado com cobertura não escreva `.gcda` fora dali.

### Resultado registrado

`ct02-saida.txt` — 6 de 6 checagens aprovadas contra o binário do commit `8ff043d`.

### Controle negativo

```bash
python3 ct02_htoprc_fora_da_faixa.py /bin/true    # espera-se 2 FAIL e código 1
```

O controle existe para provar que o teste não passa por vacuidade: se o objeto deixar de se comportar como o esperado, a verificação acusa.

## Casos ainda não implementados

CT-01, CT-03, CT-04, CT-05 e CT-06 estão especificados no relatório com pré-condição, passos e resultado esperado no formato IEEE 829. Os dois mais próximos deste wrapper são CT-03 (`htoprc` com linha de 8.192 bytes) e CT-06 (linha de `cgroup` acima de 4.096 bytes), que exercitam limite de buffer — a mesma classe das vulnerabilidades apontadas na análise estática.
