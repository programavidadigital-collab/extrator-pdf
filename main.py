from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from openai import OpenAI
import fitz
import os
import html
import traceback

app = FastAPI()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

PROMPT = """
Você é um Organizador de Exames Laboratoriais.
Extraia todos os exames do documento.
Organize em formato de laudo.
Não interprete clinicamente.
Não sugira doenças, tratamentos, medicamentos ou condutas.
Ao final escreva:
Resumo gerado automaticamente a partir dos dados presentes no documento.
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <body style="font-family:Arial;max-width:900px;margin:auto;padding:40px;">
        <h2>Organizador de Exames Laboratoriais</h2>
        <form action="/processar" method="post" enctype="multipart/form-data">
            <input type="file" name="arquivo" accept=".pdf" required>
            <br><br>
            <button type="submit">Processar PDF</button>
        </form>
        <p>Após clicar, aguarde. PDFs grandes podem demorar.</p>
    </body>
    </html>
    """

@app.post("/processar", response_class=HTMLResponse)
async def processar(arquivo: UploadFile = File(...)):
    try:
        conteudo = await arquivo.read()

        doc = fitz.open(stream=conteudo, filetype="pdf")

        paginas = []
        for i in range(len(doc)):
            texto = doc[i].get_text("text")
            paginas.append(f"--- PÁGINA {i+1} DE {len(doc)} ---\n{texto}")

        texto_completo = "\n\n".join(paginas)

        resposta = client.responses.create(
            model="gpt-4o-mini",
            input=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": texto_completo}
            ]
        )

        laudo = html.escape(resposta.output_text)

        return f"""
        <html>
        <body style="font-family:Arial;max-width:1200px;margin:auto;padding:40px;">
            <h2>Resultado</h2>
            <pre style="white-space:pre-wrap;">{laudo}</pre>
            <br>
            <a href="/">Processar outro PDF</a>
        </body>
        </html>
        """

    except Exception as e:
        erro = html.escape(traceback.format_exc())
        return f"""
        <html>
        <body style="font-family:Arial;max-width:1200px;margin:auto;padding:40px;">
            <h2>Erro ao processar</h2>
            <pre style="white-space:pre-wrap;color:red;">{erro}</pre>
            <br>
            <a href="/">Voltar</a>
        </body>
        </html>
        """
