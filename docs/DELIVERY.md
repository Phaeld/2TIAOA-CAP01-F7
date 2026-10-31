# Registro de entrega e evidências

Atualização: 31/10/2026. Preencher apenas com resultados verificados.

| Item | Estado |
|---|---|
| Repositório | https://github.com/Phaeld/2TIAOA-CAP01-F7 |
| Privacidade e tutor | Pendente: observado público, requer proprietário |
| Vercel pública | Conta conectada; publicação pendente |
| Backend público | Pendente |
| CI/CD Git | Backend, Web e Mobile aprovados no CI remoto; deploy automático depende de token/configuração |
| EAS / APK | Projeto yancotta/cardioia-fiap-final criado; bundle validado, build EAS pendente |
| Android físico | Pendente: aparelho, Android, data, login e painel |
| Wokwi | Raphael: simulação e link público pendentes |
| Gemini real | Aguardando chave e chamada de validação |
| Vídeo até 5 min | Pendente |
| PDF até 5 páginas | Rascunho técnico; fechar após deploy/evidências |

## Verificação local

27 testes passaram: autenticação/expiração, chaves e escopo, tipos/faixas, idempotência e conflito, persistência, ordenação, estado antigo, saída original da fase 6, NLP, fallback, contrato do provedor, visão desativada, limite de corpo e CORS.

Caso de referência F6: probabilidade 0,99, classe HIGH, protocolos P02/P05/P08/P10. Web: build concluído. Mobile: dependências compatíveis e export Android concluído, **não é APK assinado**. ResNet50/Grad-CAM executados com imagem sintética para smoke de runtime, **não é avaliação de acurácia**.

Navegador local: login real e envio normal/alerta atualizaram painel (132 bpm, 39,1 °C, alertas HIGH e risco operacional LOW 18,5%, corretamente separados).

Evidência local: [painel com leitura e alerta](evidence/local-dashboard.jpg). Validados também login, estado sem sinal e indicação de visão desativada no perfil gratuito. Esta imagem não comprova hospedagem pública.

## Evidências a coletar

1. Vercel Ready e URL pública; CI GitHub aprovado e commit associado ao deploy.
2. Web atualizada pelo Wokwi; mesmo evento no APK instalado.
3. EAS Finished com link APK; aparelho e versão Android.
4. Wokwi MicroPython e LED/OLED reagindo.

Guardar imagens sem segredos em `docs/evidence/`. Identificar prints locais como locais, não como prova de deploy.

## Roteiro do vídeo: 4min40s

- 00:00-00:30: equipe, proposta acadêmica e diagrama.
- 00:30-01:15: login na URL Vercel, painel.
- 01:15-02:15: alterar Wokwi, mostrar HTTP/LED e atualização Web.
- 02:15-03:00: explicar dez features, previsão F6 e pergunta Gemini.
- 03:00-03:40: APK instalado, mesmo evento; imagem se perfil completo ativo.
- 03:40-04:15: desconexão/estado antigo e erro.
- 04:15-04:40: links, CI/CD, README, PDF e limitações.

CI verificado: https://github.com/Phaeld/2TIAOA-CAP01-F7/actions/runs/41211945766. Histórico por branch: https://github.com/Phaeld/2TIAOA-CAP01-F7/actions/workflows/ci.yml. PR de integração: https://github.com/Phaeld/2TIAOA-CAP01-F7/pull/1.
