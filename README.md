# Engenharia de Dados — Grupo 05

Projeto desenvolvido para a **Parte 1 — AV1** da disciplina de Engenharia de Dados.

O objetivo é provisionar, utilizando **Terraform**, um Data Lake na AWS capaz de responder a uma pergunta de negócio relacionada ao impacto financeiro de faltas em consultas médicas, mantendo schema explícito, state remoto, workspace e medição do custo da consulta no Amazon Athena.

## Cenário

A rede de clínicas possui unidades distribuídas pelo Brasil e sistemas de origem heterogêneos, nos quais informações equivalentes podem ser registradas de maneiras diferentes.

Para representar esse cenário, foram gerados dados sintéticos provenientes de três sistemas distintos. Esses dados passam por uma etapa local de normalização antes de formar o dataset confiável utilizado pela infraestrutura da AV1.

Exemplos de normalização:

- `M`, `Masculino` e `MALE` → `MASCULINO`;
- `No-Show`, `FALTOU` e `AUSENTE` → `NO_SHOW`;
- diferentes formatos de datas → `YYYY-MM-DD`;
- diferentes representações monetárias → formato decimal padronizado;
- nomes diferentes para a mesma especialidade → nomenclatura única.

A normalização é realizada localmente e não representa uma arquitetura de camadas na AWS.

## Pergunta de negócio

> **Qual é o impacto financeiro mensal dos no-shows na rede de clínicas e como esse impacto se distribui por perfil demográfico dos pacientes, unidade e especialidade?**

O impacto financeiro utilizado neste projeto representa uma **estimativa de receita potencial não realizada associada aos horários reservados em que houve no-show**.

## Evento e grão

O evento analisado é um agendamento de consulta realizado em uma unidade da rede.

**Grão da tabela trusted:**

> **1 registro = 1 agendamento de consulta em uma unidade da rede.**

A chave identificadora do evento é:

```text
agendamento_id
```

## Dataset

O dataset final possui **10.000 agendamentos sintéticos**.

Os dados pessoais diretamente identificáveis não são utilizados. Os pacientes são representados por identificadores anonimizados.

Principais atributos:

| Campo | Tipo |
|---|---|
| agendamento_id | string |
| paciente_id | string |
| unidade_id | string |
| estado_unidade | string |
| regiao_unidade | string |
| sexo | string |
| faixa_etaria | string |
| especialidade | string |
| profissional_id | string |
| data_agendamento | date |
| data_consulta | date |
| hora_consulta | string |
| status | string |
| canal_agendamento | string |
| tipo_consulta | string |
| valor_consulta | decimal(10,2) |
| dias_antecedencia | int |
| no_shows_anteriores | int |
| sistema_origem | string |

O schema é declarado explicitamente no Terraform. **Não é utilizado Glue Crawler para inferência de schema.**

## Fluxo de dados

```text
Sistemas A, B e C
       │
       ▼
dados/origem/*.csv
       │
       ▼
normalizar_agendamentos.py
       │
       ▼
dados/trusted/agendamentos.csv
       │
       ▼
Amazon S3
       │
       ▼
AWS Glue Data Catalog
       │
       ▼
Amazon Athena
       │
       ▼
Consulta de negócio
```

## Arquitetura AWS

A infraestrutura utilizada na AV1 é composta por:

```text
Terraform
   │
   ├── S3 — Dataset trusted
   │       └── agendamentos_csv/agendamentos.csv
   │
   ├── S3 — Resultados do Athena
   │
   ├── Glue Data Catalog
   │       ├── Database: eda262_g05_clinica
   │       └── Table: agendamentos
   │
   └── Athena
           └── Workgroup: eda262-g05-athena
```

Recursos principais:

```text
eda262-g05-lake-trusted
eda262-g05-athena-results
eda262_g05_clinica
agendamentos
eda262-g05-athena
```

O dataset CSV utilizado pela tabela está em:

```text
s3://eda262-g05-lake-trusted/agendamentos_csv/agendamentos.csv
```

## Terraform

A infraestrutura principal foi organizada em módulo:

```text
parte-1/
├── modules/
│   └── lake/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── versions.tf
├── backend.hcl.example
└── terraform.tfvars.example
```

O projeto utiliza backend remoto com:

```text
S3:      eda262-g05-tfstate
DynamoDB: eda262-g05-tflock
```

Workspace utilizado:

```text
dev
```

O state correspondente ao workspace está armazenado remotamente.

## Tags

Os recursos utilizam as tags:

```hcl
turma   = "eda262"
grupo   = "g05"
projeto = "engenharia-de-dados"
```

## Consulta principal

```sql
SELECT
    year(data_consulta) AS ano,
    month(data_consulta) AS mes,
    faixa_etaria,
    sexo,
    unidade_id,
    especialidade,
    COUNT(*) AS total_consultas,
    SUM(
        CASE
            WHEN status = 'NO_SHOW' THEN 1
            ELSE 0
        END
    ) AS total_no_shows,
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN status = 'NO_SHOW' THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS taxa_no_show,
    ROUND(
        SUM(
            CASE
                WHEN status = 'NO_SHOW' THEN valor_consulta
                ELSE 0
            END
        ),
        2
    ) AS impacto_financeiro
FROM agendamentos
WHERE status IN ('REALIZADO', 'NO_SHOW')
GROUP BY
    year(data_consulta),
    month(data_consulta),
    faixa_etaria,
    sexo,
    unidade_id,
    especialidade
ORDER BY impacto_financeiro DESC;
```

Para o cálculo da taxa de no-show são considerados somente:

```text
REALIZADO
NO_SHOW
```

Status como `CANCELADO` não são tratados como ausência do paciente.

## Resultado obtido

No conjunto sintético analisado:

```text
Registros do dataset:             10.000
Consultas consideradas:            8.367
No-shows:                          1.214
Taxa geral de no-show:            14,51%
Impacto financeiro estimado: R$ 351.607,97
```

Os resultados permitem analisar como os no-shows se distribuem por:

```text
mês
faixa etária
sexo
unidade
especialidade
```

Os padrões encontrados representam exclusivamente o **dataset sintético criado para o projeto** e não devem ser interpretados como conclusões sobre pacientes reais ou relações causais.

## Custo da consulta

A execução da consulta principal no Amazon Athena apresentou:

```text
Linhas de entrada:       10.000
Dados processados:       729,61 KB
Linhas de saída:         aproximadamente 4,51 mil
Tempo total:             1,2 s
```

Considerando a cobrança mínima aplicável por consulta do Athena, o custo estimado da execução foi de aproximadamente:

```text
US$ 0,00005
```
### Cálculo da taxa de no-show

A taxa de no-show considera somente consultas cujo status final é
`REALIZADO` ou `NO_SHOW`.

Taxa de no-show = NO_SHOW / (REALIZADO + NO_SHOW) × 100

Consultas canceladas não são consideradas faltas e, portanto, são
excluídas do cálculo.

No conjunto analisado:

- Consultas consideradas: 8.367
- No-shows: 1.214
- Taxa de no-show: 14,51%

A evidência das estatísticas da consulta encontra-se no diretório:

```text
evidencias/
```

## Validação da infraestrutura

Após a aplicação e validação dos recursos, foi executado:

```powershell
terraform plan
```

Resultado:

```text
No changes. Your infrastructure matches the configuration.
```

Isso demonstra que o código Terraform, o state remoto e os recursos provisionados estão sincronizados.

## Execução

Inicialização do backend:

```powershell
terraform init -reconfigure "-backend-config=.\backend.hcl"
```

Seleção do workspace:

```powershell
terraform workspace select dev
```

Validação:

```powershell
terraform fmt -recursive
terraform validate
terraform plan
```

Aplicação:

```powershell
terraform apply
```

## Verificação do workspace

```powershell
terraform workspace show
```

Resultado esperado:

```text
dev
```

## Destruição da infraestrutura

Antes da destruição:

```powershell
terraform plan -destroy
```

Para remover os recursos gerenciados pela stack:

```powershell
terraform destroy
```

Após a destruição, os recursos devem ser verificados para confirmar que não permaneceram recursos órfãos.

O backend remoto é tratado separadamente da stack principal, pois armazena o próprio state utilizado pelo Terraform.

## Escopo da AV1

Atendidos:

- provisionamento em Terraform;
- bucket S3;
- Glue Data Catalog;
- schema explicitamente declarado em IaC;
- Athena Workgroup;
- módulo Terraform;
- backend remoto S3 + DynamoDB;
- workspace `dev`;
- tabela trusted com grão declarado;
- consulta de negócio executada no Athena;
- custo da consulta medido;
- validação com `terraform plan` sem alterações.

Fora do escopo desta etapa:

- Glue Crawler;
- Glue ETL Jobs;
- Parquet;
- particionamento;
- arquitetura de camadas;
- idempotência de pipelines;
- processamento distribuído.

## Estrutura do repositório

```text
eda2026-projeto-g05/
├── parte-1/
│   ├── bootstrap/
│   ├── modules/
│   │   └── lake/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── versions.tf
│   ├── backend.hcl.example
│   └── terraform.tfvars.example
├── dados/
│   ├── gerar_agendamentos.py
│   ├── normalizar_agendamentos.py
│   ├── origem/
│   └── trusted/
├── consultas/
├── verificacao/
├── evidencias/
├── DECISOES.md
├── README.md
└── .gitignore
```

## Checklist AV1

- [x] S3 provisionado em Terraform
- [x] Glue Data Catalog provisionado em Terraform
- [x] Athena Workgroup provisionado em Terraform
- [x] Schema declarado no IaC
- [x] Sem Glue Crawler
- [x] Stack organizada em módulo
- [x] Backend remoto em S3
- [x] Lock com DynamoDB
- [x] Workspace `dev`
- [x] Tabela trusted definida
- [x] Grão declarado
- [x] Pergunta de negócio respondida
- [x] Consulta executada no Athena
- [x] Dados processados registrados
- [x] Custo estimado registrado
- [x] `terraform plan` retornando `No changes`
- [ ] `terraform destroy` validado sem recursos órfãos