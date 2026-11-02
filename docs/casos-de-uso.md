# Casos de Uso — Sistema de Gestão de Eventos e Auditórios ("Auditório Inteligente")

Este documento descreve os casos de uso do sistema, com base na Visão e Escopo do Projeto (`visao.md`), nas User Stories (`user-stories.md`) e no Modelo de Domínio (`docs/modelo-dominio.md`).

**Atores considerados:** Administrador/Organizador (ADM), Participante (PART), Voluntário (VOL), Gestor/Coordenação (GES).

**Convenção de fluxos:** cada caso de uso apresenta um Fluxo Principal (cenário de sucesso), Fluxos Alternativos (variações válidas do cenário principal) e Fluxos de Exceção (situações de erro ou recusa).

---

## UC01 — Acessar o sistema

**Atores:** ADM, PART, VOL, GES
**Referências:** F01, US01, US02

**Descrição:** Permite que um usuário se autentique no sistema e tenha seu perfil reconhecido, restringindo o acesso a áreas e funções conforme esse perfil.

**Pré-condições:** Usuário possui cadastro/credenciais válidas no sistema.

**Pós-condições:** Usuário autenticado, com acesso liberado apenas às funcionalidades do seu perfil.

**Fluxo Principal:**
1. Usuário acessa a tela de login e informa suas credenciais.
2. Sistema valida as credenciais informadas.
3. Sistema identifica o perfil do usuário (ADM, PART, VOL ou GES).
4. Sistema libera o acesso às funcionalidades correspondentes ao perfil identificado.
5. Caso de uso é encerrado.

**Fluxos Alternativos:**
- **FA01 — Tentativa de acesso direto a função restrita:** um usuário tenta acessar, por URL direta ou ação equivalente, uma função não autorizada ao seu perfil (ex.: PART tentando acessar cadastro de eventos, ou VOL tentando acessar telas administrativas). O sistema bloqueia a ação e registra a tentativa.

**Fluxos de Exceção:**
- **FE01 — Credenciais inválidas:** o sistema recusa o acesso e exibe mensagem genérica, sem indicar qual campo está incorreto.

---

## UC02 — Gerenciar locais e auditórios

**Ator principal:** ADM
**Referências:** F02, US03, US04, US05

**Descrição:** Permite ao administrador cadastrar, consultar, alterar e desativar locais utilizáveis em eventos, além de registrar bloqueios de agenda.

**Pré-condições:** ADM autenticado (UC01).

**Pós-condições:** Local cadastrado/atualizado/desativado, ou bloqueio de agenda registrado, disponível para consultas de disponibilidade (UC03).

**Fluxo Principal (Cadastrar local):**
1. ADM acessa a área de gestão de locais e seleciona "Novo local".
2. ADM informa nome/identificação, capacidade e informações de localização.
3. Sistema valida o preenchimento dos campos obrigatórios.
4. Sistema salva o local com status "ativo".
5. Local passa a estar disponível para consultas de disponibilidade (UC03) e associação a eventos (UC04).

**Fluxos Alternativos:**
- **FA01 — Consultar/listar locais:** ADM lista e busca locais já cadastrados.
- **FA02 — Alterar local existente:** ADM atualiza capacidade e/ou informações; alterações não afetam eventos já concluídos.
- **FA03 — Desativar local:** sistema verifica se o local possui eventos futuros já agendados; havendo, alerta o ADM antes de confirmar a desativação. Local desativado não aparece mais para novos eventos, mas eventos já vinculados permanecem consultáveis.
- **FA04 — Registrar bloqueio/indisponibilidade de agenda:** ADM informa data/horário de início e fim e, opcionalmente, um motivo; sistema verifica se o bloqueio conflita com evento já confirmado no local e alerta explicitamente, se for o caso.

**Fluxos de Exceção:**
- **FE01 — Campos obrigatórios não preenchidos:** sistema impede salvar o cadastro e indica os campos pendentes.

**Regras de negócio relacionadas:** RN01, RN02.

---

## UC03 — Consultar disponibilidade de local

**Ator principal:** ADM
**Referências:** F03, US06

**Descrição:** Permite consultar quais locais estão disponíveis para uma data, horário e (opcionalmente) capacidade desejada.

**Pré-condições:** Existir ao menos um local ativo cadastrado (UC02).

**Pós-condições:** Lista de locais compatíveis apresentada ao ADM.

**Fluxo Principal:**
1. ADM informa data e intervalo de horário (início e fim) desejados.
2. ADM informa, opcionalmente, a capacidade mínima esperada.
3. Sistema identifica os locais ativos sem conflito de agenda no intervalo informado (RN01).
4. Quando informada capacidade, sistema filtra apenas os locais compatíveis (RN02).
5. Sistema apresenta a lista de locais disponíveis.

**Fluxos Alternativos:**
- **FA01 — Consulta sem capacidade informada:** sistema retorna todos os locais sem conflito de agenda no período, independentemente da capacidade.

**Fluxos de Exceção:**
- **FE01 — Nenhum local disponível:** sistema informa explicitamente a ausência de opções compatíveis, em vez de apresentar uma lista vazia sem explicação.

**Regras de negócio relacionadas:** RN01, RN02.

---

## UC04 — Gerenciar evento

**Ator principal:** ADM
**Referências:** F04, US07, US08, US09, US10, US11, US12, US13

**Descrição:** Permite criar, consultar, alterar e encerrar eventos, incluindo a organização de subeventos, classificação por categoria e suporte a eventos presenciais, remotos ou híbridos.

**Pré-condições:** ADM autenticado; para associação a local físico, local deve estar cadastrado e ativo (UC02).

**Pós-condições:** Evento criado/atualizado/encerrado, disponível no catálogo (UC05) quando aplicável.

**Fluxo Principal (Criar evento):**
1. ADM acessa "Novo evento".
2. ADM informa título, descrição, data, horário de início e término, local (ou modalidade remota/híbrida) e quantidade de vagas; opcionalmente, associa categoria(s) (palestra, oficina/workshop, hackathon, seminário, talk, evento de grande porte).
3. Sistema valida o preenchimento dos campos obrigatórios conforme a modalidade (evento remoto dispensa local físico, mas exige link/plataforma de acesso; evento híbrido exige ambos).
4. Sistema verifica conflito de horário no local selecionado, para o componente presencial do evento (RN01).
5. Sistema considera a capacidade do local ao validar a quantidade de vagas solicitada (RN02).
6. Sistema salva o evento com estado "aberto".
7. Evento passa a estar disponível no catálogo de eventos (UC05) e sujeito a inscrição (UC06).

**Fluxos Alternativos:**
- **FA01 — Alterar dados de um evento:** ADM atualiza título, descrição, data, horário, local ou vagas; alterações de horário/local passam pelas mesmas validações de conflito (RN01); alteração relevante (ex.: mudança de horário) fica registrada para consulta administrativa.
- **FA02 — Reduzir vagas abaixo do número já confirmado:** sistema exige confirmação explícita do ADM sobre o impacto antes de aplicar a alteração.
- **FA03 — Encerrar evento:** evento passa a não aceitar novas inscrições (bloqueio tratado em UC06/FE02); inscrições já confirmadas continuam visíveis na área do participante, com o estado do evento atualizado; dados de presença e certificados já emitidos são preservados.
- **FA04 — Organizar subevento vinculado a evento principal:** ADM cria um subevento associado a um evento "guarda-chuva" já existente, com local, horário e vagas próprios, validados independentemente (RN01/RN02); subeventos ficam listados na consulta do evento principal (UC05).
- **FA05 — Classificar evento por categoria:** ADM seleciona uma ou mais categorias; evento sem categoria continua sendo criado normalmente (campo não bloqueante).
- **FA06 — Definir modalidade remota ou híbrida:** ao marcar o evento como remoto, o campo de local físico deixa de ser obrigatório e passa a existir campo de link/plataforma; evento híbrido exige tanto local físico quanto informação de acesso remoto.

**Fluxos de Exceção:**
- **FE01 — Conflito de horário no local:** sistema rejeita a criação/alteração e informa o conflito (RN01).
- **FE02 — Campos obrigatórios ausentes:** sistema impede salvar e indica os campos pendentes.

**Regras de negócio relacionadas:** RN01, RN02.

---

## UC05 — Consultar catálogo e detalhes de eventos

**Ator principal:** PART
**Referências:** F05, US14, US15, US16

**Descrição:** Permite ao participante visualizar os eventos disponíveis, consultar seus detalhes (incluindo subeventos) e filtrar por categoria.

**Pré-condições:** PART autenticado (UC01).

**Pós-condições:** Participante visualiza informações suficientes para decidir sobre inscrição.

**Fluxo Principal:**
1. PART acessa o catálogo de eventos.
2. Sistema lista os eventos em estado "aberto", exibindo data, horário, local (ou modalidade remota) e situação das vagas.
3. PART seleciona um evento para ver seus detalhes.
4. Sistema exibe descrição completa, local/modalidade, horário, vagas e, quando existirem, os subeventos vinculados com suas próprias informações.
5. A partir da tela de detalhes, PART pode iniciar a inscrição (UC06), quando aplicável.

**Fluxos Alternativos:**
- **FA01 — Filtrar por categoria:** PART seleciona uma ou mais categorias (ex.: oficina, palestra, talk); sistema retorna eventos que atendam a pelo menos uma das categorias selecionadas.

**Fluxos de Exceção:**
- **FE01 — Nenhum evento disponível ou filtro sem resultado:** sistema exibe mensagem clara informando a ausência de eventos, sem apresentar erro.

---

## UC06 — Inscrever-se em evento

**Ator principal:** PART
**Referências:** F06, US17, US19, US20

**Descrição:** Permite que um participante se inscreva em um evento aberto, reservando sua vaga.

**Pré-condições:** PART autenticado; evento em estado "aberto".

**Pós-condições:** Inscrição criada com estado "confirmado" (ou encaminhada à fila de espera, ver UC07) e exibida na área do participante (UC09).

**Fluxo Principal:**
1. PART seleciona a opção de inscrição no evento desejado.
2. Sistema verifica se o PART já possui inscrição ativa (confirmada ou em espera) no mesmo evento (RN06).
3. Sistema verifica se há vagas disponíveis no evento (RN03).
4. Sistema confirma a inscrição imediatamente, com estado "confirmado".
5. Inscrição passa a ser exibida na área do participante (UC09).

**Fluxos Alternativos:**
- **FA01 — Evento lotado:** não havendo vagas disponíveis, o sistema encaminha o participante ao fluxo de fila de espera (UC07), em vez de recusar a solicitação com um erro genérico.

**Fluxos de Exceção:**
- **FE01 — Inscrição duplicada:** ao identificar inscrição ativa já existente do mesmo participante no mesmo evento, o sistema recusa a nova inscrição e informa que ele já está inscrito (RN06). Uma inscrição previamente cancelada não bloqueia nova inscrição, caso ainda haja vagas.
- **FE02 — Evento indisponível:** tentativa de inscrição em evento encerrado, fechado ou já realizado é recusada com mensagem explicativa, mesmo em caso de ação direta que ignore a interface padrão.

**Regras de negócio relacionadas:** RN03, RN04, RN06.

---

## UC07 — Entrar na fila de espera

**Ator principal:** PART (entrada na fila); Sistema (promoção automática)
**Referências:** F07, US21, US22

**Descrição:** Permite que um participante entre na fila de espera de um evento lotado, e define a promoção automática de participantes da fila quando surgem vagas.

**Pré-condições:** Evento sem vagas disponíveis e fila de espera habilitada.

**Pós-condições:** Participante posicionado na fila com estado "em fila de espera"; participantes promovidos passam a estado "confirmado".

**Fluxo Principal:**
1. Sistema adiciona o participante ao final da fila de espera do evento (RN04).
2. Sistema atribui a posição do participante na fila.
3. Área do participante (UC09) passa a exibir o estado "em fila de espera" e, quando disponível, a posição na fila.

**Fluxos Alternativos:**
- **FA01 — Promoção automática da fila:** quando uma vaga é liberada (por cancelamento — UC08 — ou aumento de vagas — UC13), o sistema promove automaticamente o participante há mais tempo na fila, respeitando a ordem de entrada (RN05); o estado da inscrição promovida muda de "em espera" para "confirmado", e o participante passa a visualizá-la como confirmada em sua área pessoal.

**Fluxos de Exceção:**
- **FE01 — Participante já está na fila do mesmo evento:** sistema recusa uma segunda entrada na fila para o mesmo participante e evento (RN06 aplicado à fila).

**Regras de negócio relacionadas:** RN04, RN05, RN06.

---

## UC08 — Cancelar inscrição e promover fila

**Ator principal:** PART (cancelamento); Sistema (promoção)
**Referências:** F06, F07, US18, US22

**Descrição:** Permite que um participante cancele uma inscrição confirmada, liberando a vaga e disparando a promoção automática do próximo participante elegível da fila de espera.

**Pré-condições:** Participante possui inscrição confirmada no evento.

**Pós-condições:** Inscrição com estado "cancelado"; vaga liberada; se houver fila, próximo participante elegível promovido a "confirmado" (UC07/FA01).

**Fluxo Principal:**
1. PART seleciona cancelar uma inscrição confirmada em sua área pessoal.
2. Sistema altera o estado da inscrição para "cancelado".
3. Inscrição deixa de aparecer na lista de inscrições ativas do participante.
4. Sistema libera a vaga correspondente ao evento.
5. Sistema verifica se há participantes na fila de espera do evento.
6. Havendo participantes na fila, sistema promove o primeiro elegível, respeitando a ordem de entrada (RN05), alterando seu estado para "confirmado" (UC07/FA01).

**Fluxos de Exceção:**
- **FE01 — Cancelamento após check-in:** um participante que já teve presença registrada (check-in efetuado) não pode cancelar a inscrição retroativamente; sistema impede a operação.

**Regras de negócio relacionadas:** RN04, RN05.

---

## UC09 — Consultar área do participante

**Ator principal:** PART
**Referências:** F08, US23

**Descrição:** Permite ao participante consultar todas as suas inscrições e os respectivos estados, além de acessar identificador de check-in e certificados quando cabível.

**Pré-condições:** PART autenticado (UC01).

**Pós-condições:** Participante visualiza situação atualizada de suas inscrições.

**Fluxo Principal:**
1. PART acessa sua área pessoal.
2. Sistema lista todas as inscrições do participante, exibindo o estado de cada uma (confirmado, em fila de espera, cancelado ou concluído).
3. A partir da lista, PART pode acessar o identificador de check-in (quando a inscrição estiver confirmada — UC10) e o certificado (quando emitido — UC11).

**Fluxos Alternativos:**
- **FA01 — Consultar histórico de inscrições canceladas:** inscrições canceladas continuam disponíveis para consulta, sinalizadas como tal.

---

## UC10 — Realizar check-in

**Ator principal:** ADM (validação); Ator secundário: PART (apresentação do identificador)
**Referências:** F09, US24, US25, US26, US27

**Descrição:** Permite gerar um identificador individual de check-in para inscrições confirmadas e validar esse identificador no momento do evento, registrando a presença.

**Pré-condições:** Participante possui inscrição confirmada no evento (RN07).

**Pós-condições:** Presença registrada com data/hora, habilitando a emissão de certificado (UC11).

**Fluxo Principal:**
1. Participante com inscrição confirmada acessa sua área pessoal (UC09) e obtém seu identificador individual de check-in (QR Code ou mecanismo equivalente), exclusivo por inscrição/evento (RN07).
2. No momento do evento, o participante apresenta o identificador na entrada.
3. ADM realiza a leitura/validação do identificador apresentado.
4. Sistema verifica se o identificador corresponde a uma inscrição confirmada no evento correspondente (RN07).
5. Sistema verifica se o identificador já foi utilizado anteriormente (RN08).
6. Sistema registra a presença com data e horário e informa que o check-in foi aceito.

**Fluxos Alternativos:**
- **FA01 — Check-in por chip do crachá:** quando o chip identificador do crachá do aluno está associado ao participante, sua leitura é aceita como forma válida de check-in, sujeita às mesmas validações de RN07/RN08.
- **FA02 — Check-in por QR Code via aplicativo:** leitura do QR Code por aplicativo de celular é aceita como forma válida de check-in, realizada preferencialmente na entrada do evento (não na saída), para evitar filas ao término da atividade.

**Fluxos de Exceção:**
- **FE01 — Identificador de participante não inscrito no evento:** check-in é rejeitado, com mensagem explicando o motivo.
- **FE02 — Identificador já utilizado:** uma segunda tentativa de check-in com o mesmo identificador é rejeitada, informando que ele já foi utilizado (RN08).

**Regras de negócio relacionadas:** RN07, RN08.

---

## UC11 — Emitir e consultar certificado

**Ator principal:** Sistema (emissão); Ator secundário: PART (consulta), ADM/Organização (conferência)
**Referências:** F10, US28, US29, US30

**Descrição:** Gera certificados para participantes com presença registrada, disponibiliza sua consulta e permite conferir a validade de um certificado a partir do código de verificação.

**Pré-condições:** Participante possui presença (check-in) registrada no evento (RN09).

**Pós-condições:** Certificado emitido com código único, disponível na área do participante.

**Fluxo Principal:**
1. Após o check-in ser validado (UC10), sistema verifica se o participante possui presença registrada no evento (RN09).
2. Sistema gera o certificado, contendo nome do participante, nome do evento, data e carga horária.
3. Sistema associa ao certificado um código único de verificação (RN10).
4. Certificado fica disponível na área do participante (UC09).
5. Participante acessa e obtém seu certificado.

**Fluxos Alternativos:**
- **FA01 — Conferir validade de certificado:** ADM/organização informa o código de verificação de um certificado; sistema retorna os dados básicos associados (participante, evento, data, carga horária), caso o código seja válido. Não é necessário portal público automatizado — basta um mecanismo de conferência acessível à organização.

**Fluxos de Exceção:**
- **FE01 — Certificado ainda não disponível:** participante sem presença registrada que tenta acessar o certificado recebe mensagem informando que ele ainda não está disponível, em vez de um erro genérico.
- **FE02 — Código de verificação inválido:** ao informar um código inexistente ou inválido na conferência, o sistema informa claramente que o certificado não foi encontrado.

**Regras de negócio relacionadas:** RN09, RN10.

---

## UC12 — Acompanhar evento e indicadores administrativos

**Ator principal:** ADM
**Referências:** F11, US31, US33

**Descrição:** Permite ao administrador consultar contagens básicas de um evento e indicadores agregados de participação ao longo de um período.

**Pré-condições:** ADM autenticado; evento cadastrado.

**Pós-condições:** ADM visualiza informações atualizadas sobre o andamento do(s) evento(s).

**Fluxo Principal:**
1. ADM seleciona um evento para acompanhamento.
2. Sistema exibe, no mínimo: total de vagas, inscritos confirmados, pessoas em fila de espera, presenças registradas e certificados emitidos.
3. ADM pode listar separadamente os participantes inscritos e os participantes presentes.
4. Os números exibidos são atualizados conforme novas inscrições, check-ins e emissões de certificado ocorrem.

**Fluxos Alternativos:**
- **FA01 — Consultar indicadores agregados por período:** ADM informa um período; sistema apresenta quantos eventos foram realizados e quantas pessoas efetivamente compareceram no total, considerando apenas presenças registradas (check-in), não apenas inscrições.

**Fluxos de Exceção:**
- **FE01 — Ausência de dados no período:** sistema informa de forma clara a ausência de dados, sem apresentar erro.

---

## UC13 — Ajustar quantidade de vagas

**Ator principal:** ADM
**Referências:** F11, US32

**Descrição:** Permite ao administrador ajustar a quantidade de vagas de um evento em andamento, liberando vagas adicionais (com promoção automática da fila) ou corrigindo o cadastro inicial.

**Pré-condições:** Evento cadastrado; ADM autenticado.

**Pós-condições:** Quantidade de vagas atualizada; fila de espera promovida quando aplicável (UC07/FA01).

**Fluxo Principal:**
1. ADM acessa a gestão do evento e seleciona a opção de ajustar a quantidade de vagas.
2. ADM informa a nova quantidade de vagas.
3. Sistema verifica se a nova quantidade é maior que a anterior.
4. Sendo maior, sistema libera as vagas adicionais e dispara a promoção automática de participantes da fila de espera, respeitando a ordem de entrada (UC07/FA01, RN05).

**Fluxos Alternativos:**
- **FA01 — Redução de vagas:** se a nova quantidade informada for menor que o número de inscrições já confirmadas, o sistema exige confirmação explícita do ADM sobre o impacto antes de aplicar a alteração, já que inscrições confirmadas não podem ser removidas automaticamente.

**Regras de negócio relacionadas:** RN04, RN05.

---

## UC14 — Registrar voluntário e contabilizar horas

**Ator principal:** ADM (registro); Ator secundário: VOL (consulta/confirmação)
**Referências:** F12, US34, US35

**Descrição:** Permite identificar pessoas que atuaram como voluntárias em um evento e contabilizar suas horas para fins de atividades complementares.

**Pré-condições:** Evento cadastrado; pessoa identificável no sistema.

**Pós-condições:** Vínculo de voluntariado registrado; horas contabilizadas e consultáveis pelo voluntário.

**Fluxo Principal:**
1. ADM associa uma pessoa a um evento com o papel "voluntário", distinto do papel "participante", informando ao menos a identificação da pessoa e do evento em que atuou.
2. Sistema registra o vínculo (uma mesma pessoa pode ser voluntária em um evento e participante em outro, sem conflito de cadastro).
3. Ao final do evento, o envolvimento do voluntário é confirmado no sistema.
4. Sistema gera um registro consultável (equivalente a um certificado/declaração) com o evento, a data e a carga horária correspondente (RN12).
5. VOL acessa o registro de suas horas contabilizadas.

**Fluxos de Exceção:**
- **FE01 — Voluntário sem registro associado:** um voluntário sem envolvimento registrado para um evento não consegue solicitar/obter contabilização de horas para ele (RN12).

**Regras de negócio relacionadas:** RN12.

---

## UC15 — Consultar visão institucional

**Ator principal:** GES
**Referências:** US36

**Descrição:** Permite ao gestor/coordenação (ex.: direção da FCI, coordenação de extensão) consultar indicadores consolidados de participação e evidências dos eventos realizados, como apoio a relatórios de gestão, sem acesso às funções operacionais de criação/alteração de evento.

**Pré-condições:** GES autenticado (UC01).

**Pós-condições:** GES visualiza indicadores consolidados do período consultado.

**Fluxo Principal:**
1. GES acessa a visão institucional/indicadores consolidados.
2. GES informa, opcionalmente, um período (ex.: semestre) para filtrar a consulta.
3. Sistema exibe os indicadores agregados de participação dos eventos realizados no período (equivalentes aos de UC12/FA01), sem oferecer acesso a funções de criação ou alteração de evento.

**Fluxos de Exceção:**
- **FE01 — Nenhum evento realizado no período:** sistema informa essa condição de forma explícita.

---

## Rastreabilidade — Casos de uso x Funcionalidades x User Stories

| Caso de uso | Funcionalidade(s) | User Stories |
| --- | --- | --- |
| UC01 — Acessar o sistema | F01 | US01, US02 |
| UC02 — Gerenciar locais e auditórios | F02 | US03, US04, US05 |
| UC03 — Consultar disponibilidade de local | F03 | US06 |
| UC04 — Gerenciar evento | F04 | US07–US13 |
| UC05 — Consultar catálogo e detalhes de eventos | F05 | US14–US16 |
| UC06 — Inscrever-se em evento | F06 | US17, US19, US20 |
| UC07 — Entrar na fila de espera | F07 | US21, US22 |
| UC08 — Cancelar inscrição e promover fila | F06, F07 | US18, US22 |
| UC09 — Consultar área do participante | F08 | US23 |
| UC10 — Realizar check-in | F09 | US24–US27 |
| UC11 — Emitir e consultar certificado | F10 | US28–US30 |
| UC12 — Acompanhar evento e indicadores administrativos | F11 | US31, US33 |
| UC13 — Ajustar quantidade de vagas | F11 | US32 |
| UC14 — Registrar voluntário e contabilizar horas | F12 | US34, US35 |
| UC15 — Consultar visão institucional | — | US36 |
