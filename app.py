import tempfile
import os

import streamlit as st

from utils_senasa.parser_dj_senasa import extract_dj_senasa
from utils_senasa.parser_di_excel import extract_di_excel
from utils_senasa.parser_di_pdf import extract_di_pdf
from utils_senasa.validator import validate, merge_di_sources

st.set_page_config(page_title="Corrector SENASA", page_icon="✅", layout="centered")

st.title("Corrector SENASA")
st.caption(
    "Cruza la Declaración Jurada de SENASA (embalajes de madera) contra la DI. "
    "Aduanas soportadas en esta v1: **Ezeiza** y **Buenos Aires**."
)

st.markdown("### 1. Subí la Declaración Jurada de SENASA (PDF)")
dj_file = st.file_uploader("DJ SENASA (PDF)", type=["pdf"], key="dj")

st.markdown("### 2. Subí la DI")
col1, col2 = st.columns(2)
with col1:
    di_excel_file = st.file_uploader("DI (Excel) — recomendado", type=["xlsx", "xls"], key="di_excel")
with col2:
    di_pdf_file = st.file_uploader("DI (PDF) — opcional / fallback", type=["pdf"], key="di_pdf")

if st.button("Revisar", type="primary"):
    if not dj_file or (not di_excel_file and not di_pdf_file):
        st.warning("Subí la DJ SENASA y al menos un formato de la DI (Excel o PDF).")
        st.stop()

    with tempfile.TemporaryDirectory() as tmp:
        dj_path = os.path.join(tmp, "dj.pdf")
        with open(dj_path, "wb") as f:
            f.write(dj_file.getbuffer())
        dj_data = extract_dj_senasa(dj_path)

        di_excel_data = {}
        if di_excel_file:
            di_excel_path = os.path.join(tmp, "di.xlsx")
            with open(di_excel_path, "wb") as f:
                f.write(di_excel_file.getbuffer())
            di_excel_data = extract_di_excel(di_excel_path)

        di_pdf_data = {}
        if di_pdf_file:
            di_pdf_path = os.path.join(tmp, "di.pdf")
            with open(di_pdf_path, "wb") as f:
                f.write(di_pdf_file.getbuffer())
            di_pdf_data = extract_di_pdf(di_pdf_path)

        di_data = merge_di_sources(di_excel_data, di_pdf_data)

    resultado = validate(dj_data, di_data)

    st.divider()

    if not resultado["aduana_reconocida"]:
        st.error(
            f"No se reconoció la aduana informada en la DI "
            f"('{resultado.get('aduana_texto') or 'no detectada'}'). "
            f"Esta v1 solo soporta Ezeiza y Buenos Aires."
        )
        st.stop()

    checks = resultado["checks"]
    errores = [c for c in checks if not c["ok"]]

    st.markdown(f"### Resumen general — Aduana: **{resultado['aduana_key']}**")
    if errores:
        st.error(f"⚠️ Se encontraron {len(errores)} de {len(checks)} campos con diferencias.")
    else:
        st.success(f"✅ Los {len(checks)} campos revisados coinciden correctamente.")

    st.markdown("### Detalle por campo")
    for c in checks:
        icon = "✅" if c["ok"] else "❌"
        with st.container(border=True):
            st.markdown(f"{icon} **{c['campo']}**")
            cols = st.columns(2)
            with cols[0]:
                st.caption("DJ SENASA")
                st.write(c["valor_dj"] or "*(no detectado)*")
            with cols[1]:
                label = c["detalle_esperado"] or "Valor esperado"
                st.caption(label)
                st.write(c["valor_esperado"] or "*(no detectado)*")

    with st.expander("Ver datos crudos extraídos"):
        st.write("**DJ SENASA:**", dj_data)
        st.write("**DI (combinada):**", di_data)
