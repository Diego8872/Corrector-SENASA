# Corrector SENASA

Cruza la Declaración Jurada de SENASA (embalajes de madera, Res. 614/2015)
contra la DI, para las aduanas de **Ezeiza** (aéreo) y **Buenos Aires** (marítimo).

## Campos que revisa

| Campo | Fuente DJ | Comparación |
|---|---|---|
| Punto de ingreso | DJ SENASA | Constante fija por aduana |
| Medio de transporte | DJ SENASA | Constante fija por aduana |
| Lugar de destino de la mercadería | DJ SENASA | Ezeiza: constante fija · Buenos Aires: contra el campo "Depósito" de la DI |
| País de procedencia | DJ SENASA | Contra la DI |
| País de origen | DJ SENASA | Contra la DI |

## Archivos que se suben

- **DJ SENASA**: PDF (obligatorio)
- **DI**: Excel (recomendado) y/o PDF (fallback). Si se suben ambos, el Excel
  tiene prioridad campo por campo, y el PDF completa lo que falte (ej. el
  Depósito, que en el Excel a veces viene vacío).

## Estructura

```
app.py                          # UI Streamlit
utils_senasa/
  constants.py                  # tabla de reglas esperadas por aduana
  parser_dj_senasa.py           # extrae campos de la DJ SENASA (PDF)
  parser_di_excel.py            # extrae campos de la DI (Excel) — fuente principal
  parser_di_pdf.py              # extrae campos de la DI (PDF) — fallback
  validator.py                  # normalización + lógica de cruce
```

## Agregar una aduana nueva

Sumar una entrada en `utils_senasa/constants.py` → `ADUANA_RULES`, con
`puerto_ingreso`, `medio_transporte` y `lugar_destino` (o `None` si el
lugar de destino se valida contra el Depósito de la DI en vez de una
constante fija).

## Limitaciones conocidas (v1)

- No se cruza contra BL / Guía Aérea.
- `parser_di_pdf.py` usa coordenadas fijas calibradas contra el formato SIM
  de ARCA vigente a jul/2026; si ARCA cambia el layout del PDF, hay que
  reajustar las bandas de coordenadas (`Y_BANDS`).
- Un solo ítem por despacho para Origen/Procedencia (toma el primer ítem
  con datos del Excel).

## Deploy

Igual que los demás portales: Streamlit Cloud apuntando a este repo,
`app.py` como entrypoint, `requirements.txt` con las dependencias.
