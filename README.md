# eda2026-projeto-g05

# EDA — Projeto de Engenharia de Dados

## Análise de No-Show em Agendamentos de Clínica

Projeto desenvolvido para a disciplina **EDA— Engenharia de Dados**.

A Parte 1 do projeto tem como objetivo provisionar, utilizando **Terraform**, uma infraestrutura de dados na AWS capaz de armazenar dados de agendamentos de uma clínica, catalogá-los e responder a uma pergunta analítica utilizando o **Amazon Athena**.

---

## 1. Cenário

O cenário representa uma clínica que possui um sistema de agendamento de consultas.

Cada agendamento registra informações como paciente, especialidade, profissional responsável, unidade, data da consulta e status do atendimento.

Um dos problemas enfrentados pela clínica é o **no-show**, situação em que o paciente possui uma consulta marcada, mas não comparece.

As faltas podem gerar horários ociosos e prejudicar o planejamento da capacidade de atendimento da clínica.


## 2. Pergunta de negócio

A pergunta analítica escolhida para o projeto é:

> **Qual é a taxa de faltas (no-show) por especialidade da clínica?**

A consulta será executada no Amazon Athena e permitirá identificar quais especialidades apresentam maior proporção de faltas.

---

## 3. Evento analisado

O evento utilizado pelo projeto é:

> **Um agendamento de consulta.**

Cada registro do conjunto de dados representa um agendamento realizado no sistema da clínica.

---

## 4. Grão da tabela trusted

O grão definido para a tabela `agendamentos` é:

> **1 registro = 1 agendamento de consulta.**

Cada agendamento possui um identificador próprio (`agendamento_id`).

---

## 5. Métrica

Para a análise da taxa de no-show serão consideradas apenas consultas com resultado conhecido:

* `REALIZADO`
* `NO_SHOW`

Consultas com status `CANCELADO`, `AGENDADO` ou `CONFIRMADO` não entram no cálculo.

A métrica utilizada é:

```text
                 quantidade de NO_SHOW
Taxa no-show = --------------------------- × 100
               REALIZADO + NO_SHOW
```

---

## 6. Dados

A tabela utilizada no projeto se chama:

```text
agendamentos
```

Schema:

| Campo               | Tipo   | Descrição                               |
| ------------------- | ------ | --------------------------------------- |
| `agendamento_id`    | string | Identificador do agendamento            |
| `paciente_id`       | string | Identificador do paciente               |
| `clinica_id`        | string | Identificador da unidade                |
| `especialidade`     | string | Especialidade médica                    |
| `profissional_id`   | string | Identificador do profissional           |
| `data_agendamento`  | date   | Data em que o agendamento foi realizado |
| `data_consulta`     | date   | Data da consulta                        |
| `hora_consulta`     | string | Horário da consulta                     |
| `status`            | string | Status do agendamento                   |
| `canal_agendamento` | string | Canal utilizado no agendamento          |
| `tipo_consulta`     | string | Tipo da consulta                        |

Exemplo:

```csv
agendamento_id,paciente_id,clinica_id,especialidade,profissional_id,data_agendamento,data_consulta,hora_consulta,status,canal_agendamento,tipo_consulta
A000001,P0001,C01,Cardiologia,M001,2026-08-01,2026-08-10,08:00,REALIZADO,APP,ROTINA
A000002,P0002,C01,Dermatologia,M002,2026-08-01,2026-08-10,09:00,NO_SHOW,SITE,ROTINA
A000003,P0003,C02,Ortopedia,M003,2026-08-02,2026-08-12,10:30,REALIZADO,TELEFONE,RETORNO
```

O schema da tabela foi declarado diretamente no Terraform.

Não foi utilizado Glue Crawler para inferência do schema.

---

## 7. Qualidade dos dados

O cenário permite a existência de dados inconsistentes na origem.

Exemplos:

### Status inconsistentes

```text
NO_SHOW
No-Show
no_show
FALTOU
```

Padronização:

```text
NO_SHOW
```

### Especialidades inconsistentes

```text
Cardiologia
cardiologia
CARDIOLOGIA
Cardio
```

Padronização:

```text
Cardiologia
```

### Datas inconsistentes

```text
15/08/2026
2026-08-15
15-08-2026
```

Padronização:

```text
2026-08-15
```

Também podem existir registros duplicados, identificados pelo mesmo `agendamento_id`.

As decisões relacionadas ao tratamento dos dados foram documentadas no arquivo `DECISOES.md`.

---

## 8. Arquitetura da Parte 1

A infraestrutura utiliza:

* Amazon S3;
* AWS Glue Data Catalog;
* Amazon Athena;
* Terraform;
* S3 para armazenamento remoto do Terraform State;
* DynamoDB para controle de lock do Terraform;
* Terraform Workspace.

Fluxo principal:

```text
Dataset
   │
   ▼
Amazon S3
   │
   ▼
Glue Data Catalog
   │
   ▼
Tabela agendamentos
   │
   ▼
Amazon Athena
   │
   ▼
Consulta SQL
   │
   ▼
Taxa de no-show por especialidade
```

---

## 9. Pré-requisitos

Para executar o projeto é necessário possuir:

* Terraform;
* AWS CLI;
* Git;
* Bash;
* conta AWS com permissões para criação dos recursos necessários.

Verifique o Terraform:

```bash
terraform --version
```

Verifique a AWS CLI:

```bash
aws --version
```

Verifique a conta autenticada:

```bash
aws sts get-caller-identity
```

---

## 10. Região AWS

Região utilizada:

```text
<REGIAO_AWS>
```
---

## 11. Backend remoto

O Terraform utiliza backend remoto para armazenamento do state.

O state é armazenado em um bucket S3 separado do bucket utilizado pelo Data Lake.

O controle de lock utiliza DynamoDB.

Configuração:

```text
Terraform
    │
    ├── S3 → Terraform State
    │
    └── DynamoDB → Lock
```
---

## 12. Terraform Workspace

O projeto utiliza Terraform Workspace.

Exemplo de criação:

```bash
terraform workspace new dev
```

Caso já exista:

```bash
terraform workspace select dev
```

Para verificar:

```bash
terraform workspace show
```

---

## 13. Deploy

Entre na pasta da Parte 1:

```bash
cd parte-1
```

Inicialize o Terraform:

```bash
terraform init
```

Formate os arquivos:

```bash
terraform fmt -recursive
```

Valide:

```bash
terraform validate
```

Visualize o plano:

```bash
terraform plan
```

Crie a infraestrutura:

```bash
terraform apply
```

Após o `apply`, devem existir os recursos necessários para armazenamento, catálogo e consulta dos dados.

---

## 14. Dados no S3

Após a criação da infraestrutura, o dataset deverá estar disponível no bucket utilizado pelo Data Lake.

Exemplo:

```bash
aws s3 cp dados/agendamentos.csv s3://eda262-gNN-lake-trusted/
```

Para verificar:

```bash
aws s3 ls s3://eda262-gNN-lake-trusted/
```

---

## 15. Consulta analítica -- PONTOS FUTUROS

A consulta principal do projeto é:

```sql
SELECT
    especialidade,
    COUNT(*) AS total_consultas,
    SUM(
        CASE
            WHEN status = 'NO_SHOW' THEN 1
            ELSE 0
        END
    ) AS total_no_show,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN status = 'NO_SHOW' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS taxa_no_show
FROM agendamentos
WHERE status IN ('REALIZADO', 'NO_SHOW')
GROUP BY especialidade
ORDER BY taxa_no_show DESC;
```

A consulta responde:

> **Qual é a taxa de faltas (no-show) por especialidade da clínica?**

---

## 16. Custo da consulta

Após a execução no Athena será registrada a quantidade de dados processados pela consulta.

O Athena apresenta essa informação como:

```text
Data scanned
```

O valor medido será registrado no `DECISOES.md`.

Formato:

```text
Consulta:
Taxa de no-show por especialidade

Dados processados:
<VALOR_MEDIDO>

Custo estimado:
<VALOR_MEDIDO>
```

Os valores finais serão preenchidos após a execução real da consulta.

---

## 17. Script de verificação

O projeto possui o script:

```text
verificacao/verifica.sh
```

Ele existe para verificar os principais requisitos da entrega e imprimir resultados no formato:

```text
[PASSA] Bucket existe
[PASSA] Tags obrigatórias encontradas
[PASSA] Glue Database existe
[PASSA] Glue Table existe
[PASSA] Athena Workgroup existe
```

Para executar:

```bash
chmod +x verificacao/verifica.sh
./verificacao/verifica.sh
```

A saída será armazenada como evidência da entrega.

---

## 18. Destroy

A infraestrutura principal deve poder ser removida completamente utilizando Terraform.

Na pasta `parte-1`:

```bash
terraform destroy
```

Após a execução, deverá ser verificado se não permaneceram recursos órfãos relacionados ao projeto.

O processo de destroy faz parte dos critérios de aceite da Parte 1.

---

## 19. Evidências

Para a Parte 1 foram armazenadas evidências de:

* execução do `verifica.sh`;
* resultado da consulta no Athena;
* dados processados pela consulta;
* custo estimado;
* funcionamento da infraestrutura.

---

## 20. DECISOES.md

O arquivo `DECISOES.md` registra as principais decisões de engenharia da Parte 1:

* cenário;
* pergunta de negócio;
* evento;
* grão;
* schema;
* regra de cálculo da taxa de no-show;
* tratamento dos dados;
* infraestrutura;
* backend remoto;
* workspace;
* SQL utilizada;
* quantidade de dados processados;
* custo da consulta;
* destroy.

---

## 21. Fora do escopo da Parte 1

Nesta entrega não serão implementados como requisitos:

* Parquet;
* particionamento;
* idempotência;
* pipelines ETL complexos;
* Lambda;
* Step Functions;
* EMR;
* ECS;
* Kinesis.

Esses itens não fazem parte dos requisitos avaliados na Parte 1.

---

## 22. Identificação

**Disciplina:** EDA262 — Engenharia de Dados
**Entrega:** Parte 1 — AV1
**Cenário:** Análise de faltas em agendamentos de clínica
**Slug:** `clinica-no-show`
**Grupo:** `gNN`
