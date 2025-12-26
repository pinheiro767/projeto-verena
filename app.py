import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# --- CONFIGURAÇÃO DA CHAVE ---
# Tenta pegar a chave segura do Windows
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# --- PERSONALIDADE DA VERENA (SEGURANÇA) ---
instrucoes = """
Você é a VERENA, assistente virtual de saúde geriátrica.
1. Seja empática e nunca use termos infantilizados (ex: 'vózinha').
2. Se houver risco de queda na conversa ou imagem, ALERTE.
3. Não dê diagnósticos médicos, apenas orientações de suporte e literacia.
4. Explique termos técnicos de forma simples para cuidadores leigos.
"""

# --- CÉREBRO 2.0 (COM VISÃO E SEGURANÇA) ---
# Aqui ligamos a Visão (Vision) e o Prompt de Sistema
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash-exp',
    system_instruction=instrucoes
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        texto_usuario = request.form.get('message')
        imagem_enviada = request.files.get('image')

        # CASO 1: Tem imagem? (Visão Computacional)
        if imagem_enviada:
            img = Image.open(imagem_enviada)
            prompt = [texto_usuario or "Analise esta imagem clinicamente para um cuidador.", img]
            response = model.generate_content(prompt)
        
        # CASO 2: Só texto?
        elif texto_usuario:
            response = model.generate_content(texto_usuario)
            
        else:
            return jsonify({'response': "Não entendi. Mande texto ou imagem."})

        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'response': f"Erro: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)