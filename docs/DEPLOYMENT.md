# Deploy e distribuição

Um backend Python, Web na Vercel e APK via Expo EAS. Não há banco externo obrigatório.

## Backend Render

Raiz do repositório como contexto, `Backend/Dockerfile`, health check `/health`, porta `$PORT`, um worker.

Variáveis: `CARDIOIA_SECRET` (mínimo 32 caracteres), `CARDIOIA_DEMO_PASSWORD` (12), `CARDIOIA_DEVICE_KEY` (24), `CARDIOIA_CORS_ORIGINS` (URL Vercel exata), `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-2.5-flash`. Somente dados simulados. Segredos ficam no servidor.

`render.yaml` prepara perfil gratuito: sensores, risco, NLP e chat, sem TensorFlow. A rota de visão retorna 503 honestamente. Histórico SQLite é efêmero nesse perfil e pode ser perdido ao reiniciar/republicar; o serviço pode suspender por inatividade.

**Perfil completo:** instância de pelo menos 2 GB (`1c-2g`, antigo Standard), build arg `ENABLE_VISION=true`, runtime `CARDIOIA_VISION_ENABLED=true`, disco persistente 1 GB em `/app/data`, `CARDIOIA_DB_PATH=/app/data/cardioia.db`. Custo depende de aprovação do responsável. Não declarar integração completa da visão com perfil gratuito.

Configurar integração Git, branch de produção e `autoDeployTrigger: checksPass`. Validar login, leitura, Gemini e imagem na URL real. Modelo de visão é carregado sob demanda; o primeiro upload é mais lento.

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
npx eas-cli init
npx eas-cli env:create --environment preview --name EXPO_PUBLIC_API_URL --value https://<backend> --visibility plaintext
npx eas-cli build --platform android --profile preview
```

`eas init` grava o ID real do projeto. Nunca inserir UUID fictício. A URL da API é incorporada ao APK; alterá-la exige novo build. Não usar localhost na entrega móvel.

Ao terminar, registrar link do build e APK em `docs/DELIVERY.md` e README. Baixar no Android, permitir instalação da fonte quando solicitado, instalar e testar login e dados. Registrar aparelho, Android, data e resultado. Bundle exportado/Expo Go não substitui APK em aparelho físico.

## Credenciais e privacidade

`python3 scripts/setup_local.py` cria `.env` ignorado pelo Git. `python3 scripts/configure_services.py` recebe chaves sem eco no terminal. Vercel, EAS e Render suportam login CLI no navegador.

Em 31/10/2026, F7 estava público e YanCotta possuía `WRITE`, não `ADMIN`. Phaeld precisa torná-lo privado e adicionar o tutor (conta GitHub a confirmar), verificando depois acesso das integrações. Não declarar esse requisito cumprido antes da alteração real.

Fontes: [Vercel](https://vercel.com/docs/project-configuration/vercel-json), [EAS APK](https://docs.expo.dev/build-reference/apk/), [Render discos](https://render.com/docs/disks).
