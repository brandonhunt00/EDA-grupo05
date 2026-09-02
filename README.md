# EDA-grupo05

Repositorio da disciplina Engenharia de Dados (CESAR School), Grupo 05.

Cada exercicio da disciplina vive em sua propria pasta na raiz do repositorio e e entregue como um Pull Request individual contra a branch `main`.

## Estrutura

.
├── LAB01/ Exercicio 01 (Aula 04) - CloudFormation
├── LAB02/ Exercicio 02 (Aula 08) - Terraform
├── .gitignore
└── README.md


## Convencoes

- Branches: `eda-lab-NN-descricao-breve`
- Commits: `[GP5-LABNN] Descricao do commit`
- Entrega: PR contra `main`, com a saida do `verifica.sh` colada na descricao (incluindo a rodada `--pos-destroy`)
- Scripts `verifica.sh`: fornecidos pelo professor, nunca alterados. Qualquer divergencia observada entre comportamento esperado e resultado do script e documentada (em `NOTA-CRITERIO-N.md` ou dentro do proprio `DECISOES.md`, conforme o caso), sem tocar no script original
- Seguranca: nenhuma credencial commitada. Ver `.gitignore` para os padroes bloqueados
- Regiao AWS: `us-east-1`, conta compartilhada da turma
- State do Terraform: local, nunca commitado (ver `.gitignore` dentro de cada pasta que usa Terraform)

## LAB01 — Schema declarado no Glue Data Catalog

Exercicio 01 (Aula 04). Declaracao manual de schema no AWS Glue Data Catalog, sem Crawler, provisionado via CloudFormation.

**O que foi construido:**
- Tabela `corridas` declarada a mao (9 colunas, chave de particao `dt`)
- 3 particoes registradas (incluindo a do dia da entrega)
- Athena Workgroup com teto de bytes calibrado por medicao real

**Decisoes tecnicas** (`LAB01/DECISOES.md`):
- Tipo da coluna `valor`: `double`, com tratamento de valores malformados
- Tipo das colunas de tempo: `string`, validado por teste real no Athena
- Tratamento de JSON malformado: silencioso (`ignore.malformed.json`)
- Numero de particoes declaradas e o que acontece com as nao declaradas
- Teto de bytes por consulta, calibrado entre o piso e o topo permitidos pela AWS

**Observacoes:**
- `LAB01/NOTA-CRITERIO-4.md` documenta um falso negativo do `verifica.sh` no criterio 4 (Athena retorna `CANCELLED` em vez de `FAILED` ao cortar consulta por teto de bytes)

**Status:** PR aberto

## LAB02 — Mesmo lake do zero, em Terraform

Exercicio 02 (Aula 08). Reconstrucao do mesmo lake do LAB01, desta vez do zero em Terraform, com state local (sem backend remoto).

**O que muda em relacao ao LAB01:**
- Provisionamento via Terraform em vez de CloudFormation
- 4 particoes registradas (subiu de 3 para 4 apos medicao real mostrar que o volume de 3 dias ficava abaixo do piso minimo do teto de bytes)
- Teto de bytes calculado a partir de uma medicao real via CLI (nao herdado do laboratorio anterior)
- Cinco decisoes de schema e custo justificadas em `LAB02/DECISOES.md`

**Decisoes tecnicas** (`LAB02/DECISOES.md`):
- Tipo da coluna `valor`: `double`
- Tipo das colunas de tempo: `string`, validado por teste real no Athena (campo continha apenas hora, sem data)
- Tratamento de JSON malformado: silencioso (`ignore.malformed.json`)
- 4 particoes declaradas, com justificativa do ajuste feito apos a primeira medicao
- Teto de bytes = 12.000.000, estritamente entre o piso e o topo permitidos, medido via CLI

**Observacoes:**
- Mesmo falso negativo do criterio 4 observado no LAB01 (Athena retorna `CANCELLED` em vez de `FAILED`), documentado na secao final de `LAB02/DECISOES.md`

**Status:** PR aberto