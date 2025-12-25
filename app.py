import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import datetime

# --- CONFIGURAÇÕES ---
load_dotenv()
API_KEY = os.getenv("MINHA_KEY")

app = Flask(__name__)
# Permitir uploads maiores (até 16MB) para fotos de exames
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
    
    # URL do modelo Google Gemini 2.0 Flash (Multimodal)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    ano_atual = datetime.datetime.now().year
    
    # --- PROMPT MESTRE (CÉREBRO DA VERENA) ---
    prompt_sistema = f"""
    ATUE COMO: VERENA (Especialista em Neurociência, Leitura de Exames, Direito e Saúde).
    
    SEU OBJETIVO AO RECEBER UMA IMAGEM:
    1. Se for EXAME MÉDICO: Leia os valores técnicos. Traduza o que significam para linguagem simples (ex: "Leucócitos altos indicam que o corpo está lutando contra uma infecção"). Nunca dê diagnóstico de doença fatal, sugira levar ao médico.
    2. Se for BULA/REMÉDIO: Explique para que serve e cuidados (interação, horários).
    3. Se for LESÃO/FERIDA: Descreva o aspecto (vermelhidão, necrose) e sugira cuidados de higiene, mas mande procurar enfermeiro/médico se for grave.
    
    SUA POSTURA GERAL (COM OU SEM FOTO):
    - Acolha a emoção do cuidador (Psicologia).
    - Explique a base biológica (Neurociência).
    - Cite leis/direitos (Estatuto do Idoso/SUS).
    - Use dados científicos recentes (2020-{ano_atual}) e cite DOI se possível.
    - Considere a economia do idoso (soluções baratas).
    
    PERGUNTA DO USUÁRIO: '{msg_texto}'
    """
    
    # Montar o pacote de dados
    partes_conteudo = []
    
    # Adiciona o texto (prompt + pergunta)
    partes_conteudo.append({"text": prompt_sistema})
    
    # SE TIVER IMAGEM, anexa ela no pacote
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
                texto_ia = "Consegui ver a imagem, mas não soube interpretar. Tente uma foto mais nítida."
            
            return jsonify({"resposta": texto_ia.replace('\n', '<br>')})
        else:
            return jsonify({"resposta": f"Erro no Google: {response.text}"})
            
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)