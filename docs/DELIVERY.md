# Registro de entrega e evidências

Atualização: 31/10/2026. Apenas resultados verificados são marcados como concluídos.

| Item | Estado |
|---|---|
| Repositório / integração | [PR #1](https://github.com/Phaeld/2TIAOA-CAP01-F7/pull/1) merged; código e atualizações em `main` |
| Privacidade e tutor | Pendente: observado público; Phaeld precisa tornar privado e compartilhar com tutor |
| Vercel pública | https://cardioia-fiap-final.vercel.app — login, painel, alertas e Gemini verificados |
| Backend público | https://cardioia-api-6efu.onrender.com — 16 verificações passaram; plano gratuito |
| CI/CD Git | [Push em main → testes → deploy Vercel aprovado](https://github.com/Phaeld/2TIAOA-CAP01-F7/actions/runs/41214343191) |
| EAS / APK | [Build FINISHED](https://expo.dev/accounts/yancotta/projects/cardioia-fiap-final/builds/01b49027-ce04-4310-8c76-30e3ada07c04) · [APK](https://expo.dev/artifacts/eas/FaDIB1IArS8CZvkOeWZqxYtCvV3GeZZCKNhp7r080Qg.apk) |
| Android físico | Pendente: Raphael ou outro integrante fará instalação, login e leitura |
| Wokwi | Raphael: captura MicroPython, pinagem, LED/OLED e link público pendentes |
| Gemini real | Validado pela API pública e Web; nenhuma chave de provedor pendente |
| Visão F4 | ResNet50/Grad-CAM validados localmente; hospedagem adiada por escolha de Yan |
| Vídeo até 5 min | Pendente: gravar depois do teste Wokwi → Web/APK |
| PDF até 5 páginas | Relatório de 4 páginas atualizado; fechar com Wokwi e evidência física |

## Verificações realizadas

27 testes de integração passaram localmente e no GitHub Actions: autenticação/expiração, escopo do dispositivo, validação, idempotência/conflito, persistência local, ordenação e estado antigo, modelo F6, NLP, fallback/contrato Gemini, visão desativada, limites e CORS. Build Web e bundle Android passaram.

Na API pública, 16 verificações passaram: health, login, proteção de acesso, sinais normal/alerta/emergência, reenvio idempotente, conflito, histórico e painel, modelo F6 original, NLP, Gemini real, CORS e indicação correta de visão indisponível. [Registro JSON](evidence/public-api-validation.json).

Caso original F6: probabilidade 0,99, classe HIGH e protocolos P02/P05/P08/P10. ResNet50 e Grad-CAM executaram com imagem sintética pelo backend local; isso verifica runtime, não acurácia clínica.

Na Web pública: login, cenário de alerta (132 bpm, 39,1 °C), histórico, estado sem sinal recente e conversa Gemini reais. O risco operacional LOW 18,5% e o alerta de sensor HIGH aparecem separados. A URL funciona sem autenticação Vercel e uma rota SPA profunda retorna a aplicação.

APK de 56.987.279 bytes, pacote `br.com.cardioia.fiap`, integridade ZIP verificada, bloco de assinatura presente e URL HTTPS de produção encontrada no bundle. Build baseado em `8446d0bd4b071d0f5f02f3d25cc1c3683af545d4`. [Registro e SHA-256](evidence/apk-validation.json). Isso não substitui instalar e testar em aparelho físico.

## Evidências disponíveis

- [Painel público](evidence/public-dashboard.jpg).
- [Gemini pela Web pública](evidence/public-gemini.jpg).
- [GitHub Actions com deploy concluído](evidence/ci-deploy-success.jpg).
- [Expo Succeeded e QR de instalação](evidence/expo-apk-install.jpg).
- [Painel local anterior](evidence/local-dashboard.jpg), identificado como local.

## Aceite restante do grupo

1. Raphael conclui `IoT/main.py`, sensores, Wi-Fi/retry e LED/OLED no Wokwi, usando [contrato e URL publicados](../IoT/README.md).
2. Instalar APK no Android e registrar modelo do aparelho, versão Android, data, login e visualização da mesma leitura da Web/Wokwi. Confirmar uma nova leitura normal, um alerta e o estado sem sinal após desconexão.
3. Adicionar link público Wokwi e prints reais do fluxo completo.
4. Gravar vídeo de até 5 minutos e inserir o link no README e relatório.
5. Phaeld torna o repositório privado e compartilha com o tutor. Confirmar acesso das integrações após a mudança de visibilidade.
6. Revisar nomes/RMs e atualizar o PDF sem ultrapassar 5 páginas. A visão hospedada continua sendo uma limitação explícita do perfil gratuito escolhido.

Senha do login e chave IoT são fornecidas por Yan em canal privado. Não inserir credenciais em prints, vídeo, repositório ou projeto Wokwi público.

## Roteiro do vídeo: 4min40s

- 00:00-00:30: equipe, proposta acadêmica e diagrama.
- 00:30-01:15: login na URL Vercel e painel.
- 01:15-02:15: alterar Wokwi, mostrar HTTP/LED e atualização Web.
- 02:15-03:00: explicar dez features, previsão F6 e pergunta Gemini.
- 03:00-03:40: APK instalado mostrando a mesma leitura; visão local como módulo adiado na hospedagem.
- 03:40-04:15: desconexão/estado antigo e tratamento de falha.
- 04:15-04:40: links, CI/CD, README, PDF e limitações.
