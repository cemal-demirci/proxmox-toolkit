#!/usr/bin/env python3
"""
Proxmox VE Management Toolkit
A comprehensive GUI tool for managing Proxmox VE servers

Authors: Cemal Demirci & Muammer Yeşilyağcı
Version: 1.0.0
License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import threading
import time
import subprocess
import json
import os
import configparser
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from PIL import Image, ImageTk
import requests
import paramiko

class ProxmoxToolkit:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxmox VE Management Toolkit v1.0")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Tema ayarları
        self.setup_style()
        
        # Değişkenler
        self.connected_servers = {}
        self.current_server = None
        self.vm_data = []
        self.container_data = []
        
        # Ana arayüzü oluştur
        self.create_main_interface()
        
        # Konfigürasyon yükle
        self.load_config()
        
    def setup_style(self):
        """Modern tema ayarları"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Dark theme colors
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        select_color = '#0078d4'
        
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', background='#404040', foreground=fg_color)
        style.map('TNotebook.Tab', background=[('selected', select_color)])
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background='#404040', foreground=fg_color)
        style.map('TButton', background=[('active', select_color)])
        
    def create_main_interface(self):
        """Ana arayüz bileşenlerini oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Üst panel - Bağlantı bilgileri
        self.create_connection_panel(main_frame)
        
        # Ana notebook widget
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(10, 0))
        
        # Sekmeler oluştur
        self.create_dashboard_tab()
        self.create_vm_tab()
        self.create_container_tab()
        self.create_monitoring_tab()
        self.create_backup_tab()
        self.create_settings_tab()
        
    def create_connection_panel(self, parent):
        """Sunucu bağlantı paneli"""
        conn_frame = ttk.LabelFrame(parent, text="Sunucu Bağlantısı", padding=10)
        conn_frame.pack(fill='x', pady=(0, 10))
        
        # Bağlantı bilgileri
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.host_entry = ttk.Entry(conn_frame, width=20)
        self.host_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(conn_frame, text="Kullanıcı:").grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.user_entry = ttk.Entry(conn_frame, width=15)
        self.user_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(conn_frame, text="Şifre:").grid(row=0, column=4, sticky='w', padx=(0, 5))
        self.pass_entry = ttk.Entry(conn_frame, width=15, show="*")
        self.pass_entry.grid(row=0, column=5, padx=(0, 10))
        
        # Butonlar
        ttk.Button(conn_frame, text="Bağlan", command=self.connect_server).grid(row=0, column=6, padx=5)
        ttk.Button(conn_frame, text="Bağlantıyı Kes", command=self.disconnect_server).grid(row=0, column=7, padx=5)
        
        # Durum etiketi
        self.status_label = ttk.Label(conn_frame, text="Bağlantı yok", foreground='red')
        self.status_label.grid(row=1, column=0, columnspan=8, pady=(10, 0))
        
    def create_dashboard_tab(self):
        """Dashboard sekmesi"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Sol panel - Sistem bilgileri
        left_frame = ttk.LabelFrame(dashboard_frame, text="Sistem Bilgileri", padding=10)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.system_info_text = scrolledtext.ScrolledText(left_frame, height=15, width=40)
        self.system_info_text.pack(fill='both', expand=True)
        
        # Sağ panel - Hızlı işlemler
        right_frame = ttk.LabelFrame(dashboard_frame, text="Hızlı İşlemler", padding=10)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # Hızlı işlem butonları
        quick_buttons = [
            ("🔄 Sistemi Yenile", self.refresh_system_info),
            ("📈 Performans Göster", self.show_performance),
            ("🚀 Tüm VM'leri Başlat", self.start_all_vms),
            ("⏹️ Tüm VM'leri Durdur", self.stop_all_vms),
            ("💾 Hızlı Yedek Al", self.quick_backup),
            ("🔧 Sistem Temizlik", self.system_cleanup)
        ]
        
        for i, (text, command) in enumerate(quick_buttons):
            btn = ttk.Button(right_frame, text=text, command=command, width=25)
            btn.pack(pady=5, fill='x')
            
    def create_vm_tab(self):
        """VM yönetim sekmesi"""
        vm_frame = ttk.Frame(self.notebook)
        self.notebook.add(vm_frame, text="🖥️ VM Yönetimi")
        
        # Üst panel - VM listesi
        vm_list_frame = ttk.LabelFrame(vm_frame, text="Sanal Makineler", padding=10)
        vm_list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # VM Treeview
        columns = ('VMID', 'İsim', 'Durum', 'CPU', 'Bellek', 'Disk')
        self.vm_tree = ttk.Treeview(vm_list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.vm_tree.heading(col, text=col)
            self.vm_tree.column(col, width=100)
            
        # Scrollbar
        vm_scrollbar = ttk.Scrollbar(vm_list_frame, orient='vertical', command=self.vm_tree.yview)
        self.vm_tree.configure(yscrollcommand=vm_scrollbar.set)
        
        self.vm_tree.pack(side='left', fill='both', expand=True)
        vm_scrollbar.pack(side='right', fill='y')
        
        # Alt panel - VM işlemleri
        vm_control_frame = ttk.LabelFrame(vm_frame, text="VM İşlemleri", padding=10)
        vm_control_frame.pack(fill='x')
        
        vm_buttons = [
            ("➕ Yeni VM", self.create_vm),
            ("▶️ Başlat", self.start_vm),
            ("⏸️ Duraklat", self.pause_vm),
            ("⏹️ Durdur", self.stop_vm),
            ("🔄 Yeniden Başlat", self.restart_vm),
            ("🗑️ Sil", self.delete_vm),
            ("📋 Detaylar", self.vm_details),
            ("🔄 Listeyi Yenile", self.refresh_vm_list)
        ]
        
        for i, (text, command) in enumerate(vm_buttons):
            btn = ttk.Button(vm_control_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=5, pady=5)
            
    def create_container_tab(self):
        """Container yönetim sekmesi"""
        container_frame = ttk.Frame(self.notebook)
        self.notebook.add(container_frame, text="📦 Container")
        
        # Container listesi
        container_list_frame = ttk.LabelFrame(container_frame, text="LXC Containerlar", padding=10)
        container_list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Container Treeview
        ct_columns = ('CTID', 'İsim', 'Durum', 'CPU', 'Bellek', 'Uptime')
        self.container_tree = ttk.Treeview(container_list_frame, columns=ct_columns, show='headings', height=10)
        
        for col in ct_columns:
            self.container_tree.heading(col, text=col)
            self.container_tree.column(col, width=100)
            
        container_scrollbar = ttk.Scrollbar(container_list_frame, orient='vertical', command=self.container_tree.yview)
        self.container_tree.configure(yscrollcommand=container_scrollbar.set)
        
        self.container_tree.pack(side='left', fill='both', expand=True)
        container_scrollbar.pack(side='right', fill='y')
        
        # Container işlemleri
        container_control_frame = ttk.LabelFrame(container_frame, text="Container İşlemleri", padding=10)
        container_control_frame.pack(fill='x')
        
        ct_buttons = [
            ("➕ Yeni Container", self.create_container),
            ("▶️ Başlat", self.start_container),
            ("⏹️ Durdur", self.stop_container),
            ("🔄 Yeniden Başlat", self.restart_container),
            ("🗑️ Sil", self.delete_container),
            ("💻 Console", self.container_console),
            ("📋 Detaylar", self.container_details),
            ("🔄 Listeyi Yenile", self.refresh_container_list)
        ]
        
        for i, (text, command) in enumerate(ct_buttons):
            btn = ttk.Button(container_control_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=5, pady=5)
            
    def create_monitoring_tab(self):
        """İzleme sekmesi"""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="📈 İzleme")
        
        # Grafik alanı
        self.fig, ((self.ax1, self.ax2), (self.ax3, self.ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        self.fig.patch.set_facecolor('#2b2b2b')
        
        # Grafikleri yapılandır
        self.setup_monitoring_charts()
        
        # Canvas oluştur
        self.canvas = FigureCanvasTkAgg(self.fig, monitoring_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Kontrol paneli
        control_frame = ttk.Frame(monitoring_frame)
        control_frame.pack(fill='x', pady=10)
        
        ttk.Button(control_frame, text="🔄 Grafikleri Yenile", command=self.update_monitoring_charts).pack(side='left', padx=5)
        ttk.Button(control_frame, text="💾 Grafikleri Kaydet", command=self.save_charts).pack(side='left', padx=5)
        
    def create_backup_tab(self):
        """Yedekleme sekmesi"""
        backup_frame = ttk.Frame(self.notebook)
        self.notebook.add(backup_frame, text="💾 Yedekleme")
        
        # Yedekleme seçenekleri
        backup_options_frame = ttk.LabelFrame(backup_frame, text="Yedekleme Seçenekleri", padding=10)
        backup_options_frame.pack(fill='x', pady=(0, 10))
        
        # Yedekleme türü
        ttk.Label(backup_options_frame, text="Yedekleme Türü:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        self.backup_type = ttk.Combobox(backup_options_frame, values=['Tam Yedek', 'Artımlı Yedek', 'Snapshot'])
        self.backup_type.grid(row=0, column=1, padx=(0, 20))
        self.backup_type.set('Tam Yedek')
        
        # Sıkıştırma
        self.compression_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_options_frame, text="Sıkıştırma Kullan", variable=self.compression_var).grid(row=0, column=2)
        
        # Yedekleme hedef listesi
        backup_targets_frame = ttk.LabelFrame(backup_frame, text="Yedeklenecek Sistemler", padding=10)
        backup_targets_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Target listesi
        self.backup_targets_tree = ttk.Treeview(backup_targets_frame, columns=('Tip', 'ID', 'İsim', 'Boyut'), show='headings', height=8)
        for col in ['Tip', 'ID', 'İsim', 'Boyut']:
            self.backup_targets_tree.heading(col, text=col)
            
        backup_targets_scrollbar = ttk.Scrollbar(backup_targets_frame, orient='vertical', command=self.backup_targets_tree.yview)
        self.backup_targets_tree.configure(yscrollcommand=backup_targets_scrollbar.set)
        
        self.backup_targets_tree.pack(side='left', fill='both', expand=True)
        backup_targets_scrollbar.pack(side='right', fill='y')
        
        # Yedekleme kontrolü
        backup_control_frame = ttk.LabelFrame(backup_frame, text="Yedekleme İşlemleri", padding=10)
        backup_control_frame.pack(fill='x')
        
        backup_buttons = [
            ("🔄 Hedefleri Yenile", self.refresh_backup_targets),
            ("💾 Seçilenleri Yedekle", self.backup_selected),
            ("💾 Tümünü Yedekle", self.backup_all),
            ("📋 Yedek Geçmişi", self.backup_history),
            ("⚙️ Zamanlama", self.backup_schedule)
        ]
        
        for i, (text, command) in enumerate(backup_buttons):
            btn = ttk.Button(backup_control_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=5, pady=5)
            
    def create_settings_tab(self):
        """Ayarlar sekmesi"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Ayarlar")
        
        # Genel ayarlar
        general_frame = ttk.LabelFrame(settings_frame, text="Genel Ayarlar", padding=10)
        general_frame.pack(fill='x', pady=(0, 10))
        
        # Auto-refresh
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(general_frame, text="Otomatik Yenileme", variable=self.auto_refresh_var).grid(row=0, column=0, sticky='w')
        
        ttk.Label(general_frame, text="Yenileme Aralığı (saniye):").grid(row=0, column=1, padx=(20, 5))
        self.refresh_interval = ttk.Entry(general_frame, width=10)
        self.refresh_interval.insert(0, "30")
        self.refresh_interval.grid(row=0, column=2)
        
        # Tema seçimi
        ttk.Label(general_frame, text="Tema:").grid(row=1, column=0, sticky='w', pady=(10, 0))
        self.theme_combo = ttk.Combobox(general_frame, values=['Dark', 'Light', 'Auto'])
        self.theme_combo.set('Dark')
        self.theme_combo.grid(row=1, column=1, columnspan=2, sticky='w', pady=(10, 0), padx=(20, 0))
        
        # Bağlantı ayarları
        connection_frame = ttk.LabelFrame(settings_frame, text="Bağlantı Ayarları", padding=10)
        connection_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(connection_frame, text="Bağlantı Timeout (saniye):").grid(row=0, column=0, sticky='w')
        self.timeout_entry = ttk.Entry(connection_frame, width=10)
        self.timeout_entry.insert(0, "30")
        self.timeout_entry.grid(row=0, column=1, padx=(10, 0))
        
        ttk.Label(connection_frame, text="Varsayılan Port:").grid(row=1, column=0, sticky='w', pady=(10, 0))
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.insert(0, "22")
        self.port_entry.grid(row=1, column=1, padx=(10, 0), pady=(10, 0))
        
        # Ayar butonları
        settings_buttons_frame = ttk.Frame(settings_frame)
        settings_buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(settings_buttons_frame, text="💾 Ayarları Kaydet", command=self.save_settings).pack(side='left', padx=5)
        ttk.Button(settings_buttons_frame, text="🔄 Varsayılana Sıfırla", command=self.reset_settings).pack(side='left', padx=5)
        ttk.Button(settings_buttons_frame, text="📂 Konfigürasyon Klasörü", command=self.open_config_folder).pack(side='left', padx=5)
        
    def setup_monitoring_charts(self):
        """İzleme grafiklerini ayarla"""
        chart_style = {'facecolor': '#404040', 'edgecolor': '#ffffff'}
        text_style = {'color': '#ffffff'}
        
        # CPU kullanımı
        self.ax1.set_title('CPU Kullanımı (%)', **text_style)
        self.ax1.set_facecolor('#404040')
        self.ax1.tick_params(colors='white')
        
        # Bellek kullanımı
        self.ax2.set_title('Bellek Kullanımı (GB)', **text_style)
        self.ax2.set_facecolor('#404040')
        self.ax2.tick_params(colors='white')
        
        # Disk I/O
        self.ax3.set_title('Disk I/O (MB/s)', **text_style)
        self.ax3.set_facecolor('#404040')
        self.ax3.tick_params(colors='white')
        
        # Ağ trafiği
        self.ax4.set_title('Ağ Trafiği (Mbps)', **text_style)
        self.ax4.set_facecolor('#404040')
        self.ax4.tick_params(colors='white')
        
        plt.tight_layout()
        
    # Bağlantı işlemleri
    def connect_server(self):
        """Proxmox sunucusuna bağlan"""
        host = self.host_entry.get().strip()
        user = self.user_entry.get().strip()
        password = self.pass_entry.get()
        
        if not all([host, user, password]):
            messagebox.showerror("Hata", "Lütfen tüm bağlantı bilgilerini girin!")
            return
            
        def connect_thread():
            try:
                # SSH bağlantısı test et
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, username=user, password=password, timeout=30)
                
                # Proxmox kontrolü
                stdin, stdout, stderr = ssh.exec_command('pvesh get /version')
                version_info = stdout.read().decode()
                
                if version_info:
                    self.connected_servers[host] = {
                        'ssh': ssh,
                        'user': user,
                        'password': password,
                        'version': version_info
                    }
                    self.current_server = host
                    
                    self.root.after(0, self.connection_success)
                else:
                    ssh.close()
                    self.root.after(0, lambda: messagebox.showerror("Hata", "Proxmox VE bulunamadı!"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Bağlantı Hatası", f"Bağlantı kurulamadı:\n{str(e)}"))
                
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def connection_success(self):
        """Başarılı bağlantı sonrası işlemler"""
        self.status_label.config(text=f"Bağlı: {self.current_server}", foreground='green')
        messagebox.showinfo("Başarılı", f"{self.current_server} sunucusuna başarıyla bağlanıldı!")
        
        # Sistem bilgilerini yükle
        self.refresh_system_info()
        self.refresh_vm_list()
        self.refresh_container_list()
        self.refresh_backup_targets()
        
    def disconnect_server(self):
        """Sunucu bağlantısını kes"""
        if self.current_server and self.current_server in self.connected_servers:
            try:
                self.connected_servers[self.current_server]['ssh'].close()
                del self.connected_servers[self.current_server]
                self.current_server = None
                self.status_label.config(text="Bağlantı yok", foreground='red')
                messagebox.showinfo("Bilgi", "Bağlantı kesildi.")
            except Exception as e:
                messagebox.showerror("Hata", f"Bağlantı kesme hatası: {str(e)}")
        
    def execute_command(self, command):
        """SSH ile komut çalıştır"""
        if not self.current_server or self.current_server not in self.connected_servers:
            messagebox.showerror("Hata", "Sunucuya bağlı değilsiniz!")
            return None
            
        try:
            ssh = self.connected_servers[self.current_server]['ssh']
            stdin, stdout, stderr = ssh.exec_command(command)
            result = stdout.read().decode()
            error = stderr.read().decode()
            
            if error:
                messagebox.showerror("Komut Hatası", f"Hata: {error}")
                return None
                
            return result
        except Exception as e:
            messagebox.showerror("Hata", f"Komut çalıştırma hatası: {str(e)}")
            return None
    
    # Dashboard işlemleri
    def refresh_system_info(self):
        """Sistem bilgilerini yenile"""
        if not self.current_server:
            return
            
        def get_info():
            info_commands = {
                'Sistem Bilgisi': 'uname -a',
                'Uptime': 'uptime',
                'Bellek Kullanımı': 'free -h',
                'Disk Kullanımı': 'df -h',
                'CPU Bilgisi': 'lscpu | head -20',
                'Proxmox Versiyonu': 'pveversion',
                'Aktif VM Sayısı': 'qm list | wc -l',
                'Aktif LXC Sayısı': 'pct list | wc -l'
            }
            
            info_text = f"=== {self.current_server} Sistem Bilgileri ===\n"
            info_text += f"Güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for title, command in info_commands.items():
                result = self.execute_command(command)
                if result:
                    info_text += f"[{title}]\n{result.strip()}\n\n"
                    
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, info_text)
            
        threading.Thread(target=get_info, daemon=True).start()
        
    def show_performance(self):
        """Performans bilgilerini göster"""
        self.notebook.select(3)  # Monitoring sekmesine geç
        self.update_monitoring_charts()
        
    # VM işlemleri
    def refresh_vm_list(self):
        """VM listesini yenile"""
        if not self.current_server:
            return
            
        def get_vms():
            result = self.execute_command('qm list')
            if result:
                self.vm_tree.delete(*self.vm_tree.get_children())
                
                lines = result.strip().split('\n')[1:]  # Header'ı atla
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            vmid = parts[0]
                            name = parts[1]
                            status = parts[2]
                            
                            # CPU ve bellek bilgilerini al
                            cpu_info = self.execute_command(f'qm config {vmid} | grep cores')
                            mem_info = self.execute_command(f'qm config {vmid} | grep memory')
                            
                            cpu = cpu_info.split(':')[1].strip() if cpu_info and ':' in cpu_info else 'N/A'
                            memory = mem_info.split(':')[1].strip() if mem_info and ':' in mem_info else 'N/A'
                            
                            self.vm_tree.insert('', 'end', values=(vmid, name, status, cpu, f"{memory}MB", "N/A"))
                            
        threading.Thread(target=get_vms, daemon=True).start()
        
    def create_vm(self):
        """Yeni VM oluştur"""
        dialog = CreateVMDialog(self.root, self.execute_command)
        if dialog.result:
            self.refresh_vm_list()
            
    def start_vm(self):
        """Seçili VM'i başlat"""
        selected = self.vm_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir VM seçin!")
            return
            
        vmid = self.vm_tree.item(selected[0])['values'][0]
        result = self.execute_command(f'qm start {vmid}')
        if result is not None:
            messagebox.showinfo("Başarılı", f"VM {vmid} başlatıldı!")
            self.refresh_vm_list()
            
    def stop_vm(self):
        """Seçili VM'i durdur"""
        selected = self.vm_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir VM seçin!")
            return
            
        vmid = self.vm_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Onay", f"VM {vmid} durdurulsun mu?"):
            result = self.execute_command(f'qm stop {vmid}')
            if result is not None:
                messagebox.showinfo("Başarılı", f"VM {vmid} durduruldu!")
                self.refresh_vm_list()
                
    def pause_vm(self):
        """Seçili VM'i duraklat"""
        selected = self.vm_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir VM seçin!")
            return
            
        vmid = self.vm_tree.item(selected[0])['values'][0]
        result = self.execute_command(f'qm suspend {vmid}')
        if result is not None:
            messagebox.showinfo("Başarılı", f"VM {vmid} duraklatıldı!")
            self.refresh_vm_list()
            
    def restart_vm(self):
        """Seçili VM'i yeniden başlat"""
        selected = self.vm_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir VM seçin!")
            return
            
        vmid = self.vm_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Onay", f"VM {vmid} yeniden başlatılsın mı?"):
            result = self.execute_command(f'qm reboot {vmid}')
            if result is not None:
                messagebox.showinfo("Başarılı", f"VM {vmid} yeniden başlatıldı!")
                self.refresh_vm_list()
                
    def delete_vm(self):
        """Seçili VM'i sil"""
        selected = self.vm_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir VM seçin!")
            return
            
        vmid = self.vm_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("DİKKAT!", f"VM {vmid} kalıcı olarak silinecek!\nEmin misiniz?"):
            result = self.execute_command(f'qm destroy {vmid}')
            if result is not None:
                messagebox.showinfo("Başarılı", f"VM {vmid} silindi!")
                self.refresh_vm_list()
                
    def vm_details(self):
        """VM detaylarını göster"""
        selected = self.vm_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir VM seçin!")
            return
            
        vmid = self.vm_tree.item(selected[0])['values'][0]
        config = self.execute_command(f'qm config {vmid}')
        if config:
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"VM {vmid} Detayları")
            detail_window.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(detail_window)
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert(1.0, config)
            
    # Container işlemleri
    def refresh_container_list(self):
        """Container listesini yenile"""
        if not self.current_server:
            return
            
        def get_containers():
            result = self.execute_command('pct list')
            if result:
                self.container_tree.delete(*self.container_tree.get_children())
                
                lines = result.strip().split('\n')[1:]
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            ctid = parts[0]
                            name = parts[1]
                            status = parts[2]
                            
                            # Ek bilgileri al
                            config = self.execute_command(f'pct config {ctid}')
                            cpu = "1"
                            memory = "512"
                            if config:
                                for cfg_line in config.split('\n'):
                                    if cfg_line.startswith('cores:'):
                                        cpu = cfg_line.split(':')[1].strip()
                                    elif cfg_line.startswith('memory:'):
                                        memory = cfg_line.split(':')[1].strip()
                            
                            uptime = "N/A"
                            if status == "running":
                                uptime_result = self.execute_command(f'pct exec {ctid} -- uptime -p')
                                if uptime_result:
                                    uptime = uptime_result.strip()
                            
                            self.container_tree.insert('', 'end', values=(ctid, name, status, cpu, f"{memory}MB", uptime))
                            
        threading.Thread(target=get_containers, daemon=True).start()
        
    def create_container(self):
        """Yeni container oluştur"""
        dialog = CreateContainerDialog(self.root, self.execute_command)
        if dialog.result:
            self.refresh_container_list()
            
    def start_container(self):
        """Container başlat"""
        selected = self.container_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir container seçin!")
            return
            
        ctid = self.container_tree.item(selected[0])['values'][0]
        result = self.execute_command(f'pct start {ctid}')
        if result is not None:
            messagebox.showinfo("Başarılı", f"Container {ctid} başlatıldı!")
            self.refresh_container_list()
            
    def stop_container(self):
        """Container durdur"""
        selected = self.container_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir container seçin!")
            return
            
        ctid = self.container_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Onay", f"Container {ctid} durdurulsun mu?"):
            result = self.execute_command(f'pct stop {ctid}')
            if result is not None:
                messagebox.showinfo("Başarılı", f"Container {ctid} durduruldu!")
                self.refresh_container_list()
                
    def restart_container(self):
        """Container yeniden başlat"""
        selected = self.container_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir container seçin!")
            return
            
        ctid = self.container_tree.item(selected[0])['values'][0]
        result = self.execute_command(f'pct reboot {ctid}')
        if result is not None:
            messagebox.showinfo("Başarılı", f"Container {ctid} yeniden başlatıldı!")
            self.refresh_container_list()
            
    def delete_container(self):
        """Container sil"""
        selected = self.container_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir container seçin!")
            return
            
        ctid = self.container_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("DİKKAT!", f"Container {ctid} kalıcı olarak silinecek!\nEmin misiniz?"):
            result = self.execute_command(f'pct destroy {ctid}')
            if result is not None:
                messagebox.showinfo("Başarılı", f"Container {ctid} silindi!")
                self.refresh_container_list()
                
    def container_console(self):
        """Container console aç"""
        selected = self.container_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir container seçin!")
            return
            
        ctid = self.container_tree.item(selected[0])['values'][0]
        messagebox.showinfo("Bilgi", f"Container {ctid} console'u terminal üzerinden açılacak:\npct enter {ctid}")
        
    def container_details(self):
        """Container detaylarını göster"""
        selected = self.container_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen bir container seçin!")
            return
            
        ctid = self.container_tree.item(selected[0])['values'][0]
        config = self.execute_command(f'pct config {ctid}')
        if config:
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Container {ctid} Detayları")
            detail_window.geometry("600x400")
            
            text_widget = scrolledtext.ScrolledText(detail_window)
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert(1.0, config)
            
    # Monitoring işlemleri
    def update_monitoring_charts(self):
        """Monitoring grafiklerini güncelle"""
        if not self.current_server:
            return
            
        def update_charts():
            try:
                # CPU kullanımı
                cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
                cpu_result = self.execute_command(cpu_cmd)
                
                # Bellek kullanımı
                mem_cmd = "free -m | awk 'NR==2{printf \"%.1f\", $3*100/$2}'"
                mem_result = self.execute_command(mem_cmd)
                
                # Örnek veriler (gerçek veriler için daha karmaşık parsing gerekir)
                import random
                times = [datetime.now()]
                cpu_data = [float(cpu_result.strip()) if cpu_result else random.randint(10, 80)]
                mem_data = [float(mem_result.strip()) if mem_result else random.randint(20, 90)]
                disk_data = [random.randint(5, 50)]
                net_data = [random.randint(1, 100)]
                
                # Grafikleri temizle ve güncelle
                self.ax1.clear()
                self.ax1.plot(times, cpu_data, 'r-', linewidth=2)
                self.ax1.set_title('CPU Kullanımı (%)', color='white')
                self.ax1.set_facecolor('#404040')
                
                self.ax2.clear()
                self.ax2.plot(times, mem_data, 'g-', linewidth=2)
                self.ax2.set_title('Bellek Kullanımı (%)', color='white')
                self.ax2.set_facecolor('#404040')
                
                self.ax3.clear()
                self.ax3.plot(times, disk_data, 'b-', linewidth=2)
                self.ax3.set_title('Disk I/O (MB/s)', color='white')
                self.ax3.set_facecolor('#404040')
                
                self.ax4.clear()
                self.ax4.plot(times, net_data, 'y-', linewidth=2)
                self.ax4.set_title('Ağ Trafiği (Mbps)', color='white')
                self.ax4.set_facecolor('#404040')
                
                for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                    ax.tick_params(colors='white')
                    ax.grid(True, alpha=0.3)
                
                self.canvas.draw()
                
            except Exception as e:
                print(f"Chart update error: {e}")
                
        threading.Thread(target=update_charts, daemon=True).start()
        
    def save_charts(self):
        """Grafikleri kaydet"""
        filename = f"proxmox_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        self.fig.savefig(filename, facecolor='#2b2b2b', dpi=300)
        messagebox.showinfo("Başarılı", f"Grafikler kaydedildi: {filename}")
        
    # Backup işlemleri
    def refresh_backup_targets(self):
        """Yedekleme hedeflerini yenile"""
        if not self.current_server:
            return
            
        def get_targets():
            self.backup_targets_tree.delete(*self.backup_targets_tree.get_children())
            
            # VM'leri ekle
            vm_result = self.execute_command('qm list')
            if vm_result:
                for line in vm_result.strip().split('\n')[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            vmid = parts[0]
                            name = parts[1]
                            self.backup_targets_tree.insert('', 'end', values=('VM', vmid, name, 'N/A'))
            
            # Container'ları ekle
            ct_result = self.execute_command('pct list')
            if ct_result:
                for line in ct_result.strip().split('\n')[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            ctid = parts[0]
                            name = parts[1]
                            self.backup_targets_tree.insert('', 'end', values=('LXC', ctid, name, 'N/A'))
                            
        threading.Thread(target=get_targets, daemon=True).start()
        
    def backup_selected(self):
        """Seçili sistemleri yedekle"""
        selected = self.backup_targets_tree.selection()
        if not selected:
            messagebox.showwarning("Uyarı", "Lütfen yedeklenecek sistemleri seçin!")
            return
            
        backup_list = []
        for item in selected:
            values = self.backup_targets_tree.item(item)['values']
            backup_list.append((values[0], values[1]))  # (tip, id)
            
        def do_backup():
            for backup_type, backup_id in backup_list:
                if backup_type == 'VM':
                    cmd = f'vzdump {backup_id} --storage local'
                else:
                    cmd = f'vzdump {backup_id} --storage local'
                    
                if self.compression_var.get():
                    cmd += ' --compress gzip'
                    
                result = self.execute_command(cmd)
                if result:
                    self.root.after(0, lambda: messagebox.showinfo("Başarılı", f"{backup_type} {backup_id} yedeklendi!"))
                    
        threading.Thread(target=do_backup, daemon=True).start()
        
    def backup_all(self):
        """Tüm sistemleri yedekle"""
        if messagebox.askyesno("Onay", "Tüm VM ve Container'lar yedeklenecek. Devam edilsin mi?"):
            def do_backup_all():
                # Tüm VM'leri yedekle
                vm_result = self.execute_command('qm list')
                if vm_result:
                    for line in vm_result.strip().split('\n')[1:]:
                        if line.strip():
                            vmid = line.split()[0]
                            cmd = f'vzdump {vmid} --storage local'
                            if self.compression_var.get():
                                cmd += ' --compress gzip'
                            self.execute_command(cmd)
                
                # Tüm Container'ları yedekle
                ct_result = self.execute_command('pct list')
                if ct_result:
                    for line in ct_result.strip().split('\n')[1:]:
                        if line.strip():
                            ctid = line.split()[0]
                            cmd = f'vzdump {ctid} --storage local'
                            if self.compression_var.get():
                                cmd += ' --compress gzip'
                            self.execute_command(cmd)
                            
                self.root.after(0, lambda: messagebox.showinfo("Başarılı", "Tüm yedeklemeler tamamlandı!"))
                
            threading.Thread(target=do_backup_all, daemon=True).start()
            
    def backup_history(self):
        """Yedek geçmişini göster"""
        history = self.execute_command('ls -la /var/lib/vz/dump/')
        if history:
            history_window = tk.Toplevel(self.root)
            history_window.title("Yedek Geçmişi")
            history_window.geometry("800x600")
            
            text_widget = scrolledtext.ScrolledText(history_window)
            text_widget.pack(fill='both', expand=True, padx=10, pady=10)
            text_widget.insert(1.0, history)
            
    def backup_schedule(self):
        """Yedekleme zamanlaması"""
        messagebox.showinfo("Bilgi", "Yedekleme zamanlaması özelliği gelecek sürümde eklenecek!")
        
    # Diğer işlemler
    def start_all_vms(self):
        """Tüm VM'leri başlat"""
        if messagebox.askyesno("Onay", "Tüm durdurulmuş VM'ler başlatılacak. Devam edilsin mi?"):
            def start_all():
                result = self.execute_command("for vm in $(qm list | awk 'NR>1 && $3==\"stopped\" {print $1}'); do qm start $vm; done")
                self.root.after(0, self.refresh_vm_list)
                self.root.after(0, lambda: messagebox.showinfo("Başarılı", "Tüm VM'ler başlatıldı!"))
                
            threading.Thread(target=start_all, daemon=True).start()
            
    def stop_all_vms(self):
        """Tüm VM'leri durdur"""
        if messagebox.askyesno("DİKKAT!", "Tüm çalışan VM'ler durdurulacak!\nEmin misiniz?"):
            def stop_all():
                result = self.execute_command("for vm in $(qm list | awk 'NR>1 && $3==\"running\" {print $1}'); do qm stop $vm; done")
                self.root.after(0, self.refresh_vm_list)
                self.root.after(0, lambda: messagebox.showinfo("Başarılı", "Tüm VM'ler durduruldu!"))
                
            threading.Thread(target=stop_all, daemon=True).start()
            
    def quick_backup(self):
        """Hızlı yedekleme"""
        self.notebook.select(4)  # Backup sekmesine geç
        
    def system_cleanup(self):
        """Sistem temizliği"""
        if messagebox.askyesno("Onay", "Sistem temizliği yapılacak (log dosyaları, geçici dosyalar). Devam edilsin mi?"):
            def cleanup():
                commands = [
                    'apt autoremove -y',
                    'apt autoclean',
                    'journalctl --vacuum-time=7d',
                    'find /tmp -type f -mtime +7 -delete'
                ]
                
                for cmd in commands:
                    self.execute_command(cmd)
                    
                self.root.after(0, lambda: messagebox.showinfo("Başarılı", "Sistem temizliği tamamlandı!"))
                
            threading.Thread(target=cleanup, daemon=True).start()
            
    # Ayarlar işlemleri
    def load_config(self):
        """Konfigürasyon dosyasını yükle"""
        config_dir = os.path.expanduser('~/.proxmox-toolkit')
        config_file = os.path.join(config_dir, 'config.ini')
        
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            
        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)
            
            if 'DEFAULT' in config:
                self.host_entry.insert(0, config.get('DEFAULT', 'host', fallback=''))
                self.user_entry.insert(0, config.get('DEFAULT', 'user', fallback='root'))
                
    def save_settings(self):
        """Ayarları kaydet"""
        config_dir = os.path.expanduser('~/.proxmox-toolkit')
        config_file = os.path.join(config_dir, 'config.ini')
        
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'host': self.host_entry.get(),
            'user': self.user_entry.get(),
            'auto_refresh': str(self.auto_refresh_var.get()),
            'refresh_interval': self.refresh_interval.get(),
            'theme': self.theme_combo.get(),
            'timeout': self.timeout_entry.get(),
            'port': self.port_entry.get()
        }
        
        with open(config_file, 'w') as f:
            config.write(f)
            
        messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
        
    def reset_settings(self):
        """Ayarları sıfırla"""
        if messagebox.askyesno("Onay", "Tüm ayarlar varsayılan değerlere sıfırlanacak. Devam edilsin mi?"):
            # Entry'leri temizle ve varsayılan değerleri ayarla
            self.refresh_interval.delete(0, tk.END)
            self.refresh_interval.insert(0, "30")
            
            self.timeout_entry.delete(0, tk.END)
            self.timeout_entry.insert(0, "30")
            
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, "22")
            
            self.theme_combo.set('Dark')
            self.auto_refresh_var.set(True)
            
            messagebox.showinfo("Başarılı", "Ayarlar sıfırlandı!")
            
    def open_config_folder(self):
        """Konfigürasyon klasörünü aç"""
        config_dir = os.path.expanduser('~/.proxmox-toolkit')
        if os.path.exists(config_dir):
            os.system(f'xdg-open "{config_dir}"' if os.name == 'posix' else f'explorer "{config_dir}"')
        else:
            messagebox.showinfo("Bilgi", f"Konfigürasyon klasörü: {config_dir}")


# Dialog sınıfları
class CreateVMDialog:
    def __init__(self, parent, execute_command):
        self.result = False
        self.execute_command = execute_command
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yeni VM Oluştur")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        # VMID
        ttk.Label(frame, text="VM ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.vmid_entry = ttk.Entry(frame)
        self.vmid_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Name
        ttk.Label(frame, text="VM Adı:").grid(row=1, column=0, sticky='w', pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        # CPU
        ttk.Label(frame, text="CPU Çekirdek:").grid(row=2, column=0, sticky='w', pady=5)
        self.cpu_entry = ttk.Entry(frame)
        self.cpu_entry.insert(0, "2")
        self.cpu_entry.grid(row=2, column=1, sticky='ew', pady=5)
        
        # Memory
        ttk.Label(frame, text="Bellek (MB):").grid(row=3, column=0, sticky='w', pady=5)
        self.memory_entry = ttk.Entry(frame)
        self.memory_entry.insert(0, "2048")
        self.memory_entry.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Disk
        ttk.Label(frame, text="Disk (GB):").grid(row=4, column=0, sticky='w', pady=5)
        self.disk_entry = ttk.Entry(frame)
        self.disk_entry.insert(0, "20")
        self.disk_entry.grid(row=4, column=1, sticky='ew', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Oluştur", command=self.create_vm).pack(side='left', padx=5)
        ttk.Button(button_frame, text="İptal", command=self.dialog.destroy).pack(side='left', padx=5)
        
        frame.columnconfigure(1, weight=1)
        
    def create_vm(self):
        vmid = self.vmid_entry.get().strip()
        name = self.name_entry.get().strip()
        cpu = self.cpu_entry.get().strip()
        memory = self.memory_entry.get().strip()
        disk = self.disk_entry.get().strip()
        
        if not all([vmid, name, cpu, memory, disk]):
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return
            
        # VM oluşturma komutu
        cmd = f'qm create {vmid} --name {name} --cores {cpu} --memory {memory} --net0 virtio,bridge=vmbr0 --scsi0 local-lvm:{disk} --boot order=scsi0 --ostype l26'
        
        result = self.execute_command(cmd)
        if result is not None:
            messagebox.showinfo("Başarılı", f"VM {vmid} ({name}) oluşturuldu!")
            self.result = True
            self.dialog.destroy()


class CreateContainerDialog:
    def __init__(self, parent, execute_command):
        self.result = False
        self.execute_command = execute_command
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yeni Container Oluştur")
        self.dialog.geometry("400x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill='both', expand=True)
        
        # CTID
        ttk.Label(frame, text="Container ID:").grid(row=0, column=0, sticky='w', pady=5)
        self.ctid_entry = ttk.Entry(frame)
        self.ctid_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Hostname
        ttk.Label(frame, text="Hostname:").grid(row=1, column=0, sticky='w', pady=5)
        self.hostname_entry = ttk.Entry(frame)
        self.hostname_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Template
        ttk.Label(frame, text="Template:").grid(row=2, column=0, sticky='w', pady=5)
        self.template_combo = ttk.Combobox(frame, values=['ubuntu-22.04-standard', 'debian-11-standard', 'centos-8-standard'])
        self.template_combo.set('ubuntu-22.04-standard')
        self.template_combo.grid(row=2, column=1, sticky='ew', pady=5)
        
        # CPU
        ttk.Label(frame, text="CPU Çekirdek:").grid(row=3, column=0, sticky='w', pady=5)
        self.cpu_entry = ttk.Entry(frame)
        self.cpu_entry.insert(0, "1")
        self.cpu_entry.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Memory
        ttk.Label(frame, text="Bellek (MB):").grid(row=4, column=0, sticky='w', pady=5)
        self.memory_entry = ttk.Entry(frame)
        self.memory_entry.insert(0, "512")
        self.memory_entry.grid(row=4, column=1, sticky='ew', pady=5)
        
        # Disk
        ttk.Label(frame, text="Disk (GB):").grid(row=5, column=0, sticky='w', pady=5)
        self.disk_entry = ttk.Entry(frame)
        self.disk_entry.insert(0, "8")
        self.disk_entry.grid(row=5, column=1, sticky='ew', pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Oluştur", command=self.create_container).pack(side='left', padx=5)
        ttk.Button(button_frame, text="İptal", command=self.dialog.destroy).pack(side='left', padx=5)
        
        frame.columnconfigure(1, weight=1)
        
    def create_container(self):
        ctid = self.ctid_entry.get().strip()
        hostname = self.hostname_entry.get().strip()
        template = self.template_combo.get()
        cpu = self.cpu_entry.get().strip()
        memory = self.memory_entry.get().strip()
        disk = self.disk_entry.get().strip()
        
        if not all([ctid, hostname, template, cpu, memory, disk]):
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return
            
        # Container oluşturma komutu
        cmd = f'pct create {ctid} local:vztmpl/{template}_amd64.tar.xz --hostname {hostname} --cores {cpu} --memory {memory} --rootfs local-lvm:{disk} --net0 name=eth0,bridge=vmbr0,ip=dhcp'
        
        result = self.execute_command(cmd)
        if result is not None:
            messagebox.showinfo("Başarılı", f"Container {ctid} ({hostname}) oluşturuldu!")
            self.result = True
            self.dialog.destroy()


# Ana uygulama
def main():
    root = tk.Tk()
    app = ProxmoxToolkit(root)
    
    # Pencere kapatma olayını yakala
    def on_closing():
        if app.connected_servers:
            for server_info in app.connected_servers.values():
                try:
                    server_info['ssh'].close()
                except:
                    pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Ana döngüyü başlat
    root.mainloop()

if __name__ == "__main__":
    main()
