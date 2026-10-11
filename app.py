import json

import google.generativeai as genai
import streamlit as st


st.set_page_config(page_title="Menú Inteligente", page_icon="🍳", layout="centered")

st.title("🍳 Generador de Menú y Supermercado")
st.write(
    "Dime qué tienes en casa y armaré 3 recetas, más la lista exacta de lo que te falta comprar."
)

api_key = st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

ingredientes_usuario = st.text_area(
    "¿Qué ingredientes tienes disponibles?",
    placeholder="Ej: 2 tomates, arroz, media cebolla, huevos, un poco de queso...",
)

if st.button("🪄 Generar mi Menú Semanal", type="primary"):
    if not api_key:
        st.warning("⚠️ Por favor, ingresa tu API Key en la barra lateral.")
        st.stop()

    if not ingredientes_usuario.strip():
        st.warning("⚠️ Necesito saber qué ingredientes tienes.")
        st.stop()

    with st.spinner("Creando recetas y calculando tu lista de compras..."):
        try:
            # Configurar el cliente de IA
        genai.configure(api_key=api_key)
        
        # Usamos el modelo estándar global
        model = genai.GenerativeModel('gemini-pro')

        prompt = f"""
        Eres un chef experto. El usuario tiene estos ingredientes: {ingredientes_usuario}.
        Crea un menú de 3 recetas prácticas priorizando lo que ya tiene.
        
        Devuelve un JSON estricto con esta estructura exacta, sin texto extra y sin usar bloques de código Markdown:
        {{
            "menu": [
                {{
                    "nombre": "Nombre del plato",
                    "tiempo": "15 min",
                    "pasos": ["Paso 1", "Paso 2"]
                }}
            ],
            "lista_compras": ["Ingrediente a comprar - Cantidad"]
        }}
        """
        
        # Llamada a la API
        respuesta = model.generate_content(prompt)
        
        # Limpiamos el texto por si la IA responde con formato de código (```json ... ```)
        texto_limpio = respuesta.text.replace('```json', '').replace('```', '').strip()
        
        datos = json.loads(texto_limpio)
            datos = json.loads(respuesta.text)

            st.header("🍽️ Tu Menú")
            for receta in datos.get("menu", []):
                nombre = receta.get("nombre", "Receta")
                tiempo = receta.get("tiempo", "N/A")
                with st.expander(f"**{nombre}** (⏱️ {tiempo})"):
                    for paso in receta.get("pasos", []):
                        st.write(f"- {paso}")

            st.divider()

            st.header("🛒 Lista del Supermercado")
            lista_compras = datos.get("lista_compras", [])

            if not lista_compras:
                st.success("¡Tienes todo lo necesario! No necesitas comprar nada.")
            else:
                st.write("Marca lo que vayas echando al carrito:")
                for indice, item in enumerate(lista_compras):
                    st.checkbox(item, key=f"compra_{indice}_{item}")

        except Exception as error:
            st.error(f"Ocurrió un error al procesar la solicitud: {error}")
