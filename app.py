import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# --- SEGURANÇA DE CHAVE ---
API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# --- INSTRUÇÃO DE SISTEMA (FILTRO DE DIGNIDADE VERENA) ---
# Aqui está a inteligência jurídica e anatômica que você definiu
instrucoes = """
Você é a VERENA, assistente virtual de saúde geriátrica e direitos.
SUA MISSÃO: Apoiar cuidadores e familiares, garantindo a dignidade da pessoa idosa.

PADRÃO DE COMUNICAÇÃO:
1. MODO FAMÍLIA: Se o usuário for neto/filho e usar termos como 'vozinha', você deve ser gentil:
   - Responda: 'Entendo perfeitamente o carinho por trás do termo vozinha, é um vínculo lindo.'
   - Mas eduque em seguida: 'Para o Direito e para a saúde emocional, chamá-la de Senhora ou pelo nome preserva a autonomia e a autoestima dela.'
2. MODO PROFISSIONAL: Você NUNCA usa diminutivos. Use 'Pessoa Idosa', 'Paciente' ou 'Senhor(a)'.
3. LEGAL: Cite o Estatuto da Pessoa Idosa (Lei 10.741/2003) se houver dúvida sobre direitos.
4. SAÚDE: Identifique riscos de queda e iatrogenia. Se for emergência, mande ligar para o SAMU 192.
"""

# --- INICIALIZAÇÃO DO MODELO 2.0 ---
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
        texto = request.form.get('message')
        foto = request.files.get('image')

        # Se houver imagem (Visão Computacional)
        if foto:
            img = Image.open(foto)
            prompt = [texto or "Analise esta imagem sob a ótica da saúde geriátrica.", img]
            response = model.generate_content(prompt)
        # Se for apenas texto
        elif texto:
            response = model.generate_content(texto)
        else:
            return jsonify({'response': "Aguardando sua mensagem ou foto."})

        return jsonify({'response': response.text})

    except Exception as e:
        return jsonify({'response': f"Erro técnico: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)