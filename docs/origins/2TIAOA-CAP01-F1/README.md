# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Projeto: Exploração e Implementação de Dados de Saúde 

## CardioIA Vision Lab

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/jonastadeufernandes">Jonas Tadeu V. Fernandes - RM563027</a>
- <a href="https://www.linkedin.com/">Levi Passos Silveira Marques - RM56557</a>
- <a href="https://www.linkedin.com/in/raphaelsilva-phael">Raphael da Silva - RM561452</a> 
- <a href="https://www.linkedin.com/in/raphael-dinelli-8a01b278">Raphael Dinelli Neto - RM562892</a> 
- <a href="https://www.linkedin.com/in/yan-cotta">Yan Pimental Cotta - RM562836</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/caique-nonato/">Caique Nonato da Silva Bezerra</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato">André Godoi</a>


## 📜 Descrição

### 1. Visão Geral do Conjunto de Dados

O trabalho consiste na coleta de dados quantitativos, textuais e de imagem para futura construção de uma plataforma de Inteligência artificial capaz de monitorar pacientes cardíacos, auxiliando no diagnóstico, tratamento e acompanhamento desses. A aplicação terá por objetivo simular um ecossistema de inteligência médica aplicado à cardiologia moderna.

Para tanto, foram coletados a partir de fontes públicas como Kaggle e Scielo. Isso implica que os dados não sofrem com questões críticas de governança, dados que foram obtidos de forma legal e previamente tratados para manter o sigilo de informações pessoais necessário. Ademais, a utilização para fins exclusivamente didáticos também está em conformidade com a finalidade de uso, pois todo projeto aqui desenvolvido não implica utilização comercial que possa desviar os termos de consentimento de compartilhamento desses dados por suas origens.

### 2. Dataset de dados quantitativos

O dataset de dados quantitativos foi coletado na plataforma Kaggle, comumente utilizada na comunidade de Data Science para fins educacionais.   

O dataset utilizado foi [Heart Disease Dataset](https://www.kaggle.com/datasets/sintariosatya/heart-disease-dataset), datado de 1988 e obtido por meio da coleta de dados de saúde originários dos Estados Unidos da América e da União Europeia. Originalmente, ele possui 76 atributos, mas o conjunto publicado que aqui será utilizado possui 14 atributos. 

Ele contém 1.024 registros, com as 14 variáveis clínicas relacionadas a fatores de risco, exames e indicadores de doença cardíaca. As variáveis incluem atributos demográficos (idade e sexo), medidas fisiológicas (pressão arterial em repouso, colesterol sérico, frequência cardíaca máxima), além de variáveis categóricas associadas a exames e sintomas clínicos. A variável-alvo descreve a presença ou ausência de doença cardíaca no paciente no momento das medições dos demais atributos. Não constam informações sobre o desfecho do tratamento (óbito ou recuperação). 

Também foi verificada a representatividade da amostra em termos de sexo: o dataset conta com proporção aproximada de 30% de mulheres para 70% de homens. Dado que doenças cardíacas afetam majoritariamente os homens, entendemos que o conjunto de dados é representativo da população estudada.

#### 2.1 Verificação de Qualidade e Integridade dos Dados

Foi realizada uma análise inicial com o objetivo de verificar a integridade, consistência e adequação dos dados para uso futuro em modelos de Inteligência Artificial aplicados à saúde cardiovascular.

#### Observação: o script utilizado para a análise do dataset está disponível em: 
[Script de análise exploratória](./src/analisys.py)

Foram conduzidas as seguintes verificações:

- Identificação de valores nulos (NaN);
- Busca por possíveis valores ausentes mascarados (ex.: "?");
- Avaliação de valores mínimos para detectar possíveis inconsistências clínicas (como pressão arterial ou colesterol iguais a zero).

Os resultados indicaram:

- Ausência de valores nulos explícitos;
- Ausência de valores inválidos representados por caracteres especiais;
- Valores mínimos clinicamente plausíveis nas variáveis contínuas (idade mínima de 18 anos, colesterol mínimo de 100 mg/dL e pressão arterial mínima dentro de limites fisiológicos possíveis).

Dessa forma, conclui-se que o dataset apresenta boa qualidade estrutural para uso analítico, não sendo necessária, nesta fase, imputação ou tratamento adicional de dados ausentes.

#### 2.2. Definição e Análise das Variáveis Alvo

Para nossa análise do conjunto de dados elegemos duas variáveis relacionadas ao diagnóstico:

- target_binary: indica presença (1) ou ausência (0) de doença cardíaca;
- num: representa o grau de severidade da doença, variando de 0 a 4.

Observou-se que:

- 554 registros (54,1%) correspondem a pacientes sem doença cardíaca;
- 470 registros (45,9%) correspondem a pacientes com diagnóstico positivo.

Essa distribuição demonstra um bom balanceamento para classificação binária, reduzindo o risco de viés estatístico em modelos supervisionados que venham a ser treinados posteriormente.

Entretanto, ao analisar a variável de severidade (num), verificou-se desbalanceamento entre as classes de gravidade. A classe 2 concentra a maior parte dos casos positivos, enquanto as classes 3 e 4 possuem representatividade significativamente menor. Esse comportamento pode influenciar o desempenho de modelos multiclasses, favorecendo a predição da classe majoritária.

#### 2.3. Análise Visual

Foram gerados gráficos de distribuição para:

### Figura 1 – Distribuição da Doença Cardíaca (Binária)

![Distribuição Binária](assets/images/grafico_target.png)

A Figura 1 demonstra o equilíbrio entre pacientes saudáveis e diagnosticados com doença cardíaca.

---

### Figura 2 – Distribuição da Gravidade da Doença

![Distribuição Gravidade](assets/images/grafico_gravidade.png)

Observa-se desbalanceamento entre as classes de severidade.

---

### Figura 3 – Distribuição Etária dos Pacientes

![Distribuição Idade](assets/images/grafico_idade.png)

A maior concentração de pacientes encontra-se em faixas etárias adultas e idosas.

A visualização reforça o equilíbrio da variável binária e evidencia o desbalanceamento das subclasses de gravidade. A distribuição de idade demonstra predominância de pacientes em faixas etárias adultas e idosas, perfil esperado em estudos cardiovasculares.

#### 2.4 Considerações para Aplicação em IA
A análise exploratória confirma que o dataset é adequado para aplicações de:

- Classificação binária (detecção de doença cardíaca);
- Classificação multiclasses (predição de severidade);
- Estudos comparativos de fatores de risco.

Contudo, para modelos multiclasses, poderá ser necessária a aplicação de técnicas de balanceamento (como oversampling, undersampling ou ponderação de classes) a fim de mitigar possíveis vieses decorrentes da distribuição desigual das classes de gravidade.

Logo, acreditamos que a partir deste dataset será possível trabalhar predições de diagnósticos cardíacos bem como os seus graus de severidade associados. A partir dele pretendemos treinar modelos de IA capazes de captar informações correspondentes de outras origens de dados, como dispositivos IOT e devolver as predições aos usuários competentes a tomada de decisão sobre o paciente.

### 3. Dados de Textos e Justificativa 

Para coleta dos dados de texto utilizamos a plataforma de artigos científicos [Scielo.org](https://www.scielo.org/pt-br/). Trata-se de uma organização pública à qual se pode ter acesso a publicações de diversas revistas científicas, nos termos da plataforma. 

O objetivo dos textos coletados é formar uma base inicial que permita a construção de chatbots, que auxiliem no processo de condução, diagnose e suporte psicológico, fisíco, administrativo e social do pacientes e demais públicos de interesse envolvidos no tratamento. Os textos permitirão futuras análises NLP (Natural Language Processing) e servirão de base de conhecimento para os chatbots.

Os são artigos selecionados foram:

- "A pessoa com insuficiência cardíaca na perspectiva da finitude: uma compreensão à luz de Martin Heidegger": selecionado pelo potencial de corpus analítico para análise de sentimentos utilizando NLP. O artigo relata sentimentos de pacientes com quadro de insuficiência cardíaca crônica e avança. No âmbito do chatbot pode suportar médicos a oferecer melhor suporte psicológico aos pacientes terminais.
- "Síndrome da Função Cardíaca Deficiente: um novo diagnóstico de enfermagem para pessoas com insuficiência cardíaca": selecionado por descrever quadros de insuficiência cardíaca de acordo com parâmetros de diagnóstico prévio realizado na enfermaria. Selecionado pelo potencial que o chatbot treinado poderá oferecer à enfermagem.
- "O custo do tratamento médico na insuficiência cardíaca avançada: uma perspectiva latino-americana": selecionado por descrever o entendimento dos custos de tratamento médico no quadro de insuficiência cardíaca, podendo oferecer mais suporte aos gestores hospitalares sobre a melhor condução dos casos do ponto de vista administrativo. 
- "Conhecimento dos fatores de risco modificáveis para doença cardiovascular entre mulheres e seus fatores associados": um estudo de base populacional: selecionado para controlar o viés de amostral e algorítmico da população masculina na base de conhecimento, dado que é sabido que os sintomas e diagnóstico de doenças cardiovasculares são distintos entre homens e mulheres. Desta forma, refletimos e antecipamos problemas de "preconceito algorítmico" subjacentes em nosso conjunto de dados.

#### 3.1 Processo de Limpeza e Vetorização do Corpus Textual

O objetivo do arquivo text_preprocessing.py é realizar a higienização e padronização dos textos brutos armazenados em data/raw/texts/. O pipeline de pré-processamento inclui a normalização para letras minúsculas, remoção de caracteres especiais, eliminação de stopwords, tokenização e filtragem de termos muito curtos. Os dados limpos são salvos em data/processed/texts/.

Contudo, a limpeza é apenas a etapa inicial. Para que os modelos de Inteligência Artificial possam compreender e analisar esses artigos, transformaremos os textos processados em representações matemáticas através de técnicas de Vetorização e Word Embeddings (como TF-IDF, Word2Vec ou modelos pré-treinados como BERT).

Essa transformação permite que a máquina calcule a similaridade semântica entre as palavras. Além disso, planejamos utilizar técnicas de reconhecimentoe  classificação informações cruciais dentro do texto livre, como a extração automática de sintomas (ex: dispneia, fadiga), medicamentos e fatores de risco.

#### 3.2 Processo de Limpeza e Vetorização do Corpus Textual

A integração de Processamento de Linguagem Natural é um dos pilares para simular um ecossistema de cardiologia moderna no projeto CardioIA. O corpus textual selecionado e as técnicas de NLP propostas atuarão em três frentes principais:

Base de Conhecimento para Assistentes Virtuais (Chatbots): Os artigos sobre insuficiência cardíaca e fatores de risco servirão como um banco de dados estruturado. Um agente conversacional inteligente poderá consultar esse acervo (utilizando técnicas como Retrieval-Augmented Generation - RAG) para fornecer respostas precisas e seguras a dúvidas frequentes de pacientes, atuando como um canal de triagem primária e orientação.

Extração e Estruturação de Prontuários (NER): Na prática clínica, a maior parte dos dados do paciente está em formato de texto livre (anotações médicas e de enfermagem). Ao treinar modelos de extração (NER) nos artigos científicos do Scielo, capacitamos a IA a ler prontuários desestruturados, extrair as variáveis clínicas (como "pressão alta" ou "tabagismo") e transformá-las em dados numéricos. Isso permitirá cruzar as informações textuais com o nosso dataset da Fase 1 para retroalimentar os modelos preditivos.

Suporte Psicológico e Análise de Sentimento: Utilizando o artigo sobre a perspectiva da finitude, podemos treinar modelos analíticos para identificar o tom emocional em relatos de pacientes. Isso fornece à equipe multidisciplinar (enfermagem e psicologia) um "termômetro" do estado mental do paciente com doença avançada, permitindo abordagens terapêuticas mais humanizadas e direcionadas.

#### 3.3 Justificativa

A integração de Processamento de Linguagem Natural é um dos pilares para simular um ecossistema de cardiologia moderna no projeto CardioIA. O corpus textual selecionado e as técnicas de NLP propostas atuarão em 2 frentes principais:

- Base de Conhecimento para Assistentes Virtuais (Chatbots): Os artigos sobre práticas clínicas servirão como um banco de dados estruturado. Um agente conversacional inteligente poderá consultar esse acervo (para fornecer respostas precisas e seguras a dúvidas frequentes e elaborar respostas de segundo o público de interesse (médicos, pacientes ou enfermeiros, por exemplo) , atuando como um canal de triagem primária e orientação.
- Suporte Psicológico e Análise de Sentimento: Utilizando o artigo sobre a perspectiva da finitude, podemos treinar modelos analíticos para identificar o tom emocional em relatos de pacientes. Isso fornece à equipe multidisciplinar (enfermagem e psicologia) um "termômetro" do estado mental do paciente permitindo abordagens terapêuticas mais humanizadas e direcionadas.


### 4. Dados de Imagens

A nossa base de dados de imagens também foi obtida através do Kaggle. O dataset chamado [ECG Images Dataset of Cardiac Patients]([https://www.kaggle.com](https://www.kaggle.com/datasets/evilspirit05/ecg-analysis)), é composto por 100 imagens de exames de ECG (Eletrocardiograma), tendo 25 variações do exame e 4 categorias principais (`post mi history ecg`,`normal ecg`,`myocardial infarction ecg` e `abnormal heartbeat ecg`) os dados foram coletado pelo Instituto de Cardiologia Ch. Pervaiz Elahi, em Multan, Paquistão. 

O dataset foi construído com o objetivo de treinar modelos de detecção de doenças cardíacas, interpretação de sinais e métodos de aprendizado profundo baseados em imagens. Segundo a documentação, os casos foram classificados da seguinte maneira:

   - Os casos de batimentos cardíacos anormais contêm imagens de ECG que exibem padrões de ritmo irregulares.
   - Os casos com histórico de infarto do miocárdio incluem pacientes previamente diagnosticados com infarto do miocárdio, mas que não estão apresentando um episódio agudo no momento.
   - Os casos normais representam imagens de ECG de indivíduos sem anormalidades cardíacas relatadas."

#### 4.1 Processo seleção das Imagens

As imagens escolhidas têm as seguintes classes clínicas:<br>

- `PMI` --> `post mi history ecg`;
- `N` --> `normal ecg`;
- `MI` --> `mycardial infraction ecg`;
- `HB` --> `abnormal heartbeat ecg`;

Sendo exames de pacientes do sexo **masculino M** e **Femenino F**.

> **As imagens estão disponíveis no Google Drive pelo link: [https://drive.google.com/drive/folders/1Xv7WWRR0PPGk-MJ5Ww2kr072cdV-DQix?usp=sharing](https://drive.google.com/drive/folders/1Xv7WWRR0PPGk-MJ5Ww2kr072cdV-DQix?usp=sharing)**


#### 4.2 Planejamento e pré-análise do corpus de imagens

A regra utilizada para a escolha das imagens foi:

25 imagens de cada classe clínica, totalizando 100 imagens no total;

Separação balanceada de aproximadamente 11 a 13 imagens por sexo (masculino e feminino) em cada classe.

A escolha de organizar as imagens de ECG mantendo informações estruturadas na nomenclatura dos arquivos (como classe clínica e sexo, por exemplo, HB01-M e HB02-F) é fundamental porque preserva variáveis relevantes para futuras análises e evita a perda de contexto clínico. Ao garantir diversidade nas classes (normal, arritmia, infarto, etc.) e considerar características demográficas, o conjunto de dados se torna mais representativo da população real. Isso reduz o risco de vieses no desenvolvimento do sistema, visto que a ausência de diversidade pode levar os modelos a apresentarem desempenho desigual entre grupos, gerando discriminação algorítmica. Portanto, essa seleção equilibrada e documentada contribui para uma maior robustez, transparência e responsabilidade no uso da IA aplicada à saúde.

Posteriormente, aplicaremos técnicas de pré-processamento para isolar os sinais elétricos (as curvas do traçado) do plano de fundo, transformando a imagem original em uma matriz binária livre de ruídos (como o quadriculado do papel milimetrado).

Esses dados tratados serão utilizados para analisar a morfologia das curvas do eletrocardiograma. O mapeamento da geometria do sinal permitirá a identificação e medição de indicadores médicos essenciais para o diagnóstico (Onda P, Complexo QRS e Onda T), além da extração de outras métricas espaciais, como amplitude e intervalos sistemáticos.

Dessa forma, as imagens serão tratadas como objetos espaciais. Para isso, utilizaremos a biblioteca Python OpenCV (cv2), aplicando técnicas clássicas de detecção de bordas e contornos baseadas em gradientes de intensidade, como os filtros de Canny ou Sobel.

Nosso objetivo final na trilha de Visão Computacional será processar esses dados utilizando Redes Neurais Convolucionais (CNNs). O emprego das CNNs visa treinar o modelo para aprender a hierarquia de características visuais de maneira autônoma, tornando-o capaz de reconhecer padrões complexos — como a elevação do segmento ST ou inversões da onda T — e correlacioná-los às classes de diagnóstico clínico já definidas no dataset (myocardial infarction, abnormal heartbeat, entre outras).

#### 4.3 Justificativa e Impacto Clínico

Entendemos que o modelo de CNN a ser desenvolvido poderá agregar valor ao ecossistema hospitalar de pelo menos três maneiras:

- Suporte ao Diagnóstico Individual: O algoritmo pode ser treinado para realizar uma primeira leitura do eletrocardiograma, indicando possíveis anomalias para a equipe de enfermagem e médicos. Isso funciona como um sistema de suporte à decisão, padronizando protocolos de triagem e priorizando o encaminhamento de casos graves, mitigando erros humanos decorrentes de fadiga.
- Integração com Wearables e IoT: O modelo poderá ser acoplado a dispositivos de monitoramento contínuo (IoT), permitindo a análise do traçado em tempo real. Isso viabiliza a notificação imediata do paciente e da equipe médica à distância, atuando de forma preditiva ao reconhecer padrões morfológicos que antecedem eventos cardíacos críticos.
- Saúde Populacional e Pesquisa: De forma agregada, a ferramenta permitirá que médicos e pesquisadores identifiquem correlações entre padrões eletrocardiográficos específicos e seus desfechos clínicos ao longo do tempo, auxiliando na formulação de tratamentos de longo prazo e na gestão de saúde populacional.


### Figura 4 - Exemplo de Dado Classe Clínica Normal

![Image ECG](assets/images/Normal(3).jpg)

### 5. Considerações Sobre Dados 

A seleção e organização cuidadosa dos dados textuais e das imagens são fundamentais para reduzir vieses e promover maior responsabilidade no desenvolvimento de sistemas de IA aplicados à saúde. 

No caso dos textos, utilizar fontes confiáveis e incluir diferentes perspectivas (como diretrizes clínicas, estudos científicos e documentos de saúde pública) contribui para evitar uma visão limitada ou enviesada sobre doenças cardíacas, garantindo que os modelos futuros aprendam padrões mais amplos e contextualizados. Já nas imagens de ECG, manter diversidade de classes clínicas e considerar variáveis relevantes, como sexo biológico, ajuda a tornar o conjunto de dados mais representativo da população real. Conjuntos desequilibrados ou homogêneos podem levar a modelos que performam melhor para um grupo específico e pior para outros, gerando discriminação algorítmica. Assim, a organização estruturada e a diversidade intencional dos dados fortalecem a qualidade, a equidade e a confiabilidade de futuras aplicações de Inteligência Artificial na área da saúde.


## 📁 Estrutura de pastas

Dentre os arquivos e pastas presentes na raiz do projeto, definem-se:

- <b>.github</b>: Nesta pasta ficarão os arquivos de configuração específicos do GitHub que ajudam a gerenciar e automatizar processos no repositório.

- <b>assets</b>: aqui estão os arquivos relacionados a elementos não-estruturados deste repositório, como imagens.

- <b>config</b>: Posicione aqui arquivos de configuração que são usados para definir parâmetros e ajustes do projeto.

- <b>data</b>: Nesta pasta serve para armazenar os dados de textos e artigos.

- <b>document</b>: aqui estão todos os documentos do projeto que as atividades poderão pedir. Na subpasta "other", adicione documentos complementares e menos importantes.

- <b>scripts</b>: Posicione aqui scripts auxiliares para tarefas específicas do seu projeto. Exemplo: deploy, migrações de banco de dados, backups.

- <b>src</b>: Todo o código fonte criado para o desenvolvimento do projeto ao longo das 7 fases.

- <b>README.md</b>: arquivo que serve como guia e explicação geral sobre o projeto (o mesmo que você está lendo agora).

## 🔧 Como executar o código

Toda a análise exploratória do dataset pode ser executada navegando até o diretório src e executando o comando.
```bash
python analisys.py
```
Para executar código de tratamento e limpeza dos textos brutos de artigos, execute o comando.
```bash
python text_preprocessing.py
```

## 🗃 Histórico de lançamentos

* 0.1.0 - XX/XX/2026
    *

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>


