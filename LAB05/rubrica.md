# Rubrica — Exercício 05 (Aula 25): o pipeline que pode rodar de novo

Pública desde a Aula 24. É a mesma tabela do `enunciado.html` e a que o `verifica.sh` imprime.
Sem nota própria: é o segundo incremento da Parte 2 do projeto (AV2).

| # | Critério | Como é verificado | Peso |
| --- | --- | --- | --- |
| 0 | Terraform com backend remoto; a trusted `corridas` declarada como Parquet | `verifica.sh` (estado do backend + Glue API) | **elimina** |
| 1 | **A resposta certa:** a madrugada dos últimos 7 dias tem **11.137** corridas — com a madrugada atrasada e sem o reenvio contado duas vezes | `verifica.sh` · Athena | 20% |
| 2 | **Rodar de novo não muda nada:** o `verifica.sh` roda o job mais uma vez; linhas e madrugada iguais antes e depois | `verifica.sh` · Glue + Athena | 25% |
| 3 | **Uma linha por corrida:** `count(*)` = `count(DISTINCT corrida_id)` = 518.400 | `verifica.sh` · Athena | 15% |
| 4 | **A infraestrutura também é idempotente:** `terraform plan` limpo depois do apply | `verifica.sh` · `plan -detailed-exitcode` | 10% |
| 5 | `destroy` limpo: nenhum recurso `eda-a25-<sufixo>` sobra | `verifica.sh --pos-destroy` | 10% |
| 6 | `DECISOES.md`: uma frase e **um número medido** por decisão (as três do código e a quarta, do backfill) | leitura | 20% |

**O critério 2 é o exercício.** Ele roda o job de novo, de verdade, e compara. Igual passa;
diferente reprova. Nada de argumentação.

**O que mais reprova**

1. `append`: a segunda execução dobra a tabela — o critério 2 e o 3 caem juntos.
2. `sobrescrever` sem chave: rodar de novo não muda nada (o 2 passa), mas o reenvio fica
   contado duas vezes — o 1 e o 3 caem.
3. Janela menor que o atraso: idempotente e sem duplicata, mas a madrugada atrasada fica de
   fora — o 1 cai.
4. Recurso órfão depois do destroy — o 5 cai inteiro.

**O que não conta na nota:** elegância do HCL, recursos extras que ninguém pediu, e ter chegado
à mesma escolha do lab. Uma janela diferente da do lab, bem justificada e com número, vale 10.

**Entrega:** PR com `terraform/` (sem `terraform.tfvars` de outro grupo, sem `backend.hcl`,
sem `.terraform/`, sem `*.tfstate`), `DECISOES.md` e a saída do `verifica.sh` colada.
Fora do prazo, nota inicial 8,0.
