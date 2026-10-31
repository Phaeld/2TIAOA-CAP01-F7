# Auditoria e migração das fases anteriores

As seis entregas permanecem intactas como clones irmãos em `Documents/FIAP_final`. A fase 7 importa apenas os componentes necessários ao runtime; notebooks e fontes selecionadas ficam em `docs/origins`. `migration-manifest.json` registra repositório, SHA do commit, caminho original e SHA-256 de cada cópia.

| Fase | Encontrado no código | Decisão de integração |
|---|---|---|
| 1 | Três textos limpos e scripts exploratórios; dataset quantitativo descrito, mas não versionado | Corpus alimenta busca TF-IDF do assistente. Não inventar dataset ausente. |
| 2 | Extração por CSV, notebook TF-IDF, portal React com JWT falso e respostas simuladas; ECG MLP sem artefato exportado | CSV + regressão logística real no Python; refazer autenticação/telas via API. ECG opcional permanece referência, sem anunciar modelo inexistente. |
| 3 | ESP32 C++, MQTT, Flask de sinais e regras de alertas | Preservar semântica dos campos e regras; convergir em HTTP autenticado. Raphael converte captura para MicroPython. E-mail não é disparado. |
| 4 | ResNet50 de 97 MB, CNN, Flask e Expo; URL móvel fixada à LAN | Importar ResNet50 + pré-processamento + Grad-CAM; Expo consome URL HTTPS configurável e passa a ter login/painel/chat. |
| 5 | Watson, interface separada/mock e notebook Gemini de extração | Reutilizar fluxo generativo Gemini, escolhido para uma única credencial de LLM; corpus e previsão são contexto do chat. Watson não é obrigatório no runtime. |
| 6 | Random Forest de dez features, protocolos e orquestração Agents SDK/Gemini | Modelo e ProtocolAgent importados; Python executa a sequência explicitamente e Gemini explica a saída. Não confundir risco operacional com diagnóstico individual. |
| 7 | Somente template FIAP | Monorepo com `Backend`, `Web`, `Mobile`, `IoT`, CI e documentação. |

## Principais incompatibilidades resolvidas

- Remoção do JWT fictício, da inferência aleatória e do diagnóstico baseado em nome de arquivo do portal antigo.
- Caminho do `joblib` passa a ser fornecido explicitamente ao agente original; dependência scikit-learn fixada em 1.9.1, versão gravada no artefato.
- TensorFlow/Keras legado é isolado como dependência opcional para manter o núcleo leve. Arquivo `.keras` importado sem retreino e com checksum preservado.
- Notebook NLP antigo referenciava um CSV do Colab com nome diferente e ajustava TF-IDF antes do split. Runtime recompõe pipeline sobre o CSV versionado; não reutiliza acurácias desse notebook como avaliação atual.
- Esquema de sensores é validado em vez de converter strings livremente. Evento possui ID, timestamp e retorno para feedback visual.
- Chat distingue `gemini` de `local_fallback`; falha de provedor retorna 503, sem respostas simuladas rotuladas como IA real.

## O que não constitui evidência de entrega

Build do bundle Android não equivale a APK EAS instalado. Teste com imagem sintética verifica execução, não acurácia. Helper MicroPython não equivale a projeto Wokwi concluído. Ter `vercel.json` e workflow não comprova integração Git/deploy ativa. Links, prints e vídeo serão preenchidos apenas após validação real.
