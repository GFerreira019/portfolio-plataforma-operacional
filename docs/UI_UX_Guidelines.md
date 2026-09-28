# Padrões Visuais e de Interface (UI/UX Guidelines)

Este documento estabelece as diretrizes de desenvolvimento frontend para a Plataforma Operacional (Timesheet e Gestão). Ao criar ou modificar telas, a IDE ou desenvolvedor deve obrigatoriamente seguir as convenções abaixo, alinhadas à nova stack com React e Django.

## 1. Stack Tecnológica Base
O frontend é construído para ser responsivo, rápido e totalmente isolado do backend, consumindo a API via HTTP:
* **Estilização e CSS:** TailwindCSS.
* **Componentes e Templates:** React (JSX/TSX).
* **Reatividade e Estado:** React Hooks (`useState`, `useEffect`) ou bibliotecas de estado global.
* **Comunicação com a API:** Axios ou Fetch API interagindo com o Django REST Framework (DRF).

## 2. Princípios de Ergonomia e Design
O sistema é utilizado por técnicos em campo (mobile) e planejadores no escritório (desktop). A carga cognitiva deve ser mínima.
* **Ergonomia Mobile (Regra dos 4 Toques):** Formulários de campo devem ser hiper-simplificados. Priorize seleções em vez de digitação livre, limitando a ação a poucos toques (ex: Selecionar Projeto > Equipamento > Atividade > Quantidade).
* **Botões de Ação Rápida:** Utilize botões de toque único ou ícones claros para evitar que o técnico gaste tempo interpretando a interface.
* **Bloqueio de Campos (UX Defensiva):** Dados que o sistema herda ou auto-preenche não devem ser editáveis livremente. O campo deve receber a propriedade `readOnly` e/ou `disabled`.

## 3. Comportamento Dinâmico e Reatividade (React)
As telas devem antecipar a necessidade do usuário com reatividade instantânea:
* **Seleção em Cascata:** Formulários de apontamento devem usar `useEffect` para carregar dependências progressivamente. Exemplo: A lista de *Equipamentos* só é carregada (filtrada via API) após a seleção do *Projeto*; a lista de *Atividades* só é liberada após a escolha do *Equipamento*.
* **Feedback Imediato (Validação assíncrona):** A digitação em campos críticos (como Códigos de Cliente ou Projeto) deve disparar validações silenciosas em background (`onChange` com debounce) para verificar duplicidades ou buscar dados complementares, travando o formulário se necessário antes mesmo do envio.

## 4. Gestão de Acesso Visual (Role-Based UI)
A interface deve refletir as permissões do backend e omitir funções que o usuário não tem direito de usar:
* **Ocultação de Funcionalidades por Papel:** O *Técnico de Campo* não deve visualizar formulários de Lançamento por Terceiros, que são restritos ao perfil *Planejador/Analista*.
* **Regra Anti-Autoaprovação:** Nas centrais de aprovação do *Planejador*, a interface deve garantir que apontamentos criados pelo próprio usuário logado não apareçam na lista de "pendentes de aprovação", espelhando a filtragem de segurança que já existe na API.
* **Tratamento de Erros:** O frontend deve exibir erros estruturados retornados pela API (ex: 400 Bad Request, 403 Forbidden) de forma amigável (Toast/Alerts), sem tentar substituir ou bypassar a validação do backend.

## 5. Padrões de Componentes e Performance
Dado o volume de dados transacionados e o uso em redes móveis (3G/4G), a performance do React deve ser rigorosa:
* **Listagens e Tabelas (Paginação Obrigatória):** Nunca renderize coleções completas em tela. Componentes de tabela devem acoplar à paginação nativa da API (`LimitOffsetPagination` ou `PageNumberPagination`), garantindo que apenas os dados da página atual sejam baixados.
* **Responsabilidade do Backend (Prevenção de N+1):** O frontend não deve fazer múltiplos loops de chamadas de rede para montar uma tabela. A API (via `select_related` no Django) deve fornecer o JSON já hidratado e pronto para renderização no React.
* **Estados Visuais (Carregamento e Vazio):** Todas as chamadas assíncronas devem tratar explicitamente os estados: `isLoading` (exibindo skeleton loaders ou spinners), `isError` (feedback de falha de conexão) e Empty State (quando a listagem retorna 0 resultados).