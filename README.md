# Engenharia de Dados — Grupo 05

Projeto desenvolvido para a **Parte 1 — AV1** da disciplina de Engenharia de Dados.

O objetivo é provisionar, utilizando **Terraform**, um Data Lake na AWS capaz de responder a uma pergunta de negócio relacionada ao impacto financeiro de faltas em consultas médicas, mantendo schema explícito, state remoto, workspace e medição do custo das consultas no Amazon Athena.

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

| Campo               | Tipo          |
| ------------------- | ------------- |
| agendamento_id      | string        |
| paciente_id         | string        |
| unidade_id          | string        |
| estado_unidade      | string        |
| regiao_unidade      | string        |
| sexo                | string        |
| faixa_etaria        | string        |
| especialidade       | string        |
| profissional_id     | string        |
| data_agendamento    | date          |
| data_consulta       | date          |
| hora_consulta       | string        |
| status              | string        |
| canal_agendamento   | string        |
| tipo_consulta       | string        |
| valor_consulta      | decimal(10,2) |
| dias_antecedencia   | int           |
| no_shows_anteriores | int           |
| sistema_origem      | string        |

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
Consultas de negócio
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
S3:       eda262-g05-tfstate
DynamoDB: eda262-g05-tflock
```

Workspace utilizado:

```text
dev
```

O state correspondente ao workspace é armazenado remotamente.

## Tags

Os recursos utilizam as tags:

```hcl
turma   = "eda262"
grupo   = "g05"
projeto = "engenharia-de-dados"
```

## Consulta principal

A consulta principal cruza período, perfil demográfico, unidade e especialidade, permitindo identificar a distribuição dos no-shows e de seu impacto financeiro estimado.

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

## Cálculo da taxa de no-show

A taxa de no-show considera somente consultas cujo status final é `REALIZADO` ou `NO_SHOW`.

```text
Taxa de no-show =
NO_SHOW
-------------------------- × 100
REALIZADO + NO_SHOW
```

Consultas com status `CANCELADO` não são consideradas faltas e, portanto, são excluídas tanto do numerador quanto do denominador.

No conjunto analisado:

```text
Consultas consideradas: 8.367
No-shows:                1.214

Taxa de no-show =
1.214 / 8.367 × 100
≈ 14,51%
```

Essa abordagem evita classificar cancelamentos previamente registrados como ausência do paciente.

## Consultas analíticas

Além da consulta principal, foram realizadas consultas complementares para responder separadamente a cada dimensão da pergunta de negócio.

### 1. KPI geral da rede

A primeira consulta sintetiza o tamanho geral do problema na rede.

Resultado:

```text
Consultas consideradas:       8.367
Total de no-shows:            1.214
Taxa geral de no-show:       14,51%
Impacto financeiro:    R$ 351.607,97
```

O resultado indica que, entre as consultas consideradas como efetivamente realizadas ou com ausência, **14,51% resultaram em no-show**.

O valor de **R$ 351.607,97** representa a soma dos valores associados às consultas com status `NO_SHOW`, sendo interpretado neste projeto como uma estimativa de receita potencial não realizada.

A execução gerou apenas uma linha de saída e teve runtime aproximado de **1,2 segundo**.

### 2. Evolução mensal

A consulta mensal permite avaliar quando os no-shows e seu impacto financeiro se concentram durante o ano.

Principais resultados:

| Mês       | Consultas | No-shows |   Taxa | Impacto financeiro |
| --------- | --------: | -------: | -----: | -----------------: |
| Janeiro   |       228 |       27 | 11,84% |        R$ 7.575,35 |
| Fevereiro |       510 |       66 | 12,94% |       R$ 18.728,62 |
| Março     |       794 |       92 | 11,59% |       R$ 27.571,89 |
| Abril     |       750 |      108 | 14,40% |       R$ 29.185,93 |
| Maio      |       799 |      125 | 15,64% |       R$ 36.783,87 |
| Junho     |       707 |      107 | 15,13% |       R$ 32.141,11 |
| Julho     |       771 |      134 | 17,38% |       R$ 38.696,00 |
| Agosto    |       762 |      105 | 13,78% |       R$ 30.802,87 |
| Setembro  |       707 |      100 | 14,14% |       R$ 28.755,84 |
| Outubro   |       791 |       92 | 11,63% |       R$ 26.837,56 |
| Novembro  |       752 |      115 | 15,29% |       R$ 33.815,62 |
| Dezembro  |       796 |      143 | 17,96% |       R$ 40.713,31 |

No conjunto sintético analisado, **dezembro apresentou a maior taxa de no-show, 17,96%, e o maior impacto financeiro mensal, R$ 40.713,31**.

Julho também apresentou concentração elevada, com taxa de **17,38%** e impacto estimado de **R$ 38.696,00**.

Esses resultados indicam uma associação temporal presente no dataset sintético, sem implicar relação causal.

### 3. Perfil demográfico

A terceira consulta agrupa os registros por `faixa_etaria` e `sexo`.

Entre os grupos analisados, destacaram-se:

| Faixa etária | Sexo      | Consultas | No-shows |   Taxa | Impacto financeiro |
| ------------ | --------- | --------: | -------: | -----: | -----------------: |
| 18–21        | MASCULINO |       161 |       29 | 18,01% |        R$ 8.163,40 |
| 22–30        | MASCULINO |       412 |       70 | 16,99% |       R$ 20.323,87 |
| 61+          | MASCULINO |     1.269 |      206 | 16,23% |       R$ 58.980,79 |
| 22–30        | FEMININO  |       451 |       71 | 15,74% |       R$ 20.572,36 |
| 31–45        | MASCULINO |       770 |      115 | 14,94% |       R$ 33.747,91 |

A maior taxa observada entre as combinações foi no grupo **18–21 / MASCULINO**, com **18,01%**.

Entretanto, taxa e impacto absoluto devem ser analisados separadamente. O grupo **61+ / MASCULINO**, por exemplo, apresentou uma taxa menor, de **16,23%**, mas concentrou **206 no-shows** e aproximadamente **R$ 58.980,79** de impacto devido ao maior volume de consultas.

Ao agregar os resultados por sexo:

```text
MASCULINO:
640 no-shows / 4.139 consultas ≈ 15,46%

FEMININO:
574 no-shows / 4.228 consultas ≈ 13,58%
```

Essas diferenças representam somente associações existentes no conjunto sintético analisado.

### 4. Concentração por unidade e especialidade

A quarta consulta identifica em quais combinações de unidade e especialidade o impacto financeiro se concentra.

O maior valor observado foi:

```text
Unidade:              U010
Especialidade:        Cardiologia
Consultas:            161
No-shows:             40
Taxa de no-show:      24,84%
Impacto financeiro:   R$ 12.880,65
```

Isso significa que, dentro desse recorte sintético, aproximadamente uma em cada quatro consultas de Cardiologia da unidade U010 resultou em no-show.

Outras combinações de Cardiologia também aparecem entre os maiores impactos, como U005 e U003.

Essa consulta possui uma interpretação operacional: além de mostrar o tamanho geral do problema, permite identificar **onde** os no-shows e o impacto financeiro estão mais concentrados dentro da rede.

A consulta retornou **50 combinações de unidade e especialidade**, com runtime aproximado de **949 milissegundos**.

## Síntese dos resultados

As consultas permitem responder à pergunta de negócio em quatro perspectivas complementares:

| Dimensão                | Resultado principal                                       |
| ----------------------- | --------------------------------------------------------- |
| Rede inteira            | 1.214 no-shows, taxa de 14,51% e R$ 351.607,97 de impacto |
| Período                 | Dezembro apresentou 17,96% e R$ 40.713,31                 |
| Perfil demográfico      | Maior taxa combinada em 18–21 / MASCULINO, com 18,01%     |
| Unidade + especialidade | U010 / Cardiologia apresentou 24,84% e R$ 12.880,65       |

Os resultados mostram que o impacto dos no-shows não está uniformemente distribuído no conjunto analisado.

Por se tratar de um **dataset sintético**, os padrões encontrados não devem ser interpretados como características de pacientes reais nem como evidência de causalidade. Eles foram produzidos para permitir a validação técnica da solução e a demonstração das análises propostas.

## Custo da consulta principal

A execução da consulta principal no Amazon Athena apresentou:

```text
Linhas de entrada:  10.000
Bytes de entrada:   729,61 KB
Linhas de saída:    aproximadamente 4,51 mil
Tempo total:        1,2 s
```

O volume processado ficou abaixo do mínimo faturável por consulta no modelo de cobrança por dados escaneados do Athena.

Considerando o mínimo de **10 MB por consulta** e o preço de referência de **US$ 5 por TB processado**, o custo estimado da execução é:

```text
10 MB / 1.048.576 MB × US$ 5
≈ US$ 0,0000477
≈ US$ 0,00005 por execução
```

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

Isso demonstra que, naquele momento, o código Terraform, o state remoto e os recursos provisionados estavam sincronizados.

## Execução

Inicialização do backend:

```powershell
terraform init -reconfigure "-backend-config=.\backend.hcl"
```

Seleção do workspace:

```powershell
terraform workspace select dev
```

Verificação:

```powershell
terraform workspace show
```

Resultado:

```text
dev
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

## Destruição da infraestrutura

Antes da destruição foi executado:

```powershell
terraform plan -destroy
```

O Terraform apresentou:

```text
Plan: 0 to add, 0 to change, 8 to destroy.
```

Foi então gerado e aplicado um plano de destruição:

```powershell
terraform plan -destroy -out=destroy.tfplan
terraform apply destroy.tfplan
```

Resultado:

```text
Apply complete! Resources: 0 added, 0 changed, 8 destroyed.
```

Foram removidos os recursos da stack principal:

```text
Athena Workgroup
Glue Database
Glue Table
S3 do dataset trusted
S3 de resultados do Athena
Public Access Block do bucket trusted
Public Access Block do bucket de resultados
Objeto agendamentos_csv/agendamentos.csv
```

Após a destruição, foram realizadas verificações adicionais.

O comando:

```powershell
terraform state list
```

não retornou recursos.

Também foram verificados:

```text
Amazon S3
AWS Glue Data Catalog
Amazon Athena
```

As verificações confirmaram que os recursos pertencentes à stack principal haviam sido removidos, sem recursos órfãos.

O backend remoto é tratado separadamente da stack principal, pois mantém o state utilizado pelo próprio Terraform:

```text
S3:       eda262-g05-tfstate
DynamoDB: eda262-g05-tflock
```

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
- pergunta de negócio respondida;
- consulta executada no Athena;
- custo da consulta medido;
- validação com `terraform plan` sem alterações;
- destruição limpa da stack principal.

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
- [x] `terraform destroy` validado sem recursos órfãos
