# Decisões — Exercício 01 (Aula 04)

## DECISAO 01 — tipo de valor

`valor` foi declarado como `double` com `use.null.for.invalid.data: true`. Na
partição de hoje (`dt=2026-08-22`), `count(*) = 17280` e `count(valor) = 17035`
— 245 linhas (1,42%) viraram `null` por causa dos eventos que chegam com
vírgula decimal em vez de ponto. Aceito perder essas 245 linhas da agregação
numérica em troca de nunca derrubar a consulta inteira por causa delas.

## DECISAO 02 — tipo das colunas de tempo

`data_corrida` e `fim` foram declaradas como `string`. Testado com `SELECT`
contra o ambiente `eda-grupo05`: os valores voltaram legíveis em ISO 8601
(ex: `2026-08-22T00:47:19Z`), sem nenhum `null`. Não converti para `timestamp`
porque o teste real não indicou necessidade, e `string` evita o risco de um
formato futuro do produtor quebrar o parse silenciosamente.

## DECISAO 03 — ignore.malformed.json

Mantive `ignore.malformed.json: true`. É uma decisão preventiva — não observei
nenhum caso real de JSON malformado nos dados gerados. Prefiro silêncio (linha
quebrada vira `null`) a deixar uma linha ruim futura derrubar a consulta
inteira com `HIVE_BAD_DATA`; quem paga essa escolha é quem for auditar dados
faltantes sem aviso, não quem só quer rodar `SELECT count(*)`.

## DECISAO 04 — quantas partições declarar

Declarei 3 das 30 partições (as de hoje e dos dois dias anteriores). As
outras 27 existem no S3 — e são pagas — mas ficam invisíveis via SQL até
serem catalogadas. Como o `deploy.sh` recalcula sempre "hoje, ontem,
anteontem" a cada execução, no dia 31 uma partição antiga (a mais velha das
três atuais) fica órfã do conjunto declarado e uma nova precisa ser
adicionada manualmente — o catálogo nunca acompanha o S3 sozinho.

## DECISAO 05 — teto de bytes por consulta

Medi via CLI (`DataScannedInBytes`, não o valor arredondado do console): a
consulta larga (`SELECT count(*) FROM corridas`, sem `WHERE`) escaneou
exatamente 11.765.273 bytes; a consulta estreita (`WHERE dt = '2026-08-22'`)
escaneou ~3,74 MB. Escolhi `TetoBytesPorConsulta = 10.485.760` — o próprio
piso mínimo permitido pela AWS. Esse valor fica confortavelmente abaixo dos
11.765.273 bytes da larga (o freio toca) e acima dos ~3,74 MB da estreita (ela
passa). Existe margem real entre o teto e a larga — cerca de 1.279.513 bytes
(~1,28 MB) — mas é uma margem apertada: se o lake crescer, a consulta
estreita de hoje pode se aproximar desse teto em poucos ciclos de partições
novas, e o valor vai precisar ser remedido antes que ela também comece a ser
cortada.
