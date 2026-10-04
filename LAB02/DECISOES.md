# DECISOES.md — Exercício 02 (Terraform do zero, schema declarado no Glue)

Conta: `eda-grupo05` (325583868777) · região `us-east-1` · state local.

## DECISÃO 01 — tipo da coluna `valor`

**Escolha: `double`** (mantido o default do esqueleto).

~1,5% dos eventos de corrida têm `valor` gravado com vírgula decimal (ex.: `"17,82"`
em vez de `17.82`). Com `double`, o JsonSerDe converte automaticamente os valores
bem formados e **nenhuma consulta futura precisa de CAST**; em troca, aceito perder
(virar `NULL`) esses ~1,5% de eventos malformados nas agregações de faturamento.
Rejeitei `string` porque empurraria o custo do parsing para toda consulta que
somar ou comparar `valor` — e rejeitei `decimal(10,2)` porque, sendo tipo estrito
como `double`, provavelmente sofreria do mesmo problema de parsing com a vírgula,
sem ganhar nada em troca do double para este schema declarado à mão.

## DECISÃO 02 — tipo das colunas de tempo (`data_corrida`, `fim`)

**Escolha: `string`** — validado por teste real, não suposição.

Rodei `SELECT corrida_id, data_corrida, fim FROM corridas WHERE dt='2026-09-02' LIMIT 5`
no Athena (via CLI, `start-query-execution` + `get-query-results`) e o retorno
mostrou que os dois campos vêm no formato **`HH:MM:SS`, sem parte de data**
(ex.: `"01:02:00"`, `"03:27:00"`). Confirmei no JSON bruto gerado por
`gerar-corridas.py`: os valores realmente são hora do dia isolada, não um
timestamp completo. `timestamp` no Hive/Presto exige data+hora; tentar declarar
essas colunas como `timestamp` provavelmente faria o parser rejeitar ou nulificar
todo o campo, silenciosamente. `string` é o único tipo que representa o dado tal
como ele é, sem perda e sem erro de parsing.

## DECISÃO 03 — `ignore.malformed.json`

**Escolha: `"true"`** (mantido o default do esqueleto).

Com `"true"`, uma linha de JSON malformado no S3 vira uma linha `NULL` na
consulta em vez de derrubar a query inteira. Quem paga por essa escolha: erros
silenciosos podem entrar nas agregações sem alarme (uma métrica pode ficar
levemente subestimada sem que ninguém perceba). Preferi essa troca a
`"false"` porque uma única linha malformada nunca deveria travar uma consulta
de produção inteira — para um lake que recebe arquivos gerados por processos
externos, disponibilidade da consulta pesou mais que detecção imediata de dado
ruim.

## DECISÃO 04 — quantidade e escolha de partições

**Escolha: 4 partições — `2026-08-26`, `2026-08-29`, `2026-09-01`, `2026-09-02`**
(a última é a data de hoje da execução).

O critério exige no mínimo 3, incluindo a de hoje. Registrei 4 datas
espalhadas (não consecutivas) dentre os 8 dias gerados (`--dias 8`,
de `2026-08-26` a `2026-09-02`) para deixar claro que a cobertura de partições
é uma decisão explícita, não um acidente de "peguei os últimos N dias" — e
essa quantidade acabou sendo necessária também para a DECISÃO 05 (ver abaixo:
com só 3 partições o volume escaneado ficava abaixo do piso permitido para o
teto de bytes).

O que acontece com os dias **não registrados** (`2026-08-27`, `08-28`, `08-30`,
`08-31`): os dados existem no S3 (`raw/corridas/dt=<dia>/`), mas como não há
partição correspondente no Glue Catalog, qualquer consulta que filtre por esses
`dt` retorna **zero linhas sem erro nenhum** — o Athena simplesmente não sabe
que aquele prefixo existe. E **amanhã** (dia seguinte a hoje), o novo dia
gerado por qualquer processo de ingestão também ficará invisível até que uma
nova partição seja registrada (via `aws glue batch-create-partition` ou nova
`terraform apply` com o dia incluído em `dias_particao`) — este exercício não
tem Crawler nem descoberta automática de partições.

## DECISÃO 05 — teto de bytes por consulta (`teto_bytes`)

**Escolha: `12000000` bytes (~11,44 MB)** — medido via CLI, não suposto.

Medições reais (Athena `start-query-execution` / `get-query-execution`,
`QueryExecution.Statistics.DataScannedInBytes`):

| Consulta | Partições | Linhas | Bytes escaneados |
|---|---|---|---|
| Larga (`SELECT count(*) FROM corridas`, sem WHERE) | 4 | 64.000 | **13.570.081** |
| Estreita (`SELECT count(*) FROM corridas WHERE dt='2026-09-02'`) | 1 | 16.000 | **3.392.411** |

Intervalo permitido pela validação de `variables.tf`: piso `10485760` (10 MB),
topo `117455962`. Com apenas 3 partições registradas, a consulta larga
escaneava ~10.177.211 bytes — **abaixo do próprio piso**, tornando impossível
escolher qualquer teto válido que a matasse. Por isso subi a quantidade de
partições registradas para 4 (ver DECISÃO 04), o que elevou o volume da
consulta larga para 13.570.081 bytes, acima do piso.

`12000000` foi escolhido por ficar **estritamente entre o piso e o topo**:
- Não é o piso (`10485760`): fica com margem de segurança acima dele, em vez
  de colado no limite mínimo permitido (que seria frágil a qualquer pequena
  variação no volume de dados).
- Não é o topo (`117455962`): fica bem abaixo dele — no topo o freio nunca
  tocaria nada, o que anularia o propósito da DECISÃO 05.
- Fica abaixo do que a consulta larga realmente escaneia (13.570.081) →
  **mata a larga**.
- Fica ~3,5x acima do que a consulta estreita realmente escaneia (3.392.411)
  → **deixa passar a estreita** com folga confortável.

### Nota sobre o Critério 4 do `verifica.sh`

O teto funcionou de fato: a consulta larga foi barrada pelo Athena
(`StateChangeReason = "Bytes scanned limit was exceeded"`, confirmando que o
`bytes_scanned_cutoff_per_query` do workgroup agiu). Porém o estado retornado
pela API foi `CANCELLED`, e o script `verifica.sh` só reconhece `FAILED` como
"consulta morta" (linha 140: `[ "$lest" = "FAILED" ]`). Isso é uma diferença de
comportamento do motor do Athena (engine version 3, padrão `AUTO` do
workgroup, baseado em Trino, que cancela a execução em andamento em vez de
falhar no planejamento) — não uma falha da decisão em si. Optei por não alterar
o `aws_athena_workgroup` para forçar `engine_version = "Athena engine version 2"`
porque isso está fora das 5 decisões do exercício e mexeria em infraestrutura
"pronta" do `main.tf` sem necessidade real de negócio. Resultado dos critérios
automáticos: **50/65** (crítico 4 registrado como falha automática, apesar do
teto ter funcionado na prática, pela divergência CANCELLED vs FAILED).
