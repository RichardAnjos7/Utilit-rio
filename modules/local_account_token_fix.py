"""
Módulo para correção automática do LocalAccountTokenFilterPolicy
Ferramenta para corrigir problemas de autenticação em contas locais do Windows
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import ctypes
import winreg
import threading


class LocalAccountTokenFixModule:
    """Módulo para corrigir LocalAccountTokenFilterPolicy"""
    
    def __init__(self):
        self.root_window = None
        self.is_admin = False
        self.current_value = None
    
    def get_display_name(self):
        """Retorna o nome de exibição do módulo"""
        return "LocalAccountTokenFilterPolicy - Auto Repair"
    
    def create_ui(self, parent):
        """Cria a interface do módulo"""
        self.root_window = parent.winfo_toplevel()
        frame = ttk.Frame(parent, padding="20")
        
        # Título
        title_label = ttk.Label(
            frame,
            text="LocalAccountTokenFilterPolicy - Auto Repair",
            font=("Segoe UI", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Descrição
        desc_label = ttk.Label(
            frame,
            text="Esta ferramenta verifica e corrige automaticamente a política de token de conta local.\n"
                 "Requer execução como Administrador.",
            font=("Segoe UI", 9),
            wraplength=600,
            justify="left"
        )
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Frame de status
        status_frame = ttk.LabelFrame(frame, text="Status", padding="15")
        status_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Status de administrador
        self.admin_status_label = ttk.Label(
            status_frame,
            text="Verificando privilégios de administrador...",
            font=("Segoe UI", 9)
        )
        self.admin_status_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Status do valor atual
        self.value_status_label = ttk.Label(
            status_frame,
            text="Valor atual: Verificando...",
            font=("Segoe UI", 9)
        )
        self.value_status_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Botão para verificar/corrigir
        self.fix_button = ttk.Button(
            frame,
            text="Verificar e Corrigir",
            command=self._check_and_fix,
            width=30,
            state="disabled"
        )
        self.fix_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Frame de informações
        info_frame = ttk.LabelFrame(frame, text="Informações", padding="15")
        info_frame.grid(row=4, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        info_text = (
            "O LocalAccountTokenFilterPolicy controla se contas locais podem ser usadas\n"
            "para autenticação remota. Quando definido como 0 (padrão), o Windows filtra\n"
            "tokens de contas locais, o que pode causar problemas de autenticação.\n\n"
            "Esta ferramenta define o valor como 1 para permitir autenticação completa, permitindo acessar outra máquina remota usando \\<ip>\c$."
        )
        info_label = ttk.Label(
            info_frame,
            text=info_text,
            font=("Segoe UI", 9),
            justify="left"
        )
        info_label.grid(row=0, column=0, sticky=tk.W)
        
        # Verifica status inicial em thread separada
        self._check_admin_status_async()
        
        return frame
    
    def _check_admin_status_async(self):
        """Verifica status de administrador em thread separada"""
        def check_in_thread():
            try:
                is_admin = self._is_admin()
                current_value = self._get_current_value()
                
                # Atualiza UI na thread principal
                if self.root_window:
                    self.root_window.after(0, lambda: self._update_status_ui(is_admin, current_value))
            except Exception as e:
                if self.root_window:
                    self.root_window.after(0, lambda: messagebox.showerror("Erro", f"Erro ao verificar status: {str(e)}"))
        
        thread = threading.Thread(target=check_in_thread, daemon=True)
        thread.start()
    
    def _is_admin(self):
        """Verifica se está executando como administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def _get_current_value(self):
        """Obtém o valor atual da chave de registro"""
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        value_name = "LocalAccountTokenFilterPolicy"
        
        try:
            # Tenta ler do registro
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                reg_path,
                0,
                winreg.KEY_READ
            )
            try:
                value, _ = winreg.QueryValueEx(key, value_name)
                return value
            except FileNotFoundError:
                return None
            finally:
                winreg.CloseKey(key)
        except FileNotFoundError:
            # Chave não existe
            return None
        except PermissionError:
            # Sem permissão para ler
            return "permission_error"
        except Exception:
            return None
    
    def _update_status_ui(self, is_admin, current_value):
        """Atualiza a interface com o status"""
        self.is_admin = is_admin
        self.current_value = current_value
        
        # Atualiza status de administrador
        if is_admin:
            self.admin_status_label.config(
                text="✓ Executando como Administrador",
                foreground="green"
            )
        else:
            self.admin_status_label.config(
                text="✗ Não está executando como Administrador",
                foreground="red"
            )
        
        # Atualiza status do valor
        if current_value == "permission_error":
            self.value_status_label.config(
                text="Valor atual: Erro de permissão (requer administrador)",
                foreground="orange"
            )
        elif current_value is None:
            self.value_status_label.config(
                text="Valor atual: Não definido (será criado como 1)",
                foreground="orange"
            )
        elif current_value == 1:
            self.value_status_label.config(
                text="Valor atual: 1 (correto)",
                foreground="green"
            )
        else:
            self.value_status_label.config(
                text=f"Valor atual: {current_value} (deve ser 1)",
                foreground="red"
            )
        
        # Habilita botão se for administrador
        if is_admin:
            self.fix_button.config(state="normal")
        else:
            self.fix_button.config(state="disabled")
    
    def _check_and_fix(self):
        """Verifica e corrige o valor da chave de registro"""
        if not self.is_admin:
            # Solicita elevação via PowerShell
            response = messagebox.askyesno(
                "Elevação de Privilégios Necessária",
                "Esta operação requer privilégios de administrador.\n\n"
                "Deseja executar a correção via PowerShell com elevação?\n\n"
                "Será solicitado o UAC (Controle de Conta de Usuário)."
            )
            if response:
                self._request_admin_elevation()
            return
        
        # Executa correção em thread separada
        def fix_in_thread():
            try:
                success = self._fix_registry_value()
                
                # Atualiza UI e mostra notificação
                if self.root_window:
                    if success:
                        self.root_window.after(0, lambda: self._show_success())
                    else:
                        self.root_window.after(0, lambda: self._show_error())
                    
                    # Atualiza status
                    self.root_window.after(0, lambda: self._check_admin_status_async())
            except Exception as e:
                if self.root_window:
                    self.root_window.after(0, lambda: messagebox.showerror("Erro", f"Erro ao corrigir: {str(e)}"))
        
        thread = threading.Thread(target=fix_in_thread, daemon=True)
        thread.start()
    
    def _fix_registry_value(self):
        """Corrige o valor da chave de registro"""
        reg_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
        value_name = "LocalAccountTokenFilterPolicy"
        
        try:
            # Abre ou cria a chave
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    reg_path,
                    0,
                    winreg.KEY_WRITE
                )
            except FileNotFoundError:
                # Cria a chave se não existir
                policies_key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies",
                    0,
                    winreg.KEY_WRITE
                )
                key = winreg.CreateKey(policies_key, "System")
                winreg.CloseKey(policies_key)
            
            try:
                # Define o valor como 1
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
                
                # Verifica se foi aplicado corretamente
                value, _ = winreg.QueryValueEx(key, value_name)
                return value == 1
            finally:
                winreg.CloseKey(key)
        except PermissionError:
            return False
        except Exception as e:
            print(f"Erro ao corrigir registro: {e}")
            return False
    
    def _request_admin_elevation(self):
        """Solicita elevação de privilégios via PowerShell"""
        try:
            # Cria um script PowerShell temporário para elevar e executar
            ps_script = f'''
$RegPath = "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
$ValueName = "LocalAccountTokenFilterPolicy"

# Garante que o caminho exista
if (-not (Test-Path $RegPath)) {{
    New-Item -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies" -Name "System" -Force | Out-Null
}}

# Define o valor como 1
New-ItemProperty -Path $RegPath -Name $ValueName -Value 1 -PropertyType DWord -Force | Out-Null

# Verifica se foi aplicado
$NewValue = (Get-ItemProperty -Path $RegPath -Name $ValueName -ErrorAction SilentlyContinue).$ValueName
if ($NewValue -eq 1) {{
    [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
    $notify = New-Object System.Windows.Forms.NotifyIcon
    $notify.Icon = [System.Drawing.SystemIcons]::Information
    $notify.Visible = $true
    $notify.ShowBalloonTip(5000, "Configuração aplicada", "LocalAccountTokenFilterPolicy foi corrigido para 1.", [System.Windows.Forms.ToolTipIcon]::Info)
    Start-Sleep -Seconds 6
    $notify.Dispose()
}} else {{
    [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
    $notify = New-Object System.Windows.Forms.NotifyIcon
    $notify.Icon = [System.Drawing.SystemIcons]::Error
    $notify.Visible = $true
    $notify.ShowBalloonTip(5000, "Erro", "Não foi possível aplicar LocalAccountTokenFilterPolicy!", [System.Windows.Forms.ToolTipIcon]::Error)
    Start-Sleep -Seconds 6
    $notify.Dispose()
}}
'''
            
            # Salva script temporário
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False, encoding='utf-8') as f:
                f.write(ps_script)
                ps_file = f.name
            
            try:
                # Executa PowerShell com elevação usando ShellExecute
                # Usa ctypes para chamar ShellExecute com RunAs
                shell32 = ctypes.windll.shell32
                result = shell32.ShellExecuteW(
                    None,
                    "runas",  # Solicita elevação
                    "powershell.exe",
                    f'-ExecutionPolicy Bypass -File "{ps_file}"',
                    None,
                    1  # SW_SHOWNORMAL
                )
                
                # Se o usuário cancelar o UAC, result será <= 32
                if result <= 32:
                    if result == 1223:  # ERROR_CANCELLED
                        messagebox.showinfo("Cancelado", "A operação foi cancelada pelo usuário.")
                    else:
                        messagebox.showerror("Erro", f"Falha ao solicitar elevação. Código: {result}")
            finally:
                # Remove arquivo temporário após um delay (para dar tempo de executar)
                def cleanup():
                    try:
                        import time
                        time.sleep(2)
                        if os.path.exists(ps_file):
                            os.unlink(ps_file)
                    except:
                        pass
                
                # Executa limpeza em thread separada
                cleanup_thread = threading.Thread(target=cleanup, daemon=True)
                cleanup_thread.start()
            
            # Atualiza status após um delay maior (para dar tempo do PowerShell executar)
            if self.root_window:
                self.root_window.after(3000, self._check_admin_status_async)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao solicitar elevação: {str(e)}")
    
    def _show_success(self):
        """Mostra notificação de sucesso"""
        self._show_toast("Configuração aplicada", "LocalAccountTokenFilterPolicy foi corrigido para 1.")
        messagebox.showinfo("Sucesso", "LocalAccountTokenFilterPolicy foi corrigido com sucesso!")
    
    def _show_error(self):
        """Mostra notificação de erro"""
        self._show_toast("Erro", "Não foi possível aplicar LocalAccountTokenFilterPolicy!")
        messagebox.showerror("Erro", "Não foi possível corrigir o LocalAccountTokenFilterPolicy.\nVerifique se você tem privilégios de administrador.")
    
    def _show_toast(self, title, message):
        """Mostra notificação toast usando PowerShell"""
        try:
            ps_command = f'''
[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.ShowBalloonTip(5000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 6
$notify.Dispose()
'''
            subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
        except Exception:
            # Se falhar, apenas ignora (a messagebox já foi mostrada)
            pass

