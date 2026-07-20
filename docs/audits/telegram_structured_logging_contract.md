# F2H5-F2 — Contrato canônico do logging JSON

## Resumo

- Campos obrigatórios: 6
- Níveis: 5
- Campos proibidos: 13
- Uma linha por evento: True
- `allow_nan`: False
- UTC: UTC

## Campos obrigatórios

- `timestamp`
- `level`
- `event`
- `component`
- `outcome`
- `fields`

## Níveis

- `debug` → `10`
- `info` → `20`
- `warning` → `30`
- `error` → `40`
- `critical` → `50`
