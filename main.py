from fastapi import FastAPI, UploadFile, File
import fitz

app = FastAPI()

@app.get("/")
def home():
    return {"status": "API funcionando"}

@app.post("/extrair")
async def extrair_pdf_completo(arquivo: UploadFile = File(...)):
    conteudo = await arquivo.read()
    doc = fitz.open(stream=conteudo, filetype="pdf")

    paginas = []

    for i in range(len(doc)):
        texto = doc[i].get_text("text")
        paginas.append({
            "numero": i + 1,
            "texto": texto
        })

    return {
        "paginas_totais": len(doc),
        "paginas_extraidas": len(paginas),
        "paginas": paginas
    }
