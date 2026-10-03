# eda2026-projeto-g05

## EDA — Projeto de Engenharia de Dados  
### Análise de No-Show em uma Rede de Clínicas

Projeto desenvolvido para a disciplina **EDA — Engenharia de Dados**.

A Parte 1 tem como objetivo provisionar, utilizando **100% Terraform**, um Data Lake na AWS capaz de armazenar, catalogar e consultar dados de agendamentos de uma grande rede de clínicas.

A análise busca identificar **quem mais falta às consultas, quando essas faltas acontecem e qual o impacto financeiro mensal estimado dos no-shows**.

---

## 1. Cenário

O cenário representa uma **rede de clínicas com unidades distribuídas pelo Brasil**.

Cada unidade registra agendamentos de consultas, porém diferentes sistemas podem representar os mesmos dados de formas distintas.

Exemplos:

```text
M | Masculino | MALE
NO_SHOW | No-Show | FALTOU
Cardiologia | CARDIOLOGIA | Cardio
```

Esses valores são normalizados antes da utilização do dataset trusted.

Além da inconsistência entre unidades, a rede enfrenta o problema de pacientes que agendam consultas e não comparecem, situação denominada **no-show**.

---

## 2. Pergunta de negócio

> **Qual é o impacto financeiro mensal dos no-shows na rede de clínicas e como esse impacto se distribui por perfil demográfico dos pacientes, unidade e especialidade?**

A análise também permite observar:

- faixa etária;
- sexo;
- unidade e região;
- especialidade;
- canal de agendamento;
- histórico de faltas;
- sazonalidade mensal.

As conclusões são baseadas nos resultados encontrados nos dados, sem pressupor previamente qual perfil apresenta mais faltas.

---

## 3. Evento e grão

**Evento:** um agendamento de consulta.

**Grão da tabela trusted:**

> **1 registro = 1 agendamento de consulta em uma unidade da rede.**

Cada agendamento é identificado por:

```text
agendamento_id
```

Esse nível de detalhe permite realizar agregações posteriores por paciente, mês, unidade, especialidade e perfil.

---

## 4. Métricas

### Taxa de no-show

São consideradas apenas consultas com resultado conhecido:

```text
REALIZADO
NO_SHOW
```

A fórmula é:

```text
                 quantidade de NO_SHOW
Taxa no-show = --------------------------- × 100
               REALIZADO + NO_SHOW
```

Status como `CANCELADO`, `AGENDADO` e `CONFIRMADO` não participam do cálculo.

### Impacto financeiro estimado

```text
SUM(valor_consulta)
WHERE status = 'NO_SHOW'
```

O valor representa a **receita potencial associada ao horário reservado e não utilizado**, não necessariamente o prejuízo contábil integral da clínica.

---

## 5. Tabela trusted

A tabela principal será:

```text
agendamentos
```

Schema:

| Campo | Tipo |
|---|---|
| `agendamento_id` | string |
| `paciente_id` | string |
| `unidade_id` | string |
| `estado_unidade` | string |
| `regiao_unidade` | string |
| `sexo` | string |
| `faixa_etaria` | string |
| `especialidade` | string |
| `profissional_id` | string |
| `data_agendamento` | date |
| `data_consulta` | date |
| `hora_consulta` | string |
| `status` | string |
| `canal_agendamento` | string |
| `tipo_consulta` | string |
| `valor_consulta` | decimal |
| `dias_antecedencia` | integer |
| `no_shows_anteriores` | integer |
| `sistema_origem` | string |

O schema é **declarado diretamente no Terraform**.

Não é utilizado Glue Crawler.

---

## 6. Qualidade dos dados

O cenário considera inconsistências plausíveis provenientes das diferentes unidades.

Exemplos:

```text
M / Masculino / MALE
→ MASCULINO

No-Show / FALTOU / AUSENTE
→ NO_SHOW

Cardio / CARDIOLOGIA
→ Cardiologia

R$ 250,00 / 250,00 / 250
→ 250.00
```

Também podem existir:

- datas em formatos diferentes;
- canais de agendamento inconsistentes;
- registros duplicados pelo `agendamento_id`.

Para a Parte 1, será utilizado um **dataset trusted já normalizado**. A construção de pipelines e camadas não faz parte do escopo desta entrega.

As regras de normalização são documentadas no `DECISOES.md`.

---

## 7. Arquitetura

```text
Dataset trusted
      │
      ▼
  Amazon S3
      │
      ▼
Glue Data Catalog
      │
      ▼
 Glue Database
      │
      ▼
Glue Table
agendamentos
      │
      ▼
Amazon Athena
      │
      ▼
Consultas analíticas
      │
 ┌────┼───────────┐
 ▼    ▼           ▼
Perfil Sazonalidade Impacto
                  financeiro
```

Toda a infraestrutura é provisionada utilizando Terraform.

---

## 8. Requisitos da Parte 1

O projeto atende aos requisitos da AV1:

| Requisito | Implementação |
|---|---|
| Bucket | Amazon S3 |
| Catálogo | AWS Glue Data Catalog |
| Tabela trusted | `agendamentos` |
| Grão declarado | 1 linha = 1 agendamento |
| Schema no IaC | Declarado no Terraform |
| Crawler | Não utilizado |
| Workgroup | Amazon Athena Workgroup |
| Stack em módulo | `modules/data_lake/` |
| Backend remoto | S3 + DynamoDB |
| Workspace | Terraform Workspace |
| Consulta analítica | Amazon Athena |
| Custo | `Data scanned` + custo estimado |
| Destroy | Sem recursos órfãos |

---

## 9. Estrutura do repositório

```text
eda2026-projeto-g05/
│
├── parte-1/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── backend.tf
│   │
│   └── modules/
│       └── data_lake/
│           ├── main.tf
│           ├── variables.tf
│           └── outputs.tf
│
├── dados/
│   └── agendamentos.csv
│
├── consultas/
│   ├── analise_no_show.sql
│   ├── impacto_mensal.sql
│   └── sazonalidade.sql
│
├── evidencias/
├── verificacao/
│   └── verifica.sh
│
├── DECISOES.md
├── README.md
└── apresentacao-parte-1-g05.pdf
```

---

## 10. Backend remoto e workspace

O Terraform utiliza backend remoto:

```text
Terraform State → Amazon S3
State Lock      → DynamoDB
```

O bucket de state é separado do bucket do Data Lake.

O projeto também utiliza Terraform Workspace:

```bash
terraform workspace new dev
```

ou:

```bash
terraform workspace select dev
```

---

## 11. Tags obrigatórias

```hcl
tags = {
  turma   = "eda262"
  grupo   = "g05"
  projeto = "engenharia-de-dados"
}
```

---

## 12. Deploy

```bash
cd parte-1

terraform init

terraform workspace select dev

terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Após o `apply`, devem existir:

- bucket S3;
- Glue Database;
- Glue Table;
- Athena Workgroup.

---

## 13. Dataset no S3

Exemplo:

```bash
aws s3 cp dados/agendamentos.csv \
s3://eda2026-g05-lake-trusted/
```

Verificação:

```bash
aws s3 ls s3://eda2026-g05-lake-trusted/
```

---

## 14. Consulta principal

A consulta principal relaciona **mês, perfil, unidade, especialidade, taxa de no-show e impacto financeiro**.

```sql
SELECT
    YEAR(data_consulta) AS ano,
    MONTH(data_consulta) AS mes,
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
                WHEN status = 'NO_SHOW'
                THEN valor_consulta
                ELSE 0
            END
        ),
        2
    ) AS impacto_financeiro

FROM agendamentos

WHERE status IN ('REALIZADO', 'NO_SHOW')

GROUP BY
    YEAR(data_consulta),
    MONTH(data_consulta),
    faixa_etaria,
    sexo,
    unidade_id,
    especialidade

ORDER BY impacto_financeiro DESC;
```

A consulta responde à pergunta:

> **Qual é o impacto financeiro mensal dos no-shows na rede de clínicas e como esse impacto se distribui por perfil demográfico dos pacientes, unidade e especialidade?**

---

## 15. Custo da consulta

Após a execução no Athena serão registrados:

```text
Dados processados: <DATA_SCANNED>
Custo estimado:    <VALOR_MEDIDO>
```

Esses valores serão adicionados ao `DECISOES.md` e às evidências após a execução real.

---

## 16. Verificação

O script:

```text
verificacao/verifica.sh
```

verifica os principais critérios da entrega.

Exemplo de saída:

```text
[PASSA] Bucket existe
[PASSA] Tags obrigatórias encontradas
[PASSA] Glue Database existe
[PASSA] Glue Table existe
[PASSA] Athena Workgroup existe
```

Execução:

```bash
chmod +x verificacao/verifica.sh
./verificacao/verifica.sh
```

---

## 17. Destroy

A infraestrutura é completamente removível com:

```bash
terraform destroy
```

Após a execução, não devem permanecer recursos órfãos relacionados ao projeto.

---

## 18. Fora do escopo da Parte 1

Não fazem parte desta entrega:

- Parquet;
- particionamento;
- arquitetura de camadas;
- idempotência;
- Glue Crawler;
- Glue ETL;
- Lambda;
- Step Functions;
- EMR;
- ECS;
- Kinesis.

---

## 19. Identificação

**Disciplina:** EDA — Engenharia de Dados  
**Entrega:** Parte 1 — AV1  
**Grupo:** `g05`  
**Cenário:** Perfil, sazonalidade e impacto financeiro de no-shows em uma rede de clínicas  
**Slug:** `clinica-no-show`  
**Repositório:** `eda2026-projeto-g05`
