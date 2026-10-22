# Nota: falso positivo no Critério 6 no macOS

O `verificacao/verifica.sh --pos-destroy` imprimiu `PASSA [6]`, mas com o sufixo vazio:

```
PASSA  [6]  (10%)  nenhum recurso eda-a21-*- sobrou.
```

Sem o sufixo, o script procurou recursos chamados `eda-a21-lake-`, `eda_a21_` etc., que não existem em conta nenhuma. O `PASSA` saiu sem conferir nada.

## A causa

A função `tfvar` do script lê o sufixo do `terraform.tfvars` com `\s` nas expressões regulares do `grep -E` e do `sed -E`. O `grep` e o `sed` do macOS (BSD) não reconhecem `\s`, então a linha `sufixo = "grupo05"` não casa, e o sufixo volta vazio. Num Linux, com o grep e o sed do GNU, o script funciona. A mesma regex com `[[:space:]]` no lugar de `\s` lê `grupo05` corretamente no macOS.

## A conferência de verdade

O script não foi alterado. Rodei à mão as mesmas 5 checagens do critério 6, com o sufixo correto, depois do `terraform destroy`:

| Recurso | Nome | Resultado |
|---|---|---|
| Bucket | `eda-a21-lake-grupo05` | não existe |
| Job Glue | `eda-a21-trusted-grupo05` | não existe |
| Database | `eda_a21_grupo05` | não existe |
| Workgroup | `eda-a21-wg-grupo05` | não existe |
| Papel IAM | `eda-a21-glue-grupo05` | não existe |

O state do lab no backend (`aula21/grupo-05/terraform.tfstate`) ficou sem nenhum recurso. Os recursos `eda-a21-*` que ainda aparecem na conta compartilhada são dos grupos 04 e 08.
