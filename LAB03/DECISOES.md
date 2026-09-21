# Decisões - Exercício 03 (Aula 12): refatorar em módulo, com plan limpo

Conta `eda-grupo05` (325583868777), região `us-east-1`, sufixo `grupo05`. Ponto de partida: a stack plana canônica do enunciado (6 recursos).

## DECISAO 01 - a fronteira do módulo

Os seis recursos da stack (dois buckets, o public access block do lake, o database, a tabela `corridas` e o workgroup) entraram em `modules/lake/` sem mudar nome nem propriedade. Na raiz ficaram só a chamada `module "lake"`, as variáveis, o provider com as tags, o `backend.tf` e os cinco outputs de contrato. Deixei os outputs e o provider fora do módulo porque o `verifica.sh` lê os nomes dos outputs na raiz e a região e as tags valem para a stack inteira; o módulo recebe apenas `sufixo` e `teto_bytes`, o mínimo de que os recursos precisam para existir.

## DECISAO 02 - mover o estado

Usei `terraform state mv`, um comando por recurso (seis), sem `moved {}`. Prefiro o `state mv` aqui porque a ordem fica explícita e visível: o plan antes dele mostrou `6 to add, 0 to change, 6 to destroy`, e depois dos seis comandos passou a `No changes`, o que mostra a causa e a cura. Aprendi que o `state mv` só mexe no endereço dentro do estado e não faz chamada à AWS. A desvantagem é que ele é manual e não fica no código: quem clonar o repositório e tiver um estado antigo não recebe o mapeamento, coisa que um bloco `moved {}` versionado resolveria.

## DECISAO 03 - workspace no lugar de pasta

Criei o workspace `dev` e voltei para o `default`, onde a stack migrada continua. O backend já separa o estado por workspace (`workspace_key_prefix = "eda-a12"`), então um workspace novo é o caminho para um ambiente novo com o mesmo código; uma pasta por ambiente duplicaria o código. A stack ficou no `default` porque passá-la para `dev` mudaria o caminho do estado, e eu teria que mover ou recriar tudo, o que o exercício proíbe. Mantive o `dev` existindo, vazio, porque é ele que prova o uso de um workspace nomeado. O custo é que o `default` vira um ambiente sem nome que alguém pode usar por engano.

## DECISAO 04 - o que o plan limpo prova

O `No changes` prova que o código em módulo descreve exatamente o que o estado registra: o Terraform não encontra nada a criar, alterar ou destruir. Ele não prova que a AWS continua igual ao que o estado guarda além do que o código controla: uma tag posta à mão no console ou uma propriedade que nunca declarei é drift que o plan não enxerga. Também não prova que os dados estão certos, já que este exercício não sobe nenhum arquivo para o lake.

## DECISAO 05 - a ordem

Antes do `state mv`, o mesmo código dava `6 to add, 0 to change, 6 to destroy`: para o Terraform, `aws_s3_bucket.lake` sumiu e `module.lake.aws_s3_bucket.lake` apareceu. Não dei `apply` nesse momento, então não medi o estrago, mas o plano dizia que destruiria os seis recursos e criaria seis com os mesmos nomes. Como bucket, database e workgroup têm nome único, esperaria uma stack meio quebrada: a criação colidiria com o nome de um recurso ainda existente, ou os objetos dos buckets seriam apagados junto (`force_destroy = true`). Só depois dos seis `state mv` o plan ficou limpo, e só então migrei o estado para o S3, o que também terminou em `No changes`.

## Observações

- O `main.tf` do ponto de partida não passa em `terraform validate`: os três blocos `columns { name = ... type = ... }` estavam em uma linha, e o HCL só aceita um argumento por bloco em linha única. Reescrevi esses três blocos em várias linhas, sem mudar nenhum atributo.
- O bucket de estado `eda-tfstate-grupo05` não existia, e eu o criei (versionamento, AES256, acesso público bloqueado). Ele e a tabela `eda-tflock` são o backend compartilhado e ficam após o `destroy`.
- O `terraform` avisa que `dynamodb_table` está obsoleto em favor de `use_lockfile`; mantive `dynamodb_table` porque é o que o enunciado pede.
