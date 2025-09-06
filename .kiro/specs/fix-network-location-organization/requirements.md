# Requirements Document

## Introduction

O Movie Organizer está falhando ao processar arquivos em localizações de rede devido a uma função ausente (`organize_movie_file`) no serviço `FileMover`. O sistema consegue escanear e analisar os arquivos com IA, mas falha durante a organização real dos arquivos, causando encerramento abrupto da aplicação.

## Requirements

### Requirement 1

**User Story:** Como usuário, quero que o sistema organize arquivos de filmes em localizações de rede (drives mapeados) sem falhar, para que eu possa usar o organizador com meus arquivos armazenados em servidores de rede.

#### Acceptance Criteria

1. WHEN o usuário seleciona uma pasta em localização de rede (ex: X:/Mídia/Filmes) THEN o sistema SHALL processar todos os arquivos sem falhar
2. WHEN o sistema tenta organizar um arquivo THEN o sistema SHALL usar uma função válida que existe no FileMover
3. WHEN ocorre um erro durante a organização THEN o sistema SHALL continuar processando os demais arquivos ao invés de encerrar abruptamente
4. WHEN a organização é concluída THEN o sistema SHALL mostrar um relatório detalhado dos sucessos e falhas

### Requirement 2

**User Story:** Como desenvolvedor, quero que o FileMover tenha uma função `organize_movie_file` que combine renomeação e movimentação de arquivos, para que o código seja consistente com as chamadas existentes.

#### Acceptance Criteria

1. WHEN o FileMover é inicializado THEN o sistema SHALL ter uma função `organize_movie_file` disponível
2. WHEN `organize_movie_file` é chamada com parâmetros válidos THEN o sistema SHALL renomear o arquivo baseado nos metadados
3. WHEN `organize_movie_file` é chamada THEN o sistema SHALL mover o arquivo para a pasta de destino
4. WHEN `organize_movie_file` encontra conflitos de nome THEN o sistema SHALL resolver automaticamente adicionando números
5. WHEN `organize_movie_file` falha THEN o sistema SHALL retornar uma mensagem de erro clara sem encerrar a aplicação

### Requirement 3

**User Story:** Como usuário, quero que o sistema seja robusto ao trabalhar com localizações de rede, para que problemas de conectividade ou permissões não causem falhas catastróficas.

#### Acceptance Criteria

1. WHEN há problemas de conectividade de rede THEN o sistema SHALL mostrar mensagens de erro específicas
2. WHEN há problemas de permissão THEN o sistema SHALL informar claramente sobre permissões insuficientes
3. WHEN um arquivo individual falha THEN o sistema SHALL continuar processando os demais arquivos
4. WHEN há timeout de rede THEN o sistema SHALL implementar retry com backoff exponencial
5. WHEN a operação é interrompida THEN o sistema SHALL permitir cancelamento gracioso sem corrupção de dados