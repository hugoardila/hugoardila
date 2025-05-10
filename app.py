import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Calculadora de Pagos", layout="wide")

# ---------- Funciones ----------
def cargar_empleados():
    if os.path.exists("empleados.xlsx"):
        return pd.read_excel("empleados.xlsx")
    return pd.DataFrame(columns=["nombre", "enganches", "retaques", "eng_dolar", "ret_dolar"])

def guardar_empleados(df):
    df.to_excel("empleados.xlsx", index=False)

def calcular_totales(df, mxn_cop, usd_cop):
    resultados = {}
    gastos_oficina = 0

    for _, e in df.iterrows():
        total = ((e['enganches'] * mxn_cop) / 2) + \
                ((e['retaques'] * mxn_cop) / 3) + \
                ((e['eng_dolar'] * usd_cop) / 2) + \
                ((e['ret_dolar'] * usd_cop) / 3)
        
        if total > 210000:
            total -= 10000
            gastos_oficina += 10000

        nombre = e["nombre"]
        resultados[nombre] = resultados.get(nombre, 0) + total

    return resultados, gastos_oficina

# ---------- Interfaz ----------

st.title("💼 Calculadora de Pagos a Empleados")

# Cargar datos existentes
df_empleados = cargar_empleados()

# ---------- Formulario ----------
st.subheader("📝 Registro de Empleado")
with st.form("form_empleado"):
    col1, col2, col3 = st.columns(3)
    nombre = col1.text_input("Nombre")
    enganches = col2.number_input("Enganches (MXN)", value=0.0, min_value=0.0)
    retaques = col3.number_input("Retaques (MXN)", value=0.0, min_value=0.0)
    eng_dolar = col1.number_input("Enganche (USD)", value=0.0, min_value=0.0)
    ret_dolar = col2.number_input("Retaque (USD)", value=0.0, min_value=0.0)
    submitted = st.form_submit_button("Agregar Empleado")

    if submitted:
        nuevo = pd.DataFrame([{
            "nombre": nombre,
            "enganches": enganches,
            "retaques": retaques,
            "eng_dolar": eng_dolar,
            "ret_dolar": ret_dolar
        }])
        df_empleados = pd.concat([df_empleados, nuevo], ignore_index=True)
        guardar_empleados(df_empleados)
        st.success(f"Empleado '{nombre}' agregado correctamente.")

# ---------- Tasas de cambio ----------
st.subheader("💱 Tasas de Cambio")
col1, col2 = st.columns(2)
mxn_cop = col1.number_input("MXN → COP", value=0.0)
usd_cop = col2.number_input("USD → COP", value=0.0)

# ---------- Calcular totales ----------
if st.button("📊 Calcular Totales"):
    if mxn_cop <= 0 or usd_cop <= 0:
        st.error("Por favor ingresa tasas de cambio válidas.")
    else:
        resultados, gastos = calcular_totales(df_empleados, mxn_cop, usd_cop)
        st.success("Totales calculados correctamente.")

        st.subheader("🧾 Totales por Empleado")
        st.dataframe(pd.DataFrame(list(resultados.items()), columns=["Empleado", "Total a Pagar (COP)"]))

        st.info(f"🏢 Gastos de oficina acumulados: **{gastos:,} COP**")

        # Exportar Excel
        df_export = pd.DataFrame(list(resultados.items()), columns=["Empleado", "Total a Pagar"])
        df_export.to_excel("pago_neto.xlsx", index=False)
        with open("pago_neto.xlsx", "rb") as f:
            st.download_button("📥 Descargar Totales en Excel", f, file_name="pago_neto.xlsx")

# ---------- Ver todos los registros ----------
st.subheader("📚 Ver Todos los Registros")

filtro_nombre = st.text_input("Filtrar por nombre").lower()
if filtro_nombre:
    df_filtrado = df_empleados[df_empleados["nombre"].str.lower().str.contains(filtro_nombre)]
else:
    df_filtrado = df_empleados

st.dataframe(df_filtrado)

# ---------- Descargar registros ----------
if not df_empleados.empty:
    df_empleados.to_excel("todos_los_empleados.xlsx", index=False)
    with open("todos_los_empleados.xlsx", "rb") as f:
        st.download_button("📥 Descargar Todos los Registros", f, file_name="todos_los_empleados.xlsx")
