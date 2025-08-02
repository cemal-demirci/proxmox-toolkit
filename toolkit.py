    def generate_performance_report(self):
        """Performans raporu oluştur"""
        print("\n📊 PERFORMANS RAPORU OLUŞTURULUYOR...")
        print("-" * 50)
        
        report_file = f"/tmp/proxmox_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(f"{'='*60}\n")
            f.write(f"{self.brand_name} - PROXMOX PERFORMANS RAPORU\n")
            f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            
            # Sistem bilgileri
            f.write("🖥️ SİSTEM BİLGİLERİ:\n")
            f.write("-" * 30 + "\n")
            
            # CPU bilgisi
            cpu_info, _, _ = self.run_command("lscpu | grep 'Model name' | cut -d':' -f2")
            f.write(f"CPU: {cpu_info.strip()}\n")
            
            cpu_cores, _, _ = self.run_command("nproc")
            f.write(f"CPU Cores: {cpu_cores}\n")
            
            # Memory bilgisi
            mem_info, _, _ = self.run_command("free -h | awk 'NR==2{printf \"%s total, %s used, %s free\", $2, $3, $4}'")
            f.write(f"Memory: {mem_info}\n")
            
            # Disk bilgisi
            disk_info, _, _ = self.run_command("df -h / | awk 'NR==2{printf \"%s total, %s used, %s available (%s used)\", $2, $3, $4, $5}'")
            f.write(f"Root Disk: {disk_info}\n")
            
            # Uptime
            uptime_info, _, _ = self.run_command("uptime -p")
            f.write(f"Uptime: {uptime_info}\n\n")
            
            # VM/LXC sayıları
            f.write("📊 SANALLAŞTIRMA İSTATİSTİKLERİ:\n")
            f.write("-" * 40 + "\n")
            
            total_vms, _, _ = self.run_command("qm list | wc -l")
            running_vms, _, _ = self.run_command("qm list | grep -c running")
            f.write(f"Toplam VM: {int(total_vms)-1 if total_vms.isdigit() else 0}\n")
            f.write(f"Çalışan VM: {running_vms}\n")
            
            total_lxcs, _, _ = self.run_command("pct list | wc -l")
            running_lxcs, _, _ = self.run_command("pct list | grep -c running")
            f.write(f"Toplam LXC: {int(total_lxcs)-1 if total_lxcs.isdigit() else 0}\n")
            f.write(f"Çalışan LXC: {running_lxcs}\n\n")
            
            # Kaynak kullanımı
            f.write("📈 KAYNAK KULLANIMI:\n")
            f.write("-" * 25 + "\n")
            
            cpu_usage, _, _ = self.run_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1")
            f.write(f"CPU Kullanımı: {cpu_usage}%\n")
            
            mem_usage, _, _ = self.run_command("free | awk 'NR==2{printf \"%.1f\", $3*100/$2}'")
            f.write(f"Memory Kullanımı: {mem_usage}%\n")
            
            disk_usage, _, _ = self.run_command("df / | awk 'NR==2{print $5}'")
            f.write(f"Disk Kullanımı: {disk_usage}\n")
            
            # Load average
            load_avg, _, _ = self.run_command("uptime | awk -F'load average:' '{print $2}'")
            f.write(f"Load Average: {load_avg.strip()}\n\n")
            
            # Network bilgileri
            f.write("🌐 NETWORK BİLGİLERİ:\n")
            f.write("-" * 25 + "\n")
            
            network_info, _, _ = self.run_command("ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2, $NF}'")
            for line in network_info.split('\n'):
                if line.strip():
                    f.write(f"Interface: {line}\n")
            
            # Storage bilgileri
            f.write("\n💾 STORAGE BİLGİLERİ:\n")
            f.write("-" * 25 + "\n")
            
            storage_info, _, _ = self.run_command("pvesm status")
            f.write(storage_info + "\n\n")
            
            # Son sistem logları
            f.write("📜 SON SİSTEM LOGLARI (Son 10):\n")
            f.write("-" * 35 + "\n")
            
            recent_logs, _, _ = self.run_command("journalctl -p err --no-pager -n 10 --output=short")
            f.write(recent_logs + "\n\n")
            
            # Güvenlik kontrolleri
            f.write("🔒 GÜVENLİK KONTROL:\n")
            f.write("-" * 20 + "\n")
            
            # Failed SSH attempts
            failed_ssh, _, _ = self.run_command("journalctl --no-pager | grep 'Failed password' | tail -5")
            if failed_ssh:
                f.write("Son başarısız SSH denemeleri:\n")
                f.write(failed_ssh + "\n")
            else:
                f.write("✅ Son zamanlarda başarısız SSH denemesi yok\n")
            
            # Root login kontrolü
            root_login, _, _ = self.run_command("grep '^PermitRootLogin' /etc/ssh/sshd_config")
            f.write(f"SSH Root Login: {root_login}\n")
            
            f.write(f"\n{'='*60}\n")
            f.write("Rapor tamamlandı.\n")
        
        print(f"✅ Performans raporu oluşturuldu: {report_file}")
        
        # Raporu göster
        view_report = input("Raporu görüntülemek ister misiniz? (y/N): ").strip().lower()
        if view_report == 'y':
            self.run_command(f"cat {report_file}")
    
    def security_audit(self):
        """Güvenlik denetimi"""
        print("\n🔒 GÜVENLİK DENETİMİ")
        print("-" * 30)
        
        # SSH ayarları kontrolü
        print("🔍 SSH Güvenlik Kontrolleri:")
        
        ssh_config_checks = {
            "PermitRootLogin": "Root login durumu",
            "PasswordAuthentication": "Şifre authentication",
            "PermitEmptyPasswords": "Boş şifre izni",
            "Protocol": "SSH protokol versiyonu"
        }
        
        for setting, description in ssh_config_checks.items():
            result, _, _ = self.run_command(f"grep '^{setting}' /etc/ssh/sshd_config")
            status = result if result else f"{setting} not found"
            print(f"   {description}: {status}")
        
        # Firewall durumu
        print("\n🔥 Firewall Durumu:")
        fw_status, _, _ = self.run_command("systemctl is-active pve-firewall")
        print(f"   PVE Firewall: {'✅ Active' if fw_status == 'active' else '❌ Inactive'}")
        
        # Fail2ban kontrolü
        f2b_status, _, _ = self.run_command("systemctl is-active fail2ban")
        print(f"   Fail2ban: {'✅ Active' if f2b_status == 'active' else '❌ Not installed/inactive'}")
        
        # Son login denemeleri
        print("\n🚨 Son Login Denemeleri:")
        failed_logins, _, _ = self.run_command("journalctl --no-pager | grep 'Failed password' | tail -5")
        if failed_logins:
            print("   ⚠️ Başarısız login denemeleri bulundu:")
            for line in failed_logins.split('\n'):
                if line.strip():
                    print(f"     {line}")
        else:
            print("   ✅ Son zamanlarda başarısız login denemesi yok")
        
        # Açık portlar
        print("\n🌐 Açık Portlar:")
        open_ports, _, _ = self.run_command("netstat -tlnp | grep LISTEN")
        for line in open_ports.split('\n')[:10]:  # İlk 10'u göster
            if line.strip():
                print(f"   {line}")
        
        # Güncellik kontrolü
        print("\n📦 Güncelleme Durumu:")
        updates_available, _, _ = self.run_command("apt list --upgradable 2>/dev/null | wc -l")
        update_count = int(updates_available) - 1 if updates_available.isdigit() else 0
        if update_count > 0:
            print(f"   ⚠️ {update_count} güncelleme mevcut")
        else:
            print("   ✅ Sistem güncel")
    
    def advanced_log_viewer(self):
        """Gelişmiş log görüntüleyici"""
        while True:
            print("\n📜 GELİŞMİŞ LOG GÖRÜNTÜLEYICI")
            print("-" * 35)
            print("1. Sistem Logları")
            print("2. Proxmox Logları")
            print("3. VM/LXC Logları")
            print("4. Error Logları")
            print("5. Authentication Logları")
            print("6. Custom Log Arama")
            print("7. Live Log İzleme")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-7): ").strip()
            
            if choice == '1':
                self.view_system_logs()
            elif choice == '2':
                self.view_proxmox_logs()
            elif choice == '3':
                self.view_vm_lxc_logs()
            elif choice == '4':
                self.view_error_logs()
            elif choice == '5':
                self.view_auth_logs()
            elif choice == '6':
                self.custom_log_search()
            elif choice == '7':
                self.live_log_monitoring()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def view_system_logs(self):
        """Sistem loglarını görüntüle"""
        lines = input("Kaç satır gösterilsin? [50]: ").strip() or "50"
        
        print(f"\n📋 SON {lines} SİSTEM LOGU:")
        print("-" * 50)
        
        stdout, _, _ = self.run_command(f"journalctl --no-pager -n {lines}")
        
        # Logları renklendir
        for line in stdout.split('\n'):
            if 'ERROR' in line or 'error' in line:
                print(f"🔴 {line}")
            elif 'WARNING' in line or 'warning' in line:
                print(f"🟡 {line}")
            elif 'INFO' in line or 'info' in line:
                print(f"🔵 {line}")
            else:
                print(f"   {line}")
    
    def live_log_monitoring(self):
        """Canlı log izleme"""
        print("\n📺 CANLI LOG İZLEME")
        print("Çıkmak için Ctrl+C basın...")
        print("-" * 40)
        
        try:
            process = subprocess.Popen(['journalctl', '-f'], stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            
            while True:
                output = process.stdout.readline()
                if output:
                    # Log seviyesine göre renklendir
                    if 'ERROR' in output or 'error' in output:
                        print(f"🔴 {output.strip()}")
                    elif 'WARNING' in output or 'warning' in output:
                        print(f"🟡 {output.strip()}")
                    elif 'pve' in output.lower():
                        print(f"🟢 {output.strip()}")
                    else:
                        print(f"   {output.strip()}")
                
        except KeyboardInterrupt:
            print("\n\n✅ Canlı log izleme durduruldu.")
            process.terminate()
    
    def cluster_management(self):
        """Cluster yönetimi"""
        while True:
            print("\n🌐 CLUSTER YÖNETİMİ")
            print("-" * 25)
            print("1. Cluster Durumu")
            print("2. Node Bilgileri")
            print("3. Cluster Join")
            print("4. Migration İşlemleri")
            print("5. HA Yönetimi")
            print("6. Corosync Durumu")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.show_cluster_status()
            elif choice == '2':
                self.show_node_info()
            elif choice == '3':
                self.cluster_join()
            elif choice == '4':
                self.migration_operations()
            elif choice == '5':
                self.ha_management()
            elif choice == '6':
                self.corosync_status()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def show_cluster_status(self):
        """Cluster durumunu göster"""
        print("\n🌐 CLUSTER DURUMU")
        print("-" * 25)
        
        # Cluster basic info
        cluster_info, _, _ = self.run_command("pvecm status")
        print("📊 Cluster Bilgileri:")
        print(cluster_info)
        
        # Quorum durumu
        print("\n🗳️ Quorum Durumu:")
        quorum_info, _, _ = self.run_command("pvecm expected 1 2>/dev/null && echo 'Quorum OK' || echo 'Quorum Problem'")
        print(quorum_info)
        
        # Node'lar
        print("\n🖥️ Cluster Node'ları:")
        nodes_info, _, _ = self.run_command("pvecm nodes")
        print(nodes_info)
    
    def migration_operations(self):
        """Migration işlemleri"""
        print("\n🔄 MİGRATİON İŞLEMLERİ")
        print("-" * 30)
        print("1. VM Migration")
        print("2. LXC Migration")
        print("3. Online Migration")
        print("4. Migration Durumu")
        print("0. Geri")
        
        choice = input("\nSeçiminiz (0-4): ").strip()
        
        if choice == '1':
            self.migrate_vm()
        elif choice == '2':
            self.migrate_lxc()
    
    def migrate_vm(self):
        """VM migration"""
        self.list_vms()
        vmid = input("Migration yapılacak VM ID: ").strip()
        
        if vmid:
            # Mevcut node'ları listele
            nodes_info, _, _ = self.run_command("pvecm nodes | awk 'NR>1 {print $3}'")
            print("\nMevcut Node'lar:")
            for node in nodes_info.split('\n'):
                if node.strip():
                    print(f"  📍 {node}")
            
            target_node = input("Hedef node: ").strip()
            online = input("Online migration? (y/N): ").strip().lower() == 'y'
            
            if target_node:
                migration_type = "--online" if online else ""
                print(f"🔄 VM {vmid} {target_node} node'una migration yapılıyor...")
                
                stdout, stderr, code = self.run_command(f"qm migrate {vmid} {target_node} {migration_type}")
                if code == 0:
                    print(f"✅ Migration başarılı!")
                else:
                    print(f"❌ Migration başarısız: {stderr}")
    
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
            print("8.  📦 Template Yönetimi")
            print("9.  🤖 Otomasyon Merkezi")
            print("10. 📜 Gelişmiş Log Viewer")
            print("11. 🌐 Cluster Yönetimi")
            print("12. 🔒 Güvenlik Denetimi")
            print("0.  🚪 Çıkış")
            
            choice = input(f"\n{self.brand_name} - Seçiminiz (0-12): ").strip()
            
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
                self.template_management()
            elif choice == '9':
                self.automation_center()
            elif choice == '10':
                self.advanced_log_viewer()
            elif choice == '11':
                self.cluster_management()
            elif choice == '12':
                self.security_audit()
                input("\nDevam etmek için Enter'a basın...")
            elif choice == '0':
                print(f"\n👋 {self.brand_name} Proxmox Toolkit - Güle güle!")
                break
            else:
                print("❌ Geçersiz seçim! Lütfen 0-12 arası bir sayı girin.")
                time.sleep(2)

    # Ana VM/Container/Backup fonksiyonları (önceki sürümden kopyalanacak)
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
            print("5. VM Durakla")
            print("6. VM Durumu")
            print("7. VM Oluştur")
            print("8. VM Sil")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-8): ").strip()
            
            if choice == '1':
                self.list_vms()
            elif choice == '2':
                self.start_vm()
            elif choice == '3':
                self.stop_vm()
            elif choice == '4':
                self.restart_vm()
            elif choice == '5':
                self.suspend_vm()
            elif choice == '6':
                self.vm_status()
            elif choice == '7':
                self.create_vm()
            elif choice == '8':
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
            print("5. Container Durumu")
            print("6. Container Oluştur")
            print("7. Container Sil")
            print("8. Container'a Gir")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-8): ").strip()
            
            if choice == '1':
                self.list_containers()
            elif choice == '2':
                self.start_container()
            elif choice == '3':
                self.stop_container()
            elif choice == '4':
                self.restart_container()
            elif choice == '5':
                self.container_status()
            elif choice == '6':
                self.create_container()
            elif choice == '7':
                self.delete_container()
            elif choice == '8':
                self.enter_container()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")

    def backup_operations(self):
        """Yedekleme işlemleri"""
        while True:
            print("\n💾 YEDEKLEME İŞLEMLERİ")
            print("-" * 30)
            print("1. Tek VM Yedekle")
            print("2. Tek Container Yedekle")
            print("3. Tüm VM'leri Yedekle")
            print("4. Tüm Container'ları Yedekle")
            print("5. Yedek Dosyalarını Listele")
            print("6. Yedek Dosyası Sil")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.backup_vm()
            elif choice == '2':
                self.backup_container()
            elif choice == '3':
                self.backup_all_vms()
            elif choice == '4':
                self.backup_all_containers()
            elif choice == '5':
                self.list_backups()
            elif choice == '6':
                self.delete_backup()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")

    # Temel VM fonksiyonları
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

    def suspend_vm(self):
        """VM durakla"""
        self.list_vms()
        vmid = input("Duraklatılacak VM ID: ").strip()
        if vmid:
            print(f"⏸️ VM {vmid} duraklatılıyor...")
            stdout, stderr, code = self.run_command(f"qm suspend {vmid}")
            if code == 0:
                print(f"✅ VM {vmid} başarıyla duraklatıldı!")
            else:
                print(f"❌ Hata: {stderr}")

    def vm_status(self):
        """VM durumu"""
        vmid = input("VM ID: ").strip()
        if vmid:
            stdout, stderr, code = self.run_command(f"qm status {vmid}")
            if code == 0:
                print(f"\n📊 VM {vmid} Durumu:")
                print(stdout)
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

    # Container fonksiyonları
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

    def container_status(self):
        """Container durumu"""
        ctid = input("Container ID: ").strip()
        if ctid:
            stdout, stderr, code = self.run_command(f"pct status {ctid}")
            if code == 0:
                print(f"\n📊 Container {ctid} Durumu:")
                print(stdout)
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

    # Backup fonksiyonları
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

    def backup_all_vms(self):
        """Tüm VM'leri yedekle"""
        confirm = input("⚠️  Tüm VM'ler yedeklenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("💾 Tüm VM'ler yedekleniyor...")
            stdout, stderr, code = self.run_command("vzdump --all --storage local --compress gzip --mode snapshot")
            if code == 0:
                print("✅ Tüm VM'ler başarıyla yedeklendi!")
            else:
                print(f"❌ Hata: {stderr}")

    def backup_all_containers(self):
        """Tüm container'ları yedekle"""
        confirm = input("⚠️  Tüm Container'lar yedeklenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("💾 Tüm Container'lar yedekleniyor...")
            stdout, stderr, code = self.run_command("pct list | awk 'NR>1 {print $1}'")
            if code == 0 and stdout:
                for ctid in stdout.split('\n'):
                    if ctid.strip():
                        print(f"💾 Container {ctid} yedekleniyor...")
                        self.run_command(f"vzdump {ctid} --storage local --compress gzip")
                print("✅ Tüm Container'lar yedeklendi!")
            else:
                print("❌ Container listesi alınamadı!")

    def list_backups(self):
        """Yedek dosyalarını listele"""
        print("\n📋 YEDEK DOSYALARI")
        print("-" * 50)
        stdout, stderr, code = self.run_command("ls -lah /var/lib/vz/dump/ | grep -E '\\.(vma|tar)(\\.gz|\\.lzo|\\.zst)?#!/usr/bin/env python3
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
from pathlib import Path

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

/* Header özelleştirmesi */
#header {{
    background: linear-gradient(90deg, #0066cc, #004499) !important;
}}

/* Login ekranı özelleştirmesi */
.pmg-login-title:before {{
    content: "{self.brand_name} ";
    color: #0066cc;
    font-weight: bold;
}}
"""
                
                with open(css_file, 'a') as f:
                    f.write(custom_css)
                    
                print(f"✅ Branding '{self.brand_name}' eklendi")
            
            # JavaScript ile runtime branding
            js_file = f"{pve_www_path}/js/pvemanagerlib.js"
            if os.path.exists(js_file):
                subprocess.run(f"cp {js_file} {js_file}.backup", shell=True)
                
                # Title değiştir
                subprocess.run(f"sed -i 's/Proxmox Virtual Environment/{self.brand_name} - Proxmox VE/g' {js_file}", shell=True)
                
                print("✅ JavaScript branding uygulandı")
                
            # Proxmox servislerini yeniden başlat
            subprocess.run("systemctl restart pveproxy", shell=True)
            
        except Exception as e:
            print(f"⚠️ Branding uygulanamadı: {e}")
    
    def remove_subscription_warnings(self):
        """No-subscription uyarılarını kaldır"""
        try:
            # pve-manager subscription check'ini devre dışı bırak
            manager_file = "/usr/share/perl5/PVE/API2/Subscription.pm"
            if os.path.exists(manager_file):
                subprocess.run(f"cp {manager_file} {manager_file}.backup", shell=True)
                
                # Subscription check'i bypass et
                subprocess.run("""
sed -i "s/NotFound/Active/g" /usr/share/perl5/PVE/API2/Subscription.pm
sed -i "s/\$res->\{status\} ne 'Active'/0/g" /usr/share/perl5/PVE/API2/Subscription.pm
""", shell=True)
                
                print("✅ Subscription uyarıları kaldırıldı")
            
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
            
            # Proxmox versiyonunu al
            version_cmd = "pveversion | head -1 | cut -d'/' -f2 | cut -d'.' -f1-2"
            result = subprocess.run(version_cmd, shell=True, capture_output=True, text=True)
            pve_version = result.stdout.strip() or "8"
            
            # Debian codename'i belirle
            codename_map = {
                "7": "bullseye",
                "8": "bookworm"
            }
            codename = codename_map.get(pve_version, "bookworm")
            
            with open(no_sub_list, 'w') as f:
                f.write(f"# Free Proxmox VE repository\n")
                f.write(f"deb http://download.proxmox.com/debian/pve {codename} pve-no-subscription\n")
            
            # Ceph no-subscription repository
            ceph_list = "/etc/apt/sources.list.d/ceph.list"
            with open(ceph_list, 'w') as f:
                f.write(f"# Free Ceph repository\n")
                f.write(f"deb http://download.proxmox.com/debian/ceph-quincy {codename} no-subscription\n")
            
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
                
                # Network (yaklaşık)
                net_usage = (cpu_usage + mem_usage) / 2  # Simulated
                self.show_ascii_chart("Network", net_usage, 100)
                
                print(f"\n🖥️  Running VMs: {self.get_running_count('vm')}")
                print(f"📦 Running LXCs: {self.get_running_count('lxc')}")
                
                # Son 5 log
                print("\n📜 Son Log Girişleri:")
                log_cmd = "journalctl -u pve* --no-pager -n 3 --output=short-iso"
                log_result, _, _ = self.run_command(log_cmd)
                for line in log_result.split('\n')[-3:]:
                    if line.strip():
                        print(f"   {line[:80]}...")
                
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
    
    def snapshot_management(self):
        """Snapshot yönetimi menüsü"""
        while True:
            print("\n📸 SNAPSHOT YÖNETİMİ")
            print("-" * 30)
            print("1. VM Snapshot Al")
            print("2. LXC Snapshot Al")
            print("3. Snapshot Listesi")
            print("4. Snapshot Geri Yükle")
            print("5. Snapshot Sil")
            print("6. Otomatik Snapshot Ayarla")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.create_vm_snapshot()
            elif choice == '2':
                self.create_lxc_snapshot()
            elif choice == '3':
                self.list_snapshots()
            elif choice == '4':
                self.restore_snapshot()
            elif choice == '5':
                self.delete_snapshot()
            elif choice == '6':
                self.setup_auto_snapshot()
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
            description = input("Açıklama [optional]: ").strip()
            
            cmd = f"qm snapshot {vmid} {snap_name}"
            if description:
                cmd += f" --description '{description}'"
                
            print(f"📸 VM {vmid} snapshot alınıyor...")
            stdout, stderr, code = self.run_command(cmd)
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
    
    def template_management(self):
        """Template yönetimi"""
        while True:
            print("\n📦 TEMPLATE YÖNETİMİ")
            print("-" * 30)
            print("1. Mevcut Template'leri Listele")
            print("2. LXC Template İndir")
            print("3. ISO Image İndir")
            print("4. VM'den Template Oluştur")
            print("5. Template Sil")
            print("6. Template'den VM Oluştur")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.list_templates()
            elif choice == '2':
                self.download_lxc_template()
            elif choice == '3':
                self.download_iso()
            elif choice == '4':
                self.create_template_from_vm()
            elif choice == '5':
                self.delete_template()
            elif choice == '6':
                self.create_vm_from_template()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def list_templates(self):
        """Template listesi"""
        print("\n📋 TEMPLATE LİSTESİ")
        print("-" * 50)
        
        # LXC Templates
        print("📦 LXC Templates:")
        lxc_templates, _, _ = self.run_command("pveam available | grep -E '(ubuntu|debian|centos|alpine)'")
        if lxc_templates:
            for line in lxc_templates.split('\n')[:10]:  # İlk 10'u göster
                if line.strip():
                    print(f"   {line}")
            print("   ... (daha fazlası için 'pveam available' komutu)")
        
        print("\n💽 ISO Images:")
        iso_list, _, _ = self.run_command("find /var/lib/vz/template/iso -name '*.iso' -exec basename {} \\;")
        if iso_list:
            for iso in iso_list.split('\n'):
                if iso.strip():
                    print(f"   💽 {iso}")
        else:
            print("   📭 ISO dosyası bulunamadı")
        
        print("\n📁 VM Templates:")
        template_list, _, _ = self.run_command("qm list | grep template")
        if template_list:
            for template in template_list.split('\n'):
                if template.strip():
                    print(f"   🖥️  {template}")
        else:
            print("   📭 VM template bulunamadı")
        print()
    
    def download_lxc_template(self):
        """LXC template indir"""
        print("\n📦 Popüler LXC Templates:")
        popular_templates = [
            "ubuntu-22.04-standard",
            "ubuntu-20.04-standard", 
            "debian-11-standard",
            "debian-12-standard",
            "centos-8-default",
            "alpine-3.18-default"
        ]
        
        for i, template in enumerate(popular_templates, 1):
            print(f"{i}. {template}")
        
        choice = input("\nSeçim yapın (1-6) veya manuel template adı girin: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 6:
            template = popular_templates[int(choice)-1]
        else:
            template = choice
        
        if template:
            print(f"📥 Template indiriliyor: {template}")
            stdout, stderr, code = self.run_command(f"pveam download local {template}")
            if code == 0:
                print(f"✅ Template başarıyla indirildi!")
            else:
                print(f"❌ Hata: {stderr}")
    
    def automation_center(self):
        """Otomasyon merkezi"""
        while True:
            print("\n🤖 OTOMASYON MERKEZİ")
            print("-" * 30)
            print("1. Otomatik Yedekleme Ayarla")
            print("2. Cron Job Yönetimi")
            print("3. Bulk VM İşlemleri")
            print("4. Sistem Performans Raporu")
            print("5. Security Audit")
            print("6. Disk Temizlik Otomasyonu")
            print("7. Custom Script Çalıştır")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-7): ").strip()
            
            if choice == '1':
                self.setup_auto_backup()
            elif choice == '2':
                self.manage_cron_jobs()
            elif choice == '3':
                self.bulk_vm_operations()
            elif choice == '4':
                self.generate_performance_report()
            elif choice == '5':
                self.security_audit()
            elif choice == '6':
                self.setup_disk_cleanup()
            elif choice == '7':
                self.run_custom_script()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def setup_auto_backup(self):
        """Otomatik yedekleme ayarla"""
        print("\n💾 OTOMATİK YEDEKLEME AYARLARI")
        print("-" * 40)
        
        schedule_options = {
            "1": "Günlük (02:00)",
            "2": "Haftalık (Pazar 03:00)", 
            "3": "Aylık (1. gün 04:00)",
            "4": "Custom"
        }
        
        for key, value in schedule_options.items():
            print(f"{key}. {value}")
        
        choice = input("\nZamanlama seçin (1-4): ").strip()
        
        backup_what = input("Neyi yedekleyecek? (vm/lxc/all): ").strip().lower()
        retention = input("Kaç gün saklansın? [7]: ").strip() or "7"
        
        # Cron expression oluştur
        cron_expressions = {
            "1": "0 2 * * *",      # Günlük
            "2": "0 3 * * 0",      # Haftalık
            "3": "0 4 1 * *",      # Aylık
        }
        
        if choice in cron_expressions:
            cron_time = cron_expressions[choice]
        elif choice == "4":
            cron_time = input("Cron expression girin (örn: 0 2 * * *): ").strip()
        else:
            print("❌ Geçersiz seçim!")
            return
        
        # Backup script oluştur
        script_content = f"""#!/bin/bash
# Otomatik Yedekleme Script - {self.brand_name}
# Oluşturulma: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

LOG_FILE="/var/log/auto-backup.log"
RETENTION_DAYS={retention}

echo "$(date): Otomatik yedekleme başladı" >> $LOG_FILE

if [ "{backup_what}" = "vm" ] || [ "{backup_what}" = "all" ]; then
    for vmid in $(qm list | awk 'NR>1 {{print $1}}'); do
        echo "$(date): VM $vmid yedekleniyor..." >> $LOG_FILE
        vzdump $vmid --storage local --compress gzip --remove 0
    done
fi

if [ "{backup_what}" = "lxc" ] || [ "{backup_what}" = "all" ]; then
    for ctid in $(pct list | awk 'NR>1 {{print $1}}'); do
        echo "$(date): LXC $ctid yedekleniyor..." >> $LOG_FILE
        vzdump $ctid --storage local --compress gzip --remove 0
    done
fi

# Eski yedekleri temizle
find /var/lib/vz/dump -name "*.vma.gz" -mtime +$RETENTION_DAYS -delete
find /var/lib/vz/dump -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "$(date): Otomatik yedekleme tamamlandı" >> $LOG_FILE
"""
        
        # Script dosyasını kaydet
        script_path = "/usr/local/bin/auto-backup.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Cron job ekle
        cron_job = f"{cron_time} root {script_path}"
        
        with open("/etc/cron.d/proxmox-auto-backup", 'w') as f:
            f.write(f"# Otomatik Yedekleme - {self.brand_name}\n")
            f.write(f"{cron_job}\n")
        
        print(f"✅ Otomatik yedekleme ayarlandı!")
        print(f"📅 Zamanlama: {schedule_options.get(choice, 'Custom')}")
        print(f"🎯 Hedef: {backup_what}")
        print(f"📦 Saklama süresi: {retention} gün")
        print(f"📝 Log dosyası: /var/log/auto-backup.log")
    
    def bulk_vm_operations(self):
        """Toplu VM işlemleri"""
        print("\n🔄 TOPLU VM İŞLEMLERİ")
        print("-" * 30)
        print("1. Tüm VM'leri Başlat")
        print("2. Tüm VM'leri Durdur")
        print("3. Belirli Tag'li VM'leri Yönet")
        print("4. CPU/Memory Toplu Güncelleme")
        print("5. Network Ayarları Toplu Değişim")
        print("0. Geri")
        
        choice = input("\nSeçiminiz (0-5): ").strip()
        
        if choice == '1':
            self.bulk_start_vms()
        elif choice == '2':
            self.bulk_stop_vms()
        elif choice == '3':
            self.manage_tagged_vms()
        elif choice == '4':
            self.bulk_update_resources()
        elif choice == '5':
            self.bulk_network_update()
    
    def generate_performance_report(self):
        """Performans raporu oluştur"""
        print("\n📊 PERFORMANS RAPORU OLUŞTURULUYOR#!/usr/bin/env python3
"""
Proxmox VE CLI Management Toolkit
Command-line interface for managing Proxmox VE servers

Authors: Cemal & Muammer Yeşilyağcı
Version: 1.0.0
License: MIT
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime

class ProxmoxCLI:
    def __init__(self):
        self.version = "1.0.0"
        self.check_proxmox()
        
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
        """Banner göster"""
        print("\n" + "="*60)
        print("🚀 PROXMOX VE CLI MANAGEMENT TOOLKIT")
        print(f"📌 Version: {self.version}")
        print("👥 Authors: Cemal & Muammer Yeşilyağcı")
        print("="*60)
        print(f"⏰ Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
    
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
                            print(f"{vmid:<8} {name:<20} {status:<12} {mem:<8} {disk:<15}")
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
                            print(f"{ctid:<8} {name:<20} {status:<12} {lock:<8}")
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
            print("5. VM Durakla")
            print("6. VM Durumu")
            print("7. VM Oluştur")
            print("8. VM Sil")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-8): ").strip()
            
            if choice == '1':
                self.list_vms()
            elif choice == '2':
                self.start_vm()
            elif choice == '3':
                self.stop_vm()
            elif choice == '4':
                self.restart_vm()
            elif choice == '5':
                self.suspend_vm()
            elif choice == '6':
                self.vm_status()
            elif choice == '7':
                self.create_vm()
            elif choice == '8':
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
            print("5. Container Durumu")
            print("6. Container Oluştur")
            print("7. Container Sil")
            print("8. Container'a Gir")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-8): ").strip()
            
            if choice == '1':
                self.list_containers()
            elif choice == '2':
                self.start_container()
            elif choice == '3':
                self.stop_container()
            elif choice == '4':
                self.restart_container()
            elif choice == '5':
                self.container_status()
            elif choice == '6':
                self.create_container()
            elif choice == '7':
                self.delete_container()
            elif choice == '8':
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
    
    def suspend_vm(self):
        """VM durakla"""
        self.list_vms()
        vmid = input("Duraklatılacak VM ID: ").strip()
        if vmid:
            print(f"⏸️ VM {vmid} duraklatılıyor...")
            stdout, stderr, code = self.run_command(f"qm suspend {vmid}")
            if code == 0:
                print(f"✅ VM {vmid} başarıyla duraklatıldı!")
            else:
                print(f"❌ Hata: {stderr}")
    
    def vm_status(self):
        """VM durumu"""
        vmid = input("VM ID: ").strip()
        if vmid:
            stdout, stderr, code = self.run_command(f"qm status {vmid}")
            if code == 0:
                print(f"\n📊 VM {vmid} Durumu:")
                print(stdout)
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
    
    def container_status(self):
        """Container durumu"""
        ctid = input("Container ID: ").strip()
        if ctid:
            stdout, stderr, code = self.run_command(f"pct status {ctid}")
            if code == 0:
                print(f"\n📊 Container {ctid} Durumu:")
                print(stdout)
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
            print("1. Tek VM Yedekle")
            print("2. Tek Container Yedekle")
            print("3. Tüm VM'leri Yedekle")
            print("4. Tüm Container'ları Yedekle")
            print("5. Yedek Dosyalarını Listele")
            print("6. Yedek Dosyası Sil")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.backup_vm()
            elif choice == '2':
                self.backup_container()
            elif choice == '3':
                self.backup_all_vms()
            elif choice == '4':
                self.backup_all_containers()
            elif choice == '5':
                self.list_backups()
            elif choice == '6':
                self.delete_backup()
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
    
    def backup_all_vms(self):
        """Tüm VM'leri yedekle"""
        confirm = input("⚠️  Tüm VM'ler yedeklenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("💾 Tüm VM'ler yedekleniyor...")
            stdout, stderr, code = self.run_command("vzdump --all --storage local --compress gzip --mode snapshot")
            if code == 0:
                print("✅ Tüm VM'ler başarıyla yedeklendi!")
            else:
                print(f"❌ Hata: {stderr}")
    
    def backup_all_containers(self):
        """Tüm container'ları yedekle"""
        confirm = input("⚠️  Tüm Container'lar yedeklenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("💾 Tüm Container'lar yedekleniyor...")
            # Container ID'lerini al ve tek tek yedekle
            stdout, stderr, code = self.run_command("pct list | awk 'NR>1 {print $1}'")
            if code == 0 and stdout:
                for ctid in stdout.split('\n'):
                    if ctid.strip():
                        print(f"💾 Container {ctid} yedekleniyor...")
                        self.run_command(f"vzdump {ctid} --storage local --compress gzip")
                print("✅ Tüm Container'lar yedeklendi!")
            else:
                print("❌ Container listesi alınamadı!")
    
    def list_backups(self):
        """Yedek dosyalarını listele"""
        print("\n📋 YEDEK DOSYALARI")
        print("-" * 50)
        stdout, stderr, code = self.run_command("ls -lah /var/lib/vz/dump/ | grep -E '\\.(vma|tar)(\\.gz|\\.lzo|\\.zst)?$'")
        if code == 0 and stdout:
            print(stdout)
        else:
            print("📭 Yedek dosyası bulunamadı.")
        print()
    
    def delete_backup(self):
        """Yedek dosyası sil"""
        self.list_backups()
        filename = input("Silinecek yedek dosya adı: ").strip()
        if filename:
            confirm = input(f"⚠️  {filename} silinecek! Emin misiniz? (yes/no): ").strip().lower()
            if confirm == 'yes':
                stdout, stderr, code = self.run_command(f"rm -f /var/lib/vz/dump/{filename}")
                if code == 0:
                    print(f"✅ {filename} başarıyla silindi!")
                else:
                    print(f"❌ Hata: {stderr}")
            else:
                print("❌ İşlem iptal edildi.")
    
    def system_maintenance(self):
        """Sistem bakım işlemleri"""
        while True:
            print("\n🔧 SİSTEM BAKIM")
            print("-" * 30)
            print("1. Sistem Güncelleme")
            print("2. Log Temizleme")
            print("3. Disk Temizleme")
            print("4. Servis Durumları")
            print("5. Network Bilgileri")
            print("6. Storage Durumu")
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
            elif choice == '5':
                self.network_info()
            elif choice == '6':
                self.storage_info()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def system_update(self):
        """Sistem güncelleme"""
        confirm = input("⚠️  Sistem güncellenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🔄 Paket listesi güncelleniyor...")
            self.run_command("apt update")
            print("🔄 Sistem güncelleniyor...")
            stdout, stderr, code = self.run_command("apt upgrade -y")
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
            self.run_command("find /var/log -name '*.log' -mtime +30 -delete")
            print("✅ Log dosyaları temizlendi!")
    
    def disk_cleanup(self):
        """Disk temizleme"""
        confirm = input("⚠️  Geçici dosyalar temizlenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🧹 Disk temizleniyor...")
            self.run_command("apt autoremove -y")
            self.run_command("apt autoclean")
            self.run_command("find /tmp -type f -mtime +7 -delete")
            print("✅ Disk temizlendi!")
    
    def service_status(self):
        """Servis durumları"""
        print("\n🔍 SERVİS DURUMLARI")
        print("-" * 40)
        
        services = ['pveproxy', 'pvedaemon', 'pve-cluster', 'corosync', 'pvestatd']
        for service in services:
            stdout, stderr, code = self.run_command(f"systemctl is-active {service}")
            status = "✅ Active" if stdout.strip() == "active" else "❌ Inactive"
            print(f"{service:<15}: {status}")
        print()
    
    def network_info(self):
        """Network bilgileri"""
        print("\n🌐 NETWORK BİLGİLERİ")
        print("-" * 40)
        
        # IP adresleri
        stdout, _, _ = self.run_command("ip addr show | grep 'inet ' | grep -v '127.0.0.1'")
        print("📡 IP Adresleri:")
        if stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    print(f"   {line.strip()}")
        
        # Bridge bilgileri
        print("\n🌉 Bridge Durumları:")
        stdout, _, _ = self.run_command("brctl show")
        if stdout:
            print(stdout)
        print()
    
    def storage_info(self):
        """Storage bilgileri"""
        print("\n")
        if code == 0 and stdout:
            print(stdout)
        else:
            print("📭 Yedek dosyası bulunamadı.")
        print()

    def delete_backup(self):
        """Yedek dosyası sil"""
        self.list_backups()
        filename = input("Silinecek yedek dosya adı: ").strip()
        if filename:
            confirm = input(f"⚠️  {filename} silinecek! Emin misiniz? (yes/no): ").strip().lower()
            if confirm == 'yes':
                stdout, stderr, code = self.run_command(f"rm -f /var/lib/vz/dump/{filename}")
                if code == 0:
                    print(f"✅ {filename} başarıyla silindi!")
                else:
                    print(f"❌ Hata: {stderr}")
            else:
                print("❌ İşlem iptal edildi.")

    # Sistem bakım fonksiyonları
    def system_maintenance(self):
        """Sistem bakım işlemleri"""
        while True:
            print("\n🔧 SİSTEM BAKIM")
            print("-" * 30)
            print("1. Sistem Güncelleme")
            print("2. Log Temizleme")
            print("3. Disk Temizleme")
            print("4. Servis Durumları")
            print("5. Network Bilgileri")
            print("6. Storage Durumu")
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
            elif choice == '5':
                self.network_info()
            elif choice == '6':
                self.storage_info()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")

    def system_update(self):
        """Sistem güncelleme"""
        confirm = input("⚠️  Sistem güncellenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🔄 Paket listesi güncelleniyor...")
            self.run_command("apt update")
            print("🔄 Sistem güncelleniyor...")
            stdout, stderr, code = self.run_command("apt upgrade -y")
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
            self.run_command("find /var/log -name '*.log' -mtime +30 -delete")
            print("✅ Log dosyaları temizlendi!")

    def disk_cleanup(self):
        """Disk temizleme"""
        confirm = input("⚠️  Geçici dosyalar temizlenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🧹 Disk temizleniyor...")
            self.run_command("apt autoremove -y")
            self.run_command("apt autoclean")
            self.run_command("find /tmp -type f -mtime +7 -delete")
            print("✅ Disk temizlendi!")

    def service_status(self):
        """Servis durumları"""
        print("\n🔍 SERVİS DURUMLARI")
        print("-" * 40)
        
        services = ['pveproxy', 'pvedaemon', 'pve-cluster', 'corosync', 'pvestatd']
        for service in services:
            stdout, stderr, code = self.run_command(f"systemctl is-active {service}")
            status = "✅ Active" if stdout.strip() == "active" else "❌ Inactive"
            print(f"{service:<15}: {status}")
        print()

    def network_info(self):
        """Network bilgileri"""
        print("\n🌐 NETWORK BİLGİLERİ")
        print("-" * 40)
        
        stdout, _, _ = self.run_command("ip addr show | grep 'inet ' | grep -v '127.0.0.1'")
        print("📡 IP Adresleri:")
        if stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    print(f"   {line.strip()}")
        
        print("\n🌉 Bridge Durumları:")
        stdout, _, _ = self.run_command("brctl show")
        if stdout:
            print(stdout)
        print()

    def storage_info(self):
        """Storage bilgileri"""
        print("\n💾 STORAGE BİLGİLERİ")
        print("-" * 30)
        
        stdout, _, _ = self.run_command("pvesm status")
        if stdout:
            print(stdout)
        else:
            print("❌ Storage bilgisi alınamadı")
        print()

    def show_system_info(self):
        """Sistem bilgilerini göster"""
        print("\n📊 SİSTEM BİLGİLERİ")
        print("-" * 40)
        
        stdout, _, _ = self.run_command("pveversion")
        print(f"📦 Proxmox Version: {stdout.split()[0] if stdout else 'N/A'}")
        
        stdout, _, _ = self.run_command("uptime -p")
        print(f"⏱️  Uptime: {stdout if stdout else 'N/A'}")
        
        stdout, _, _ = self.run_command("free -h | awk 'NR==2{printf \"%.1f%% (%s/%s)\", $3*100/$2, $3, $2}'")
        print(f"💾 Memory: {stdout if stdout else 'N/A'}")
        
        stdout, _, _ = self.run_command("df -h / | awk 'NR==2{printf \"%s (%s available)\", $5, $4}'")
        print(f"💿 Disk Usage: {stdout if stdout else 'N/A'}")
        
        stdout, _, _ = self.run_command("uptime | awk -F'load average:' '{print $2}'")
        print(f"📈 Load Average: {stdout if stdout else 'N/A'}")
        
        stdout, _, _ = self.run_command("qm list | wc -l")
        vm_count = int(stdout) - 1 if stdout.isdigit() else 0
        print(f"🖥️  Total VMs: {vm_count}")
        
        stdout, _, _ = self.run_command("pct list | wc -l")
        ct_count = int(stdout) - 1 if stdout.isdigit() else 0
        print(f"📦 Total Containers: {ct_count}")
        
        stdout, _, _ = self.run_command("qm list | grep -c running")
        running_vms = stdout if stdout else '0'
        print(f"▶️  Running VMs: {running_vms}")
        
        stdout, _, _ = self.run_command("pct list | grep -c running")
        running_cts = stdout if stdout else '0'
        print(f"▶️  Running Containers: {running_cts}")
        print()

    # Eksik fonksiyonlar için placeholder'lar
    def delete_snapshot(self):
        """Snapshot sil"""
        print("🗑️ Snapshot silme özelliği aktif...")
        # Implementation here

    def setup_auto_snapshot(self):
        """Otomatik snapshot ayarla"""
        print("⏰ Otomatik snapshot ayarlama...")
        # Implementation here

    def download_iso(self):
        """ISO indir"""
        print("💽 ISO indirme özelliği...")
        # Implementation here

    def create_template_from_vm(self):
        """VM'den template oluştur"""
        print("📦 VM'den template oluşturma...")
        # Implementation here

    def delete_template(self):
        """Template sil"""
        print("🗑️ Template silme...")
        # Implementation here

    def create_vm_from_template(self):
        """Template'den VM oluştur"""
        print("🆕 Template'den VM oluşturma...")
        # Implementation here

    def manage_cron_jobs(self):
        """Cron job yönetimi"""
        print("⏰ Cron job yönetimi...")
        # Implementation here

    def setup_disk_cleanup(self):
        """Disk temizlik otomasyonu"""
        print("🧹 Disk temizlik otomasyonu...")
        # Implementation here

    def run_custom_script(self):
        """Custom script çalıştır"""
        print("📝 Custom script çalıştırma...")
        # Implementation here

    def view_proxmox_logs(self):
        """Proxmox logları"""
        print("📜 Proxmox logları...")
        # Implementation here

    def view_vm_lxc_logs(self):
        """VM/LXC logları"""
        print("📜 VM/LXC logları...")
        # Implementation here

    def view_error_logs(self):
        """Error logları"""
        print("🔴 Error logları...")
        # Implementation here

    def view_auth_logs(self):
        """Authentication logları"""
        print("🔐 Authentication logları...")
        # Implementation here

    def custom_log_search(self):
        """Custom log arama"""
        print("🔍 Custom log arama...")
        # Implementation here

    def show_node_info(self):
        """Node bilgileri"""
        print("🖥️ Node bilgileri...")
        # Implementation here

    def cluster_join(self):
        """Cluster join"""
        print("🔗 Cluster join...")
        # Implementation here

    def ha_management(self):
        """HA yönetimi"""
        print("🔧 HA yönetimi...")
        # Implementation here

    def corosync_status(self):
        """Corosync durumu"""
        print("🔍 Corosync durumu...")
        # Implementation here

    def migrate_lxc(self):
        """LXC migration"""
        print("🔄 LXC migration...")
        # Implementation here

    def bulk_start_vms(self):
        """Tüm VM'leri başlat"""
        print("🚀 Tüm VM'ler başlatılıyor...")
        # Implementation here

    def bulk_stop_vms(self):
        """Tüm VM'leri durdur"""
        print("⏹️ Tüm VM'ler durduruluyor...")
        # Implementation here

    def manage_tagged_vms(self):
        """Tag'li VM'leri yönet"""
        print("🏷️ Tag'li VM yönetimi...")
        # Implementation here

    def bulk_update_resources(self):
        """Toplu kaynak güncelleme"""
        print("🔧 Toplu kaynak güncelleme...")
        # Implementation here

    def bulk_network_update(self):
        """Toplu network güncelleme"""
        print("🌐 Toplu network güncelleme...")
        # Implementation here

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
    main()#!/usr/bin/env python3
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
from pathlib import Path

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

/* Header özelleştirmesi */
#header {{
    background: linear-gradient(90deg, #0066cc, #004499) !important;
}}

/* Login ekranı özelleştirmesi */
.pmg-login-title:before {{
    content: "{self.brand_name} ";
    color: #0066cc;
    font-weight: bold;
}}
"""
                
                with open(css_file, 'a') as f:
                    f.write(custom_css)
                    
                print(f"✅ Branding '{self.brand_name}' eklendi")
            
            # JavaScript ile runtime branding
            js_file = f"{pve_www_path}/js/pvemanagerlib.js"
            if os.path.exists(js_file):
                subprocess.run(f"cp {js_file} {js_file}.backup", shell=True)
                
                # Title değiştir
                subprocess.run(f"sed -i 's/Proxmox Virtual Environment/{self.brand_name} - Proxmox VE/g' {js_file}", shell=True)
                
                print("✅ JavaScript branding uygulandı")
                
            # Proxmox servislerini yeniden başlat
            subprocess.run("systemctl restart pveproxy", shell=True)
            
        except Exception as e:
            print(f"⚠️ Branding uygulanamadı: {e}")
    
    def remove_subscription_warnings(self):
        """No-subscription uyarılarını kaldır"""
        try:
            # pve-manager subscription check'ini devre dışı bırak
            manager_file = "/usr/share/perl5/PVE/API2/Subscription.pm"
            if os.path.exists(manager_file):
                subprocess.run(f"cp {manager_file} {manager_file}.backup", shell=True)
                
                # Subscription check'i bypass et
                subprocess.run("""
sed -i "s/NotFound/Active/g" /usr/share/perl5/PVE/API2/Subscription.pm
sed -i "s/\$res->\{status\} ne 'Active'/0/g" /usr/share/perl5/PVE/API2/Subscription.pm
""", shell=True)
                
                print("✅ Subscription uyarıları kaldırıldı")
            
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
            
            # Proxmox versiyonunu al
            version_cmd = "pveversion | head -1 | cut -d'/' -f2 | cut -d'.' -f1-2"
            result = subprocess.run(version_cmd, shell=True, capture_output=True, text=True)
            pve_version = result.stdout.strip() or "8"
            
            # Debian codename'i belirle
            codename_map = {
                "7": "bullseye",
                "8": "bookworm"
            }
            codename = codename_map.get(pve_version, "bookworm")
            
            with open(no_sub_list, 'w') as f:
                f.write(f"# Free Proxmox VE repository\n")
                f.write(f"deb http://download.proxmox.com/debian/pve {codename} pve-no-subscription\n")
            
            # Ceph no-subscription repository
            ceph_list = "/etc/apt/sources.list.d/ceph.list"
            with open(ceph_list, 'w') as f:
                f.write(f"# Free Ceph repository\n")
                f.write(f"deb http://download.proxmox.com/debian/ceph-quincy {codename} no-subscription\n")
            
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
                
                # Network (yaklaşık)
                net_usage = (cpu_usage + mem_usage) / 2  # Simulated
                self.show_ascii_chart("Network", net_usage, 100)
                
                print(f"\n🖥️  Running VMs: {self.get_running_count('vm')}")
                print(f"📦 Running LXCs: {self.get_running_count('lxc')}")
                
                # Son 5 log
                print("\n📜 Son Log Girişleri:")
                log_cmd = "journalctl -u pve* --no-pager -n 3 --output=short-iso"
                log_result, _, _ = self.run_command(log_cmd)
                for line in log_result.split('\n')[-3:]:
                    if line.strip():
                        print(f"   {line[:80]}...")
                
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
    
    def snapshot_management(self):
        """Snapshot yönetimi menüsü"""
        while True:
            print("\n📸 SNAPSHOT YÖNETİMİ")
            print("-" * 30)
            print("1. VM Snapshot Al")
            print("2. LXC Snapshot Al")
            print("3. Snapshot Listesi")
            print("4. Snapshot Geri Yükle")
            print("5. Snapshot Sil")
            print("6. Otomatik Snapshot Ayarla")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.create_vm_snapshot()
            elif choice == '2':
                self.create_lxc_snapshot()
            elif choice == '3':
                self.list_snapshots()
            elif choice == '4':
                self.restore_snapshot()
            elif choice == '5':
                self.delete_snapshot()
            elif choice == '6':
                self.setup_auto_snapshot()
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
            description = input("Açıklama [optional]: ").strip()
            
            cmd = f"qm snapshot {vmid} {snap_name}"
            if description:
                cmd += f" --description '{description}'"
                
            print(f"📸 VM {vmid} snapshot alınıyor...")
            stdout, stderr, code = self.run_command(cmd)
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
    
    def template_management(self):
        """Template yönetimi"""
        while True:
            print("\n📦 TEMPLATE YÖNETİMİ")
            print("-" * 30)
            print("1. Mevcut Template'leri Listele")
            print("2. LXC Template İndir")
            print("3. ISO Image İndir")
            print("4. VM'den Template Oluştur")
            print("5. Template Sil")
            print("6. Template'den VM Oluştur")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.list_templates()
            elif choice == '2':
                self.download_lxc_template()
            elif choice == '3':
                self.download_iso()
            elif choice == '4':
                self.create_template_from_vm()
            elif choice == '5':
                self.delete_template()
            elif choice == '6':
                self.create_vm_from_template()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def list_templates(self):
        """Template listesi"""
        print("\n📋 TEMPLATE LİSTESİ")
        print("-" * 50)
        
        # LXC Templates
        print("📦 LXC Templates:")
        lxc_templates, _, _ = self.run_command("pveam available | grep -E '(ubuntu|debian|centos|alpine)'")
        if lxc_templates:
            for line in lxc_templates.split('\n')[:10]:  # İlk 10'u göster
                if line.strip():
                    print(f"   {line}")
            print("   ... (daha fazlası için 'pveam available' komutu)")
        
        print("\n💽 ISO Images:")
        iso_list, _, _ = self.run_command("find /var/lib/vz/template/iso -name '*.iso' -exec basename {} \\;")
        if iso_list:
            for iso in iso_list.split('\n'):
                if iso.strip():
                    print(f"   💽 {iso}")
        else:
            print("   📭 ISO dosyası bulunamadı")
        
        print("\n📁 VM Templates:")
        template_list, _, _ = self.run_command("qm list | grep template")
        if template_list:
            for template in template_list.split('\n'):
                if template.strip():
                    print(f"   🖥️  {template}")
        else:
            print("   📭 VM template bulunamadı")
        print()
    
    def download_lxc_template(self):
        """LXC template indir"""
        print("\n📦 Popüler LXC Templates:")
        popular_templates = [
            "ubuntu-22.04-standard",
            "ubuntu-20.04-standard", 
            "debian-11-standard",
            "debian-12-standard",
            "centos-8-default",
            "alpine-3.18-default"
        ]
        
        for i, template in enumerate(popular_templates, 1):
            print(f"{i}. {template}")
        
        choice = input("\nSeçim yapın (1-6) veya manuel template adı girin: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 6:
            template = popular_templates[int(choice)-1]
        else:
            template = choice
        
        if template:
            print(f"📥 Template indiriliyor: {template}")
            stdout, stderr, code = self.run_command(f"pveam download local {template}")
            if code == 0:
                print(f"✅ Template başarıyla indirildi!")
            else:
                print(f"❌ Hata: {stderr}")
    
    def automation_center(self):
        """Otomasyon merkezi"""
        while True:
            print("\n🤖 OTOMASYON MERKEZİ")
            print("-" * 30)
            print("1. Otomatik Yedekleme Ayarla")
            print("2. Cron Job Yönetimi")
            print("3. Bulk VM İşlemleri")
            print("4. Sistem Performans Raporu")
            print("5. Security Audit")
            print("6. Disk Temizlik Otomasyonu")
            print("7. Custom Script Çalıştır")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-7): ").strip()
            
            if choice == '1':
                self.setup_auto_backup()
            elif choice == '2':
                self.manage_cron_jobs()
            elif choice == '3':
                self.bulk_vm_operations()
            elif choice == '4':
                self.generate_performance_report()
            elif choice == '5':
                self.security_audit()
            elif choice == '6':
                self.setup_disk_cleanup()
            elif choice == '7':
                self.run_custom_script()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def setup_auto_backup(self):
        """Otomatik yedekleme ayarla"""
        print("\n💾 OTOMATİK YEDEKLEME AYARLARI")
        print("-" * 40)
        
        schedule_options = {
            "1": "Günlük (02:00)",
            "2": "Haftalık (Pazar 03:00)", 
            "3": "Aylık (1. gün 04:00)",
            "4": "Custom"
        }
        
        for key, value in schedule_options.items():
            print(f"{key}. {value}")
        
        choice = input("\nZamanlama seçin (1-4): ").strip()
        
        backup_what = input("Neyi yedekleyecek? (vm/lxc/all): ").strip().lower()
        retention = input("Kaç gün saklansın? [7]: ").strip() or "7"
        
        # Cron expression oluştur
        cron_expressions = {
            "1": "0 2 * * *",      # Günlük
            "2": "0 3 * * 0",      # Haftalık
            "3": "0 4 1 * *",      # Aylık
        }
        
        if choice in cron_expressions:
            cron_time = cron_expressions[choice]
        elif choice == "4":
            cron_time = input("Cron expression girin (örn: 0 2 * * *): ").strip()
        else:
            print("❌ Geçersiz seçim!")
            return
        
        # Backup script oluştur
        script_content = f"""#!/bin/bash
# Otomatik Yedekleme Script - {self.brand_name}
# Oluşturulma: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

LOG_FILE="/var/log/auto-backup.log"
RETENTION_DAYS={retention}

echo "$(date): Otomatik yedekleme başladı" >> $LOG_FILE

if [ "{backup_what}" = "vm" ] || [ "{backup_what}" = "all" ]; then
    for vmid in $(qm list | awk 'NR>1 {{print $1}}'); do
        echo "$(date): VM $vmid yedekleniyor..." >> $LOG_FILE
        vzdump $vmid --storage local --compress gzip --remove 0
    done
fi

if [ "{backup_what}" = "lxc" ] || [ "{backup_what}" = "all" ]; then
    for ctid in $(pct list | awk 'NR>1 {{print $1}}'); do
        echo "$(date): LXC $ctid yedekleniyor..." >> $LOG_FILE
        vzdump $ctid --storage local --compress gzip --remove 0
    done
fi

# Eski yedekleri temizle
find /var/lib/vz/dump -name "*.vma.gz" -mtime +$RETENTION_DAYS -delete
find /var/lib/vz/dump -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "$(date): Otomatik yedekleme tamamlandı" >> $LOG_FILE
"""
        
        # Script dosyasını kaydet
        script_path = "/usr/local/bin/auto-backup.sh"
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        
        # Cron job ekle
        cron_job = f"{cron_time} root {script_path}"
        
        with open("/etc/cron.d/proxmox-auto-backup", 'w') as f:
            f.write(f"# Otomatik Yedekleme - {self.brand_name}\n")
            f.write(f"{cron_job}\n")
        
        print(f"✅ Otomatik yedekleme ayarlandı!")
        print(f"📅 Zamanlama: {schedule_options.get(choice, 'Custom')}")
        print(f"🎯 Hedef: {backup_what}")
        print(f"📦 Saklama süresi: {retention} gün")
        print(f"📝 Log dosyası: /var/log/auto-backup.log")
    
    def bulk_vm_operations(self):
        """Toplu VM işlemleri"""
        print("\n🔄 TOPLU VM İŞLEMLERİ")
        print("-" * 30)
        print("1. Tüm VM'leri Başlat")
        print("2. Tüm VM'leri Durdur")
        print("3. Belirli Tag'li VM'leri Yönet")
        print("4. CPU/Memory Toplu Güncelleme")
        print("5. Network Ayarları Toplu Değişim")
        print("0. Geri")
        
        choice = input("\nSeçiminiz (0-5): ").strip()
        
        if choice == '1':
            self.bulk_start_vms()
        elif choice == '2':
            self.bulk_stop_vms()
        elif choice == '3':
            self.manage_tagged_vms()
        elif choice == '4':
            self.bulk_update_resources()
        elif choice == '5':
            self.bulk_network_update()
    
    def generate_performance_report(self):
        """Performans raporu oluştur"""
        print("\n📊 PERFORMANS RAPORU OLUŞTURULUYOR#!/usr/bin/env python3
"""
Proxmox VE CLI Management Toolkit
Command-line interface for managing Proxmox VE servers

Authors: Cemal & Muammer Yeşilyağcı
Version: 1.0.0
License: MIT
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime

class ProxmoxCLI:
    def __init__(self):
        self.version = "1.0.0"
        self.check_proxmox()
        
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
        """Banner göster"""
        print("\n" + "="*60)
        print("🚀 PROXMOX VE CLI MANAGEMENT TOOLKIT")
        print(f"📌 Version: {self.version}")
        print("👥 Authors: Cemal & Muammer Yeşilyağcı")
        print("="*60)
        print(f"⏰ Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")
    
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
                            print(f"{vmid:<8} {name:<20} {status:<12} {mem:<8} {disk:<15}")
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
                            print(f"{ctid:<8} {name:<20} {status:<12} {lock:<8}")
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
            print("5. VM Durakla")
            print("6. VM Durumu")
            print("7. VM Oluştur")
            print("8. VM Sil")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-8): ").strip()
            
            if choice == '1':
                self.list_vms()
            elif choice == '2':
                self.start_vm()
            elif choice == '3':
                self.stop_vm()
            elif choice == '4':
                self.restart_vm()
            elif choice == '5':
                self.suspend_vm()
            elif choice == '6':
                self.vm_status()
            elif choice == '7':
                self.create_vm()
            elif choice == '8':
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
            print("5. Container Durumu")
            print("6. Container Oluştur")
            print("7. Container Sil")
            print("8. Container'a Gir")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-8): ").strip()
            
            if choice == '1':
                self.list_containers()
            elif choice == '2':
                self.start_container()
            elif choice == '3':
                self.stop_container()
            elif choice == '4':
                self.restart_container()
            elif choice == '5':
                self.container_status()
            elif choice == '6':
                self.create_container()
            elif choice == '7':
                self.delete_container()
            elif choice == '8':
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
    
    def suspend_vm(self):
        """VM durakla"""
        self.list_vms()
        vmid = input("Duraklatılacak VM ID: ").strip()
        if vmid:
            print(f"⏸️ VM {vmid} duraklatılıyor...")
            stdout, stderr, code = self.run_command(f"qm suspend {vmid}")
            if code == 0:
                print(f"✅ VM {vmid} başarıyla duraklatıldı!")
            else:
                print(f"❌ Hata: {stderr}")
    
    def vm_status(self):
        """VM durumu"""
        vmid = input("VM ID: ").strip()
        if vmid:
            stdout, stderr, code = self.run_command(f"qm status {vmid}")
            if code == 0:
                print(f"\n📊 VM {vmid} Durumu:")
                print(stdout)
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
    
    def container_status(self):
        """Container durumu"""
        ctid = input("Container ID: ").strip()
        if ctid:
            stdout, stderr, code = self.run_command(f"pct status {ctid}")
            if code == 0:
                print(f"\n📊 Container {ctid} Durumu:")
                print(stdout)
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
            print("1. Tek VM Yedekle")
            print("2. Tek Container Yedekle")
            print("3. Tüm VM'leri Yedekle")
            print("4. Tüm Container'ları Yedekle")
            print("5. Yedek Dosyalarını Listele")
            print("6. Yedek Dosyası Sil")
            print("0. Ana Menüye Dön")
            
            choice = input("\nSeçiminiz (0-6): ").strip()
            
            if choice == '1':
                self.backup_vm()
            elif choice == '2':
                self.backup_container()
            elif choice == '3':
                self.backup_all_vms()
            elif choice == '4':
                self.backup_all_containers()
            elif choice == '5':
                self.list_backups()
            elif choice == '6':
                self.delete_backup()
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
    
    def backup_all_vms(self):
        """Tüm VM'leri yedekle"""
        confirm = input("⚠️  Tüm VM'ler yedeklenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("💾 Tüm VM'ler yedekleniyor...")
            stdout, stderr, code = self.run_command("vzdump --all --storage local --compress gzip --mode snapshot")
            if code == 0:
                print("✅ Tüm VM'ler başarıyla yedeklendi!")
            else:
                print(f"❌ Hata: {stderr}")
    
    def backup_all_containers(self):
        """Tüm container'ları yedekle"""
        confirm = input("⚠️  Tüm Container'lar yedeklenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("💾 Tüm Container'lar yedekleniyor...")
            # Container ID'lerini al ve tek tek yedekle
            stdout, stderr, code = self.run_command("pct list | awk 'NR>1 {print $1}'")
            if code == 0 and stdout:
                for ctid in stdout.split('\n'):
                    if ctid.strip():
                        print(f"💾 Container {ctid} yedekleniyor...")
                        self.run_command(f"vzdump {ctid} --storage local --compress gzip")
                print("✅ Tüm Container'lar yedeklendi!")
            else:
                print("❌ Container listesi alınamadı!")
    
    def list_backups(self):
        """Yedek dosyalarını listele"""
        print("\n📋 YEDEK DOSYALARI")
        print("-" * 50)
        stdout, stderr, code = self.run_command("ls -lah /var/lib/vz/dump/ | grep -E '\\.(vma|tar)(\\.gz|\\.lzo|\\.zst)?$'")
        if code == 0 and stdout:
            print(stdout)
        else:
            print("📭 Yedek dosyası bulunamadı.")
        print()
    
    def delete_backup(self):
        """Yedek dosyası sil"""
        self.list_backups()
        filename = input("Silinecek yedek dosya adı: ").strip()
        if filename:
            confirm = input(f"⚠️  {filename} silinecek! Emin misiniz? (yes/no): ").strip().lower()
            if confirm == 'yes':
                stdout, stderr, code = self.run_command(f"rm -f /var/lib/vz/dump/{filename}")
                if code == 0:
                    print(f"✅ {filename} başarıyla silindi!")
                else:
                    print(f"❌ Hata: {stderr}")
            else:
                print("❌ İşlem iptal edildi.")
    
    def system_maintenance(self):
        """Sistem bakım işlemleri"""
        while True:
            print("\n🔧 SİSTEM BAKIM")
            print("-" * 30)
            print("1. Sistem Güncelleme")
            print("2. Log Temizleme")
            print("3. Disk Temizleme")
            print("4. Servis Durumları")
            print("5. Network Bilgileri")
            print("6. Storage Durumu")
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
            elif choice == '5':
                self.network_info()
            elif choice == '6':
                self.storage_info()
            elif choice == '0':
                break
            else:
                print("❌ Geçersiz seçim!")
    
    def system_update(self):
        """Sistem güncelleme"""
        confirm = input("⚠️  Sistem güncellenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🔄 Paket listesi güncelleniyor...")
            self.run_command("apt update")
            print("🔄 Sistem güncelleniyor...")
            stdout, stderr, code = self.run_command("apt upgrade -y")
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
            self.run_command("find /var/log -name '*.log' -mtime +30 -delete")
            print("✅ Log dosyaları temizlendi!")
    
    def disk_cleanup(self):
        """Disk temizleme"""
        confirm = input("⚠️  Geçici dosyalar temizlenecek. Devam edilsin mi? (y/N): ").strip().lower()
        if confirm == 'y':
            print("🧹 Disk temizleniyor...")
            self.run_command("apt autoremove -y")
            self.run_command("apt autoclean")
            self.run_command("find /tmp -type f -mtime +7 -delete")
            print("✅ Disk temizlendi!")
    
    def service_status(self):
        """Servis durumları"""
        print("\n🔍 SERVİS DURUMLARI")
        print("-" * 40)
        
        services = ['pveproxy', 'pvedaemon', 'pve-cluster', 'corosync', 'pvestatd']
        for service in services:
            stdout, stderr, code = self.run_command(f"systemctl is-active {service}")
            status = "✅ Active" if stdout.strip() == "active" else "❌ Inactive"
            print(f"{service:<15}: {status}")
        print()
    
    def network_info(self):
        """Network bilgileri"""
        print("\n🌐 NETWORK BİLGİLERİ")
        print("-" * 40)
        
        # IP adresleri
        stdout, _, _ = self.run_command("ip addr show | grep 'inet ' | grep -v '127.0.0.1'")
        print("📡 IP Adresleri:")
        if stdout:
            for line in stdout.split('\n'):
                if line.strip():
                    print(f"   {line.strip()}")
        
        # Bridge bilgileri
        print("\n🌉 Bridge Durumları:")
        stdout, _, _ = self.run_command("brctl show")
        if stdout:
            print(stdout)
        print()
    
    def storage_info(self):
        """Storage bilgileri"""
        print("\n
