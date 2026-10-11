import streamlit as st
import google.generativeai as genai
import json

# Configuración de la página
st.set_page_config(page_title="Menú Inteligente", page_icon="🍳", layout="centered")

st.title("🍳 Generador de Menú y Supermercado")
st.write("Dime qué tienes en casa y armaré 3 recetas, más la lista exacta de lo que te falta comprar.")

# Configuración de la API Key
api_key = st.sidebar.text_input("Ingresa tu API Key de Gemini:", type="password")

# Input del usuario
ingredientes_usuario = st.text_area(
    "¿Qué ingredientes tienes disponibles?",
    placeholder="Ej: 2 tomates, arroz, media cebolla, huevos, un poco de queso..."
)

if st.button("🪄 Generar mi Menú Semanal", type="primary"):
    if not api_key:
        st.warning("⚠️ Por favor, ingresa tu API Key en la barra lateral.")
        st.stop()
    
    if not ingredientes_usuario:
        st.warning("⚠️ Necesito saber qué ingredientes tienes.")
        st.stop()

    with st.spinner("Conectando con la IA y calculando tu lista de compras..."):
        try:
            genai.configure(api_key=api_key)
            
            # Usamos exactamente el modelo que pidió Google en el mensaje de error
            model = genai.GenerativeModel('gemini-3.8-flash')

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
            
            respuesta = model.generate_content(prompt)
            
            # Limpiamos el texto por si la IA responde con formato de código
            texto_limpio = respuesta.text.replace('```json', '').replace('```', '').strip()
            
            datos = json.loads(texto_limpio)

            # Renderizar el Menú
            st.header("🍽️ Tu Menú")
            for receta in datos.get("menu", []):
                with st.expander(f"**{receta['nombre']}** (⏱️ {receta.get('tiempo', 'N/A')})"):
                    for paso in receta.get("pasos", []):
                        st.write(f"- {paso}")

            st.divider()

            # Renderizar la Lista de Compras interactiva
            st.header("🛒 Lista del Supermercado")
            lista_compras = datos.get("lista_compras", [])
            
            if not lista_compras or len(lista_compras) == 0:
                st.success("¡Tienes todo lo necesario! No necesitas comprar nada.")
            else:
                st.write("Marca lo que vayas echando al carrito:")
                for item in lista_compras:
                    st.checkbox(item, key=item)

        except Exception as e:
            st.error(f"Ocurrió un error al procesar la solicitud: {e}")
