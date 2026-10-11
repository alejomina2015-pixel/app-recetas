import streamlit as st
import google.generativeai as genai
import json

# Configuración de la página (ahora usamos layout="wide" para aprovechar la pantalla)
st.set_page_config(page_title="Menú Inteligente", page_icon="🍳", layout="wide")

# --- BARRA LATERAL (CONFIGURACIÓN Y FILTROS) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    api_key = st.text_input("Ingresa tu API Key de Gemini:", type="password")
    
    st.divider()
    
    st.header("🍽️ Preferencias")
    personas = st.number_input("¿Para cuántas personas?", min_value=1, max_value=10, value=2)
    dieta = st.selectbox("Tipo de dieta", ["Ninguna", "Vegetariana", "Vegana", "Sin Gluten", "Keto"])

# --- PANTALLA PRINCIPAL ---
st.title("🍳 Generador de Menú y Supermercado")
st.write("Dime qué tienes en casa, ajusta tus preferencias en el menú lateral y armaremos tu menú a medida.")

# Input del usuario
ingredientes_usuario = st.text_area(
    "¿Qué ingredientes tienes disponibles?",
    placeholder="Ej: 2 tomates, arroz, media cebolla, huevos, un poco de pollo...",
    height=100
)

if st.button("🪄 Generar mi Menú Semanal", type="primary"):
    if not api_key:
        st.warning("⚠️ Por favor, ingresa tu API Key en la barra lateral.")
        st.stop()
    
    if not ingredientes_usuario:
        st.warning("⚠️ Necesito saber qué ingredientes tienes.")
        st.stop()

    with st.spinner("Creando recetas mágicas y calculando porciones..."):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-3.8-flash')

            # El prompt ahora incluye el número de personas y la dieta
            prompt = f"""
            Eres un chef experto. El usuario tiene estos ingredientes: {ingredientes_usuario}.
            Debes crear un menú de 3 recetas prácticas para {personas} personas.
            Restricción dietética a respetar estrictamente: {dieta}.
            Prioriza usar los ingredientes que el usuario ya tiene.
            
            Devuelve un JSON estricto con esta estructura exacta, sin texto extra y sin usar bloques de código Markdown:
            {{
                "menu": [
                    {{
                        "nombre": "Nombre del plato",
                        "tiempo": "15 min",
                        "pasos": ["Paso 1", "Paso 2"]
                    }}
                ],
                "lista_compras": ["Ingrediente a comprar - Cantidad exacta para {personas} personas"]
            }}
            """
            
            respuesta = model.generate_content(prompt)
            texto_limpio = respuesta.text.replace('```json', '').replace('```', '').strip()
            datos = json.loads(texto_limpio)

            st.divider()

            # --- RENDERIZADO EN COLUMNAS ---
            col1, col2 = st.columns([2, 1]) # La columna del menú será más ancha que la del supermercado

            with col1:
                st.header("🍽️ Tu Menú")
                for receta in datos.get("menu", []):
                    with st.expander(f"**{receta['nombre']}** (⏱️ {receta.get('tiempo', 'N/A')})"):
                        for paso in receta.get("pasos", []):
                            st.write(f"- {paso}")

            with col2:
                st.header("🛒 Compras")
                lista_compras = datos.get("lista_compras", [])
                
                if not lista_compras or len(lista_compras) == 0:
                    st.success("¡Tienes todo lo necesario!")
                else:
                    st.info("Marca lo que eches al carrito:")
                    for item in lista_compras:
                        st.checkbox(item, key=item)

        except Exception as e:
            st.error(f"Ocurrió un error al procesar la solicitud. Intenta generar de nuevo o revisa tus ingredientes.")
