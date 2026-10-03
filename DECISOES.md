# DECISOES.md

## Cenário
Rede nacional de clínicas com várias unidades e sistemas de origem heterogêneos.

## Pergunta
**Qual é o impacto financeiro mensal dos no-shows na rede de clínicas e como esse impacto
se distribui por perfil demográfico dos pacientes, unidade e especialidade?**

## Evento
Um agendamento de consulta.

## Grão
**1 registro = 1 agendamento de consulta em uma unidade da rede.**

## Normalização
O projeto gera dados brutos provenientes de três sistemas distintos e os normaliza localmente
antes do envio do dataset trusted ao S3.

Regras a documentar:
- sexo;
- status;
- especialidade;
- datas;
- valores;
- canais;
- IDs;
- duplicidades.

## Métricas
Taxa de no-show:
`NO_SHOW / (REALIZADO + NO_SHOW) * 100`

Impacto financeiro estimado:
`SUM(valor_consulta) WHERE status = 'NO_SHOW'`

## Pontos a completar
- justificativa dos tipos do schema;
- módulo Terraform;
- backend remoto;
- workspace;
- resultado da consulta;
- Data scanned;
- custo;
- destroy limpo.
