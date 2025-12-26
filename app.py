import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import datetime

load_dotenv()
API_KEY = os.getenv("MINHA_KEY")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    dados = request.json
    msg_texto = dados.get('msg', '')
    img_b64 = dados.get('imagem')
    img_tipo = dados.get('tipo')
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    ano_atual = datetime.datetime.now().year
    
    # --- CÉREBRO DA VERENA (REFINADO PARA CITAÇÕES REAIS) ---
    prompt_sistema = f"""
    ATUE COMO: VERENA (Especialista em Neurociência, Leitura de Exames, Direito e Saúde).
    
    REGRAS DE CITAÇÃO CIENTÍFICA (RIGOROSO):
    1. Use dados recentes ({ano_atual-5} a {ano_atual}).
    2. SOBRE O DOI: Se você tiver o link/código DOI real, coloque-o.
    3. PROIBIDO: Se você NÃO tiver o DOI exato, NÃO invente "XXXXXX" nem códigos falsos. Nesse caso, cite apenas: "Autor, Título da Revista (Ano)". Seja honesta.
    
    REGRAS DE VISÃO (IMAGENS):
    - EXAMES: Traduza termos técnicos para linguagem simples.
    - BULAS: Resuma indicações e riscos.
    - ALERTA: Nunca dê diagnóstico fechado. Diga "sugere", "indica", "consulte o médico".
    
    POSTURA:
    - Acolha a emoção (Psicologia).
    - Explique a biologia (Neurociência).
    - Defenda direitos (Leis/SUS).
    
    PERGUNTA: '{msg_texto}'
    """
    
    partes_conteudo = []
    partes_conteudo.append({"text": prompt_sistema})
    
    if img_b64 and img_tipo:
        partes_conteudo.append({
            "inline_data": {
                "mime_type": img_tipo,
                "data": img_b64
            }
        })

    payload = {
        "contents": [{
            "parts": partes_conteudo
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            resultado = response.json()
            try:
                texto_ia = resultado['candidates'][0]['content']['parts'][0]['text']
            except:
                texto_ia = "Não consegui interpretar a resposta. Tente reformular."
            
            return jsonify({"resposta": texto_ia.replace('\n', '<br>')})
        else:
            return jsonify({"resposta": f"Erro Google: {response.text}"})
            
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
