import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuração da Chave via Variável de Ambiente para o Render
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Configuração da Verena com Filtro de Dignidade e Modelo Estável
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "Sou a Verena, especialista em anatomia, neurociência e direito. "
        "Se o usuário usar termos infantilizados como 'vozinha', "
        "devo educar gentilmente sobre a importância de chamar de Senhora ou pelo nome, "
        "preservando a autonomia e dignidade da pessoa idosa."
    )
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json.get("message")
        response = model.generate_content(user_message)
        return jsonify({"response": response.text})
    except Exception as e:
        print(f"Erro na IA: {e}")
        return jsonify({"response": f"Erro técnico: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)