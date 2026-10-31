# Roadmap de entrega - Fase 7

Prazo informado pela FIAP: **10/11/2026**. Estado inicial auditado em **31/10/2026**. Critérios de conclusão exigem evidências reais; configuração pronta não equivale a deploy concluído.

| Etapa | Entrega | Responsável | Aceite | Estado |
|---|---|---|---|---|
| 1 | Clonar fases 1-7, inventário e rastreabilidade | Yan | SHAs e arquivos de origem registrados | Concluída |
| 2 | Arquitetura e contrato IoT v1 | Yan | Documento + payload + testes de contrato | Concluída |
| 3 | Backend integrador | Yan | Login, leitura, histórico, risco, NLP e chat passam nos testes | Local validado |
| 4 | React/Vite e Expo integrados | Yan | Build web + bundle Android; login e dados via API | Builds locais validados |
| 5 | Visão real da fase 4 | Yan | ResNet50 + Grad-CAM executados, sem simular predição | Smoke local validado |
| 6 | Vercel + Render + Gemini | Yan | URLs públicas, Gemini real, push aciona deploy | Aguardando configuração/publicação |
| 7 | APK EAS preview | Yan + grupo | Build EAS concluído, APK baixado e instalado em aparelho | Aguardando conta/build/aparelho |
| 8 | MicroPython/Wokwi | Raphael | Captura + HTTP + LED/OLED; link público | Handoff pronto; implementação de Raphael |
| 9 | Evidência fim-a-fim | Grupo | Wokwi atualiza Web e APK; prints e vídeo ≤5 min | Pendente |
| 10 | Entrega final | Grupo | Repo privado + tutor, README com links, PDF ≤5 páginas | Pendente |

## Ordem sugerida até o prazo

- 31/10-02/11: fechar backend, telas, deploy e transmitir a Raphael URL + chave de dispositivo por canal privado.
- 03-05/11: integrar Wokwi, gerar APK e testar em aparelho real.
- 06-08/11: ensaio da demonstração, corrigir falhas e coletar prints.
- 09/11: revisão coletiva do PDF e README, validar acesso do tutor e links em janela anônima.
- 10/11: enviar os entregáveis na plataforma FIAP.

## Prioridade pela rubrica

1. URLs e APK funcionais (3 pontos).
2. Integração backend/interfaces/IA (2,5 pontos).
3. MicroPython e hardware demonstráveis (1,5 ponto; Raphael).
4. Diagrama e comunicação clara dos dados (1,5 ponto).
5. README, relatório e vídeo (1,5 ponto).

Não adicionar notificações externas, microserviços, treinamento de novos modelos grandes, agendamento ou prontuários. A prioridade é fechar e comprovar o fluxo básico.
