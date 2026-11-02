# Visão e Escopo do Projeto — Versão 2

## Sistema de Gestão de Eventos e Auditórios ("Auditório Inteligente")

Documento-base para desenvolvimento
*Versão 2 — complementada com informações da reunião de apresentação do projeto (17/08/2026), com o professor Fábio Silva Lopes*

> **Nota sobre esta versão:** este documento mantém integralmente o conteúdo da Versão 1 (Visão e Escopo) e o complementa com o contexto acadêmico/institucional, os stakeholders, as motivações e os requisitos adicionais apresentados na reunião de kickoff do projeto, disciplina de Práticas Profissionais em Análise e Desenvolvimento de Sistemas (2026/2). Trechos novos ou alterados em relação à Versão 1 estão sinalizados com **[NOVO]**.

---

## 1. Visão do produto

### 1.1 Contexto e problema

Instituições de ensino realizam palestras, seminários, semanas acadêmicas e outros eventos que exigem coordenação de espaços, horários, vagas, inscrições, presença e certificação. Quando essas atividades são tratadas por ferramentas desconectadas ou procedimentos manuais, a organização tende a enfrentar conflitos de agenda, dificuldade para controlar lotação e filas de espera, registro de presença pouco confiável e maior esforço para emissão de certificados.

O projeto propõe uma solução integrada para apoiar o ciclo operacional de eventos acadêmicos, desde o planejamento do evento e a reserva do auditório até a inscrição dos participantes, o controle de presença e a disponibilização de certificados.

**[NOVO] Contexto institucional.** O projeto, apelidado internamente de **"Auditório Inteligente"**, é uma demanda real da **FCI (Faculdade de Computação e Informática)** e é conduzido no âmbito da disciplina de **Práticas Profissionais em Análise e Desenvolvimento de Sistemas** (2026/2), sob orientação dos professores **Fábio Lopes** e **Tomás Mikio Sasaki**. A disciplina tem caráter **extensionista**: a proposta é desenvolver uma aplicação que sirva efetivamente à comunidade acadêmica e ao entorno da faculdade, não apenas como exercício de sala de aula.

A FCI realiza um grande volume de atividades ao longo do semestre — de grandes eventos institucionais a pequenas palestras avulsas — e boa parte desse processo ainda é manual ou pouco automatizado, gerando esforço operacional elevado para a coordenação de extensão e para a direção da faculdade, além de perda de visibilidade sobre o que está acontecendo (alunos frequentemente não ficam sabendo de eventos que poderiam ter interesse em participar).

Já existe uma iniciativa anterior parcial sobre esse tema, desenvolvida por um aluno em um laboratório de processos de software da faculdade; esse material poderá ser disponibilizado como referência para a equipe, mas não substitui os requisitos e regras de negócio definidos neste documento.

### 1.2 Declaração de visão

Para organizadores e participantes de eventos acadêmicos que precisam administrar espaços, vagas e participação de forma coordenada, o sistema de Gestão de Eventos e Auditórios é uma plataforma que centraliza a criação de eventos, a alocação de auditórios, as inscrições, o controle de presença e a certificação. Diferentemente de um conjunto de controles manuais ou ferramentas isoladas, a solução mantém essas atividades relacionadas em um fluxo único e consistente.

**[NOVO]** A solução tem caráter extensionista e não comercial: não há venda de ingressos, cobrança de inscrição ou processamento de pagamentos em nenhum fluxo do sistema.

### 1.3 Objetivos

- Reduzir o esforço operacional necessário para organizar eventos acadêmicos.
- Evitar conflitos de uso de auditórios e apoiar a escolha de espaços compatíveis com a quantidade esperada de participantes.
- Controlar automaticamente a quantidade de vagas disponíveis e o tratamento de eventos lotados.
- Dar ao participante uma visão clara de suas inscrições e de sua situação em cada evento.
- Registrar a presença dos participantes de forma rápida e auditável.
- Automatizar a emissão de certificados para participantes que efetivamente compareceram ao evento.
- Permitir que organizadores acompanhem informações básicas sobre eventos, inscrições, presença e certificação.
- **[NOVO]** Dar transparência à comunidade acadêmica sobre os eventos que estão acontecendo ou vão acontecer, reduzindo a perda de participação por simples desconhecimento da agenda.
- **[NOVO]** Apoiar a coordenação de extensão e a direção da faculdade com indicadores/consultas básicas sobre o andamento dos eventos (ex.: quantas pessoas do público-alvo efetivamente participaram), como insumo para relatórios de gestão.
- **[NOVO]** Apoiar o registro de horas de participantes e de voluntários para fins de atividades complementares.

### 1.4 Perfis de usuário

| Perfil | Responsabilidades e necessidades principais |
| --- | --- |
| Administrador / Organizador | Cadastra e administra auditórios; cria e gerencia eventos; consulta disponibilidade de espaços; acompanha vagas e inscrições; realiza o check-in; acompanha presenças e certificados. |
| Participante | Consulta eventos; realiza e cancela inscrições; acompanha inscrição confirmada ou fila de espera; apresenta sua identificação de check-in; consulta e obtém seus certificados. |
| **[NOVO] Voluntário** | Pessoa que atua no apoio operacional de um evento (não necessariamente como participante da atividade em si). Precisa ter seu envolvimento registrado no sistema para fins de contabilização de horas de atividades complementares. |
| **[NOVO] Gestor / Coordenação (visão institucional)** | Perfil de acompanhamento em nível mais alto (ex.: direção da faculdade, coordenação de extensão). Não necessariamente opera o dia a dia dos eventos, mas consulta indicadores consolidados de participação e evidências dos eventos realizados, como apoio à elaboração de relatórios de gestão da faculdade. |

**[NOVO] Stakeholders identificados na reunião de apresentação do projeto:**

- **Professora Daniela** — Diretora da Faculdade de Computação e Informática (FCI); usa informações consolidadas dos eventos para relatórios de gestão da faculdade.
- **Professora Cássia** — Coordenadora de Extensão; acompanha os eventos realizados na FCI e o registro das atividades complementares.
- **Professora Elizângela** — Apoia a coordenação de extensão no acompanhamento de eventos e no registro de atividades.

### 1.5 Perspectiva do produto

A solução deve ser entendida como um sistema de apoio à gestão do ciclo de eventos. A forma de implementação é deliberadamente aberta: a equipe poderá decidir como estruturar a aplicação e em quais plataformas disponibilizá-la, desde que os fluxos funcionais e as regras de negócio essenciais descritos neste documento sejam preservados.

**[NOVO]** Como referência de mercado (não como requisito de implementação), a reunião de apresentação mostrou exemplos de plataformas de eventos com características que podem inspirar a solução, sem que sua adoção literal seja obrigatória:

- Plataformas de eventos de grandes empresas de tecnologia, com listagem de sessões, inscrição/reserva de vaga e cancelamento ("desistência") simples.
- Plataformas internas de capacitação/trilhas de aprendizagem já usadas por docentes da instituição, com lógica semelhante de inscrição em sessões.
- Plataformas de bilheteria/eventos do tipo "Sympla" — com mapa do local do evento (sala/prédio), filtros por categoria (workshop, oficina, palestra, talk) e fluxo de reserva — **sem o componente de venda/pagamento**, que não se aplica a este projeto.

**[NOVO]** Também foi citada a existência de uma ferramenta já usada internamente pela faculdade para agendamento de apresentações de TCC, que evita conflitos de sala/horário entre bancas. Essa ferramenta pode servir de referência de solução já validada para o mesmo tipo de problema de conflito de agenda tratado na regra RN01/RN02 deste documento (não é obrigatório reaproveitá-la, mas indica que o problema de conflito de agenda já tem precedente resolvido na instituição).

---

## 2. Escopo funcional

### 2.1 Funcionalidades incluídas no escopo

**F01 — Acesso e perfis de usuário**
- Permitir que usuários acessem o sistema de forma identificada.
- Distinguir, no mínimo, os perfis Administrador/Organizador e Participante.
- Restringir as operações administrativas aos usuários autorizados.
- **[NOVO]** Contemplar, adicionalmente, o registro de participação de Voluntários em eventos (ver F12).

**F02 — Cadastro e gestão de auditórios ou locais**
- Permitir ao administrador cadastrar, consultar, alterar e desativar locais utilizados em eventos.
- Registrar, no mínimo, nome/identificação do local, capacidade e informações de localização.
- Permitir registrar indisponibilidades ou bloqueios de agenda quando necessário.
- **[NOVO]** Considerar que a faculdade opera hoje algo em torno de uma quinzena de salas/espaços que podem ser usados para eventos, o que reforça a necessidade prática da validação de conflitos (RN01/RN02).

**F03 — Consulta de disponibilidade de locais**
- Permitir consultar locais disponíveis para uma data e um intervalo de horário.
- Permitir considerar a capacidade necessária para o público esperado.
- Retornar somente locais compatíveis com o horário e, quando informado, com a capacidade requerida.
- Informar quando não houver local disponível que atenda aos critérios.

**F04 — Cadastro e gestão de eventos**
- Permitir criar, consultar, alterar e encerrar eventos.
- Registrar título, descrição, data, horário de início e término, local e quantidade de vagas.
- Permitir organizar um evento principal com subeventos, como palestras ou sessões vinculadas.
- Apresentar um estado do evento, como aberto, lotado, encerrado ou realizado.
- Impedir a associação de eventos ao mesmo local em horários conflitantes.
- **[NOVO]** Suportar tipos/categorias de evento diversos já praticados pela faculdade, como palestras, oficinas/workshops, hackathons, seminários, talks e eventos de maior porte (ex.: semana de tecnologia e inovação), de forma a permitir futura filtragem por categoria (ver F05).
- **[NOVO]** Suportar tanto eventos presenciais quanto digitais/remotos, já que parte das atividades da faculdade ocorre por meio de plataformas de reunião online.

**F05 — Catálogo e consulta de eventos**
- Apresentar aos participantes os eventos disponíveis.
- Exibir informações suficientes para decisão de inscrição, incluindo data, horário, local e situação das vagas.
- Permitir acessar os detalhes do evento e, quando existirem, seus subeventos.
- **[NOVO]** Permitir, como evolução desejável, filtrar/listar eventos por categoria (ex.: oficina, workshop, palestra, talk), de forma a facilitar a descoberta de eventos pelo participante.

**F06 — Inscrição em eventos**
- Permitir que um participante se inscreva em um evento aberto.
- Confirmar imediatamente a inscrição enquanto houver vagas disponíveis.
- Impedir inscrições duplicadas do mesmo participante no mesmo evento.
- Impedir novas inscrições em eventos encerrados, fechados ou já realizados.
- Permitir cancelamento de inscrição quando aplicável.

**F07 — Fila de espera**
- Quando as vagas estiverem esgotadas, permitir que o participante ingresse em uma fila de espera.
- Preservar a ordem de entrada na fila.
- Promover automaticamente participantes da fila quando novas vagas forem liberadas.
- Atualizar a situação do participante de "em espera" para "confirmado" após a promoção.
- **[NOVO]** Cenário real que motiva esta funcionalidade: eventos com sala de capacidade limitada (ex.: 60 lugares) recebem procura maior que a capacidade (ex.: 90 interessados), tornando a fila de espera uma necessidade prática recorrente.

**F08 — Área do participante**
- Permitir que o participante consulte suas inscrições.
- Exibir o estado de cada participação, por exemplo: confirmado, em fila de espera, cancelado ou concluído.
- Disponibilizar, quando cabível, o recurso necessário para realização do check-in e o acesso aos certificados.

**F09 — Controle de presença / check-in**
- Disponibilizar para cada inscrição confirmada um identificador individual de check-in, apresentado como QR Code ou mecanismo equivalente.
- Quando disponível, deve ser utilizado o chip identificador do crachá do aluno como forma principal de check-in.
- Permitir ao administrador validar esse identificador no momento do evento.
- Aceitar o check-in somente para participante inscrito no evento correspondente.
- Impedir que o mesmo identificador seja utilizado mais de uma vez.
- Registrar a presença e o horário em que o check-in foi efetuado.
- Informar claramente se o check-in foi aceito ou rejeitado.
- **[NOVO]** Já foi validado informalmente pela coordenação que a leitura por aplicativo de celular (ex.: leitura de QR Code na entrada) é tecnicamente viável como alternativa/complemento à leitura do chip do crachá, e é preferível fazer a leitura na entrada do evento (em vez de na saída), para evitar filas ao término da atividade.

**F10 — Certificados**
- Gerar certificado de participação apenas para quem tiver presença registrada.
- Incluir no certificado informações essenciais, como nome do participante, evento, data e carga horária.
- Associar ao certificado um código único de verificação.
- Permitir ao participante acessar ou obter seu certificado.
- Permitir que a organização confira a validade de um certificado a partir de seu código de verificação.
- **[NOVO]** Motivação de negócio reforçada na reunião: evitar a emissão/circulação de certificados falsos ou fraudados, garantindo um mecanismo mínimo de segurança/autenticidade documental.

**F11 — Acompanhamento administrativo básico**
- Permitir ao administrador consultar eventos, inscritos e participantes presentes.
- Apresentar contagens básicas úteis à operação, como vagas, inscritos, pessoas em espera, presenças e certificados emitidos.
- Permitir ajustes administrativos necessários ao andamento do evento, como alteração da quantidade de vagas.
- **[NOVO]** Apresentar, como evolução desejável, indicadores agregados de participação em relação ao público-alvo esperado (ex.: quantos dos alunos da faculdade efetivamente compareceram aos eventos realizados no período), como apoio a relatórios de gestão da direção e da coordenação de extensão.

**[NOVO] F12 — Registro de voluntários**
- Permitir identificar, dentro de um evento, as pessoas que atuaram como voluntárias no apoio à sua realização (perfil distinto do participante comum).
- Registrar a participação/horas do voluntário para fins de contabilização de atividades complementares, de forma equivalente ao que ocorre com a presença de um participante comum.

**[NOVO] F13 — Registro de evidências do evento (extensão desejável)**
- Permitir associar a um evento registros fotográficos como evidência de sua realização.
- Disponibilizar essas evidências para consulta administrativa, como apoio à elaboração de relatórios de gestão da faculdade.
- *Observação: esta funcionalidade é uma extensão desejável identificada na reunião, e não uma funcionalidade obrigatória do núcleo do sistema — ver seção 2.3.*

### 2.2 Regras de negócio essenciais

| Regra | Descrição |
| --- | --- |
| RN01 | Um local não pode receber dois eventos com horários sobrepostos. |
| RN02 | A capacidade de um local deve ser considerada na escolha do espaço para o evento. |
| RN03 | O número de inscrições confirmadas não deve ultrapassar a quantidade de vagas definida para o evento. |
| RN04 | Quando não houver vagas, novas solicitações devem ser encaminhadas para a fila de espera, se ela estiver habilitada. |
| RN05 | A promoção da fila de espera deve respeitar a ordem de entrada. |
| RN06 | Um participante não pode possuir mais de uma inscrição ativa no mesmo evento. |
| RN07 | Somente inscrições confirmadas podem resultar em check-in válido. |
| RN08 | Um check-in já registrado não pode ser contabilizado novamente. |
| RN09 | Somente participantes com presença registrada podem receber certificado. |
| RN10 | Cada certificado deve possuir um identificador único que permita sua conferência posterior. |
| **[NOVO] RN11** | Não haverá cobrança, venda de ingressos ou processamento de pagamento em nenhum fluxo do sistema — o projeto tem caráter extensionista, não comercial. |
| **[NOVO] RN12** | Assim como um participante, um voluntário só deve ter suas horas contabilizadas para atividades complementares se seu envolvimento no evento estiver devidamente registrado no sistema. |

### 2.3 Fora do escopo obrigatório

Os itens abaixo podem ser tratados como extensões, mas não são necessários para reproduzir o núcleo funcional do projeto:

- Notificações automáticas por e-mail, SMS ou push para confirmação de inscrição, promoção da fila ou liberação de certificado.
- Relatórios analíticos avançados, dashboards históricos, gráficos e exportação em múltiplos formatos.
- Portal público automatizado para validação de certificados por terceiros; basta existir mecanismo de conferência do código pela organização.
- Integrações com sistemas acadêmicos.
- Recursos financeiros, venda de ingressos, pagamentos ou cobrança de inscrições.
- **[NOVO]** Registro fotográfico de evidências do evento (F13) — desejável para apoiar relatórios de gestão, mas não obrigatório ao núcleo funcional.
- **[NOVO]** Reaproveitamento ou integração direta com a ferramenta de agendamento de bancas de TCC já usada pela faculdade — citada apenas como referência de solução já validada para o problema de conflito de agenda, não como integração obrigatória.

### 2.4 Fluxos mínimos que a solução deve demonstrar

**Fluxo A — Planejamento de evento:** O administrador cadastra um local, consulta sua disponibilidade, cria um evento com data, horário, capacidade/vagas e associa o local sem gerar conflito de agenda.

**Fluxo B — Inscrição com vaga:** Um participante consulta o catálogo, abre o evento e realiza a inscrição; o sistema confirma a vaga e passa a exibir o evento em sua área pessoal.

**Fluxo C — Evento lotado e fila de espera:** Com o evento lotado, um novo participante entra na fila. Quando uma vaga é liberada, o primeiro participante elegível da fila é promovido automaticamente.

**Fluxo D — Presença:** No período apropriado, um participante confirmado apresenta seu identificador de check-in; o administrador valida o identificador e o sistema registra a presença, rejeitando reutilizações.

**Fluxo E — Certificação:** Após o evento, um participante com presença registrada consegue acessar seu certificado, que contém um código único passível de conferência pela organização.

**[NOVO] Fluxo F — Voluntariado:** Um voluntário é registrado como apoio operacional de um evento; ao final, seu envolvimento é confirmado no sistema, permitindo a contabilização de suas horas de atividades complementares.

---

## 3. Considerações adicionais sobre o horizonte do projeto

**[NOVO]**

- O projeto é conduzido como trabalho de disciplina, mas há expectativa institucional real de que a melhor solução produzida no semestre venha a ser efetivamente implantada e utilizada pela FCI a partir do semestre seguinte.
- Já existe uma base de trabalho anterior parcial sobre o mesmo tema, produzida por um aluno em um laboratório de processos de software da faculdade, que poderá ser disponibilizada à equipe como referência (não como requisito vinculante).
- O escopo e as regras de negócio definidos nas seções 1 e 2 deste documento continuam sendo a referência formal para o desenvolvimento; o conteúdo da reunião foi usado para complementar contexto, motivação e prioridades, não para substituir os requisitos já formalizados na Versão 1.

