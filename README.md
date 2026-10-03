# eda2026-projeto-g05

# EDA — Projeto de Engenharia de Dados

## Análise de Perfil, Sazonalidade e Impacto Financeiro de No-Shows em uma Rede de Clínicas

Projeto desenvolvido para a disciplina **EDA — Engenharia de Dados**.

A Parte 1 do projeto tem como objetivo provisionar, utilizando **100% Terraform**, um Data Lake na AWS capaz de armazenar, catalogar e consultar dados de agendamentos de uma grande rede de clínicas.

A solução busca analisar o comportamento de pacientes que agendam consultas e não comparecem, identificando padrões relacionados ao perfil dos pacientes, unidades, especialidades e períodos do ano, além de estimar o impacto financeiro mensal causado pelos no-shows.

---

# 1. Cenário

O cenário representa uma **grande rede de clínicas com unidades distribuídas por diferentes regiões do Brasil**.

Cada unidade realiza diariamente diversos agendamentos de consultas médicas e registra informações relacionadas aos pacientes, profissionais, especialidades, datas, horários e resultado do atendimento.

Por se tratar de uma rede de grande porte, diferentes unidades podem utilizar sistemas e padrões distintos para registrar informações equivalentes.

Por exemplo, o sexo de um paciente pode ser registrado como:

```text
M
Masculino
masculino
MALE
```

Enquanto o status de uma ausência pode aparecer como:

```text
NO_SHOW
No-Show
no_show
FALTOU
AUSENTE
```

Essas diferenças representam um problema de qualidade e padronização dos dados antes que eles possam ser utilizados em análises corporativas.

Além disso, a rede enfrenta um problema operacional relevante: pacientes que realizam o agendamento de uma consulta, mas não comparecem no dia e horário marcados.

Esse comportamento é denominado **no-show**.

Quando ocorre um no-show, um horário que poderia ter sido utilizado por outro paciente permanece ocioso, gerando desperdício da capacidade de atendimento e impacto financeiro para a clínica.

O projeto busca consolidar essas informações para entender:

- quem são os pacientes que apresentam maior ocorrência de no-show;
- em quais unidades o problema é mais frequente;
- quais especialidades apresentam maior taxa de faltas;
- em quais períodos do ano as faltas aumentam;
- quanto os horários não utilizados representam financeiramente para a rede.

O slug definido para o cenário é:

```text
clinica-no-show
```

---

# 2. Problema de negócio

Uma grande rede de clínicas pode realizar milhares de agendamentos todos os meses.

Mesmo uma taxa relativamente pequena de pacientes que não comparecem pode representar uma quantidade significativa de horários ociosos quando analisada em escala nacional.

Conhecer somente a quantidade de faltas, entretanto, não é suficiente para compreender o problema.

É necessário relacionar os no-shows com características dos agendamentos e dos pacientes, como:

- faixa etária;
- sexo;
- unidade;
- estado;
- região;
- especialidade;
- canal de agendamento;
- tipo de consulta;
- antecedência do agendamento;
- histórico de faltas;
- mês da consulta.

Também é necessário relacionar essas ausências ao valor financeiro associado ao horário reservado.

Dessa forma, o projeto busca transformar dados operacionais de agendamentos em informações que permitam compreender **perfil, sazonalidade e impacto financeiro dos no-shows**.

---

# 3. Pergunta de negócio

A pergunta analítica principal do projeto é:

> **Qual é o impacto financeiro mensal dos no-shows na rede de clínicas e como esse impacto se distribui por perfil demográfico dos pacientes, unidade e especialidade?**

A partir dessa pergunta principal, a análise também permitirá responder questões complementares, como:

- Qual é a taxa mensal de no-show da rede?
- Quais faixas etárias apresentam maior taxa de no-show?
- Existe diferença na taxa de no-show entre os sexos registrados?
- Quais unidades apresentam maior ocorrência de faltas?
- Quais unidades apresentam maior impacto financeiro?
- Quais especialidades apresentam maior taxa de no-show?
- Quais especialidades representam maior impacto financeiro?
- Existem meses do ano com maior concentração de faltas?
- Determinados canais de agendamento apresentam maior taxa de no-show?
- Pacientes com histórico anterior de faltas apresentam maior recorrência?

As consultas serão executadas utilizando o **Amazon Athena**.

As análises buscarão identificar associações e padrões existentes nos dados, sem estabelecer relações causais.

---

# 4. Evento analisado

O evento utilizado pelo projeto é:

> **Um agendamento de consulta realizado em uma das unidades da rede de clínicas.**

Cada registro representa um evento de agendamento e contém informações relacionadas:

- ao paciente;
- à unidade;
- à especialidade;
- ao profissional;
- à data e horário;
- ao canal de agendamento;
- ao resultado da consulta;
- ao valor associado ao atendimento.

---

# 5. Grão da tabela trusted

O grão da tabela `agendamentos` é:

> **1 registro = 1 agendamento de consulta em uma unidade da rede.**

Cada registro possui um identificador único:

```text
agendamento_id
```

Esse grão permite relacionar cada agendamento individualmente com:

- perfil do paciente;
- unidade;
- especialidade;
- profissional;
- período;
- status;
- histórico de faltas;
- valor da consulta.

A partir desse nível de detalhe, será possível realizar diferentes agregações no Amazon Athena sem perder as informações necessárias para responder à pergunta de negócio.

---

# 6. Perfil analisado

O projeto utiliza um **perfil demográfico e comportamental relacionado ao processo de agendamento**.

Não serão utilizadas características psicológicas ou classificações de personalidade.

O perfil será construído a partir de atributos como:

```text
faixa_etaria
sexo
canal_agendamento
tipo_consulta
dias_antecedencia
no_shows_anteriores
unidade_id
estado_unidade
regiao_unidade
especialidade
```

Essas informações permitirão identificar padrões nos grupos que apresentam maior ou menor taxa de ausência.

Por exemplo, após a execução das consultas, poderá ser identificado que determinada faixa etária apresenta uma taxa de no-show superior à média da rede.

Qualquer conclusão desse tipo será obtida somente a partir dos resultados efetivamente encontrados no conjunto de dados.

---

# 7. Métricas

O projeto trabalhará com três métricas principais.

## 7.1 Taxa de no-show

Para o cálculo da taxa de no-show serão consideradas apenas consultas cujo resultado já é conhecido:

```text
REALIZADO
NO_SHOW
```

Consultas com status:

```text
AGENDADO
CONFIRMADO
CANCELADO
```

não serão utilizadas no denominador da taxa.

A métrica será:

```text
                 quantidade de NO_SHOW
Taxa no-show = --------------------------- × 100
               REALIZADO + NO_SHOW
```

Essa abordagem evita que consultas canceladas ou ainda não realizadas reduzam artificialmente a taxa de faltas.

---

## 7.2 Quantidade de no-shows

Também será analisada a quantidade absoluta de agendamentos com:

```text
status = 'NO_SHOW'
```

Essa métrica será utilizada principalmente para compreender o volume de faltas por:

- mês;
- unidade;
- especialidade;
- perfil.

A quantidade absoluta será analisada juntamente com a taxa de no-show para evitar interpretações incorretas.

---

## 7.3 Impacto financeiro estimado

Cada consulta possui um valor associado ao horário reservado.

Quando um paciente não comparece, esse valor será considerado como **impacto financeiro estimado do no-show**.

A métrica utilizada será:

```text
Impacto financeiro =
SUM(valor_consulta)
WHERE status = 'NO_SHOW'
```

Por exemplo:

```text
Valor da consulta: R$ 250,00
Status: NO_SHOW

Impacto financeiro estimado: R$ 250,00
```

Caso ocorram 2.000 no-shows em um mês com valor médio de R$ 220,00:

```text
2.000 × R$ 220,00 = R$ 440.000,00
```

Neste projeto, o valor será tratado como **impacto financeiro estimado associado aos horários reservados e não utilizados**.

Esse valor não representa necessariamente um prejuízo contábil integral da clínica.

---

# 8. Tabela trusted

A tabela utilizada no projeto será chamada:

```text
agendamentos
```

O schema será declarado diretamente no Terraform.

| Campo | Tipo | Descrição |
|---|---|---|
| `agendamento_id` | string | Identificador único do agendamento |
| `paciente_id` | string | Identificador anonimizado do paciente |
| `unidade_id` | string | Identificador padronizado da unidade |
| `estado_unidade` | string | Estado onde a unidade está localizada |
| `regiao_unidade` | string | Região geográfica da unidade |
| `sexo` | string | Sexo registrado no cadastro |
| `faixa_etaria` | string | Faixa etária do paciente |
| `especialidade` | string | Especialidade médica |
| `profissional_id` | string | Identificador do profissional |
| `data_agendamento` | date | Data em que o agendamento foi realizado |
| `data_consulta` | date | Data prevista para a consulta |
| `hora_consulta` | string | Horário da consulta |
| `status` | string | Status final ou atual do agendamento |
| `canal_agendamento` | string | Canal utilizado para realizar o agendamento |
| `tipo_consulta` | string | Tipo da consulta |
| `valor_consulta` | decimal | Valor associado à consulta |
| `dias_antecedencia` | integer | Quantidade de dias entre agendamento e consulta |
| `no_shows_anteriores` | integer | Quantidade de faltas anteriores do paciente |
| `sistema_origem` | string | Identificação do sistema de origem do registro |

Dados como nome completo, CPF, telefone e endereço não são necessários para responder à pergunta de negócio e não fazem parte do conjunto analítico.

---

# 9. Exemplo do dataset

```csv
agendamento_id,paciente_id,unidade_id,estado_unidade,regiao_unidade,sexo,faixa_etaria,especialidade,profissional_id,data_agendamento,data_consulta,hora_consulta,status,canal_agendamento,tipo_consulta,valor_consulta,dias_antecedencia,no_shows_anteriores,sistema_origem
A000001,P0001,U001,PE,Nordeste,MASCULINO,22-30,Cardiologia,M001,2026-06-01,2026-06-15,08:00,NO_SHOW,APP,ROTINA,250.00,14,2,SISTEMA_A
A000002,P0002,U008,SP,Sudeste,FEMININO,31-45,Dermatologia,M017,2026-06-03,2026-06-20,10:30,REALIZADO,SITE,RETORNO,180.00,17,0,SISTEMA_B
A000003,P0003,U014,RJ,Sudeste,MASCULINO,22-30,Ortopedia,M030,2026-11-10,2026-12-05,14:00,NO_SHOW,TELEFONE,ROTINA,320.00,25,1,SISTEMA_C
```

---

# 10. Qualidade e normalização dos dados

Como a rede possui diferentes unidades e sistemas, o cenário permite a existência de inconsistências plausíveis nos dados de origem.

Para a Parte 1, o projeto utilizará um **dataset trusted já padronizado**.

A construção de uma arquitetura de camadas ou pipeline automatizado de transformação não faz parte do escopo desta entrega.

As regras utilizadas para padronizar os dados serão documentadas no arquivo `DECISOES.md`.

---

## 10.1 Sexo

Exemplos encontrados na origem:

```text
M
Masc
Masculino
masculino
MALE
```

Valor padronizado:

```text
MASCULINO
```

Outro exemplo:

```text
F
Fem
Feminino
feminino
FEMALE
```

Valor padronizado:

```text
FEMININO
```

---

## 10.2 Status

Dados de origem:

```text
NO_SHOW
No-Show
no_show
FALTOU
AUSENTE
```

Valor trusted:

```text
NO_SHOW
```

---

## 10.3 Especialidade

Dados de origem:

```text
Cardiologia
cardiologia
CARDIOLOGIA
Cardio
CARD
```

Valor trusted:

```text
Cardiologia
```

---

## 10.4 Datas

Dados de origem:

```text
15/07/2026
2026-07-15
15-07-2026
```

Valor trusted:

```text
2026-07-15
```

---

## 10.5 Valores monetários

Dados de origem:

```text
250
250.00
250,00
R$ 250,00
```

Valor trusted:

```text
250.00
```

---

## 10.6 Canal de agendamento

Dados de origem:

```text
app
APP
Aplicativo
mobile
```

Valor trusted:

```text
APP
```

---

## 10.7 Duplicidade

Também podem existir registros repetidos com o mesmo:

```text
agendamento_id
```

Essas duplicidades devem ser eliminadas do dataset trusted para evitar que uma mesma consulta seja contabilizada mais de uma vez.

---

# 11. Faixas etárias

Para permitir análises por perfil, os pacientes serão agrupados em faixas etárias.

As categorias utilizadas serão:

```text
0-17
18-21
22-30
31-45
46-60
61+
```

A faixa etária já estará presente no dataset trusted utilizado pela Parte 1.

---

# 12. Arquitetura da Parte 1

A infraestrutura da Parte 1 utiliza:

- Amazon S3;
- AWS Glue Data Catalog;
- AWS Glue Database;
- AWS Glue Table;
- Amazon Athena;
- Athena Workgroup;
- Terraform;
- Amazon S3 para armazenamento remoto do Terraform State;
- DynamoDB para controle de lock;
- Terraform Workspace.

O fluxo principal será:

```text
Dados das diferentes unidades
            │
            ▼
Padronização dos dados
            │
            ▼
      Dataset Trusted
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
Glue Table: agendamentos
            │
            ▼
      Amazon Athena
            │
            ▼
    Consultas analíticas
            │
    ┌───────┼───────────┐
    ▼       ▼           ▼
 Perfil  Sazonalidade  Impacto
No-show               financeiro
```

O **schema da Glue Table será declarado diretamente no código Terraform**.

Não será utilizado Glue Crawler.

---

# 13. Infraestrutura provisionada

O Terraform será responsável por provisionar do zero:

```text
Amazon S3
AWS Glue Database
AWS Glue Table
Amazon Athena Workgroup
```

A stack será organizada em módulo Terraform.

Também será utilizado:

```text
S3 + DynamoDB
```

para o backend remoto do Terraform.

---

# 14. Organização do repositório

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
│
├── verificacao/
│   └── verifica.sh
│
├── DECISO
