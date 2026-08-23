# Nota — falso negativo no Critério 4

O `verificacao/verifica.sh` reporta `[FALHA]` no Critério 4, mas o
comportamento do freio de bytes está correto. Este arquivo documenta a
divergência sem alterar o script de avaliação.

## O que o verifica.sh checou

```
CRITERIO 4 - o teto mata a larga e deixa passar a estreita (15%)
            consulta larga   (sem WHERE dt): CANCELLED · 10485760 bytes
            consulta estreita (com WHERE dt): SUCCEEDED · 3921495 bytes
            teto declarado: 10485760 bytes
  [FALHA]   a consulta estreita nao respondeu - confira Location e particoes
```

## Por que os números mostram que o freio funcionou

- `TetoBytesPorConsulta` está configurado em `10485760` bytes (o piso mínimo
  permitido pela AWS — ver DECISOES.md, Decisão 05).
- A consulta larga (`SELECT count(*) FROM corridas;`, sem `WHERE`) escaneou
  exatamente `10485760` bytes antes de ser interrompida — o valor bate
  exatamente com o teto configurado, confirmando que o corte por
  `BytesScannedCutoffPerQuery` do workgroup foi acionado.
- A consulta estreita (`SELECT count(*) FROM corridas WHERE dt = '2026-08-22';`)
  terminou com sucesso, escaneando `3921495` bytes — bem abaixo do teto.

## Onde está o falso negativo

O script (`verificacao/verifica.sh`, condição do Critério 4) só reconhece o
freio como acionado quando o status da query larga é `FAILED`:

```bash
if [[ "${larga%%|*}" == "FAILED" && "${estreita%%|*}" == "SUCCEEDED" ]]; then
```

Neste ambiente, o Athena retornou o status `CANCELLED` para a consulta larga
ao atingir o corte de bytes do workgroup, não `FAILED`. Ambos os status
significam que a query não completou por causa do freio — a diferença é uma
nuance do motor do Athena (versão/timing de quando o corte é aplicado), não
um problema na infraestrutura declarada.

## O que não foi feito

O `verificacao/verifica.sh` não foi alterado — é o script de avaliação
fornecido pelo professor. Esta nota existe para documentar a evidência do
comportamento correto sem tocar no critério de correção.
