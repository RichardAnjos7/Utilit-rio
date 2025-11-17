"""
Módulo para coleta e exibição de Service Tag / Número de Série
"""

import tkinter as tk
from tkinter import ttk
import subprocess
import platform
import socket
import os


class ServiceTagModule:
    """Módulo para obter Service Tag do dispositivo Windows"""
    
    def __init__(self):
        self.service_tag = None
        self.root_window = None
    
    def get_display_name(self):
        """Retorna o nome de exibição do módulo"""
        return "Service Tag"
    
    def create_ui(self, parent):
        """Cria a interface do módulo"""
        # Armazena referência à janela raiz
        self.root_window = parent.winfo_toplevel()
        frame = ttk.Frame(parent, padding="20")
        
        # Título
        title_label = ttk.Label(
            frame,
            text="Service Tag / Número de Série",
            font=("Segoe UI", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Descrição
        desc_label = ttk.Label(
            frame,
            text="Clique no botão abaixo para coletar automaticamente a Service Tag do dispositivo:",
            font=("Segoe UI", 9),
            wraplength=500
        )
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Botão para coletar Service Tag
        collect_button = ttk.Button(
            frame,
            text="Coletar Service Tag",
            command=lambda: self._collect_service_tag(result_label, copy_button),
            width=30
        )
        collect_button.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Label para exibir resultado
        result_label = ttk.Label(
            frame,
            text="Service Tag não coletada",
            font=("Segoe UI", 11),
            foreground="gray"
        )
        result_label.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Botão para copiar (inicialmente desabilitado)
        copy_button = ttk.Button(
            frame,
            text="Copiar para Área de Transferência",
            command=self._copy_to_clipboard,
            state="disabled",
            width=30
        )
        copy_button.grid(row=4, column=0, columnspan=2, pady=10)
        
        # Frame de informações adicionais
        info_frame = ttk.LabelFrame(frame, text="Informações do Sistema", padding="15")
        info_frame.grid(row=5, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))
        
        # Informações do sistema
        self._add_system_info(info_frame)
        
        return frame
    
    def _collect_service_tag(self, result_label, copy_button):
        """Coleta a Service Tag do dispositivo"""
        try:
            # Tenta obter via WMI (método mais confiável)
            service_tag = self._get_service_tag_wmi()
            
            # Se não conseguir via WMI, tenta via comando do sistema
            if not service_tag or service_tag.strip() == "":
                service_tag = self._get_service_tag_cmd()
            
            if service_tag and service_tag.strip():
                self.service_tag = service_tag.strip()
                result_label.config(
                    text=f"Service Tag: {self.service_tag}",
                    font=("Segoe UI", 11, "bold"),
                    foreground="green"
                )
                copy_button.config(state="normal")
            else:
                raise Exception("Não foi possível obter a Service Tag")
                
        except Exception as e:
            result_label.config(
                text=f"Erro ao coletar Service Tag: {str(e)}",
                font=("Segoe UI", 10),
                foreground="red"
            )
            copy_button.config(state="disabled")
            self.service_tag = None
    
    def _get_service_tag_wmi(self):
        """Obtém Service Tag via WMI (Windows Management Instrumentation)"""
        try:
            import wmi
            c = wmi.WMI()
            for bios in c.Win32_BIOS():
                serial = bios.SerialNumber
                if serial and serial.strip():
                    return serial.strip()
        except ImportError:
            # Se wmi não estiver instalado, retorna None
            pass
        except Exception:
            pass
        return None
    
    def _get_service_tag_cmd(self):
        """Obtém Service Tag via comando do sistema"""
        try:
            # Método 1: wmic bios get serialnumber
            result = subprocess.run(
                ["wmic", "bios", "get", "serialnumber"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line and line.upper() != "SERIALNUMBER":
                        return line
            
            # Método 2: PowerShell
            ps_command = "Get-WmiObject Win32_BIOS | Select-Object -ExpandProperty SerialNumber"
            result = subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                serial = result.stdout.strip()
                if serial:
                    return serial
                    
        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass
        
        return None
    
    def _copy_to_clipboard(self):
        """Copia a Service Tag para a área de transferência"""
        if self.service_tag and self.root_window:
            try:
                self.root_window.clipboard_clear()
                self.root_window.clipboard_append(self.service_tag)
                self.root_window.update()
                # Feedback visual
                import tkinter.messagebox as messagebox
                messagebox.showinfo("Sucesso", "Service Tag copiada para a área de transferência!")
            except Exception as e:
                import tkinter.messagebox as messagebox
                messagebox.showerror("Erro", f"Erro ao copiar: {str(e)}")
    
    def _add_system_info(self, parent):
        """Adiciona informações do sistema ao frame"""
        try:
            import platform
            
            # Nome do computador
            computer_name = platform.node()
            ttk.Label(parent, text="Nome do Computador:", font=("Segoe UI", 9, "bold")).grid(
                row=0, column=0, sticky=tk.W, pady=5
            )
            ttk.Label(parent, text=computer_name, font=("Segoe UI", 9)).grid(
                row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5
            )
            
            # IP do computador
            try:
                # Obtém o IP principal do computador
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
            except Exception:
                ip_address = "Não disponível"
            
            ttk.Label(parent, text="Endereço IP:", font=("Segoe UI", 9, "bold")).grid(
                row=1, column=0, sticky=tk.W, pady=5
            )
            ttk.Label(parent, text=ip_address, font=("Segoe UI", 9)).grid(
                row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5
            )
            
            # Grupo de Trabalho (Domínio)
            domain_workgroup = "Não disponível"
            try:
                # Método 1: PowerShell - Win32_ComputerSystem (mais confiável para domínio real)
                ps_command = "(Get-WmiObject -Class Win32_ComputerSystem).Domain"
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_command],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                if result.returncode == 0 and result.stdout.strip():
                    domain_value = result.stdout.strip()
                    if domain_value:
                        domain_workgroup = domain_value
                
                # Método 2: WMI direto com /value
                if domain_workgroup == "Não disponível" or domain_workgroup.upper() == "WORKGROUP":
                    result = subprocess.run(
                        ["wmic", "computersystem", "get", "domain", "/value"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    if result.returncode == 0 and result.stdout:
                        for line in result.stdout.split('\n'):
                            line = line.strip()
                            if line.startswith('Domain='):
                                domain_value = line.split('=', 1)[1].strip()
                                if domain_value:
                                    domain_workgroup = domain_value
                                    break
                
                # Método 3: PowerShell - Get-ADDomain (se estiver em domínio Active Directory)
                if domain_workgroup == "Não disponível" or domain_workgroup.upper() == "WORKGROUP":
                    ps_command = "try { (Get-ADDomain).DNSRoot } catch { $null }"
                    result = subprocess.run(
                        ["powershell", "-NoProfile", "-Command", ps_command],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        domain_value = result.stdout.strip()
                        if domain_value:
                            domain_workgroup = domain_value
                
                # Método 4: Variável de ambiente USERDOMAIN (pode ser o domínio do usuário, não do computador)
                if domain_workgroup == "Não disponível":
                    domain_env = os.environ.get('USERDOMAIN', '')
                    if domain_env:
                        domain_workgroup = domain_env
                
                # Método 5: LOGONSERVER (último recurso)
                if domain_workgroup == "Não disponível":
                    logon_server = os.environ.get('LOGONSERVER', '')
                    if logon_server:
                        # Remove \\ do início se existir
                        logon_server = logon_server.replace('\\\\', '').strip()
                        if logon_server:
                            domain_workgroup = logon_server
                        
            except Exception:
                # Em caso de erro, tenta pelo menos a variável de ambiente
                try:
                    domain_env = os.environ.get('USERDOMAIN', '')
                    if domain_env:
                        domain_workgroup = domain_env
                except:
                    pass
            
            ttk.Label(parent, text="Grupo de Trabalho (Domínio):", font=("Segoe UI", 9, "bold")).grid(
                row=2, column=0, sticky=tk.W, pady=5
            )
            ttk.Label(parent, text=domain_workgroup, font=("Segoe UI", 9)).grid(
                row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5
            )
            
            # Sistema operacional
            os_info = f"{platform.system()} {platform.release()} {platform.version()}"
            ttk.Label(parent, text="Sistema Operacional:", font=("Segoe UI", 9, "bold")).grid(
                row=3, column=0, sticky=tk.W, pady=5
            )
            ttk.Label(parent, text=os_info, font=("Segoe UI", 9)).grid(
                row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5
            )
            
        except Exception:
            pass

