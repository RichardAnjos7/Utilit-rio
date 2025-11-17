"""
Módulo de Diagnóstico de Rede
Ferramenta para detectar e exibir informações de rede automaticamente
Similar ao LDWin
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import socket
import platform
import re
import threading
import time


class NetworkDiagnosticModule:
    """Módulo para diagnóstico de rede"""
    
    def __init__(self):
        self.network_info = {}
        self.root_window = None
        self.auto_refresh = False
        self.refresh_thread = None
        self.collect_thread = None
        self.is_collecting = False
        self.loading_label = None
    
    def get_display_name(self):
        """Retorna o nome de exibição do módulo"""
        return "Diagnóstico de Rede"
    
    def create_ui(self, parent):
        """Cria a interface do módulo"""
        self.root_window = parent.winfo_toplevel()
        frame = ttk.Frame(parent, padding="20")
        
        # Título
        title_label = ttk.Label(
            frame,
            text="Diagnóstico de Rede",
            font=("Segoe UI", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Descrição
        desc_label = ttk.Label(
            frame,
            text="Detecção automática de informações de rede",
            font=("Segoe UI", 9),
            wraplength=600
        )
        desc_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Frame de controles
        controls_frame = ttk.Frame(frame)
        controls_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15), sticky=(tk.W, tk.E))
        
        # Botão para atualizar
        refresh_button = ttk.Button(
            controls_frame,
            text="Atualizar Informações",
            command=lambda: self._refresh_network_info(),
            width=25
        )
        refresh_button.grid(row=0, column=0, padx=(0, 10))
        
        # Checkbox para atualização automática
        self.auto_refresh_var = tk.BooleanVar(value=False)
        auto_refresh_check = ttk.Checkbutton(
            controls_frame,
            text="Atualização Automática (5s)",
            variable=self.auto_refresh_var,
            command=self._toggle_auto_refresh
        )
        auto_refresh_check.grid(row=0, column=1, padx=(10, 0))
        
        # Frame principal de informações
        main_info_frame = ttk.Frame(frame)
        main_info_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_info_frame.columnconfigure(0, weight=1)
        main_info_frame.columnconfigure(1, weight=1)
        main_info_frame.columnconfigure(2, weight=1)
        
        # Cria um notebook para melhor organização (opcional - pode usar frames lado a lado)
        # Por enquanto, mantém frames lado a lado
        
        # Frame esquerdo - Informações básicas
        left_frame = ttk.LabelFrame(main_info_frame, text="Informações de Conexão", padding="15")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Frame central - Informações detalhadas
        right_frame = ttk.LabelFrame(main_info_frame, text="Informações Detalhadas", padding="15")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        
        # Frame direito - Informações do Switch
        switch_frame = ttk.LabelFrame(main_info_frame, text="Informações do Switch", padding="15")
        switch_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Configura grid weights
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=1)
        main_info_frame.rowconfigure(0, weight=1)
        
        # Armazena referências aos frames para atualização
        self.left_frame = left_frame
        self.right_frame = right_frame
        self.switch_frame = switch_frame
        
        # Mostra indicador de carregamento
        self._show_loading()
        
        # Carrega informações iniciais em thread separada
        self._refresh_network_info_async()
        
        return frame
    
    def _show_loading(self):
        """Mostra indicador de carregamento"""
        # Limpa frames
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        for widget in self.switch_frame.winfo_children():
            widget.destroy()
        
        # Mostra mensagem de carregamento
        self.loading_label = ttk.Label(
            self.left_frame,
            text="Carregando informações de rede...",
            font=("Segoe UI", 10),
            foreground="blue"
        )
        self.loading_label.grid(row=0, column=0, pady=50)
    
    def _toggle_auto_refresh(self):
        """Ativa/desativa atualização automática"""
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
    
    def _start_auto_refresh(self):
        """Inicia thread de atualização automática"""
        if self.refresh_thread and self.refresh_thread.is_alive():
            return
        
        def refresh_loop():
            while self.auto_refresh:
                time.sleep(5)
                if self.auto_refresh:
                    self.root_window.after(0, self._refresh_network_info)
        
        self.refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.refresh_thread.start()
    
    def _stop_auto_refresh(self):
        """Para atualização automática"""
        self.auto_refresh = False
    
    def _refresh_network_info_async(self):
        """Inicia coleta de informações de rede em thread separada"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        
        def collect_in_thread():
            try:
                # Coleta informações
                network_info = self._collect_network_info()
                
                # Debug: verifica se coletou algo
                adapters = network_info.get('adapters', [])
                if not adapters:
                    # Tenta método alternativo
                    alt_info = self._collect_network_info_alternative()
                    if alt_info.get('adapters'):
                        network_info = alt_info
                    else:
                        # Se ainda não tem adaptadores, pelo menos mostra informações básicas
                        if not network_info.get('hostname'):
                            network_info['hostname'] = socket.gethostname()
                        if not network_info.get('fqdn'):
                            network_info['fqdn'] = socket.getfqdn()
                
                # Atualiza na thread principal
                if self.root_window:
                    self.network_info = network_info
                    self.root_window.after(0, self._update_ui)
                    
            except Exception as e:
                import traceback
                error_msg = f"Erro ao coletar informações de rede: {str(e)}\n\n{traceback.format_exc()}"
                if self.root_window:
                    self.root_window.after(0, lambda: messagebox.showerror("Erro", error_msg))
            finally:
                self.is_collecting = False
        
        self.collect_thread = threading.Thread(target=collect_in_thread, daemon=True)
        self.collect_thread.start()
    
    def _refresh_network_info(self):
        """Atualiza as informações de rede (versão síncrona para auto-refresh)"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        
        def collect_in_thread():
            try:
                # Coleta informações
                network_info = self._collect_network_info()
                
                # Debug: verifica se coletou algo
                adapters = network_info.get('adapters', [])
                if not adapters:
                    # Tenta método alternativo
                    alt_info = self._collect_network_info_alternative()
                    if alt_info.get('adapters'):
                        network_info = alt_info
                    else:
                        # Se ainda não tem adaptadores, pelo menos mostra informações básicas
                        if not network_info.get('hostname'):
                            network_info['hostname'] = socket.gethostname()
                        if not network_info.get('fqdn'):
                            network_info['fqdn'] = socket.getfqdn()
                
                # Atualiza na thread principal
                if self.root_window:
                    self.network_info = network_info
                    self.root_window.after(0, self._update_ui)
                    
            except Exception as e:
                import traceback
                error_msg = f"Erro ao coletar informações de rede: {str(e)}\n\n{traceback.format_exc()}"
                if self.root_window:
                    self.root_window.after(0, lambda: messagebox.showerror("Erro", error_msg))
            finally:
                self.is_collecting = False
        
        thread = threading.Thread(target=collect_in_thread, daemon=True)
        thread.start()
    
    def _collect_network_info(self):
        """Coleta todas as informações de rede"""
        info = {
            'interfaces': [],
            'default_gateway': None,
            'dns_servers': [],
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn()
        }
        
        # Obtém informações via netsh e ipconfig
        try:
            # Obtém informações detalhadas via netsh
            netsh_info = self._get_netsh_info()
            info.update(netsh_info)
            
            # Obtém informações via ipconfig
            ipconfig_info = self._get_ipconfig_info()
            if ipconfig_info:
                info.update(ipconfig_info)
            
            # Obtém informações via WMI (se disponível)
            wmi_info = self._get_wmi_info()
            if wmi_info:
                info['wmi_info'] = wmi_info
            
            # Obtém gateway padrão via route
            gateway = self._get_default_gateway()
            if gateway:
                info['default_gateway'] = gateway
            
            # Obtém DNS via ipconfig
            dns_servers = self._get_dns_servers()
            if dns_servers:
                info['dns_servers'] = dns_servers
            
            # Obtém informações do switch
            switch_info = self._get_switch_info()
            if switch_info:
                info['switch_info'] = switch_info
            
        except Exception as e:
            print(f"Erro ao coletar informações: {e}")
        
        return info
    
    def _get_netsh_info(self):
        """Obtém informações via netsh"""
        info = {}
        try:
            # Obtém interfaces de rede
            result = subprocess.run(
                ["netsh", "interface", "show", "interface"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                interfaces = []
                lines = result.stdout.strip().split('\n')
                for line in lines[3:]:  # Pula cabeçalho
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 4:
                            state = parts[0]
                            interface_type = parts[1]
                            name = ' '.join(parts[3:])
                            interfaces.append({
                                'name': name,
                                'state': state,
                                'type': interface_type
                            })
                info['interfaces'] = interfaces
        except Exception:
            pass
        
        return info
    
    def _get_ipconfig_info(self):
        """Obtém informações via ipconfig /all"""
        info = {}
        try:
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse das informações - método mais robusto
                current_adapter = None
                adapters = []
                
                for line in output.split('\n'):
                    line = line.rstrip()
                    
                    # Detecta novo adaptador
                    # Formato típico: "Adaptador de Ethernet Ethernet:" ou "Ethernet adapter Ethernet:"
                    # ou simplesmente "Ethernet:"
                    if line:
                        # Verifica se é início de adaptador (não começa com espaço/tab e tem ':')
                        is_adapter_start = (
                            ':' in line and 
                            not line[0].isspace() and
                            not line.startswith('   ') and
                            ('adaptador' in line.lower() or 'adapter' in line.lower() or 
                             len(line.split(':')) == 2 and len(line.split(':')[0].strip()) < 50)
                        )
                        
                        if is_adapter_start:
                            # É um novo adaptador
                            if current_adapter:
                                adapters.append(current_adapter)
                            
                            # Extrai nome do adaptador
                            if ':' in line:
                                # Remove "Adaptador de" ou "adapter" e pega o nome
                                adapter_name = line.split(':')[0].strip()
                                # Limpa prefixos comuns
                                for prefix in ['Adaptador de', 'adapter', 'Adapter']:
                                    if prefix.lower() in adapter_name.lower():
                                        parts = adapter_name.split()
                                        # Pega a última parte como nome
                                        adapter_name = parts[-1] if len(parts) > 1 else adapter_name
                                        break
                            else:
                                adapter_name = line.strip()
                            
                            current_adapter = {
                                'name': adapter_name,
                                'description': '',
                                'physical_address': '',
                                'dhcp_enabled': False,
                                'ipv4_address': '',
                                'ipv4_subnet': '',
                                'ipv6_address': '',
                                'default_gateway': '',
                                'dns_servers': []
                            }
                            continue
                    
                    # Se não estamos em um adaptador, pula
                    if not current_adapter:
                        continue
                    
                    # Linhas que fazem parte do adaptador atual (começam com espaço ou têm ':')
                    if line and (line[0].isspace() or '\t' in line or ':' in line):
                        # Descrição
                        if 'Descrição' in line or 'Description' in line:
                            match = re.search(r':\s*(.+)', line)
                            if match:
                                current_adapter['description'] = match.group(1).strip()
                        
                        # Endereço físico
                        if 'Endereço Físico' in line or 'Physical Address' in line:
                            match = re.search(r':\s*([0-9A-Fa-f\-:]+)', line)
                            if match:
                                current_adapter['physical_address'] = match.group(1).strip()
                        
                        # DHCP
                        if 'DHCP' in line and ('Habilitado' in line or 'Enabled' in line):
                            current_adapter['dhcp_enabled'] = 'Sim' in line or 'Yes' in line or 'Habilitado' in line
                        
                        # IPv4
                        if 'Endereço IPv4' in line or 'IPv4 Address' in line:
                            match = re.search(r':\s*([0-9.]+)', line)
                            if match:
                                ipv4 = match.group(1).strip()
                                if ipv4 and ipv4 != '0.0.0.0':
                                    current_adapter['ipv4_address'] = ipv4
                        
                        # IPv6
                        if 'Endereço IPv6' in line or 'IPv6 Address' in line:
                            match = re.search(r':\s*([0-9a-fA-F:]+)', line)
                            if match:
                                ipv6 = match.group(1).strip()
                                # Remove sufixos como (Preferred) ou (Temporary)
                                ipv6 = re.sub(r'\s*\([^)]+\)', '', ipv6)
                                if ipv6 and not ipv6.startswith('fe80') and ipv6 != '::1':  # Ignora link-local e loopback
                                    current_adapter['ipv6_address'] = ipv6
                        
                        # Máscara de sub-rede
                        if 'Máscara de Sub-rede' in line or 'Subnet Mask' in line:
                            match = re.search(r':\s*([0-9.]+)', line)
                            if match:
                                current_adapter['ipv4_subnet'] = match.group(1).strip()
                        
                        # Gateway padrão
                        if 'Gateway Padrão' in line or 'Default Gateway' in line:
                            match = re.search(r':\s*([0-9.:a-fA-F]+)', line)
                            if match:
                                gateway = match.group(1).strip()
                                if gateway and gateway != '' and gateway.lower() != 'none':
                                    current_adapter['default_gateway'] = gateway
                        
                        # DNS
                        if 'Servidores DNS' in line or 'DNS Servers' in line:
                            match = re.search(r':\s*(.+)', line)
                            if match:
                                dns = match.group(1).strip()
                                if dns and dns.lower() != 'none':
                                    current_adapter['dns_servers'].append(dns)
                
                # Adiciona o último adaptador
                if current_adapter:
                    adapters.append(current_adapter)
                
                info['adapters'] = adapters
                
        except Exception as e:
            print(f"Erro ao obter ipconfig: {e}")
            import traceback
            traceback.print_exc()
        
        return info
    
    def _get_wmi_info(self):
        """Obtém informações detalhadas via WMI"""
        info = {}
        try:
            import wmi
            c = wmi.WMI()
            
            # Obtém adaptadores de rede
            adapters = []
            for adapter in c.Win32_NetworkAdapter(PhysicalAdapter=True):
                adapter_info = {
                    'name': adapter.Name or '',
                    'description': adapter.Description or '',
                    'manufacturer': adapter.Manufacturer or '',
                    'mac_address': adapter.MACAddress or '',
                    'speed': adapter.Speed if adapter.Speed else 0,
                    'status': adapter.NetConnectionStatus or 0,
                    'connection_id': adapter.NetConnectionID or ''
                }
                adapters.append(adapter_info)
            
            info['adapters'] = adapters
            
            # Obtém configurações de IP
            ip_configs = []
            for config in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                ip_info = {
                    'description': config.Description or '',
                    'ip_addresses': config.IPAddress or [],
                    'subnet_masks': config.IPSubnet or [],
                    'default_gateway': config.DefaultIPGateway[0] if config.DefaultIPGateway else '',
                    'dhcp_enabled': config.DHCPEnabled if config.DHCPEnabled else False,
                    'dns_servers': config.DNSServerSearchOrder or [],
                    'mac_address': config.MACAddress or ''
                }
                ip_configs.append(ip_info)
            
            info['ip_configs'] = ip_configs
            
        except ImportError:
            # WMI não disponível
            pass
        except Exception as e:
            print(f"Erro ao obter WMI: {e}")
        
        return info if info else None
    
    def _get_default_gateway(self):
        """Obtém gateway padrão via route"""
        try:
            result = subprocess.run(
                ["route", "print", "0.0.0.0"],
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '0.0.0.0' in line and 'On-link' not in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            gateway = parts[2]
                            if re.match(r'^\d+\.\d+\.\d+\.\d+$', gateway):
                                return gateway
        except Exception:
            pass
        
        return None
    
    def _get_dns_servers(self):
        """Obtém servidores DNS"""
        dns_servers = []
        try:
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            if result.returncode == 0:
                output = result.stdout
                for line in output.split('\n'):
                    if 'Servidores DNS' in line or 'DNS Servers' in line:
                        match = re.search(r':\s*([0-9.]+)', line)
                        if match:
                            dns = match.group(1).strip()
                            if dns and dns not in dns_servers:
                                dns_servers.append(dns)
        except Exception:
            pass
        
        return dns_servers
    
    def _get_switch_info(self):
        """Obtém informações do switch conectado"""
        switch_info = {
            'switch_name': 'N/A',
            'port_id': 'N/A',
            'vlan_id': 'N/A',
            'switch_ip': 'N/A',
            'switch_model': 'N/A',
            'port_duplex': 'N/A',
            'vtp_domain': 'N/A',
            'status': 'N/A'
        }
        
        try:
            # Tenta obter via LLDP (Link Layer Discovery Protocol)
            lldp_info = self._get_lldp_info()
            if lldp_info:
                switch_info.update(lldp_info)
            
            # Tenta obter via SNMP (se disponível)
            snmp_info = self._get_snmp_info()
            if snmp_info:
                # Atualiza apenas campos que não foram preenchidos
                for key, value in snmp_info.items():
                    if switch_info.get(key) == 'N/A' and value != 'N/A':
                        switch_info[key] = value
            
            # Tenta obter via ARP e outras fontes
            arp_info = self._get_switch_info_from_arp()
            if arp_info:
                for key, value in arp_info.items():
                    if switch_info.get(key) == 'N/A' and value != 'N/A':
                        switch_info[key] = value
            
            # Tenta obter via WMI (informações de porta)
            wmi_port_info = self._get_wmi_port_info()
            if wmi_port_info:
                for key, value in wmi_port_info.items():
                    if switch_info.get(key) == 'N/A' and value != 'N/A':
                        switch_info[key] = value
            
        except Exception as e:
            print(f"Erro ao obter informações do switch: {e}")
        
        return switch_info
    
    def _get_lldp_info(self):
        """Obtém informações via LLDP/CDP"""
        info = {}
        try:
            # Tenta via PowerShell Get-NetAdapterStatistics ou netsh
            # LLDP geralmente requer ferramentas específicas ou SNMP
            # Por enquanto, retorna vazio - pode ser implementado com ferramentas externas
            pass
        except Exception:
            pass
        return info
    
    def _get_snmp_info(self):
        """Obtém informações do switch via SNMP"""
        info = {}
        try:
            # SNMP requer biblioteca pysnmp ou snmpwalk instalado
            # Tenta usar snmpwalk se disponível
            result = subprocess.run(
                ["snmpwalk", "-v", "2c", "-c", "public", "localhost", "1.3.6.1.2.1.1"],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            # Se snmpwalk estiver disponível, pode processar a saída
        except FileNotFoundError:
            # snmpwalk não está instalado
            pass
        except Exception:
            pass
        return info
    
    def _get_switch_info_from_arp(self):
        """Tenta obter informações do switch via ARP e outras fontes"""
        info = {}
        try:
            # Obtém gateway que pode ser o switch
            gateway = self.network_info.get('default_gateway')
            if gateway and gateway != 'N/A' and gateway != 'None':
                info['switch_ip'] = gateway
                # Tenta resolver nome
                try:
                    hostname = socket.gethostbyaddr(gateway)[0]
                    info['switch_name'] = hostname
                    # Se conseguiu resolver, assume que está conectado
                    info['status'] = "Conectado"
                except Exception:
                    # Mesmo sem resolver nome, se tem gateway, está conectado
                    info['status'] = "Conectado"
            
            # Tenta obter informações via nbtstat para descobrir nome do dispositivo
            if gateway and gateway != 'N/A' and gateway != 'None':
                try:
                    result = subprocess.run(
                        ["nbtstat", "-A", gateway],
                        capture_output=True,
                        text=True,
                        timeout=3,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    if result.returncode == 0:
                        # Procura por nome na saída do nbtstat
                        for line in result.stdout.split('\n'):
                            if 'UNIQUE' in line or 'GROUP' in line:
                                parts = line.split()
                                if len(parts) > 0:
                                    name = parts[0].strip()
                                    if name and name != '<00>':
                                        info['switch_name'] = name
                                        break
                except Exception:
                    pass
        except Exception:
            pass
        return info
    
    def _get_wmi_port_info(self):
        """Obtém informações de porta via WMI"""
        info = {}
        try:
            import wmi
            c = wmi.WMI()
            
            # Obtém informações de adaptadores de rede
            for adapter in c.Win32_NetworkAdapter(PhysicalAdapter=True):
                if adapter.NetConnectionStatus == 2:  # Conectado
                    # Pode obter informações de velocidade/duplex
                    speed = adapter.Speed if adapter.Speed else 0
                    if speed:
                        if speed >= 1000000000:  # 1 Gbps
                            info['port_duplex'] = "Full Duplex (1 Gbps)"
                        elif speed >= 100000000:  # 100 Mbps
                            info['port_duplex'] = "Full Duplex (100 Mbps)"
                        elif speed >= 10000000:  # 10 Mbps
                            info['port_duplex'] = "Full Duplex (10 Mbps)"
                        else:
                            info['port_duplex'] = f"Full Duplex ({speed} bps)"
                    
                    # Tenta obter informações adicionais
                    if adapter.NetConnectionID:
                        # Pode usar o nome da conexão como identificador de porta
                        info['port_id'] = adapter.NetConnectionID
                    break
        except ImportError:
            pass
        except Exception:
            pass
        return info
    
    def _collect_network_info_alternative(self):
        """Método alternativo para coletar informações de rede usando socket"""
        info = {
            'interfaces': [],
            'default_gateway': None,
            'dns_servers': [],
            'hostname': socket.gethostname(),
            'fqdn': socket.getfqdn(),
            'adapters': []
        }
        
        try:
            # Obtém IP local via socket
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
                if local_ip and local_ip != '127.0.0.1':
                    adapter = {
                        'name': 'Interface Principal',
                        'description': 'Detectado via socket',
                        'physical_address': 'N/A',
                        'dhcp_enabled': False,
                        'ipv4_address': local_ip,
                        'ipv4_subnet': '255.255.255.0',  # Padrão
                        'ipv6_address': '',
                        'default_gateway': None,
                        'dns_servers': []
                    }
                    info['adapters'] = [adapter]
            except Exception:
                pass
        except Exception as e:
            print(f"Erro no método alternativo: {e}")
        
        return info
    
    def _display_switch_info(self):
        """Exibe informações do switch no frame dedicado"""
        switch_info = self.network_info.get('switch_info', {})
        
        if not switch_info:
            ttk.Label(
                self.switch_frame,
                text="Informações do switch não disponíveis",
                font=("Segoe UI", 9),
                foreground="gray"
            ).grid(row=0, column=0, columnspan=2, pady=20)
            return
        
        row = 0
        
        # Nome do Switch
        switch_name = switch_info.get('switch_name', 'N/A')
        ttk.Label(self.switch_frame, text="Nome do Switch:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.switch_frame, text=switch_name, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Identificador de Porta
        port_id = switch_info.get('port_id', 'N/A')
        ttk.Label(self.switch_frame, text="Identificador de Porta:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.switch_frame, text=port_id, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Identificador de VLAN
        vlan_id = switch_info.get('vlan_id', 'N/A')
        ttk.Label(self.switch_frame, text="Identificador de VLAN:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.switch_frame, text=vlan_id, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Endereço IP Switch
        switch_ip = switch_info.get('switch_ip', 'N/A')
        ttk.Label(self.switch_frame, text="Endereço IP Switch:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.switch_frame, text=switch_ip, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Modelo do Switch
        switch_model = switch_info.get('switch_model', 'N/A')
        ttk.Label(self.switch_frame, text="Modelo do Switch:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.switch_frame, text=switch_model, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Port Duplex
        port_duplex = switch_info.get('port_duplex', 'N/A')
        ttk.Label(self.switch_frame, text="Port Duplex:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.switch_frame, text=port_duplex, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # VTP Mgmt Domain
        vtp_domain = switch_info.get('vtp_domain', 'N/A')
        ttk.Label(self.switch_frame, text="VTP Mgmt Domain:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.switch_frame, text=vtp_domain, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Status
        status = switch_info.get('status', 'N/A')
        status_color = "green" if status and status.lower() not in ['n/a', 'desconectado'] else "gray"
        ttk.Label(self.switch_frame, text="Status:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        status_label = ttk.Label(self.switch_frame, text=status, font=("Segoe UI", 9), foreground=status_color)
        status_label.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
    
    def _update_ui(self):
        """Atualiza a interface com as informações coletadas"""
        # Remove indicador de carregamento se existir
        if self.loading_label:
            self.loading_label.destroy()
            self.loading_label = None
        
        # Limpa frames
        for widget in self.left_frame.winfo_children():
            widget.destroy()
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        for widget in self.switch_frame.winfo_children():
            widget.destroy()
        
        # Obtém adaptadores ativos
        adapters = self.network_info.get('adapters', [])
        wmi_info = self.network_info.get('wmi_info', {})
        wmi_adapters = wmi_info.get('adapters', []) if wmi_info else []
        wmi_ip_configs = wmi_info.get('ip_configs', []) if wmi_info else []
        
        # Encontra adaptador Ethernet ativo (prioriza adaptadores com IP)
        active_adapter = None
        ethernet_adapters = []
        
        for adapter in adapters:
            adapter_name = adapter.get('name', '').lower()
            adapter_desc = adapter.get('description', '').lower()
            
            # Verifica se é adaptador Ethernet (não Wi-Fi, não loopback, não virtual)
            is_ethernet = (
                'ethernet' in adapter_name or 'ethernet' in adapter_desc or
                'lan' in adapter_name or 'local area' in adapter_desc
            ) and not any(x in adapter_name or x in adapter_desc for x in [
                'wireless', 'wi-fi', 'wifi', 'bluetooth', 'loopback', 'virtual', 'vmware', 'virtualbox'
            ])
            
            if is_ethernet:
                ethernet_adapters.append(adapter)
                if adapter.get('ipv4_address') or adapter.get('ipv6_address'):
                    active_adapter = adapter
                    break
        
        # Se não encontrou Ethernet com IP, usa o primeiro Ethernet
        if not active_adapter and ethernet_adapters:
            active_adapter = ethernet_adapters[0]
        
        # Se ainda não encontrou, usa qualquer adaptador com IP
        if not active_adapter:
            for adapter in adapters:
                if adapter.get('ipv4_address') or adapter.get('ipv6_address'):
                    active_adapter = adapter
                    break
        
        # Se ainda não encontrou, usa qualquer adaptador (mesmo sem IP)
        if not active_adapter and adapters:
            # Prioriza adaptadores que não são loopback
            for adapter in adapters:
                adapter_name = adapter.get('name', '').lower()
                if 'loopback' not in adapter_name and 'lo' not in adapter_name:
                    active_adapter = adapter
                    break
            
            # Último recurso: primeiro adaptador disponível
            if not active_adapter:
                active_adapter = adapters[0]
        
        row = 0
        
        # === FRAME ESQUERDO - Informações Básicas ===
        
        # Se não há adaptadores, mostra informações básicas disponíveis
        if not adapters and not active_adapter:
            # Mostra pelo menos hostname e informações básicas
            hostname = self.network_info.get('hostname', 'N/A')
            fqdn = self.network_info.get('fqdn', 'N/A')
            
            ttk.Label(
                self.left_frame,
                text="Nenhuma interface de rede ativa detectada",
                font=("Segoe UI", 10, "bold"),
                foreground="orange"
            ).grid(row=row, column=0, columnspan=2, pady=20)
            row += 1
            
            ttk.Label(self.left_frame, text="Hostname:", font=("Segoe UI", 9, "bold")).grid(
                row=row, column=0, sticky=tk.W, pady=5
            )
            ttk.Label(self.left_frame, text=hostname, font=("Segoe UI", 9)).grid(
                row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
            )
            row += 1
            
            ttk.Label(self.left_frame, text="FQDN:", font=("Segoe UI", 9, "bold")).grid(
                row=row, column=0, sticky=tk.W, pady=5
            )
            ttk.Label(self.left_frame, text=fqdn, font=("Segoe UI", 9)).grid(
                row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
            )
            row += 1
            
            ttk.Label(
                self.left_frame,
                text="Tente executar 'ipconfig /all' no prompt de comando para verificar",
                font=("Segoe UI", 8),
                foreground="gray"
            ).grid(row=row, column=0, columnspan=2, pady=20)
            return
        
        # Status da conexão
        status_text = "Desconectado"
        status_color = "red"
        if active_adapter:
            if active_adapter.get('ipv4_address') or active_adapter.get('ipv6_address'):
                status_text = "Conectado"
                status_color = "green"
        
        ttk.Label(self.left_frame, text="Status da Conexão:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        status_label = ttk.Label(
            self.left_frame,
            text=status_text,
            font=("Segoe UI", 9, "bold"),
            foreground=status_color
        )
        status_label.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # Nome da interface
        interface_name = active_adapter.get('name', 'N/A') if active_adapter else 'N/A'
        ttk.Label(self.left_frame, text="Interface de Rede:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.left_frame, text=interface_name, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Descrição/Fabricante
        description = active_adapter.get('description', 'N/A') if active_adapter else 'N/A'
        if wmi_adapters and active_adapter:
            for wmi_adapter in wmi_adapters:
                if wmi_adapter.get('name') == interface_name or wmi_adapter.get('connection_id') == interface_name:
                    if wmi_adapter.get('manufacturer'):
                        description = f"{description} ({wmi_adapter.get('manufacturer')})"
                    break
        
        ttk.Label(self.left_frame, text="Descrição/Fabricante:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        desc_label = ttk.Label(self.left_frame, text=description, font=("Segoe UI", 9), wraplength=250)
        desc_label.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        row += 1
        
        # Endereço MAC
        mac_address = active_adapter.get('physical_address', 'N/A') if active_adapter else 'N/A'
        ttk.Label(self.left_frame, text="Endereço MAC:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.left_frame, text=mac_address, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Velocidade do link
        speed_text = "N/A"
        if wmi_adapters and active_adapter:
            for wmi_adapter in wmi_adapters:
                if wmi_adapter.get('name') == interface_name or wmi_adapter.get('connection_id') == interface_name:
                    speed = wmi_adapter.get('speed', 0)
                    if speed:
                        if speed >= 1000000000:  # 1 Gbps
                            speed_text = f"{speed / 1000000000:.0f} Gbps"
                        elif speed >= 1000000:  # 1 Mbps
                            speed_text = f"{speed / 1000000:.0f} Mbps"
                        else:
                            speed_text = f"{speed} bps"
                    break
        
        ttk.Label(self.left_frame, text="Velocidade do Link:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.left_frame, text=speed_text, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Separador
        ttk.Separator(self.left_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )
        row += 1
        
        # Endereço IPv4
        ipv4 = active_adapter.get('ipv4_address', 'N/A') if active_adapter else 'N/A'
        ttk.Label(self.left_frame, text="Endereço IPv4:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.left_frame, text=ipv4, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Máscara de sub-rede
        subnet = active_adapter.get('ipv4_subnet', 'N/A') if active_adapter else 'N/A'
        ttk.Label(self.left_frame, text="Máscara de Sub-rede:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.left_frame, text=subnet, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Endereço IPv6 (se disponível)
        ipv6 = active_adapter.get('ipv6_address', '') if active_adapter else ''
        if not ipv6 and wmi_ip_configs:
            for ip_config in wmi_ip_configs:
                if ip_config.get('mac_address') == mac_address.replace('-', ':') or \
                   ip_config.get('description') == description:
                    ip_addresses = ip_config.get('ip_addresses', [])
                    for addr in ip_addresses:
                        if ':' in addr and not addr.startswith('fe80'):
                            ipv6 = addr
                            break
                    if ipv6:
                        break
        
        if ipv6:
            ttk.Label(self.left_frame, text="Endereço IPv6:", font=("Segoe UI", 9, "bold")).grid(
                row=row, column=0, sticky=tk.W, pady=5
            )
            ipv6_label = ttk.Label(self.left_frame, text=ipv6, font=("Segoe UI", 9), wraplength=250)
            ipv6_label.grid(row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
            row += 1
        
        # Gateway padrão
        gateway = active_adapter.get('default_gateway', '') if active_adapter else ''
        if not gateway:
            gateway = self.network_info.get('default_gateway', 'N/A')
        if not gateway:
            gateway = 'N/A'
        
        ttk.Label(self.left_frame, text="Gateway Padrão:", font=("Segoe UI", 9, "bold")).grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.left_frame, text=gateway, font=("Segoe UI", 9)).grid(
            row=row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # === FRAME DIREITO - Informações Detalhadas ===
        
        right_row = 0
        
        # Hostname
        hostname = self.network_info.get('hostname', 'N/A')
        ttk.Label(self.right_frame, text="Hostname:", font=("Segoe UI", 9, "bold")).grid(
            row=right_row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.right_frame, text=hostname, font=("Segoe UI", 9)).grid(
            row=right_row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        right_row += 1
        
        # FQDN
        fqdn = self.network_info.get('fqdn', 'N/A')
        ttk.Label(self.right_frame, text="FQDN:", font=("Segoe UI", 9, "bold")).grid(
            row=right_row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.right_frame, text=fqdn, font=("Segoe UI", 9)).grid(
            row=right_row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        right_row += 1
        
        # DHCP
        dhcp_enabled = active_adapter.get('dhcp_enabled', False) if active_adapter else False
        dhcp_text = "Sim" if dhcp_enabled else "Não"
        ttk.Label(self.right_frame, text="DHCP Habilitado:", font=("Segoe UI", 9, "bold")).grid(
            row=right_row, column=0, sticky=tk.W, pady=5
        )
        ttk.Label(self.right_frame, text=dhcp_text, font=("Segoe UI", 9)).grid(
            row=right_row, column=1, sticky=tk.W, padx=(10, 0), pady=5
        )
        right_row += 1
        
        # Separador
        ttk.Separator(self.right_frame, orient='horizontal').grid(
            row=right_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )
        right_row += 1
        
        # Servidores DNS
        dns_servers = active_adapter.get('dns_servers', []) if active_adapter else []
        if not dns_servers:
            dns_servers = self.network_info.get('dns_servers', [])
        
        ttk.Label(self.right_frame, text="Servidores DNS:", font=("Segoe UI", 9, "bold")).grid(
            row=right_row, column=0, sticky=tk.W, pady=5
        )
        if dns_servers:
            dns_text = "\n".join(dns_servers) if isinstance(dns_servers, list) else str(dns_servers)
            dns_label = ttk.Label(self.right_frame, text=dns_text, font=("Segoe UI", 9))
            dns_label.grid(row=right_row, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        else:
            ttk.Label(self.right_frame, text="N/A", font=("Segoe UI", 9)).grid(
                row=right_row, column=1, sticky=tk.W, padx=(10, 0), pady=5
            )
        right_row += 1
        
        # Separador
        ttk.Separator(self.right_frame, orient='horizontal').grid(
            row=right_row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )
        right_row += 1
        
        # Informações adicionais
        ttk.Label(self.right_frame, text="Informações Adicionais:", font=("Segoe UI", 9, "bold")).grid(
            row=right_row, column=0, columnspan=2, sticky=tk.W, pady=5
        )
        right_row += 1
        
        # Teste de conectividade básico (executado em thread separada para não travar)
        ttk.Label(self.right_frame, text="Conectividade:", font=("Segoe UI", 9)).grid(
            row=right_row, column=0, sticky=tk.W, pady=2
        )
        connectivity_label = ttk.Label(self.right_frame, text="Testando...", font=("Segoe UI", 9))
        connectivity_label.grid(row=right_row, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        right_row += 1
        
        # Executa teste em thread separada
        def test_and_update_connectivity():
            try:
                # Testa conectividade com gateway
                if gateway and gateway != 'N/A':
                    result = subprocess.run(
                        ["ping", "-n", "1", "-w", "1000", gateway],
                        capture_output=True,
                        timeout=2,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    )
                    if result.returncode == 0:
                        result_text = "Gateway acessível"
                    else:
                        result_text = "Gateway não acessível"
                else:
                    result_text = "Gateway não configurado"
            except Exception:
                result_text = "Não testado"
            
            # Atualiza label na thread principal
            if self.root_window:
                # Usa uma função lambda com valor capturado corretamente
                def update_label(text=result_text):
                    connectivity_label.config(text=text)
                self.root_window.after(0, update_label)
        
        # Inicia teste em background
        threading.Thread(target=test_and_update_connectivity, daemon=True).start()
        
        # Status da interface (se disponível via WMI)
        if wmi_adapters and active_adapter:
            for wmi_adapter in wmi_adapters:
                if wmi_adapter.get('name') == interface_name or wmi_adapter.get('connection_id') == interface_name:
                    status_code = wmi_adapter.get('status', 0)
                    status_map = {
                        0: "Desconectado",
                        1: "Conectando",
                        2: "Conectado",
                        3: "Desconectando",
                        4: "Hardware não presente",
                        5: "Hardware desabilitado",
                        6: "Hardware com falha",
                        7: "Mídia desconectada",
                        8: "Autenticando",
                        9: "Autenticação bem-sucedida",
                        10: "Autenticação falhou",
                        11: "Endereço IP inválido",
                        12: "Credenciais necessárias"
                    }
                    interface_status = status_map.get(status_code, f"Status {status_code}")
                    
                    ttk.Label(self.right_frame, text="Status da Interface:", font=("Segoe UI", 9)).grid(
                        row=right_row, column=0, sticky=tk.W, pady=2
                    )
                    ttk.Label(self.right_frame, text=interface_status, font=("Segoe UI", 9)).grid(
                        row=right_row, column=1, sticky=tk.W, padx=(10, 0), pady=2
                    )
                    break
        
        # === FRAME DO SWITCH - Informações do Switch ===
        self._display_switch_info()

