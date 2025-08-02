#!/usr/bin/env python3
"""
Proxmox VE Advanced CLI Management Toolkit
Enhanced command-line interface with custom branding and advanced features

Authors: Cemal & Muammer Yeşilyağcı
Version: 2.0.0
License: MIT
"""

import subprocess
import sys
import time
import json
import os
import threading
from datetime import datetime, timedelta
import re
import shutil

class ProxmoxAdvancedCLI:
    def __init__(self):
        self.version = "2.0.0"
        self.brand_name = "CEMAL DEMIRCI"
        self.check_proxmox()
        self.apply_customizations()
        
    def check_proxmox(self):
        """Proxmox VE kurulu mu kontrol et"""
        try:
            result = subprocess.run(['pvesh', 'get', '/version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("❌ Hata: Proxmox VE bulunamadı!")
                print("Bu script Proxmox VE sunucusunda çalıştırılmalıdır.")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Proxmox kontrolü başarısız: {e}")
            sys.exit(1)
    
    def apply_customizations(self):
        """Proxmox özelleştirmelerini uygula"""
        print("🎨 Proxmox özelleştirmeleri uygulanıyor...")
        
        # Branding uygula
        self.apply_branding()
        
        # No-subscription hatalarını kaldır
        self.remove_subscription_warnings()
        
        # Free repository'lere geç
        self.setup_free_repositories()
        
        print("✅ Özelleştirmeler uygulandı!")
        time.sleep(2)
    
    def apply_branding(self):
        """Proxmox arayüzüne custom branding ekle"""
        try:
            # Proxmox web arayüzü dosyalarının yolu
            pve_www_path = "/usr/share/pve-manager"
            
            # CSS dosyasını özelleştir
            css_file = f"{pve_www_path}/css/ext6-pve.css"
            if os.path.exists(css_file):
                # Backup al
                subprocess.run(f"cp {css_file} {css_file}.backup", shell=True)
                
                # Custom CSS ekle
                custom_css = f"""
/* Custom Branding by {self.brand_name} */
.x-panel-header-title:before {{
    content: "🚀 {self.brand_name} - ";
    color: #0066cc;
    font-weight: bold;
}}

.x-title-text:after {{
    content: " | Powered by {self.brand_name}";
    font-size: 12px;
    color: #666;
}}
"""
                
                with open(css_file, 'a') as f:
                    f.write(custom_css)
                    
                print(f"✅ Branding '{self.brand_name}' eklendi")
            
            # Proxmox servislerini yeniden başlat
            subprocess.run("systemctl restart pveproxy", shell=True)
            
        except Exception as e:
            print(f"⚠️ Branding uygulanamadı: {e}")
    
    def remove_subscription_warnings(self):
        """No-subscription uyarılarını kaldır"""
        try:
            # pve-enterprise repository'yi devre dışı bırak
            enterprise_list = "/etc/apt/sources.list.d/pve-enterprise.list"
            if os.path.exists(enterprise_list):
                subprocess.run(f"mv {enterprise_list} {enterprise_list}.disabled", shell=True)
                print("✅ Enterprise repository devre dışı bırakıldı")
                
        except Exception as e:
            print(f"⚠️ Subscription uyarıları kaldırılamadı: {e}")
    
    def setup_free_repositories(self):
        """Free repository'leri ayarla"""
        try:
            # No-subscription repository ekle
            no_sub_list = "/etc/apt/sources.list.d/pve-no-subscription.list"
            
            with open(no_sub_list, 'w') as f:
                f.write(f"# Free Proxmox VE repository\n")
                f.write(f"deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription\n")
            
            print("✅ Free repository'ler ayarlandı")
            
            # APT güncelle
            subprocess.run("apt update", shell=True, capture_output=True)
            
        except Exception as e:
            print(f"⚠️ Repository ayarlanamadı: {e}")
    
    def run_command(self, command):
        """Sistem komutu çalıştır"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, 
                                  text=True, timeout=30)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", "Komut zaman aşımına uğradı", 1
        except Exception as e:
            return "", str(e), 1
    
    def show_banner(self):
        """Enhanced banner göster"""
        print("\n" + "="*70)
        print(f"🚀 {self.brand_name} - PROXMOX ADVANCED MANAGEMENT TOOLKIT")
        print(f"📌 Version: {self.version}")
        print("👥 Authors: Cemal & Muammer Yeşilyağcı")
        print("🎯 Enhanced Features: Monitoring, Snapshots, Templates, Automation")
        print("="*70)
        print(f"⏰ Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
    
    def show_ascii_chart(self, title, value, max_val=100, width=40):
        """ASCII grafik göster"""
        if max_val == 0:
            percentage = 0
        else:
            percentage = min(value / max_val * 100, 100)
        
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        
        color = "🟢" if percentage < 70 else "🟡" if percentage < 90 else "🔴"
        print(f"{title:<15} [{bar}] {percentage:5.1f}% {color}")
    
    def show_realtime_monitoring(self):
        """Gerçek zamanlı sistem izleme"""
        print("\n📊 GERÇEK ZAMANLI İZLEME")
        print("Çıkmak için Ctrl+C basın...")
        print("-" * 60)
        
        try:
            while True:
                os.system('clear')
                print(f"📊 {self.brand_name} - Sistem İzleme | {datetime.now().strftime('%H:%M:%S')}")
                print("-" * 60)
                
                # CPU kullanımı
                cpu_cmd = "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1"
                cpu_result, _, _ = self.run_command(cpu_cmd)
                cpu_usage = float(cpu_result) if cpu_result.replace('.', '').isdigit() else 0
                self.show_ascii_chart("CPU", cpu_usage, 100)
                
                # Memory kullanımı
                mem_cmd = "free | awk 'NR==2{printf \"%.1f\", $3*100/$2}'"
                mem_result, _, _ = self.run_command(mem_cmd)
                mem_usage = float(mem_result) if mem_result.replace('.', '').isdigit() else 0
                self.show_ascii_chart("Memory", mem_usage, 100)
                
                # Disk kullanımı
                disk_cmd = "df / | awk 'NR==2{print $5}' | cut -d'%' -f1"
                disk_result, _, _ = self.run_command(disk_cmd)
                disk_usage = float(disk_result) if disk_result.isdigit() else 0
                self.show_ascii_chart("Disk", disk_usage, 100)
                
                print(f"\n🖥️  Running VMs: {self.get_running_count('vm')}")
                print(f"📦 Running LXCs: {self.get_running_count('lxc')}")
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            print("\n\n✅ İzleme durduruldu.")
    
    def get_running_count(self, vm_type):
        """Çalışan VM/LXC sayısını al"""
        if vm_type == 'vm':
            cmd = "qm list | grep -c running"
        else:
            cmd = "pct list | grep -c running"
        
        result, _, _ = self.run_command(cmd)
        return result if result.isdigit() else '0'
    
    def show_system_info(self):
        """Sistem bilgilerini göster"""
        print("\n📊 SİSTEM BİLGİLERİ")
        print("-" * 40)
        
        # Proxmox version
        stdout, _, _ = self.run_command("pveversion")
        print(f"📦 Proxmox Version: {stdout.split()[0] if stdout else 'N/A'}")
        
        # Uptime
        stdout, _, _ = self.run_command("uptime -p")
        print(f"⏱️  Uptime: {stdout if stdout else 'N/A'}")
        
        # Memory
        stdout, _, _ = self.run_command("free -h | awk 'NR==2{printf \"%.1f%% (%s/%s)\", $3*100/$2, $3, $2}'")
        print(f"💾 Memory: {stdout if stdout else 'N/A'}")
        
        # Disk usage
        stdout, _, _ = self.run_command("df -h / | awk 'NR==2{printf \"%s (%s available)\", $5, $4}'")
        print(f"💿 Disk Usage: {stdout if stdout else 'N/A'}")
        
        # Load average
        stdout, _, _ = self.run_command("uptime | awk -F'load average:' '{print $2}'")
        print(f"📈 Load Average: {stdout if stdout else 'N/A'}")
        
        # VM count
        stdout, _, _ = self.run_command("qm list | wc -l")
        vm_count = int(stdout) - 1 if stdout.isdigit() else 0
        print(f"🖥️  Total VMs: {vm_count}")
        
        # Container count
        stdout, _, _ = self.run_command("pct list | wc -l")
        ct_count = int(stdout) - 1 if stdout.isdigit() else 0
        print(f"📦 Total Containers: {ct_count}")
        
        # Running VMs
        stdout, _, _ = self.run_command("qm list | grep -c running")
        running_vms = stdout if stdout else '0'
        print(f"▶️  Running VMs: {running_vms}")
        
        # Running Containers
        stdout, _, _ = self.run_command("pct list | grep -c running")
        running_cts = stdout if stdout else '0'
        print(f"▶️  Running Containers: {running_cts}")
        print()
    
    def list_vms(self):
        """VM listesini göster"""
        print("\n🖥️  SANAL MAKİNELER")
        print("-" * 60)
        
        stdout, stderr, code = self.run_command("qm list")
        if code == 0 and stdout:
            lines = stdout.split('\n')
            if len(lines) > 1:
                print(f"{'VMID':<8} {'NAME':<20} {'STATUS':<12} {'MEM':<8} {'BOOTDISK':<15}")
                print("-" * 60)
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            vmid = parts[0]
                            name = parts[1]
                            status = parts[2]
                            mem = parts[3] if len(parts) > 3 else 'N/A'
                            disk = parts[4] if len(parts) > 4 else 'N/A'
                            
                            # Status renklendir
                            if status == 'running':
                                status_colored = f"🟢 {status}"
                            elif status == 'stopped':
                                status_colored = f"🔴 {status}"
                            else:
                                status_colored = f"🟡 {status}"
                                
                            print(f"{vmid:<8} {name:<20} {status_colored:<20} {mem:<8} {disk:<15}")
            else:
                print("📭 Hiç VM bulunamadı.")
        else:
            print(f"❌ VM listesi alınamadı: {stderr}")
        print()

    def list_containers(self):
        """Container listesini göster"""
        print("\n📦 LXC CONTAINERS")
        print("-" * 60)
        
        stdout, stderr, code = self.run_command("pct list")
        if code == 0 and stdout:
            lines = stdout.split('\n')
            if len(lines) > 1:
                print(f"{'CTID':<8} {'NAME':<20} {'STATUS':<12} {'LOCK':<8}")
                print("-" * 50)
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3:
                            ctid = parts[0]
                            name = parts[1]
                            status = parts[2]
                            lock = parts[3] if len(parts) > 3 else '-'
                            
                            # Status renklendir
                            if status == 'running':
                                status_colored = f"🟢 {status}"
                            elif status == 'stopped':
                                status_colored = f"🔴 {status}"
                            else:
                                status_colored = f"🟡 {status}"
                                
                            print(f"{ctid:<8} {name:<20} {status_colored:<20} {lock:<8}")
            else:
                print("📭 Hiç container bulunamadı.")
        else:
            print(f"❌ Container listesi alınamadı: {stderr}")
        print()

    def vm_operations(self):
        """VM işlemleri menüsü"""
        while True:
            print("\n🖥️  VM İŞLEMLERİ")
            print("-" * 30)
            print("1. VM Listesi")
            print("2. VM Başlat")
            print("3. VM Durdur")
            print("4. VM Yeniden Başlat")
            print("5. VM Oluştur")
            print("6. VM Sil")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.system_update()
            elif choice == '2':
                self.clean_logs()
            elif choice == '3':
                self.disk_cleanup()
            elif choice == '4':
                self.service_status()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")

    def system_update(self):
        """Sistem güncelleme"""
        confirm = input("⚠️  Sistem güncellenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🔄 Sistem güncelleniyor...")
            stdout, stderr, code = self.run_command("apt update && apt upgrade -y")
            if code == 0:
                print("✅ Sistem başarıyla güncellendi!")
            else:
                print(f"❌ Güncelleme hatası: {stderr}")

    def clean_logs(self):
        """Log dosyalarını temizle"""
        confirm = input("⚠️  Log dosyaları temizlenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🧹 Log dosyaları temizleniyor...")
            self.run_command("journalctl --vacuum-time=7d")
            print("✅ Log dosyaları temizlendi!")

    def disk_cleanup(self):
        """Disk temizleme"""
        confirm = input("⚠️  Geçici dosyalar temizlenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🧹 Disk temizleniyor...")
            self.run_command("apt autoremove -y && apt autoclean")
            print("✅ Disk temizlendi!")

    def service_status(self):
        """Servis durumları"""
        print("\n🔍 SERVİS DURUMLARI")
        print("-" * 40)
        
        services = ['pveproxy', 'pvedaemon', 'pve-cluster', 'corosync']
        for service in services:
            stdout, stderr, code = self.run_command(f"systemctl is-active {service}")
            status = "✅ Active" if stdout.strip() == "active" else "❌ Inactive"
            print(f"{service:<15}: {status}")
        print()

    def security_audit(self):
        """Güvenlik denetimi"""
        print("\n🔒 GÜVENLİK DENETİMİ")
        print("-" * 30)
        
        # SSH ayarları kontrolü
        print("🔍 SSH Güvenlik Kontrolleri:")
        
        # Root login kontrolü
        root_login, _, _ = self.run_command("grep '^PermitRootLogin' /etc/ssh/sshd_config")
        print(f"   Root Login: {root_login if root_login else 'Default'}")
        
        # Firewall durumu
        print("\n🔥 Firewall Durumu:")
        fw_status, _, _ = self.run_command("systemctl is-active pve-firewall")
        print(f"   PVE Firewall: {'✅ Active' if fw_status == 'active' else '❌ Inactive'}")
        
        # Son login denemeleri
        print("\n🚨 Son Login Denemeleri:")
        failed_logins, _, _ = self.run_command("journalctl --no-pager | grep 'Failed password' | tail -3")
        if failed_logins:
            print("   ⚠️ Başarısız login denemeleri:")
            for line in failed_logins.split('\n'):
                if line.strip():
                    print(f"     {line[:80]}...")
        else:
            print("   ✅ Son zamanlarda başarısız login denemesi yok")
        
        # Güncellik kontrolü
        print("\n📦 Güncelleme Durumu:")
        updates_available, _, _ = self.run_command("apt list --upgradable 2>/dev/null | wc -l")
        update_count = int(updates_available) - 1 if updates_available.isdigit() else 0
        if update_count > 0:
            print(f"   ⚠️ {update_count} güncelleme mevcut")
        else:
            print("   ✅ Sistem güncel")

    def snapshot_management(self):
        """Snapshot yönetimi"""
        while True:
            print("\n📸 SNAPSHOT YÖNETİMİ")
            print("-" * 30)
            print("1. VM Snapshot Al")
            print("2. LXC Snapshot Al")
            print("3. Snapshot Listesi")
            print("4. Snapshot Geri Yükle")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-4): ").strip()
            
            if choice == '1':
                self.create_vm_snapshot()
            elif choice == '2':
                self.create_lxc_snapshot()
            elif choice == '3':
                self.list_snapshots()
            elif choice == '4':
                self.restore_snapshot()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")

    def create_vm_snapshot(self):
        """VM snapshot oluştur"""
        self.list_vms()
        vmid = input("Snapshot alınacak VM ID: ").strip()
        if vmid:
            snap_name = input("Snapshot adı [auto]: ").strip() or f"auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            print(f"📸 VM {vmid} snapshot alınıyor...")
            stdout, stderr, code = self.run_command(f"qm snapshot {vmid} {snap_name}")
            if code == 0:
                print(f"✅ Snapshot '{snap_name}' başarıyla oluşturuldu!")
            else:
                print(f"❌ Hata: {stderr}")

    def create_lxc_snapshot(self):
        """LXC snapshot oluştur"""
        self.list_containers()
        ctid = input("Snapshot alınacak Container ID: ").strip()
        if ctid:
            snap_name = input("Snapshot adı [auto]: ").strip() or f"auto-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            print(f"📸 Container {ctid} snapshot alınıyor...")
            stdout, stderr, code = self.run_command(f"pct snapshot {ctid} {snap_name}")
            if code == 0:
                print(f"✅ Snapshot '{snap_name}' başarıyla oluşturuldu!")
            else:
                print(f"❌ Hata: {stderr}")

    def list_snapshots(self):
        """Snapshot listesi"""
        print("\n📋 SNAPSHOT LİSTESİ")
        print("-" * 50)
        
        # VM snapshots
        vm_result, _, _ = self.run_command("qm list | awk 'NR>1 {print $1}'")
        if vm_result:
            print("🖥️  VM Snapshots:")
            for vmid in vm_result.split('\n'):
                if vmid.strip():
                    snap_result, _, _ = self.run_command(f"qm listsnapshot {vmid}")
                    if snap_result and "no snapshots" not in snap_result.lower():
                        print(f"   VM {vmid}:")
                        for line in snap_result.split('\n')[1:]:
                            if line.strip():
                                print(f"     📸 {line}")
        
        # LXC snapshots
        lxc_result, _, _ = self.run_command("pct list | awk 'NR>1 {print $1}'")
        if lxc_result:
            print("\n📦 LXC Snapshots:")
            for ctid in lxc_result.split('\n'):
                if ctid.strip():
                    snap_result, _, _ = self.run_command(f"pct listsnapshot {ctid}")
                    if snap_result and "no snapshots" not in snap_result.lower():
                        print(f"   LXC {ctid}:")
                        for line in snap_result.split('\n')[1:]:
                            if line.strip():
                                print(f"     📸 {line}")
        print()

    def restore_snapshot(self):
        """Snapshot geri yükle"""
        vm_or_lxc = input("VM mi LXC mi? (vm/lxc): ").strip().lower()
        
        if vm_or_lxc == 'vm':
            self.list_vms()
            vmid = input("VM ID: ").strip()
            if vmid:
                # Snapshot listesini göster
                self.run_command(f"qm listsnapshot {vmid}")
                snap_name = input("Geri yüklenecek snapshot adı: ").strip()
                if snap_name:
                    confirm = input(f"⚠️  VM {vmid} '{snap_name}' snapshot'ına geri yüklenecek! Emin misiniz? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        print(f"🔄 Snapshot geri yükleniyor...")
                        stdout, stderr, code = self.run_command(f"qm rollback {vmid} {snap_name}")
                        if code == 0:
                            print(f"✅ Snapshot başarıyla geri yüklendi!")
                        else:
                            print(f"❌ Hata: {stderr}")
        
        elif vm_or_lxc == 'lxc':
            self.list_containers()
            ctid = input("Container ID: ").strip()
            if ctid:
                # Snapshot listesini göster
                self.run_command(f"pct listsnapshot {ctid}")
                snap_name = input("Geri yüklenecek snapshot adı: ").strip()
                if snap_name:
                    confirm = input(f"⚠️  Container {ctid} '{snap_name}' snapshot'ına geri yüklenecek! Emin misiniz? (yes/no): ").strip().lower()
                    if confirm == 'yes':
                        print(f"🔄 Snapshot geri yükleniyor...")
                        stdout, stderr, code = self.run_command(f"pct rollback {ctid} {snap_name}")
                        if code == 0:
                            print(f"✅ Snapshot başarıyla geri yüklendi!")
                        else:
                            print(f"❌ Hata: {stderr}")

    def main_menu(self):
        """Ana menü"""
        while True:
            self.show_banner()
            print("🏠 ANA MENÜ")
            print("-" * 20)
            print("1.  📊 Sistem Bilgileri")
            print("2.  🖥️  VM Yönetimi")
            print("3.  📦 Container Yönetimi")
            print("4.  💾 Yedekleme İşlemleri")
            print("5.  🔧 Sistem Bakım")
            print("6.  📊 Gerçek Zamanlı İzleme")
            print("7.  📸 Snapshot Yönetimi")
            print("8.  🔒 Güvenlik Denetimi")
            print("0.  🚪 Çıkış")
            
            choice = input(f"\n{self.brand_name} - Seçiminiz (0-8): ").strip()
            
            if choice == '1':
                self.show_system_info()
                input("\nDevam etmek için Enter'a basın...")
            elif choice == '2':
                self.vm_operations()
            elif choice == '3':
                self.container_operations()
            elif choice == '4':
                self.backup_operations()
            elif choice == '5':
                self.system_maintenance()
            elif choice == '6':
                self.show_realtime_monitoring()
            elif choice == '7':
                self.snapshot_management()
            elif choice == '8':
                self.security_audit()
                input("\nDevam etmek için Enter'a basın...")
            elif choice == '0':
                print(f"\n👋 {self.brand_name} Proxmox Toolkit - Güle güle!")
                break
            else:
                print("❌ Geçersiz seçim! Lütfen 0-8 arası bir sayı girin.")
                time.sleep(2)


# Ana uygulama
def main():
    try:
        app = ProxmoxAdvancedCLI()
        app.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Program sonlandırıldı. Güle güle!")
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        print("Lütfen sistem yöneticisiyle iletişime geçin.")

if __name__ == "__main__":
    main()
                self.list_vms()
            elif choice == '2':
                self.start_vm()
            elif choice == '3':
                self.stop_vm()
            elif choice == '4':
                self.restart_vm()
            elif choice == '5':
                self.create_vm()
            elif choice == '6':
                self.delete_vm()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")

    def container_operations(self):
        """Container işlemleri menüsü"""
        while True:
            print("\n📦 CONTAINER İŞLEMLERİ")
            print("-" * 30)
            print("1. Container Listesi")
            print("2. Container Başlat")
            print("3. Container Durdur")
            print("4. Container Yeniden Başlat")
            print("5. Container Oluştur")
            print("6. Container Sil")
            print("7. Container'a Gir")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-7): ").strip()
            
            if choice == '1':
                self.list_containers()
            elif choice == '2':
                self.start_container()
            elif choice == '3':
                self.stop_container()
            elif choice == '4':
                self.restart_container()
            elif choice == '5':
                self.create_container()
            elif choice == '6':
                self.delete_container()
            elif choice == '7':
                self.enter_container()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")

    def start_vm(self):
        """VM başlat"""
        self.list_vms()
        vmid = input("Başlatılacak VM ID: ").strip()
        if vmid:
            print(f"🚀 VM {vmid} başlatılıyor...")
            stdout, stderr, code = self.run_command(f"qm start {vmid}")
            if code == 0:
                print(f"✅ VM {vmid} başarıyla başlatıldı!")
            else:
                print(f"❌ Hata: {stderr}")

    def stop_vm(self):
        """VM durdur"""
        self.list_vms()
        vmid = input("Durdurulacak VM ID: ").strip()
        if vmid:
            confirm = input(f"VM {vmid} durdurulsun mu? (y/N): ").strip().lower()
            if confirm == 'y':
                print(f"⏹️ VM {vmid} durduruluyor...")
                stdout, stderr, code = self.run_command(f"qm stop {vmid}")
                if code == 0:
                    print(f"✅ VM {vmid} başarıyla durduruldu!")
                else:
                    print(f"❌ Hata: {stderr}")

    def restart_vm(self):
        """VM yeniden başlat"""
        self.list_vms()
        vmid = input("Yeniden başlatılacak VM ID: ").strip()
        if vmid:
            confirm = input(f"VM {vmid} yeniden başlatılsın mı? (y/N): ").strip().lower()
            if confirm == 'y':
                print(f"🔄 VM {vmid} yeniden başlatılıyor...")
                stdout, stderr, code = self.run_command(f"qm reboot {vmid}")
                if code == 0:
                    print(f"✅ VM {vmid} başarıyla yeniden başlatıldı!")
                else:
                    print(f"❌ Hata: {stderr}")

    def create_vm(self):
        """VM oluştur"""
        print("\n🆕 YENİ VM OLUŞTUR")
        print("-" * 30)
        
        vmid = input("VM ID: ").strip()
        name = input("VM Adı: ").strip()
        cores = input("CPU Çekirdek sayısı [2]: ").strip() or "2"
        memory = input("Bellek (MB) [2048]: ").strip() or "2048"
        disk = input("Disk boyutu (GB) [20]: ").strip() or "20"
        
        if vmid and name:
            cmd = f"qm create {vmid} --name {name} --cores {cores} --memory {memory} --net0 virtio,bridge=vmbr0 --scsi0 local-lvm:{disk} --boot order=scsi0 --ostype l26"
            print(f"\n🔧 VM oluşturuluyor...")
            stdout, stderr, code = self.run_command(cmd)
            if code == 0:
                print(f"✅ VM {vmid} ({name}) başarıyla oluşturuldu!")
            else:
                print(f"❌ Hata: {stderr}")
        else:
            print("❌ VM ID ve ad gerekli!")

    def delete_vm(self):
        """VM sil"""
        self.list_vms()
        vmid = input("Silinecek VM ID: ").strip()
        if vmid:
            confirm = input(f"⚠️  VM {vmid} kalıcı olarak silinecek! Emin misiniz? (yes/no): ").strip().lower()
            if confirm == 'yes':
                print(f"🗑️ VM {vmid} siliniyor...")
                stdout, stderr, code = self.run_command(f"qm destroy {vmid}")
                if code == 0:
                    print(f"✅ VM {vmid} başarıyla silindi!")
                else:
                    print(f"❌ Hata: {stderr}")
            else:
                print("❌ İşlem iptal edildi.")

    def start_container(self):
        """Container başlat"""
        self.list_containers()
        ctid = input("Başlatılacak Container ID: ").strip()
        if ctid:
            print(f"🚀 Container {ctid} başlatılıyor...")
            stdout, stderr, code = self.run_command(f"pct start {ctid}")
            if code == 0:
                print(f"✅ Container {ctid} başarıyla başlatıldı!")
            else:
                print(f"❌ Hata: {stderr}")

    def stop_container(self):
        """Container durdur"""
        self.list_containers()
        ctid = input("Durdurulacak Container ID: ").strip()
        if ctid:
            confirm = input(f"Container {ctid} durdurulsun mu? (y/N): ").strip().lower()
            if confirm == 'y':
                print(f"⏹️ Container {ctid} durduruluyor...")
                stdout, stderr, code = self.run_command(f"pct stop {ctid}")
                if code == 0:
                    print(f"✅ Container {ctid} başarıyla durduruldu!")
                else:
                    print(f"❌ Hata: {stderr}")

    def restart_container(self):
        """Container yeniden başlat"""
        self.list_containers()
        ctid = input("Yeniden başlatılacak Container ID: ").strip()
        if ctid:
            print(f"🔄 Container {ctid} yeniden başlatılıyor...")
            stdout, stderr, code = self.run_command(f"pct reboot {ctid}")
            if code == 0:
                print(f"✅ Container {ctid} başarıyla yeniden başlatıldı!")
            else:
                print(f"❌ Hata: {stderr}")

    def create_container(self):
        """Container oluştur"""
        print("\n🆕 YENİ CONTAINER OLUŞTUR")
        print("-" * 30)
        
        ctid = input("Container ID: ").strip()
        hostname = input("Hostname: ").strip()
        template = input("Template [ubuntu-22.04-standard]: ").strip() or "ubuntu-22.04-standard"
        cores = input("CPU Çekirdek sayısı [1]: ").strip() or "1"
        memory = input("Bellek (MB) [512]: ").strip() or "512"
        disk = input("Disk boyutu (GB) [8]: ").strip() or "8"
        
        if ctid and hostname:
            cmd = f"pct create {ctid} local:vztmpl/{template}_amd64.tar.xz --hostname {hostname} --cores {cores} --memory {memory} --rootfs local-lvm:{disk} --net0 name=eth0,bridge=vmbr0,ip=dhcp"
            print(f"\n🔧 Container oluşturuluyor...")
            stdout, stderr, code = self.run_command(cmd)
            if code == 0:
                print(f"✅ Container {ctid} ({hostname}) başarıyla oluşturuldu!")
            else:
                print(f"❌ Hata: {stderr}")
        else:
            print("❌ Container ID ve hostname gerekli!")

    def delete_container(self):
        """Container sil"""
        self.list_containers()
        ctid = input("Silinecek Container ID: ").strip()
        if ctid:
            confirm = input(f"⚠️  Container {ctid} kalıcı olarak silinecek! Emin misiniz? (yes/no): ").strip().lower()
            if confirm == 'yes':
                print(f"🗑️ Container {ctid} siliniyor...")
                stdout, stderr, code = self.run_command(f"pct destroy {ctid}")
                if code == 0:
                    print(f"✅ Container {ctid} başarıyla silindi!")
                else:
                    print(f"❌ Hata: {stderr}")
            else:
                print("❌ İşlem iptal edildi.")

    def enter_container(self):
        """Container'a gir"""
        self.list_containers()
        ctid = input("Girilecek Container ID: ").strip()
        if ctid:
            print(f"🖥️ Container {ctid}'e giriliyor...")
            print("Çıkmak için 'exit' yazın.")
            os.system(f"pct enter {ctid}")

    def backup_operations(self):
        """Yedekleme işlemleri"""
        while True:
            print("\n💾 YEDEKLEME İŞLEMLERİ")
            print("-" * 30)
            print("1. VM Yedekle")
            print("2. Container Yedekle")
            print("3. Tüm VM'leri Yedekle")
            print("4. Yedek Dosyalarını Listele")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-4): ").strip()
            
            if choice == '1':
                self.backup_vm()
            elif choice == '2':
                self.backup_container()
            elif choice == '3':
                self.backup_all()
            elif choice == '4':
                self.list_backups()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")

    def backup_vm(self):
        """VM yedekle"""
        self.list_vms()
        vmid = input("Yedeklenecek VM ID: ").strip()
        if vmid:
            print(f"💾 VM {vmid} yedekleniyor...")
            stdout, stderr, code = self.run_command(f"vzdump {vmid} --storage local --compress gzip")
            if code == 0:
                print(f"✅ VM {vmid} başarıyla yedeklendi!")
            else:
                print(f"❌ Hata: {stderr}")

    def backup_container(self):
        """Container yedekle"""
        self.list_containers()
        ctid = input("Yedeklenecek Container ID: ").strip()
        if ctid:
            print(f"💾 Container {ctid} yedekleniyor...")
            stdout, stderr, code = self.run_command(f"vzdump {ctid} --storage local --compress gzip")
            if code == 0:
                print(f"✅ Container {ctid} başarıyla yedeklendi!")
            else:
                print(f"❌ Hata: {stderr}")

    def backup_all(self):
        """Tüm sistemleri yedekle"""
        confirm = input("⚠️  Tüm VM ve Container'lar yedeklenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("💾 Tüm sistemler yedekleniyor...")
            stdout, stderr, code = self.run_command("vzdump --all --storage local --compress gzip")
            if code == 0:
                print("✅ Tüm sistemler başarıyla yedeklendi!")
            else:
                print(f"❌ Hata: {stderr}")

    def list_backups(self):
        """Yedek dosyalarını listele"""
        print("\n📋 YEDEK DOSYALARI")
        print("-" * 50)
        stdout, stderr, code = self.run_command("ls -lah /var/lib/vz/dump/")
        if code == 0 and stdout:
            print(stdout)
        else:
            print("📭 Yedek dosyası bulunamadı.")
        print()

    def system_maintenance(self):
        """Sistem bakım işlemleri"""
        while True:
            print("\n🔧 SİSTEM BAKIM")
            print("-" * 30)
            print("1. Sistem Güncelleme")
            print("2. Log Temizleme")
            print("3. Disk Temizleme")
            print("4. Servis Durumları")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-4): ").strip()
            
            if choice == '1':
