# CardioIA · Fase 5 — Arquitetura do sistema e integração da Parte 2

> Documento produzido pela dupla responsável pela **Parte 2 (Interface de
> Interação com o Usuário)**. Ele registra o modelo mental do sistema
> integrado e o **contrato de API** que a interface espera do backend da
> Parte 1 — servindo de handoff para o restante do grupo.

## 1. Visão integrada do sistema (modelo mental)

```
Paciente
   │ mensagem em linguagem natural
   ▼
┌──────────────────────────────┐
│ PARTE 2 · Interface de chat  │  HTML + CSS + JS (src/frontend/)
│  - envia POST /api/chat      │
│  - exibe respostas, intents  │
│  - renderiza triagem (card)  │
└──────────────┬───────────────┘
               │ JSON { message, session_id }
               ▼
┌──────────────────────────────┐      ┌─────────────────────────────┐
│ PARTE 1 · Backend Flask      │─────►│ IBM Watson Assistant        │
│  - gerencia sessões          │◄─────│  intents / entities /       │
│  - traduz Watson ⇄ contrato  │      │  dialog nodes               │
└──────────────┬───────────────┘      └─────────────────────────────┘
               │ (opcional)
               ▼
┌──────────────────────────────┐      ┌─────────────────────────────┐
│ IR ALÉM 1 · IA Generativa    │      │ IR ALÉM 2 · RPA + IA        │
│ Gemini: texto clínico livre  │      │ monitora dados clínicos em  │
│ → JSON estruturado           │      │ BD relacional + logs NoSQL  │
└──────────────────────────────┘      └─────────────────────────────┘
```

Pontos de integração já contemplados pela interface:

- **Parte 1:** todo o tráfego passa pelo contrato `POST /api/chat` (abaixo).
- **Ir Além 1:** o campo opcional `structured` da resposta carrega o JSON
  clínico extraído pelo fluxo Gemini (já implementado em
  `Ir além 1/src/extracao_clinica_ia.ipynb`); a interface o renderiza como
  um cartão de triagem com destaque para o `nivel_urgencia`.
- **Ir Além 2:** os alertas do robô podem ser entregues ao usuário como
  mensagens do assistente pelo mesmo contrato, sem mudança no frontend.

## 2. Contrato de API (handoff para a Parte 1)

O backend Flask da Parte 1 deve expor:

### `POST /api/chat`

Requisição:

```json
{ "message": "Estou com dor no peito", "session_id": null }
```

Resposta:

```json
{
  "reply": "⚠️ Dor no peito pode ser sinal de emergência...",
  "session_id": "8c3f...",
  "intent": "emergencia",
  "confidence": 0.93,
  "source": "watson",
  "structured": null
}
```

Regras:

1. `session_id = null` na 1ª mensagem → o backend cria a sessão no Watson
   (API v2, `createSession`) e devolve o id; o frontend o reenvia depois.
2. `intent`/`confidence`: primeira intenção reconhecida pelo Watson
   (`output.intents[0]`), ou `null` no fallback.
3. `source`: `"watson"` no backend real; o mock usa `"mock"`. A interface
   mostra esse rótulo ao usuário — **nenhuma resposta simulada aparece como
   real** (princípio de transparência adotado pelo grupo).
4. `structured`: opcional; JSON do Ir Além 1 quando o fluxo de extração for
   acionado.
5. Erros: HTTP 400 para corpo inválido; a interface trata falhas de rede e
   códigos ≠ 2xx com mensagem amigável.

### `GET /api/health`

`{ "status": "ok", "source": "watson" | "mock" }` — usado pelo selo de
estado no cabeçalho da interface.

### Como servir o frontend

Recomendado: o próprio Flask da Parte 1 serve `src/frontend/` como estático
(mesma origem, sem CORS). O mock `src/frontend/mock_backend/server.py` já
demonstra exatamente esse arranjo e pode ser usado como esqueleto — basta
substituir a função `classificar()` pela chamada real ao Watson Assistant.

## 3. Decisões de projeto da Parte 2

| Decisão | Justificativa |
|---|---|
| HTML + CSS + JS puro (sem framework/build) | O enunciado pede "interface simples"; qualquer integrante executa com `python server.py`, sem Node/npm. |
| Contrato definido antes do backend existir | A Parte 1 ainda não está no repositório; definir o contrato agora permite desenvolvimento em paralelo e integração sem retrabalho. |
| Mock rotulado (`source: "mock"`) | A interface precisa ser demonstrável hoje; o rótulo garante que resposta simulada nunca se passe por resposta real do Watson. |
| Sessão em `sessionStorage` | Espelha o ciclo de vida de sessão do Watson v2 e zera a conversa ao fechar a aba (sem persistir dado de saúde no navegador — boa prática LGPD para um protótipo). |
| Aviso ético fixo + resposta de emergência | Assistente de saúde não diagnostica nem prescreve; emergências são direcionadas ao 192 (SAMU). |
