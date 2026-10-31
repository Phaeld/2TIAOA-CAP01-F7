# Deploy e distribuição

Um backend Python, Web na Vercel e APK via Expo EAS. Não há banco externo obrigatório.

## Ambiente publicado em 31/10/2026

Web: https://cardioia-fiap-final.vercel.app. API: https://cardioia-api-6efu.onrender.com. Gemini validado pela API pública e pela Web. CI/CD GitHub Actions → Vercel comprovado: [execução](https://github.com/Phaeld/2TIAOA-CAP01-F7/actions/runs/41214343191). Render: `srv-dbj0d6flk1mc73ftu9g0`, plano `free`, região Virginia, branch `main`, deploy via GitHub Actions após testes. Segredos estão nos serviços e no GitHub Actions, nunca no código.

## Backend Render

Raiz do repositório como contexto, `Backend/Dockerfile`, health check `/health`, porta `$PORT`, um worker.

Variáveis: `CARDIOIA_SECRET` (mínimo 32 caracteres), `CARDIOIA_DEMO_PASSWORD` (12), `CARDIOIA_DEVICE_KEY` (24), `CARDIOIA_CORS_ORIGINS` (URL Vercel exata), `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.5-flash-lite`. Somente dados simulados. Segredos ficam no servidor.

Perfil escolhido por Yan em 31/10/2026: **gratuito; hospedagem de visão adiada**. `render.yaml` prepara esse perfil: sensores, risco, NLP e chat, sem TensorFlow. A rota de visão retorna 503 honestamente. Histórico SQLite é efêmero nesse perfil e pode ser perdido ao reiniciar/republicar; o serviço pode suspender por inatividade.

**Perfil completo:** instância de pelo menos 2 GB (`1c-2g`, antigo Standard), build arg `ENABLE_VISION=true`, runtime `CARDIOIA_VISION_ENABLED=true`, disco persistente 1 GB em `/app/data`, `CARDIOIA_DB_PATH=/app/data/cardioia.db`. Custo depende de aprovação do responsável. Não declarar integração completa da visão com perfil gratuito.

O job `deploy-backend` solicita à API Render o SHA que passou no CI e aguarda o estado `live`. Configurar secret `RENDER_API_KEY` e variable `RENDER_SERVICE_ID`. Deixar `autoDeployTrigger: off` para evitar deploy duplicado pela integração Git. Validar login, leitura, Gemini e imagem na URL real. Modelo de visão é carregado sob demanda; o primeiro upload é mais lento.

## Vercel

Importar `Phaeld/2TIAOA-CAP01-F7` com raiz `/`, não `Web`. `vercel.json` define instalação/build em `Web`, saída `Web/dist` e fallback SPA. Configurar `VITE_API_URL=https://<backend>` antes do build. Essa URL é pública e não contém segredos.

Conectar GitHub e definir a branch de produção para deploy por push. Deploy CLI isolado não prova CI/CD Git. Caso a integração não enxergue o repositório de Phaeld, o proprietário deve autorizar acesso ao repo. Permissão de push de Yan não garante acesso da integração.

Validar URL em janela anônima, login, navegação SPA, atualização de leitura e tratamento de API fora do ar. Adicionar origem exata da Vercel ao CORS do backend, sem barra final.

## Expo EAS / APK

`Mobile/app.json`: `android.package=br.com.cardioia.fiap`. `Mobile/eas.json`: perfil `preview`, distribuição interna, `android.buildType=apk`.

```bash
cd Mobile
npm ci
npx eas-cli login
npx eas-cli env:set --environment preview --name EXPO_PUBLIC_API_URL --value https://<backend> --visibility plaintext
npx eas-cli build --platform android --profile preview
```

O projeto já está vinculado a `yancotta/cardioia-fiap-final` em `app.json`; não executar `eas init` novamente. A URL da API é incorporada ao APK; alterá-la exige novo build. Não usar localhost na entrega móvel.

Ao terminar, registrar link do build e APK em `docs/DELIVERY.md` e README. Baixar no Android, permitir instalação da fonte quando solicitado, instalar e testar login e dados. Registrar aparelho, Android, data e resultado. Bundle exportado/Expo Go não substitui APK em aparelho físico.

## Credenciais e privacidade

`python3 scripts/setup_local.py` cria `.env` ignorado pelo Git. `python3 scripts/configure_services.py` recebe chaves sem eco no terminal. Vercel, EAS e Render suportam login CLI no navegador.

Em 31/10/2026, F7 estava público e YanCotta possuía `WRITE`, não `ADMIN`. Phaeld precisa torná-lo privado e adicionar o tutor (conta GitHub a confirmar), verificando depois acesso das integrações. Não declarar esse requisito cumprido antes da alteração real.

Fontes: [Vercel](https://vercel.com/docs/project-configuration/vercel-json), [EAS APK](https://docs.expo.dev/build-reference/apk/), [Render discos](https://render.com/docs/disks).

## CI/CD via GitHub Actions

A conexão Git direta Vercel → repositório Phaeld não foi autorizada pela integração. Alternativa ativa: job `deploy-web` após backend/web/mobile passarem em cada push de `main`. Configurar secret `VERCEL_TOKEN`, variables `VERCEL_ORG_ID` e `VERCEL_PROJECT_ID`, e `CARDIOIA_DEPLOY_ENABLED=true` somente após o backend e `VITE_API_URL` estarem prontos. Sem essa variável, o deploy é explicitamente ignorado; testes/builds continuam ativos. A variável está habilitada neste ambiente e a publicação por push foi validada.

Projeto Vercel criado: `fiap-fase-7/cardioia-fiap-final`. Projeto Expo criado: https://expo.dev/accounts/yancotta/projects/cardioia-fiap-final. A sessão OAuth da CLI Vercel não permite criar tokens; em uma reinstalação, criar um token de deploy em Account Settings > Tokens e salvá-lo localmente com `python3 scripts/configure_services.py --provider vercel`. Usar escopo do projeto/equipe FIAP quando disponível.

Gemini padrão atualizado para `gemini-3.5-flash-lite`, também usado na F6. O acesso a modelos 2.5 é restrito para novos projetos: [nota oficial de 18/09/2026](https://ai.google.dev/gemini-api/docs/changelog?release=09-18-2026).

O auto-deploy Git nativo do Render não disparou neste repositório de colaborador. Por isso, o workflow também publica o backend pela API Render, sem mudar o plano gratuito. O job falha se o build/deploy falhar ou não chegar ao estado `live` no prazo.
