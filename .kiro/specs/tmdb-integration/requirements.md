# Requirements Document

## Introduction

Esta especificação define a integração completa do serviço TMDB (The Movie Database) ao Movie Organizer para obter nomes corretos e padronizados de filmes. O sistema atual usa apenas análise por IA, mas com a integração TMDB, teremos acesso a uma base de dados oficial de filmes com informações precisas, incluindo títulos originais, anos de lançamento e metadados adicionais.

## Requirements

### Requirement 1

**User Story:** Como usuário do Movie Organizer, eu quero que o sistema use a base de dados TMDB para obter nomes corretos de filmes, para que meus arquivos sejam organizados com títulos padronizados e precisos.

#### Acceptance Criteria

1. WHEN o sistema analisa um arquivo de filme THEN ele SHALL usar o hybrid analyzer (AI + TMDB) por padrão
2. WHEN o TMDB retorna resultados THEN o sistema SHALL priorizar o título original do TMDB sobre a análise por IA
3. WHEN o TMDB não encontra resultados THEN o sistema SHALL usar apenas a análise por IA como fallback
4. WHEN o sistema encontra múltiplos resultados no TMDB THEN ele SHALL escolher o resultado com maior popularidade e rating
5. IF o usuário configurou chaves de API do TMDB THEN o sistema SHALL usar o hybrid analyzer automaticamente

### Requirement 2

**User Story:** Como usuário, eu quero configurar minhas chaves de API do TMDB através da interface gráfica, para que eu possa habilitar a funcionalidade TMDB sem editar arquivos de configuração.

#### Acceptance Criteria

1. WHEN o usuário abre as configurações THEN o sistema SHALL mostrar campos para API Key e Bearer Token do TMDB
2. WHEN o usuário insere as chaves do TMDB THEN o sistema SHALL validar a conexão com a API
3. WHEN a validação é bem-sucedida THEN o sistema SHALL salvar as configurações e habilitar o modo hybrid
4. WHEN a validação falha THEN o sistema SHALL mostrar uma mensagem de erro clara
5. IF as chaves não estão configuradas THEN o sistema SHALL usar apenas análise por IA

### Requirement 3

**User Story:** Como usuário, eu quero ver informações adicionais do TMDB (como sinopse, rating, ano) na interface, para que eu possa verificar se o filme identificado está correto.

#### Acceptance Criteria

1. WHEN o sistema identifica um filme via TMDB THEN ele SHALL mostrar informações adicionais na interface
2. WHEN o usuário visualiza os resultados THEN o sistema SHALL exibir título original, ano, rating e sinopse
3. WHEN há poster disponível THEN o sistema SHALL mostrar uma miniatura do poster
4. WHEN o usuário clica em um filme THEN o sistema SHALL mostrar detalhes completos do TMDB
5. IF não há informações do TMDB THEN o sistema SHALL mostrar apenas os dados da análise por IA

### Requirement 4

**User Story:** Como usuário, eu quero poder corrigir manualmente identificações incorretas usando busca no TMDB, para que eu possa garantir que filmes difíceis de identificar sejam organizados corretamente.

#### Acceptance Criteria

1. WHEN o usuário não concorda com a identificação automática THEN ele SHALL poder fazer busca manual no TMDB
2. WHEN o usuário faz busca manual THEN o sistema SHALL mostrar resultados do TMDB em tempo real
3. WHEN o usuário seleciona um resultado manual THEN o sistema SHALL usar essas informações para organização
4. WHEN o usuário confirma a correção manual THEN o sistema SHALL salvar essa preferência para futuros arquivos similares
5. IF a busca manual não retorna resultados THEN o usuário SHALL poder inserir informações manualmente

### Requirement 5

**User Story:** Como usuário, eu quero que o sistema mantenha cache das consultas TMDB, para que consultas repetidas sejam mais rápidas e não excedam os limites de rate da API.

#### Acceptance Criteria

1. WHEN o sistema faz uma consulta ao TMDB THEN ele SHALL salvar o resultado em cache local
2. WHEN o mesmo filme é consultado novamente THEN o sistema SHALL usar o cache em vez de fazer nova requisição
3. WHEN o cache expira (após 7 dias) THEN o sistema SHALL fazer nova consulta ao TMDB
4. WHEN o sistema atinge limite de rate THEN ele SHALL aguardar o tempo necessário antes de nova tentativa
5. IF o cache está corrompido THEN o sistema SHALL limpar o cache e fazer nova consulta

### Requirement 6

**User Story:** Como usuário, eu quero que o sistema funcione offline ou quando o TMDB está indisponível, para que eu possa continuar organizando filmes mesmo sem conexão com a internet.

#### Acceptance Criteria

1. WHEN não há conexão com internet THEN o sistema SHALL usar apenas análise por IA
2. WHEN o TMDB está indisponível THEN o sistema SHALL fazer fallback para IA após timeout
3. WHEN há erro na API do TMDB THEN o sistema SHALL continuar processamento com IA
4. WHEN a conexão é restaurada THEN o sistema SHALL voltar a usar o modo hybrid automaticamente
5. IF há filmes processados offline THEN o usuário SHALL poder reprocessá-los com TMDB quando online

### Requirement 7

**User Story:** Como usuário, eu quero que o sistema use nomes de pastas padronizados do TMDB compatíveis com media servers (Plex, Jellyfin), para que minha biblioteca seja reconhecida corretamente por esses sistemas.

#### Acceptance Criteria

1. WHEN o sistema cria pastas usando dados do TMDB THEN ele SHALL usar formato "Título (Ano)"
2. WHEN há título original diferente THEN o sistema SHALL priorizar o título original
3. WHEN há caracteres especiais no título THEN o sistema SHALL sanitizar para compatibilidade com sistemas de arquivos
4. WHEN há múltiplas versões do mesmo filme THEN o sistema SHALL usar sufixos apropriados
5. IF o usuário preferir títulos localizados THEN o sistema SHALL permitir essa configuração

### Requirement 8

**User Story:** Como usuário, eu quero que o sistema gerencie pastas de forma inteligente baseado no número de filmes, para que pastas com um único filme sejam renomeadas e pastas com múltiplos filmes tenham subpastas individuais criadas.

#### Acceptance Criteria

1. WHEN uma pasta contém exatamente 1 filme THEN o sistema SHALL renomear a pasta existente com o nome do filme
2. WHEN uma pasta já tem nome no formato de filme (Título (Ano)) THEN o sistema SHALL manter o nome existente
3. WHEN uma pasta contém múltiplos filmes THEN o sistema SHALL criar pastas individuais para cada filme
4. WHEN cria pastas individuais THEN o sistema SHALL mover cada filme para sua respectiva pasta
5. IF a pasta original ficar vazia após mover os filmes THEN o sistema SHALL manter a estrutura de pastas pai