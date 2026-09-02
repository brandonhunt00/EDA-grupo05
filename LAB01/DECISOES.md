# Decisões - Exercício 01 (Aula 04)

## DECISAO 01 - tipo de valor

`valor` foi declarado como `double` com `use.null.for.invalid.data: true`. Na
partição de hoje (`dt=2026-08-22`), `count(*) = 17280` e `count(valor) = 17035`,
ou seja, 245 linhas (1,42%) viraram `null` por causa dos eventos que chegam com
vírgula decimal em vez de ponto. Aceito perder essas 245 linhas da agregação
numérica em troca de nunca derrubar a consulta inteira por causa delas.

## DECISAO 02 - tipo das colunas de tempo

`data_corrida` e `fim` foram declaradas como `string`. Testado com `SELECT`
contra o ambiente `eda-grupo05`: os valores voltaram legíveis em ISO 8601
(ex: `2026-08-22T00:47:19Z`), sem nenhum `null`. Não converti para `timestamp`
porque o teste real não indicou necessidade, e `string` evita o risco de um
formato futuro do produtor quebrar o parse silenciosamente.

## DECISAO 03 - ignore.malformed.json

Mantive `ignore.malformed.json: true`. É uma decisão preventiva - não observei
nenhum caso real de JSON malformado nos dados gerados. Prefiro silêncio (linha
quebrada vira `null`) a deixar uma linha ruim futura derrubar a consulta
inteira com `HIVE_BAD_DATA`; quem paga essa escolha é quem for auditar dados
faltantes sem aviso, não quem só quer rodar `SELECT count(*)`.

## DECISAO 04 - quantas partições declarar

Declarei 3 das 30 partições (as de hoje e dos dois dias anteriores). As
outras 27 existem no S3 - e são pagas - mas ficam invisíveis via SQL até
serem catalogadas. Como o `deploy.sh` recalcula sempre "hoje, ontem,
anteontem" a cada execução, no dia 31 uma partição antiga (a mais velha das
três atuais) fica órfã do conjunto declarado e uma nova precisa ser
adicionada manualmente - o catálogo nunca acompanha o S3 sozinho.

## DECISAO 05 - teto de bytes por consulta

Medi via CLI (`DataScannedInBytes`): a consulta larga (`SELECT count(*) FROM
corridas`, sem `WHERE`) foi cortada em exatamente 11.000.000 bytes (status
`CANCELLED`); a consulta estreita (`WHERE dt = '2026-08-23'`) escaneou
3.921.495 bytes e teve sucesso. Escolhi `TetoBytesPorConsulta = 11.000.000`,
nem o piso (`10.485.760`) nem o topo (`117.655.605`) do intervalo permitido.
Fica 514.240 bytes acima do piso, uma margem de segurança para não flertar
com o limite mínimo que a AWS rejeita, e fica bem abaixo do topo, garantindo
que o freio continue sendo sentido pela larga sem depender do lake inteiro
ser varrido. A margem contra a estreita (11.000.000 − 3.921.495 = 7.078.505
bytes, quase o dobro do que ela escaneia) é generosa hoje, mas encolhe
conforme o lake cresce: o valor não é permanente, é uma calibragem para o
tamanho atual dos dados.
