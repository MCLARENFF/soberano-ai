import os
import io
from flask import Flask, request, render_template_string
import PyPDF2
from google import genai

# 🌐 INICIALIZAÇÃO DA PLATAFORMA WEB
app = Flask(__name__)
GEMINI_KEY = os.environ.get("GEMINI_KEY")
client = genai.Client(api_key=GEMINI_KEY)

# 🎨 DESIGN DA PÁGINA (Interface Premium com Animação e JS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Soberano AI - Auditoria Jurídica</title>
    <style>
        /* ESTILO GERAL */
        body { font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0a0a0a; color: #e0e0e0; text-align: center; padding: 40px 20px; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 90vh;}
        .container { width: 100%; max-width: 700px; background: #141414; padding: 45px; border-radius: 20px; box-shadow: 0 0 30px rgba(0, 255, 170, 0.15); border: 1px solid #2a2a2a; position: relative; overflow: hidden;}
        
        /* CABEÇALHO */
        h1 { color: #00ffaa; font-size: 2.8em; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 3px; font-weight: 800; text-shadow: 0 0 10px rgba(0, 255, 170, 0.5);}
        p.subtitle { color: #888; font-size: 1.2em; margin-bottom: 40px; font-weight: 300;}
        
        /* ÁREA DE UPLOAD */
        .upload-area { border: 3px dashed #333; padding: 35px; border-radius: 15px; background: #0f0f0f; margin-bottom: 30px; transition: 0.3s;}
        .upload-area:hover { border-color: #00ffaa; box-shadow: inset 0 0 15px rgba(0,255,170,0.1); }
        input[type=file] { color: #fff; font-size: 1.1em;}
        
        /* BOTÕES */
        .btn-audit { background: linear-gradient(45deg, #00ffaa, #00cc88); color: #000; border: none; padding: 18px 35px; font-size: 1.2em; cursor: pointer; border-radius: 10px; font-weight: 900; transition: 0.3s; width: 100%; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 5px 15px rgba(0,255,170,0.3);}
        .btn-audit:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,255,170,0.5); }
        
        .btn-copy { background: #222; color: #00ffaa; border: 2px solid #00ffaa; padding: 10px 20px; font-size: 0.9em; cursor: pointer; border-radius: 8px; font-weight: bold; transition: 0.3s; margin-bottom: 15px; display: inline-flex; align-items: center; gap: 8px;}
        .btn-copy:hover { background: #00ffaa; color: #000; }

        /* ÁREA DO VEREDITO */
        .result-box { margin-top: 40px; text-align: left; background: #1a1a1a; padding: 30px; border-radius: 15px; border: 1px solid #333; position: relative;}
        .result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 15px;}
        .result-content { white-space: pre-wrap; line-height: 1.8; color: #d0d0d0; font-size: 1.05em;}
        
        /* RODAPÉ */
        .footer { margin-top: 40px; color: #444; font-size: 0.9em; letter-spacing: 1px;}

        /* --- ANIMAÇÃO DO MARTELO (JUSTIÇA SOBERANA) --- */
        .loader-container { display: none; /* Escondido por padrão */ padding: 40px; }
        .gavel-icon { width: 100px; height: 100px; fill: #00ffaa; animation: hammer-strike 1.2s ease-in-out infinite; transform-origin: 80% 80%; display: block; margin: 0 auto;}
        .loading-text { color: #00ffaa; margin-top: 25px; font-size: 1.4em; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; animation: text-pulse 1.2s ease-in-out infinite; }

        @keyframes hammer-strike {
            0%, 100% { transform: rotate(0deg); }
            30% { transform: rotate(-45deg); } /* Levanta */
            50% { transform: rotate(5deg); } /* Bate forte */
            70% { transform: rotate(0deg); } /* Retorna */
        }
        @keyframes text-pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }
    </style>
    <script>
        // Função para mostrar a animação quando clica no botão
        function showLoader() {
            const fileInput = document.getElementById('fileUpload');
            if (fileInput.files.length > 0) {
                document.getElementById('form-container').style.display = 'none'; // Esconde o formulário
                document.getElementById('loader-area').style.display = 'block'; // Mostra o martelo
            }
        }
        // Função de Copiar e Colar
        function copyText() {
            const text = document.getElementById('veredicto-text').innerText;
            navigator.clipboard.writeText(text).then(() => {
                const btn = document.getElementById('copy-btn');
                const originalText = btn.innerHTML;
                btn.innerHTML = '✅ COPIADO COM SUCESSO!';
                btn.style.background = '#00ffaa';
                btn.style.color = '#000';
                setTimeout(() => { 
                    btn.innerHTML = originalText; 
                    btn.style.background = '#222';
                    btn.style.color = '#00ffaa';
                }, 3000);
            }).catch(err => {
                console.error('Erro ao copiar: ', err);
                alert('Erro ao copiar texto. Seu navegador pode não suportar isso.');
            });
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>🏛️ SOBERANO AI</h1>
        <p class="subtitle">Sistema de Auditoria Jurídica de Elite</p>
        
        {% if not result %}
        <div id="form-container">
            <div class="upload-area">
                <form method="post" enctype="multipart/form-data" onsubmit="showLoader()">
                    <input type="file" id="fileUpload" name="file" accept=".pdf" required>
                    <br><br>
                    <button type="submit" class="btn-audit">⚡ INICIAR AUDITORIA</button>
                </form>
            </div>
            <div class="footer">Desenvolvido por Jhonata - Soberano Lab &copy; 2026</div>
        </div>

        <div id="loader-area" class="loader-container">
            <svg class="gavel-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21.41 12.41l-1.41-1.41-3.59 3.59-1.41-1.41 3.59-3.59-1.41-1.41-3.59 3.59-1.41-1.41 1.17-1.17-2.83-2.83-6.36 6.36 2.83 2.83 1.17-1.17 1.41 1.41-3.59 3.59 1.41 1.41 3.59-3.59 1.41 1.41 3.59-3.59 1.41 1.41 3.59-3.59zM10 4c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/></svg>
            <div class="loading-text">ANALISANDO JUSTIÇA SOBERANA...</div>
        </div>
        {% endif %}

        {% if result %}
        <div class="result-box">
            <div class="result-header">
                <h3 style="color: #00ffaa; margin:0; font-size: 1.5em;">⚖️ VEREDITO DA IA:</h3>
                <button id="copy-btn" class="btn-copy" onclick="copyText()">📋 COPIAR VEREDITO</button>
            </div>
            <div id="veredicto-text" class="result-content">{{ result }}</div>
        </div>
        <div class="footer" style="margin-top:20px;"><a href="/" style="color:#00ffaa; text-decoration:none; font-weight:bold;">⬅️ NOVA AUDITORIA</a></div>
        {% endif %}
    </div>
</body>
</html>
"""

# 🧠 ROTA PRINCIPAL (Motor Gemini 2.5 Flash)
@app.route('/', methods=['GET', 'POST'])
def home():
    veredicto = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template_string(HTML_TEMPLATE, result="⚠️ Erro: Nenhum arquivo enviado.")
        
        file = request.files['file']
        if file.filename == '':
            return render_template_string(HTML_TEMPLATE, result="⚠️ Erro: Arquivo vazio.")
        
        if file and file.filename.endswith('.pdf'):
            try:
                # Extração
                pdf_reader = PyPDF2.PdfReader(file)
                texto = ""
                for i in range(min(len(pdf_reader.pages), 3)): # Lê as 3 primeiras páginas
                    texto += pdf_reader.pages[i].extract_text()
                
                texto = texto[:4000] # Limite de segurança
                
                # Inteligência
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=f"Você é a Soberano AI, uma Auditora Jurídica. Analise este contrato de forma clara. 1. Inicie com 'STATUS: 🔴 ALTO RISCO' ou 'STATUS: 🟢 BAIXO RISCO'. 2. Liste 3 pontos de atenção ou possíveis golpes. Texto: {texto}"
                )
                veredicto = res.text
            except Exception as e:
                veredicto = f"⚠️ Erro no motor de processamento: {str(e)}"
        else:
            veredicto = "⚠️ Por favor, envie um arquivo com extensão .PDF válido."
            
    return render_template_string(HTML_TEMPLATE, result=veredicto)

# 🚀 INICIALIZAÇÃO DO SERVIDOR WEB
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
