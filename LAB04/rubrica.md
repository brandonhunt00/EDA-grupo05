# Rubrica — Exercício 04 (Aula 21)

A trusted da startup em **Parquet particionado**, em Terraform, com uma **meta de
custo** para a pergunta da madrugada **declarada e provada**. Pública desde a Aula 20.

| # | Critério | Como é verificado | Peso |
| --- | --- | --- | --- |
| 0 | **Terraform com backend remoto; trusted declarada como Parquet** | `verifica.sh` | **elimina** |
| 1 | A trusted está particionada com `dt` como primeira chave e traz as 10 colunas | `verifica.sh` · Glue | 15% |
| 2 | O dado está completo: 518.400 corridas em 30 dias | `verifica.sh` · Athena | 10% |
| 3 | Sem arquivos pequenos: no máximo 4 arquivos por pasta de partição | `verifica.sh` · S3 | 10% |
| 4 | **A meta cabe em 1 MiB, e a pergunta da madrugada de 7 dias lê menos que ela — com a resposta certa (11.137 corridas)** | `verifica.sh` · Athena | **25%** |
| 5 | O teto do workgroup vale para todos (`enforce`) e **barra a consulta que lê todas as colunas** | `verifica.sh` · Athena | 10% |
| 6 | `destroy` limpo: nenhum recurso `eda-a21-*` sobra | `verifica.sh --pos-destroy` | 10% |
| 7 | `DECISOES.md`: uma frase por decisão (01 a 05), **cada uma com número medido** | leitura | 20% |

**O critério 4 é o exercício.** A diferença para o Lab 05 não é a ferramenta: é a
meta. O grupo diz quantos bytes a pergunta pode ler, e o Athena confirma ou desmente.

**A pergunta da madrugada (a mesma do ciclo):**

```sql
SELECT bairro, count(*) AS corridas, round(sum(valor), 2) AS receita
FROM <database>.<trusted>
WHERE dt >= '<hoje − 6>' AND faixa_hora BETWEEN 0 AND 5
GROUP BY bairro;
```

**Os outputs de contrato** (o `verifica.sh` lê estes nomes): `bucket_name` ·
`database_name` · `trusted_table_name` · `job_name` · `workgroup_name` ·
`chaves_particao` · `meta_bytes_madrugada` · `teto_bytes`.

**O que NÃO conta:** elegância do HCL; ter escolhido a mesma partição do Lab 05;
número de arquivos do repositório.

> Uma decisão **diferente** da do Lab 05, **bem justificada e com número**, vale 10.
> Uma decisão **igual**, **sem número**, não passa de 8.

**O que mais reprova**

1. **Meta folgada demais** — acima de 1 MiB o critério 4 cai, mesmo com a consulta barata.
2. **Filtrar por uma coluna de dentro do arquivo** em vez da chave do caminho — é o
   erro que não dá erro (Aula 19): a resposta sai certa, a leitura não.
3. **Esquecer de registrar as partições** (DECISÃO 05) — a contagem dá zero e os
   critérios 2 e 4 caem juntos.
4. **Teto acima da trusted inteira** — o freio nunca toca e o critério 5 cai.
5. Comitar `terraform.tfstate`, `.terraform/`, `terraform.tfvars` ou `backend.hcl`.

**Entrega.** PR com a pasta `terraform/`, o `DECISOES.md` e a saída do `verifica.sh`
colada. Rode o script antes de entregar: **a nota não é surpresa.** Fora do prazo,
nota inicial **8,0**.

> **Sem nota própria.** Este exercício é o **primeiro incremento da Parte 2 do
> projeto** (AV2): a trusted em Parquet particionado, com meta de custo, é o que a
> Parte 2 cobra. O `verifica.sh` vale como aceite; a nota cai no projeto.
