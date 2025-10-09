# 🚀 Movie Organizer - Developer Setup Guide

## ⚠️ IMPORTANTE: Configuração Segura

**NUNCA commite arquivos com chaves de API reais!**

### Arquivos Sensíveis (NÃO commitar):
- `tmdb_config.json` - Contém chaves reais do TMDB
- `config.json` - Contém chaves reais do OpenAI
- `movie_organizer.log` - Logs com informações sensíveis
- `build/` - Arquivos de build do PyInstaller
- `dist/` - Executáveis compilados
- `release/` - Pacotes de distribuição

### Arquivos de Exemplo (OK para commitar):
- `tmdb_config.example.json` - Template para configuração TMDB
- `config.example.json` - Template para configuração completa

## 🔧 Setup para Desenvolvimento

### 1. Clone o Repositório
```bash
git clone https://github.com/runawaydevil/organizer-movies.git
cd organizer-movies
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Configurar APIs
1. Copie os arquivos de exemplo:
   ```bash
   cp tmdb_config.example.json tmdb_config.json
   cp config.example.json config.json
   ```

2. Edite os arquivos com suas chaves reais:
   - **OpenAI API**: https://platform.openai.com/api-keys
   - **TMDB API**: https://www.themoviedb.org/settings/api

### 4. Executar o Projeto
```bash
# GUI Mode
python main.py

# CLI Mode (Linux)
python cli.py
```

## 🏗️ Build e Distribuição

### Build Simples
```bash
python build_release.py
```

### Build Manual
```bash
# Instalar PyInstaller
pip install pyinstaller

# Build
pyinstaller MovieOrganizer.spec
```

## 📁 Estrutura do Projeto

```
MovieOrganizer/
├── main.py                    # Entry point GUI
├── cli.py                     # Entry point CLI
├── version.py                 # Centralized version info
├── models/                    # Data models
│   ├── movie_organizer_gui.py # Main GUI controller
│   ├── movie_metadata.py      # Movie metadata model
│   └── config.py              # Configuration models
├── services/                  # Core services
│   ├── ai_analyzer.py         # OpenAI integration
│   ├── tmdb_service.py        # TMDB API service
│   ├── hybrid_analyzer.py     # AI + TMDB analyzer
│   ├── file_scanner.py        # File scanning
│   ├── smart_folder_manager.py # Folder management
│   ├── movie_report_generator.py # PDF reports
│   └── secure_config_manager.py # Secure config storage
├── docs/                      # Documentation
│   ├── API_SETUP.md          # API configuration guide
│   ├── CLI_USAGE.md          # CLI usage guide
│   ├── DEVELOPER_SETUP.md    # This file
│   ├── CONTRIBUTING.md       # Contribution guidelines
│   └── TROUBLESHOOTING.md    # Common issues and solutions
├── Images/                    # UI resources
├── requirements.txt           # Dependencies
├── .gitignore                # Git ignore rules
├── .gitattributes            # Git attributes
└── README.md                 # Main documentation
```

## 🔒 Segurança

- Chaves de API são armazenadas localmente com criptografia AES-256
- Configuração é criptografada (não apenas Base64)
- Nenhum dado é enviado para servidores externos
- Logs não contêm informações sensíveis

## 🧪 Testes

```bash
# Executar testes (quando implementados)
python -m pytest tests/

# Teste de shutdown
python test_shutdown.py
```

## 📝 Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

## 🔧 Desenvolvimento Local

### Configuração do Ambiente
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências de desenvolvimento
pip install -r requirements.txt
pip install pytest black flake8
```

### Executar Testes
```bash
# Testes unitários
python -m pytest tests/ -v

# Testes de integração
python tests/test_integration.py

# Cobertura de código
python -m pytest --cov=services --cov=models tests/
```

### Formatação de Código
```bash
# Formatar código
black .

# Verificar estilo
flake8 .
```

## 🚀 Build e Release

### Preparar Release
```bash
# Atualizar versão
# Editar version.py

# Executar testes
python -m pytest tests/

# Build
python build_release.py

# Verificar executável
./dist/MovieOrganizer.exe
```

### Estrutura de Release
```
release/
├── MovieOrganizer.exe              # Aplicação principal
├── Install_MovieOrganizer.bat      # Instalador do sistema
├── Run_MovieOrganizer_Portable.bat # Launcher portátil
├── README.md                       # Documentação principal
├── docs/                          # Documentação completa
└── Images/                        # Screenshots e ícones
```

## 🐛 Debug e Troubleshooting

### Logs de Debug
```bash
# Executar com logs detalhados
python main.py --debug

# Verificar logs
tail -f movie_organizer.log
```

### Problemas Comuns

**ImportError: No module named 'tkinter'**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
```

**Erro de Permissão**
```bash
# Linux - dar permissões
chmod +x main.py

# Windows - executar como administrador
```

**Erro de API**
- Verificar chaves API nas configurações
- Testar conectividade de rede
- Verificar créditos OpenAI

## 📊 Métricas de Desenvolvimento

### Performance
- Tempo de análise por filme: ~2-5 segundos
- Uso de memória: ~50-100MB
- Uso de CPU: Baixo (exceto durante análise AI)

### Qualidade de Código
- Cobertura de testes: >80%
- Complexidade ciclomática: <10
- Linhas de código por função: <50

## 🔄 Workflow de Desenvolvimento

1. **Criar Issue** - Descrever problema ou feature
2. **Criar Branch** - `git checkout -b feature/nome-da-feature`
3. **Desenvolver** - Implementar mudanças
4. **Testar** - Executar testes localmente
5. **Commit** - `git commit -m "feat: adicionar nova feature"`
6. **Push** - `git push origin feature/nome-da-feature`
7. **Pull Request** - Criar PR no GitHub
8. **Review** - Aguardar review e aprovação
9. **Merge** - Merge para main branch

## 🆘 Suporte

- **Issues**: https://github.com/runawaydevil/organizer-movies/issues
- **Documentação**: Veja arquivos em `docs/`
- **Autor**: Pablo Murad (runawaydevil)

---

**Movie Organizer v0.1** - Desenvolvido com ❤️ por Pablo Murad (runawaydevil)