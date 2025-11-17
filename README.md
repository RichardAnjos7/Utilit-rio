# Utilitário de Suporte Técnico para Windows

Aplicativo centralizado para automação de tarefas de suporte técnico em ambientes Windows.

## Características

- **Arquitetura Modular**: Fácil adição de novas ferramentas e funcionalidades
- **Interface Intuitiva**: Interface gráfica moderna e fácil de usar
- **Extensível**: Sistema de módulos permite adicionar novas funcionalidades sem modificar o código principal

## Funcionalidades Atuais

### Service Tag / Número de Série
- Coleta automática da Service Tag do dispositivo Windows
- Múltiplos métodos de coleta (WMI e comandos do sistema)
- Copiar para área de transferência com um clique
- Exibe informações adicionais do sistema

## Requisitos

- Windows 7 ou superior
- Python 3.7 ou superior

## Instalação

1. Clone ou baixe este repositório

2. Instale as dependências (opcional, mas recomendado para melhor compatibilidade):
```bash
pip install -r requirements.txt
```

**Nota**: O aplicativo funciona sem instalar dependências adicionais, mas a biblioteca `wmi` melhora a confiabilidade na coleta da Service Tag.

## Uso

Execute o aplicativo:
```bash
python main.py
```

### Como usar o módulo Service Tag

1. Selecione "Service Tag" na lista de ferramentas no painel lateral
2. Clique no botão "Coletar Service Tag"
3. A Service Tag será exibida na tela
4. Use o botão "Copiar para Área de Transferência" para copiar o valor

## Adicionando Novos Módulos

Para adicionar um novo módulo ao aplicativo:

1. Crie um novo arquivo em `modules/` (ex: `modules/meu_modulo.py`)

2. Implemente uma classe que siga este padrão:

```python
class MeuModulo:
    def get_display_name(self):
        """Retorna o nome de exibição do módulo"""
        return "Nome do Módulo"
    
    def create_ui(self, parent):
        """Cria a interface do módulo"""
        frame = ttk.Frame(parent, padding="20")
        # Adicione seus widgets aqui
        return frame
```

3. Registre o módulo em `main.py`:

```python
from modules.meu_modulo import MeuModulo

# No método _register_modules():
self.module_manager.register_module("meu_modulo", MeuModulo())
```

## Estrutura do Projeto

```
.
├── main.py                 # Aplicativo principal
├── modules/               # Módulos de funcionalidades
│   ├── __init__.py
│   └── service_tag.py     # Módulo Service Tag
├── utils/                 # Utilitários
│   ├── __init__.py
│   └── module_manager.py  # Gerenciador de módulos
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## Desenvolvimento Futuro

A arquitetura modular permite adicionar facilmente novas funcionalidades como:
- Informações de hardware detalhadas
- Testes de conectividade de rede
- Coleta de logs do sistema
- Ferramentas de diagnóstico
- E muito mais...

## Licença

Este projeto é um utilitário de código aberto para uso em suporte técnico.

## Suporte

Para problemas ou sugestões, abra uma issue no repositório do projeto.


