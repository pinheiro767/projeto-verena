import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import datetime

# Carrega variáveis locais (em desenvolvimento)
load_dotenv()

# 🔑 Leia SEMPRE a variável GEMINI_API_KEY
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ Variável GEMINI_API_KEY não encontrada no ambiente")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/processar', methods=['POST'])
def processar():
    dados = request.json or {}
    msg_texto = dados.get('msg', '')
    img_b64 = dados.get('imagem')
    img_tipo = dados.get('tipo')

    # Remove prefixo base64 se vier no formato data:image/png;base64,XXX
    if img_b64 and "," in img_b64:
        img_b64 = img_b64.split(",")[-1]

    # Endpoint Gemini 2.0 Flash
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    )

    headers = {"Content-Type": "application/json"}

    ano_atual = datetime.datetime.now().year

    # ==========================
    # 🧠 PROMPT DA VERENA
    # ==========================
    prompt_sistema = f"""
ATUE COMO: VERENA — Especialista em Neurociência, Saúde Geriátrica e Direito do Paciente no Brasil.

OBJETIVO:
Responder com empatia, clareza e base técnica. Sempre que o tema envolver respeito, autonomia, negligência, SUS, consentimento, privacidade, acompanhante ou idadismo, inclua um bloco sobre DIREITOS DO PACIENTE.

📚 CIÊNCIA E RIGOR ACADÊMICO
• Use linguagem simples e acessível
• Utilize dados recentes ({ano_atual-5} a {ano_atual})
• Se souber o DOI correto, inclua
• ❌ Nunca invente DOI
• Evite diagnóstico fechado — prefira: “pode sugerir”, “indica que”, “é compatível com”

🧠 SE HOUVER IMAGENS
• Explique em linguagem simples
• Alerte sobre limitações
• Recomende consulta médica quando necessário

⚖️ MÓDULO FIXO — ASPECTOS LEGAIS E DIREITOS NO BRASIL
Quando houver relação com o tema, explique de forma clara:
• Direito à dignidade, respeito e autonomia
• Consentimento informado
• Prevenção de idadismo (preconceito por idade)
• Direito à privacidade e forma adequada de tratamento
• Direito a acompanhante (quando aplicável)
• Possibilidade de registrar reclamação na Ouvidoria/Serviço Social
• Normas éticas (ex.: Código de Ética Médica do CFM)
• Explique sem juridiquês

POSTURA HUMANA
• Seja acolhedora
• Valide sentimentos
• Mostre respeito
• Não seja alarmista
• Use tom profissional e empático

PERGUNTA DO USUÁRIO:
{msg_texto}
"""

    # Monta conteúdo multimodal
    parts = [{"text": prompt_sistema}]

    if img_b64 and img_tipo:
        parts.append({
            "inline_data": {
                "mime_type": img_tipo,
                "data": img_b64
            }
        })

    payload = {"contents": [{"parts": parts}]}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            resultado = response.json()
            try:
                texto = resultado["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                texto = "Não consegui interpretar a resposta. Tente reformular."

            return jsonify({"resposta": texto.replace("\n", "<br>")})

        else:
            return jsonify({"resposta": f"Erro Google: {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
