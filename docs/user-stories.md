# User Stories — Sistema de Gestão de Eventos e Auditórios ("Auditório Inteligente")

Perfis considerados: **Administrador/Organizador (ADM)**, **Participante (PART)**, **Voluntário (VOL)**, **Gestor/Coordenação (GES)**.

---

## Bloco 1 — Acesso e perfis (F01)

### US01 — Acessar o sistema de forma identificada
Como usuário do sistema (Administrador, Participante ou Voluntário), quero acessar o sistema de forma identificada, para que minhas ações e informações fiquem corretamente associadas ao meu perfil.
**Critérios de aceitação:**
- Dado que informo credenciais válidas, o sistema me autentica e reconhece meu perfil (ADM, PART ou VOL).
- Dado que informo credenciais inválidas, o sistema recusa o acesso e informa o motivo de forma genérica (sem indicar qual campo está incorreto).
- O sistema distingue, no mínimo, os perfis Administrador/Organizador e Participante em todas as telas.
- Usuários não autenticados não conseguem acessar áreas restritas (inscrição, área pessoal, telas administrativas).
**Prioridade:** Must
**Telas/fluxos relacionados:** Tela de login, Fluxo A, Fluxo B

### US02 — Restringir operações administrativas por perfil
Como administrador do sistema, quero que apenas usuários autorizados executem operações administrativas, para garantir a integridade dos dados de eventos e locais.
**Critérios de aceitação:**
- Um usuário com perfil Participante não visualiza nem aciona funções de cadastro/alteração de locais ou eventos.
- Uma tentativa de acesso direto (ex.: URL) a uma função administrativa por um perfil não autorizado é bloqueada e registrada.
- O perfil Voluntário não possui acesso às telas administrativas, apenas ao registro do seu próprio envolvimento em eventos.
**Prioridade:** Must
**Telas/fluxos relacionados:** Todas as telas administrativas

---

## Bloco 2 — Locais e disponibilidade (F02, F03)

### US03 — Cadastrar local/auditório
Como administrador, quero cadastrar um local utilizável em eventos, para que ele fique disponível para associação a futuros eventos.
**Critérios de aceitação:**
- O cadastro exige, no mínimo, nome/identificação, capacidade e informações de localização.
- O sistema impede salvar o cadastro sem esses dados obrigatórios, indicando os campos pendentes.
- Após salvo, o local passa a aparecer nas buscas de disponibilidade (US06).
**Prioridade:** Must
**Telas/fluxos relacionados:** Cadastro de locais, Fluxo A

### US04 — Consultar, alterar e desativar locais
Como administrador, quero consultar, alterar e desativar locais cadastrados, para manter as informações atualizadas e remover espaços que não devem mais ser usados.
**Critérios de aceitação:**
- É possível listar e buscar locais cadastrados.
- Alterações em capacidade ou informações não afetam eventos já concluídos.
- Um local desativado não aparece mais como opção para novos eventos, mas eventos já vinculados a ele permanecem consultáveis.
- O sistema impede desativar um local que possua eventos futuros já agendados sem antes alertar o administrador.
**Prioridade:** Must
**Telas/fluxos relacionados:** Gestão de locais

### US05 — Registrar indisponibilidade/bloqueio de agenda de um local
Como administrador, quero registrar bloqueios de agenda de um local (ex.: manutenção, uso por outro setor), para evitar que o sistema ofereça esse local em horários indisponíveis.
**Critérios de aceitação:**
- Um bloqueio possui data/horário de início e fim e um motivo opcional.
- Locais bloqueados não aparecem como disponíveis nas buscas (US06) para o período bloqueado.
- Não é possível criar um bloqueio que conflite com um evento já confirmado no local sem um alerta explícito.
**Prioridade:** Should
**Telas/fluxos relacionados:** Gestão de locais, Fluxo A

### US06 — Consultar disponibilidade de locais
Como administrador, quero consultar quais locais estão disponíveis para uma data, horário e capacidade desejada, para escolher o espaço adequado ao planejar um evento.
**Critérios de aceitação:**
- Dado um intervalo de data/horário, o sistema retorna apenas locais sem conflito de agenda (RN01) nesse intervalo.
- Quando informada uma capacidade mínima esperada, apenas locais com capacidade compatível são retornados (RN02).
- Quando nenhum local atende aos critérios, o sistema informa claramente a ausência de opções, em vez de lista vazia sem explicação.
**Prioridade:** Must
**Telas/fluxos relacionados:** Consulta de disponibilidade, Fluxo A

---

## Bloco 3 — Eventos (F04)

### US07 — Criar evento
Como administrador/organizador, quero criar um evento com título, descrição, data, horário, local e vagas, para disponibilizá-lo para inscrição dos participantes.
**Critérios de aceitação:**
- O sistema exige título, data, horário de início/fim, local e quantidade de vagas para salvar o evento.
- Ao selecionar um local com conflito de horário com outro evento já cadastrado, o sistema impede a criação e informa o conflito (RN01).
- O evento criado nasce com estado "aberto" (ou equivalente) quando dentro das condições normais.
**Prioridade:** Must
**Telas/fluxos relacionados:** Cadastro de eventos, Fluxo A

### US08 — Alterar dados de um evento
Como administrador/organizador, quero alterar dados de um evento existente (ex.: horário, descrição, vagas), para corrigir ou ajustar informações antes ou durante sua realização.
**Critérios de aceitação:**
- Alterações de horário/local passam pela mesma validação de conflito de agenda da criação (RN01).
- Reduzir o número de vagas abaixo da quantidade já confirmada é impedido ou exige confirmação explícita do impacto.
- O histórico de alteração relevante (ex.: mudança de horário) fica disponível para consulta administrativa.
**Prioridade:** Must
**Telas/fluxos relacionados:** Gestão de eventos

### US09 — Encerrar um evento
Como administrador/organizador, quero encerrar um evento, para impedir novas inscrições e sinalizar que ele não está mais em andamento.
**Critérios de aceitação:**
- Um evento encerrado não aceita novas inscrições (US17 é bloqueada com mensagem clara).
- Inscrições já confirmadas permanecem visíveis na área do participante, apenas com o estado do evento atualizado.
- O encerramento não apaga dados de presença ou certificados já emitidos.
**Prioridade:** Must
**Telas/fluxos relacionados:** Gestão de eventos, Fluxo D, Fluxo E

### US10 — Impedir conflito de agenda no mesmo local
Como administrador, quero que o sistema impeça associar dois eventos ao mesmo local em horários sobrepostos, para evitar conflitos operacionais no dia do evento.
**Critérios de aceitação:**
- Ao tentar salvar um evento (criação ou alteração) com local e horário que sobrepõem outro evento já existente nesse local, o sistema rejeita a operação e aponta o conflito.
- Eventos cancelados/excluídos não contam como conflito para novas associações.
- A regra vale tanto para eventos presenciais quanto para eventos com componente híbrido no mesmo local físico.
**Prioridade:** Must
**Telas/fluxos relacionados:** Cadastro/alteração de eventos (RN01)

### US11 — Organizar subeventos vinculados a um evento principal
Como administrador/organizador, quero vincular subeventos (palestras/sessões) a um evento principal (ex.: uma semana de tecnologia), para estruturar eventos de grande porte com múltiplas atividades.
**Critérios de aceitação:**
- É possível criar um subevento associado a um evento "guarda-chuva" já existente.
- Cada subevento pode ter local, horário e vagas próprios, respeitando a validação de conflito (RN01) de forma independente.
- Ao consultar o evento principal, os subeventos vinculados são listados (ver US15).
**Prioridade:** Should
**Telas/fluxos relacionados:** Cadastro de eventos, Catálogo de eventos

### US12 — Classificar evento por categoria/tipo
Como administrador/organizador, quero classificar um evento por categoria (palestra, oficina/workshop, hackathon, seminário, talk, evento de grande porte), para permitir que os participantes encontrem eventos do interesse deles com mais facilidade.
**Critérios de aceitação:**
- A criação/alteração de evento permite selecionar uma ou mais categorias entre as previstas.
- Um evento sem categoria informada continua sendo criado normalmente (campo não bloqueante).
- A categoria selecionada fica visível no catálogo (US14) e é usada no filtro (US16).
**Prioridade:** Should
**Telas/fluxos relacionados:** Cadastro de eventos

### US13 — Suportar eventos presenciais e remotos
Como administrador/organizador, quero cadastrar um evento como presencial, remoto ou híbrido, para refletir a forma real como a atividade acontece.
**Critérios de aceitação:**
- Ao marcar um evento como remoto, o campo de local físico deixa de ser obrigatório e passa a existir um campo para link/plataforma de acesso.
- Eventos híbridos exigem tanto local físico quanto informação de acesso remoto.
- A validação de conflito de agenda (RN01) se aplica apenas ao componente presencial do evento.
**Prioridade:** Should
**Telas/fluxos relacionados:** Cadastro de eventos

---

## Bloco 4 — Catálogo e consulta (F05)

### US14 — Consultar catálogo de eventos disponíveis
Como participante, quero visualizar os eventos disponíveis, para decidir em quais quero me inscrever.
**Critérios de aceitação:**
- A listagem exibe, para cada evento, data, horário, local (ou modalidade remota), e situação das vagas (disponível, lotado, etc.).
- Eventos encerrados/já realizados não aparecem na listagem padrão de eventos disponíveis (podem aparecer em uma listagem histórica separada).
- Quando não há eventos disponíveis, o sistema informa isso de forma explícita.
**Prioridade:** Must
**Telas/fluxos relacionados:** Catálogo de eventos, Fluxo B

### US15 — Consultar detalhes de um evento e seus subeventos
Como participante, quero acessar os detalhes completos de um evento, incluindo seus subeventos quando existirem, para entender exatamente do que se trata antes de me inscrever.
**Critérios de aceitação:**
- A tela de detalhes exibe descrição completa, local/modalidade, horário e vagas.
- Quando o evento possui subeventos, eles são listados com suas próprias informações de horário e vagas.
- É possível iniciar a inscrição diretamente a partir da tela de detalhes (quando aplicável).
**Prioridade:** Must
**Telas/fluxos relacionados:** Detalhes do evento, Fluxo B

### US16 — Filtrar eventos por categoria
Como participante, quero filtrar o catálogo de eventos por categoria (ex.: oficina, palestra, talk), para encontrar mais rapidamente eventos do meu interesse.
**Critérios de aceitação:**
- O catálogo oferece um filtro por categoria previamente cadastrada nos eventos.
- A combinação de mais de uma categoria no filtro retorna eventos que atendam a pelo menos uma delas.
- Um filtro sem resultados exibe mensagem clara de "nenhum evento encontrado", sem erro.
**Prioridade:** Could
**Telas/fluxos relacionados:** Catálogo de eventos

---

## Bloco 5 — Inscrição e fila de espera (F06, F07)

### US17 — Inscrever-se em um evento
Como participante, quero me inscrever em um evento aberto, para reservar minha vaga.
**Critérios de aceitação:**
- Havendo vagas disponíveis, a inscrição é confirmada imediatamente e passa a aparecer na área do participante.
- Uma tentativa de inscrição em evento encerrado, fechado ou já realizado é recusada com mensagem explicativa.
- Uma segunda tentativa de inscrição do mesmo participante no mesmo evento é recusada (RN06), indicando que ele já está inscrito.
- Quando o evento está lotado, o participante é direcionado ao fluxo de fila de espera (US21) em vez de erro genérico.
**Prioridade:** Must
**Telas/fluxos relacionados:** Detalhes do evento, Fluxo B

### US18 — Cancelar inscrição
Como participante, quero cancelar uma inscrição confirmada, para liberar minha vaga caso não possa mais comparecer.
**Critérios de aceitação:**
- Ao cancelar, o estado da inscrição muda para "cancelado" e some da lista de inscrições ativas do participante.
- O cancelamento de uma inscrição confirmada libera automaticamente uma vaga, disparando a promoção da fila de espera (US22), se houver.
- Um participante já com presença registrada (check-in feito) não pode cancelar a inscrição retroativamente.
**Prioridade:** Must
**Telas/fluxos relacionados:** Área do participante

### US19 — Impedir inscrição duplicada no mesmo evento
Como sistema, quero impedir que um participante tenha mais de uma inscrição ativa no mesmo evento, para manter a contagem de vagas correta (RN06).
**Critérios de aceitação:**
- Ao tentar se inscrever novamente em um evento no qual já possui inscrição ativa (confirmada ou em espera), o participante recebe aviso e nenhuma nova inscrição é criada.
- Uma inscrição previamente cancelada não impede nova inscrição no mesmo evento, caso ainda haja vagas.
**Prioridade:** Must
**Telas/fluxos relacionados:** Fluxo B (RN06)

### US20 — Impedir inscrição em evento indisponível
Como sistema, quero impedir novas inscrições em eventos encerrados, fechados ou já realizados, para manter a consistência das informações de participação.
**Critérios de aceitação:**
- Eventos com estado "encerrado" ou "realizado" não exibem a opção de inscrição.
- Uma tentativa de inscrição via ação direta em evento nessas condições é recusada pelo sistema, mesmo que a interface tenha alguma falha de exibição.
**Prioridade:** Must
**Telas/fluxos relacionados:** Detalhes do evento

### US21 — Entrar na fila de espera de um evento lotado
Como participante, quero entrar na fila de espera quando um evento estiver lotado, para ter chance de ser promovido caso surja uma vaga.
**Critérios de aceitação:**
- Ao tentar se inscrever em um evento sem vagas (mas com fila habilitada), o participante é adicionado ao fim da fila (RN04).
- A área do participante mostra claramente o estado "em fila de espera" e, quando disponível, a posição na fila.
- Um participante já na fila do mesmo evento não pode entrar duas vezes (mesma regra de RN06 aplicada à fila).
**Prioridade:** Must
**Telas/fluxos relacionados:** Detalhes do evento, Fluxo C

### US22 — Promoção automática da fila de espera
Como sistema, quero promover automaticamente o próximo participante elegível da fila quando uma vaga é liberada, para aproveitar vagas ociosas sem intervenção manual (RN05).
**Critérios de aceitação:**
- Quando uma vaga é liberada (cancelamento, aumento de vagas, etc.), o participante há mais tempo na fila é promovido primeiro.
- O estado da inscrição promovida muda de "em espera" para "confirmado" automaticamente.
- O participante promovido passa a visualizar a inscrição como confirmada em sua área pessoal.
**Prioridade:** Must
**Telas/fluxos relacionados:** Fluxo C (RN04, RN05)

---

## Bloco 6 — Área do participante (F08)

### US23 — Consultar minhas inscrições e seus estados
Como participante, quero consultar todas as minhas inscrições e seus estados atuais, para acompanhar minha situação em cada evento.
**Critérios de aceitação:**
- A listagem exibe, para cada inscrição, o estado: confirmado, em fila de espera, cancelado ou concluído.
- A partir da lista é possível acessar o identificador de check-in (quando aplicável) e o certificado (quando emitido).
- Inscrições canceladas ficam disponíveis para consulta histórica, mas sinalizadas como tal.
**Prioridade:** Must
**Telas/fluxos relacionados:** Área do participante, Fluxo B, Fluxo C

---

## Bloco 7 — Check-in / presença (F09)

### US24 — Obter identificador individual de check-in
Como participante com inscrição confirmada, quero obter um identificador individual de check-in (QR Code ou algo similar), para apresentá-lo na entrada do evento.
**Critérios de aceitação:**
- O identificador só é gerado/disponibilizado para inscrições no estado "confirmado" (RN07).
- O identificador é exclusivo por inscrição/evento, mesmo que o mesmo participante tenha check-ins em outros eventos.
- O identificador fica acessível na área do participante a qualquer momento antes do evento.
**Prioridade:** Must
**Telas/fluxos relacionados:** Área do participante, Fluxo D

### US25 — Check-in por chip do crachá
Como administrador, quero validar a presença usando o chip identificador do crachá do aluno quando disponível, para agilizar o check-in na entrada do evento.
**Critérios de aceitação:**
- Quando o chip do crachá está associado ao participante, a leitura do chip é aceita como forma válida de check-in.
- A leitura segue as mesmas regras de validação de inscrição confirmada (RN07) e não duplicação (RN08).
**Prioridade:** Should
**Telas/fluxos relacionados:** Check-in, Fluxo D

### US26 — Check-in por leitura de QR Code via aplicativo
Como administrador, quero validar a presença por leitura de QR Code via aplicativo de celular, para ter uma alternativa viável quando o chip do crachá não estiver disponível.
**Critérios de aceitação:**
- A leitura do QR Code na entrada do evento é aceita como forma válida de check-in, sujeita às mesmas regras de RN07/RN08.
- A leitura ocorre preferencialmente na entrada do evento, não na saída, para evitar filas ao término da atividade.
**Prioridade:** Should
**Telas/fluxos relacionados:** Check-in, Fluxo D

### US27 — Validar check-in e impedir reutilização
Como administrador, quero validar o identificador de check-in de um participante no momento do evento, para registrar sua presença de forma confiável.
**Critérios de aceitação:**
- Um identificador válido de participante inscrito no evento correspondente resulta em check-in aceito, com data/hora registrada.
- Um identificador de participante não inscrito no evento é rejeitado, com mensagem explicando o motivo.
- Uma segunda tentativa de check-in com o mesmo identificador é rejeitada, informando que já foi utilizado (RN08).
- O sistema informa de forma clara e imediata se o check-in foi aceito ou rejeitado, incluindo o motivo da rejeição.
**Prioridade:** Must
**Telas/fluxos relacionados:** Check-in, Fluxo D (RN07, RN08)

---

## Bloco 8 — Certificados (F10)

### US28 — Gerar certificado para participante com presença registrada
Como sistema, quero gerar certificado apenas para participantes com presença confirmada, para garantir que somente quem compareceu receba o documento (RN09).
**Critérios de aceitação:**
- Um participante inscrito mas sem check-in registrado não tem certificado disponível.
- O certificado gerado contém nome do participante, nome do evento, data e carga horária.
- Cada certificado recebe um código único de verificação (RN10), gerado no momento da emissão.
**Prioridade:** Must
**Telas/fluxos relacionados:** Fluxo E

### US29 — Consultar e obter meu certificado
Como participante, quero acessar e obter meu certificado após o evento, para comprovar minha participação.
**Critérios de aceitação:**
- Após o check-in ser processado e o certificado emitido, ele fica disponível na área do participante.
- Tentar acessar um certificado antes da emissão (sem presença registrada) exibe mensagem informando que ele ainda não está disponível, e não um erro genérico.
**Prioridade:** Must
**Telas/fluxos relacionados:** Área do participante, Fluxo E

### US30 — Conferir validade de um certificado pelo código
Como organização/administrador, quero conferir a validade de um certificado a partir do seu código único, para evitar a circulação de certificados falsos ou fraudados.
**Critérios de aceitação:**
- Ao informar um código válido, o sistema retorna os dados básicos do certificado (participante, evento, data, carga horária).
- Ao informar um código inexistente ou inválido, o sistema informa claramente que o certificado não foi encontrado.
- Não é necessário um portal público automatizado; basta um mecanismo de conferência acessível à organização.
**Prioridade:** Must
**Telas/fluxos relacionados:** Conferência de certificados (RN10)

---

## Bloco 9 — Acompanhamento administrativo (F11)

### US31 — Acompanhar contagens básicas de um evento
Como administrador, quero consultar contagens básicas de um evento (vagas, inscritos, em espera, presenças, certificados emitidos), para acompanhar seu andamento operacional.
**Critérios de aceitação:**
- A tela de acompanhamento exibe, no mínimo: total de vagas, inscritos confirmados, pessoas em fila de espera, presenças registradas e certificados emitidos.
- Os números são atualizados conforme novas inscrições, check-ins e emissões ocorrem.
- É possível listar os participantes inscritos e os presentes separadamente.
**Prioridade:** Must
**Telas/fluxos relacionados:** Acompanhamento administrativo

### US32 — Ajustar a quantidade de vagas de um evento em andamento
Como administrador, quero ajustar a quantidade de vagas de um evento, para liberar mais vagas quando o espaço permitir ou corrigir um cadastro inicial.
**Critérios de aceitação:**
- Aumentar as vagas dispara a promoção automática de participantes da fila de espera, respeitando a ordem (US22).
- Reduzir as vagas abaixo do número já confirmado exige confirmação explícita, já que inscrições confirmadas não podem ser removidas automaticamente.
**Prioridade:** Should
**Telas/fluxos relacionados:** Gestão de eventos

### US33 — Consultar indicadores agregados de participação
Como administrador, quero consultar indicadores agregados de participação em relação ao público-alvo esperado, para apoiar relatórios de gestão da direção e da coordenação de extensão.
**Critérios de aceitação:**
- É possível consultar, para um período, quantos eventos foram realizados e quantas pessoas efetivamente compareceram no total.
- Os indicadores consideram apenas presenças efetivamente registradas (check-in), não apenas inscrições.
- Ausência de dados no período consultado é informada de forma clara, sem erro.
**Prioridade:** Could
**Telas/fluxos relacionados:** Acompanhamento administrativo

---

## Bloco 10 — Voluntariado (F12)

### US34 — Registrar voluntário em um evento
Como administrador, quero identificar dentro de um evento as pessoas que atuaram como voluntárias, para diferenciá-las dos participantes comuns e viabilizar a contagem de suas horas.
**Critérios de aceitação:**
- É possível associar uma pessoa a um evento com o papel "voluntário", distinto do papel "participante".
- Uma mesma pessoa pode ser voluntária em um evento e participante em outro, sem conflito de cadastro.
- O registro de voluntário exige, no mínimo, identificação da pessoa e do evento em que atuou.
**Prioridade:** Must
**Telas/fluxos relacionados:** Fluxo F

### US35 — Contabilizar horas de voluntariado
Como voluntário, quero ter meu envolvimento em um evento confirmado no sistema, para que minhas horas sejam contabilizadas como atividade complementar (RN12).
**Critérios de aceitação:**
- Somente voluntários com envolvimento devidamente registrado (US34) têm horas contabilizadas — não há contabilização "automática" por presença simples.
- A confirmação do envolvimento gera um registro consultável (equivalente a um certificado ou declaração) com o evento, a data e a carga horária correspondente.
- Um voluntário sem registro associado a um evento não consegue solicitar/obter contabilização de horas para ele.
**Prioridade:** Should
**Telas/fluxos relacionados:** Fluxo F (RN12)

---

## Bloco 11 — Visão institucional (Gestor/Coordenação)

### US36 — Consultar indicadores consolidados como coordenação/direção
Como gestor/coordenação (ex.: direção da FCI, coordenação de extensão), quero consultar indicadores consolidados de participação e evidências dos eventos realizados, para utilizá-los como insumo em relatórios de gestão da faculdade.
**Critérios de aceitação:**
- O perfil Gestor consegue visualizar os mesmos indicadores agregados de US33, sem necessariamente operar o dia a dia dos eventos (sem acesso a funções de criação/alteração de evento).
- A consulta permite filtrar por período (ex.: semestre).
- Quando não há eventos realizados no período, isso é informado de forma explícita.
**Prioridade:** Could
**Telas/fluxos relacionados:** Acompanhamento administrativo / visão institucional

---

## Bloco 12 — Extensões desejáveis (fora do núcleo obrigatório)

### US37 — Registrar evidências fotográficas de um evento
Como administrador, quero associar registros fotográficos a um evento como evidência de sua realização, para apoiar a elaboração de relatórios de gestão da faculdade.
**Critérios de aceitação:**
- É possível anexar uma ou mais fotos a um evento já realizado.
- As fotos anexadas ficam disponíveis para consulta administrativa junto aos dados do evento.
- A ausência de fotos não impede nenhuma outra funcionalidade do evento (presença, certificados, etc.).
**Prioridade:** Could
**Telas/fluxos relacionados:** Gestão de eventos (F13)

---
