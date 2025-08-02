# Proxmox Toolkit 🛠️

Proxmox VE sunucularınızı yönetmek için geliştirilmiş kapsamlı Python araç seti

![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## 📖 Hakkında

Proxmox Toolkit, Proxmox VE (Virtual Environment) sunucularınızı kolayca yönetmenizi sağlayan kullanıcı dostu bir GUI uygulamasıdır. Karmaşık komut satırı işlemlerini basit arayüz tıklamaları ile gerçekleştirin.

## ✨ Özellikler

🖥️ **Modern GUI Arayüzü** - Tkinter tabanlı kullanıcı dostu tasarım  
📊 **VM Yönetimi** - Sanal makineleri oluşturun, başlatın, durdurun, silin  
📦 **Container Yönetimi** - LXC containerlarını tam kontrol edin  
📈 **Performans İzleme** - CPU, RAM, disk kullanımı grafikleri  
🔐 **Güvenli Bağlantı** - SSH tabanlı güvenli sunucu erişimi  
🌐 **Çoklu Sunucu** - Birden fazla Proxmox sunucusunu tek arayüzden yönetin  
💾 **Yedekleme** - Otomatik VM/Container yedekleme işlemleri  
📋 **Sistem Bilgileri** - Detaylı sunucu durumu ve kaynak kullanımı

## 🚀 Kurulum

### Gereksinimler

- Python 3.6 veya üstü
- Proxmox VE sunucusu (v6.0+)
- SSH erişimi

### Adım 1: Repository'yi klonlayın
```bash
git clone https://github.com/yourusername/proxmox-toolkit.git
cd proxmox-toolkit
```

### Adım 2: Bağımlılıkları yükleyin
```bash
pip install -r requirements.txt
```

### Adım 3: Uygulamayı çalıştırın
```bash
python src/proxmox_toolkit.py
```

## 📱 Kullanım

### İlk Bağlantı
1. Uygulamayı başlatın
2. "Sunucu Ekle" butonuna tıklayın  
3. Proxmox sunucu bilgilerinizi girin:
   - **Host:** Sunucu IP adresi
   - **Kullanıcı:** root veya yetkili kullanıcı
   - **Şifre:** SSH şifresi
   - **Port:** 22 (varsayılan)

### VM Oluşturma
1. "VM Yönetimi" sekmesine gidin
2. "Yeni VM" butonuna tıklayın
3. VM özelliklerini belirleyin
4. "Oluştur" butonuna tıklayın

### Container Yönetimi
1. "Container" sekmesini seçin
2. Mevcut containerları görüntüleyin
3. Yeni container oluşturun veya mevcut olanları yönetin

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak istiyorsanız:

1. Repository'yi **fork** edin
2. Yeni bir **feature branch** oluşturun (`git checkout -b feature/yeni-ozellik`)
3. Değişikliklerinizi **commit** edin (`git commit -am 'Yeni özellik eklendi'`)
4. Branch'inizi **push** edin (`git push origin feature/yeni-ozellik`)
5. **Pull Request** oluşturun

## 🐛 Bug Raporu ve Özellik İsteği

- **Bug bulduysanız:** GitHub Issues bölümünde bug raporu oluşturun
- **Yeni özellik istiyorsanız:** GitHub Issues bölümünde feature request açın
- **Sorularınız için:** GitHub Discussions kullanın veya linkedln üzerinden

## 📋 Yapılacaklar Listesi

- [ ] Web arayüzü desteği
- [ ] REST API entegrasyonu  
- [ ] Template yönetimi
- [ ] Otomatik güncellemeler
- [ ] Çoklu dil desteği
- [ ] Docker container desteği ( docker yapısını kafamızda tam oturtsak olcak aslında ) 

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır.

## 🙏 Teşekkürler

- Proxmox - Harika sanallaştırma platformu için
- Python topluluğu - Güçlü kütüphaneler için
- Bütün testlerimi yapıp yapamadıklarımı gören Muammer Yeşilyağcı

## 📞 İletişim

- **GitHub:** cemal-demirci
- **Email:** me@cemal.online

---

⭐ **Projeyi beğendiyseniz yıldız vermeyi unutmayın!** ⭐
