"""
Exemplo de módulo para demonstrar como adicionar novas funcionalidades
Este arquivo serve como template para criar novos módulos
"""

import tkinter as tk
from tkinter import ttk


class ExampleModule:
    """Módulo de exemplo - template para novos módulos"""
    
    def __init__(self):
        pass
    
    def get_display_name(self):
        """Retorna o nome de exibição do módulo"""
        return "Exemplo (Template)"
    
    def create_ui(self, parent):
        """Cria a interface do módulo"""
        frame = ttk.Frame(parent, padding="20")
        
        # Título
        title_label = ttk.Label(
            frame,
            text="Módulo de Exemplo",
            font=("Segoe UI", 14, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Descrição
        desc_label = ttk.Label(
            frame,
            text="Este é um exemplo de como criar novos módulos.\n"
                 "Use este arquivo como template para suas próprias funcionalidades.",
            font=("Segoe UI", 9),
            wraplength=500,
            justify=tk.LEFT
        )
        desc_label.grid(row=1, column=0, pady=(0, 20))
        
        # Botão de exemplo
        example_button = ttk.Button(
            frame,
            text="Botão de Exemplo",
            command=self._example_action,
            width=30
        )
        example_button.grid(row=2, column=0, pady=10)
        
        return frame
    
    def _example_action(self):
        """Ação de exemplo para o botão"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Exemplo", "Esta é uma ação de exemplo!")


