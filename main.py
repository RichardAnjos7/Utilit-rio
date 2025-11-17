"""
Aplicativo Utilitário de Suporte Técnico para Windows
Ferramenta centralizada para automação de tarefas de suporte
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.service_tag import ServiceTagModule
from modules.network_diagnostic import NetworkDiagnosticModule
from utils.module_manager import ModuleManager


class SupportUtilityApp:
    """Aplicativo principal de utilitários de TI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Utilitário de TI")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Gerenciador de módulos
        self.module_manager = ModuleManager()
        
        # Registra módulos disponíveis
        self._register_modules()
        
        # Cria interface
        self._create_ui()
        
        # Carrega o primeiro módulo por padrão
        if self.module_manager.get_modules():
            first_module = list(self.module_manager.get_modules().keys())[0]
            self._load_module(first_module)
    
    def _register_modules(self):
        """Registra todos os módulos disponíveis"""
        self.module_manager.register_module("service_tag", ServiceTagModule())
        self.module_manager.register_module("network_diagnostic", NetworkDiagnosticModule())
    
    def _create_ui(self):
        """Cria a interface gráfica do aplicativo"""
        # Frame principal com layout horizontal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configura grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Painel lateral com lista de módulos
        sidebar_frame = ttk.LabelFrame(main_frame, text="Ferramentas", padding="10")
        sidebar_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Lista de módulos
        self.module_listbox = tk.Listbox(sidebar_frame, width=25, font=("Segoe UI", 10))
        self.module_listbox.pack(fill=tk.BOTH, expand=True)
        self.module_listbox.bind('<<ListboxSelect>>', self._on_module_select)
        
        # Preenche lista de módulos
        for module_name, module in self.module_manager.get_modules().items():
            display_name = module.get_display_name()
            self.module_listbox.insert(tk.END, display_name)
        
        # Frame de conteúdo (onde os módulos serão exibidos)
        self.content_frame = ttk.Frame(main_frame, padding="20")
        self.content_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Frame inicial de boas-vindas
        self._show_welcome()
    
    def _show_welcome(self):
        """Exibe tela de boas-vindas"""
        welcome_label = ttk.Label(
            self.content_frame,
            text="Bem-vindo ao Utilitário de Suporte Técnico",
            font=("Segoe UI", 16, "bold")
        )
        welcome_label.grid(row=0, column=0, pady=20)
        
        info_label = ttk.Label(
            self.content_frame,
            text="Selecione uma ferramenta no painel lateral para começar",
            font=("Segoe UI", 10)
        )
        info_label.grid(row=1, column=0, pady=10)
    
    def _on_module_select(self, event):
        """Callback quando um módulo é selecionado"""
        selection = self.module_listbox.curselection()
        if selection:
            index = selection[0]
            module_names = list(self.module_manager.get_modules().keys())
            if index < len(module_names):
                module_name = module_names[index]
                self._load_module(module_name)
    
    def _load_module(self, module_name):
        """Carrega e exibe um módulo no frame de conteúdo"""
        # Para threads de módulos anteriores (especialmente network_diagnostic)
        for module in self.module_manager.get_modules().values():
            if hasattr(module, '_stop_auto_refresh'):
                module._stop_auto_refresh()
            if hasattr(module, 'is_collecting'):
                module.is_collecting = False
        
        # Limpa o frame de conteúdo
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Obtém o módulo
        module = self.module_manager.get_module(module_name)
        if module:
            try:
                # Cria a interface do módulo
                module_frame = module.create_ui(self.content_frame)
                module_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao carregar módulo: {str(e)}"
                )


def main():
    """Função principal"""
    root = tk.Tk()
    app = SupportUtilityApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()


