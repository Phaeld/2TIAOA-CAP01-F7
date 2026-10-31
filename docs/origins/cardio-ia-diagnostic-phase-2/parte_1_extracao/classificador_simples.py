import csv
import unicodedata

# Função para normalizar texto (tirar acento + lowercase)
def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto

# Ler mapa de conhecimento
mapa = []
with open("mapa_doencas.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        mapa.append({
            "Sintoma1": normalizar(row["Sintoma1"]),
            "Sintoma2": normalizar(row["Sintoma2"]),
            "Doenca": row["Doenca"]
        })

# Ler frases
with open("sintomas.txt", "r", encoding="utf-8") as file:
    frases = file.readlines()


def diagnosticar(frase):
    frase_original = frase.strip()
    frase = normalizar(frase)

    resultados = {}

    for item in mapa:
        contagem_local = 0

        # evitar falsos positivos com palavras pequenas (stopwords)
        palavras_frase = frase.split()
        palavras1 = [p for p in item["Sintoma1"].split() if len(p) > 2 and p not in ["com", "para", "por"]]
        palavras2 = [p for p in item["Sintoma2"].split() if len(p) > 2 and p not in ["com", "para", "por"]]

        # verificar se toda palavra chave aparece exatamente na lista de palavras da frase
        if palavras1 and all(p in palavras_frase for p in palavras1):
            contagem_local += 1

        if palavras2 and all(p in palavras_frase for p in palavras2):
            contagem_local += 1

        if contagem_local > 0:
            doenca = item["Doenca"]

            if doenca not in resultados:
                resultados[doenca] = 0

            resultados[doenca] += contagem_local

    if not resultados:
        return frase_original, "Diagnóstico não identificado", 0.0, "baixa"

    # escolher melhor diagnóstico
    melhor_doenca = max(resultados, key=resultados.get)
    contagem = resultados[melhor_doenca]

    # calcular score (0 a 1)
    max_sintomas = 2
    score = min(contagem / max_sintomas, 1.0)

    # classificar nível (opcional, mas bom manter)
    if score >= 0.75:
        nivel = "alta"
    elif score >= 0.4:
        nivel = "média"
    else:
        nivel = "baixa"

    return frase_original, melhor_doenca, score, nivel


# Testar
for frase in frases:
    texto, doenca, score, nivel = diagnosticar(frase)

    print(f"Frase: {texto}")
    print(f"Diagnóstico sugerido: {doenca}")
    print(f"Score: {score:.2f}")
    print(f"Nível de confiança: {nivel}")
    print("-" * 50)