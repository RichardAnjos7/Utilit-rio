"""
Gerenciador de módulos para o aplicativo utilitário
Facilita a adição e organização de novos módulos
"""


class ModuleManager:
    """Gerenciador centralizado de módulos do aplicativo"""
    
    def __init__(self):
        self.modules = {}
    
    def register_module(self, module_id, module_instance):
        """
        Registra um novo módulo no sistema
        
        Args:
            module_id: Identificador único do módulo (string)
            module_instance: Instância do módulo (deve ter método create_ui e get_display_name)
        """
        if not hasattr(module_instance, 'create_ui'):
            raise ValueError(f"Módulo {module_id} deve implementar o método 'create_ui'")
        if not hasattr(module_instance, 'get_display_name'):
            raise ValueError(f"Módulo {module_id} deve implementar o método 'get_display_name'")
        
        self.modules[module_id] = module_instance
    
    def get_module(self, module_id):
        """Retorna uma instância do módulo pelo ID"""
        return self.modules.get(module_id)
    
    def get_modules(self):
        """Retorna todos os módulos registrados"""
        return self.modules.copy()
    
    def unregister_module(self, module_id):
        """Remove um módulo do sistema"""
        if module_id in self.modules:
            del self.modules[module_id]
    
    def list_module_ids(self):
        """Retorna lista de IDs de todos os módulos"""
        return list(self.modules.keys())


