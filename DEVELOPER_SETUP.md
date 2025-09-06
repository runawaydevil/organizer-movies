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
├── models/                    # Data models
├── services/                  # Core services
├── Images/                    # UI resources
├── requirements.txt           # Dependencies
├── .gitignore                # Git ignore rules
├── .gitattributes            # Git attributes
└── README.md                 # Documentation
```

## 🔒 Segurança

- Chaves de API são armazenadas localmente
- Configuração é codificada (Base64)
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

## 🆘 Suporte

- **Issues**: https://github.com/runawaydevil/organizer-movies/issues
- **Documentação**: Veja arquivos .md incluídos
- **Autor**: Pablo Murad (runawaydevil)

---

**Movie Organizer v0.01** - Desenvolvido com ❤️ por Pablo Murad (runawaydevil)
