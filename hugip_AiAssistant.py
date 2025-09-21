from flask import Flask, request, jsonify, render_template_string, Response
import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)
app = Flask(__name__)
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)
MODEL = "gpt-4o-mini"

# HUGIP Kulübü Statik Bilgileri
CLUB_INFO = {
    "kulup_hakkinda": "2012 yılında kurulan Girişimcilik ve Pazarlama Kulübü,Haliç Üniversitesi bünyesindeki en köklü kulüptür.DIGITALMAG, FestUp, Social Media Talks, HUGİPAkademi yanında konsept etkinlik serileriyle girişimcilikvizyonunu spor, sanat ve kültürle harmanlayarakartırmaya yönelik çalışmalar yapmaktadır. Ayrıca sosyaletki uyandıran parti, festival, gezi etkinliklerine dekulübümüzde yer verilmektedir.",
    "baskan": "Ekrem Ozen",
    "baskan_yardimcisi": "Sami Basaran",
    "uyeler": ["Eren Akay", "Eren Acar", "Feyza Yurtseven", "Elif Cinar", "Olgun", "Irmak"],
    "kurulus_yili": 2012,
    "uye_sayisi": 45,
    "projeler": [
        "Ogrenci Isleri Destek Robotu",
        "Web Tasarim Atölyesi", 
        "Cesitli 101 Egitimleri",
        "Hachaton",
        "Teknofest"
    ],
    "etkinlikler": [
        "WelcomeFest",
        "Social Media Talks", 
        "Hugip Akademi",
        "Digitalmag",
        "FestUp"
    ],
    "iletisim": {
        "email": "hugip@universite.edu.tr",
        "telefon": "0212 123 4567",
        "adres": "Üniversite Kampüsü, B Blok 203"
    },
    "toplanti_gunleri": "Her Salı 14:00-16:00",
    "sosyal_medya": {
        "instagram": "@hugip",
        "linkedin": "HUGIP - Girişimcilik ve Pazarlama Kulübü",
        "twitter": "@hugip_club"
    }
}

# Detayli Etkinlik Bilgileri
EVENT_DETAILS = {
    "WelcomeFest": {
        "name": "WelcomeFest",
        "date": "2025-10-10",
        "time": "14:00-16:00",
        "location": "Haliç Üniversitesi Kampüsü",
        "description": "Öğrencilerin üniversite hayatıyla ilgili sıkça sorduğu sorulara anında cevap verebilen fiziki robot"
    },
    "Social Media Talks": {
        "name": "Social Media Talks",
        "date": "2025-10-11",
        "time": "14:00-16:00",
        "location": "Haliç Üniversitesi Kampüsü",
        "description": """Sosyal medyanın günümüzün en büyük girişimlerinden biri olduğuna
            inandığımız için düzenlediğimiz bu etkinlikte, milyonlarca takipçiye
            sahip sosyal medya fenomenleri ve ünlü isimleri konuk ediyoruz.
            20'den fazla sponsor desteğiyle gerçekleşen bu etkinlik,
            üniversitemizin tarihinde en çok ses getiren ve en yüksek etkileşimi
            sağlayan organizasyon olmuştur.
            """
    },
    "Hugip Akademi": {
        "name": "Hugip Akademi",
        "date": "2025-10-12",
        "time": "14:00-16:00",
        "location": "Haliç Üniversitesi Kampüsü",
        "description": """Kulübümüz öncülüğünde düzenlenen, borsa, e-ticaret, girişimcilik,
            yazılım gibi birçok teknik konuda alanında uzman isimlerin katılımıyla
            gerçekleştirilen özel bir eğitim etkinliğidir. Bu etkinlikte, kariyerlerinde
            önemli adımlar atmak isteyen üniversiteli arkadaşlarımıza, sektörün önde
            gelen profesyonellerinden aldıkları eğitimlerle iş dünyasına
            hazırlanmaları için eşsiz bir fırsat sunuyoruz. Katılımcılar, teorik bilgilerini
            pratiğe dökme şansı bulurken, gelecekteki kariyerleri için sağlam
            temeller atabilecekleri değerli bir deneyim elde etmektedirler.
            """
    },
    "Digitalmag": {
        "name": "Digitalmag",
        "date": "2025-10-13",
        "time": "14:00-16:00",
        "location": "Haliç Üniversitesi Kampüsü",
        "description": """Dijital alanda büyük bir etki yaratmış markalar ile Türkiye
            genelinde başarılarıyla adından söz ettiren ünlü girişimcileri bir
            araya getirerek, yenilikçi ve yıkıcı etkiyi daha da ileri taşımayı
            amaçlayan, üniversite öğrencilerine ilham veren çalışmalar
            sunmayı hedefleyen, bu yıl 5. yaşını kutladığımız
            gelenekselleşmiş etkinliğimizdir.
        """
    },
    "FestUp": {
        "name": "FestUp",
        "date": "2025-10-14",
        "time": "14:00-16:00",
        "location": "Haliç Üniversitesi Kampüsü",
        "description": """Startupları, yatırımcıları ve büyük markaları üniversite öğrencileriyle
            buluşturduğumuz, öğrencilere staj ve iş fırsatları sunarken
            startuplara da kendilerini tanıtma ve geniş bir kitleye ulaşma imkanı
            sağladığımız, ‘Startup Festivali’ konseptiyle düzenlediğimiz en
            büyük etkinliğimizdir. Ayrıca, etkinlik boyunca çeşitli workshoplar
            ve interaktif aktivitelerle katılımcıların kişisel ve profesyonel
            gelişimine katkıda bulunulmaktadır."""
    }
}

# Detaylı Proje Bilgileri
PROJECT_DETAILS = {
    "ogrenci_isleri_robotu": {
        "name": "Öğrenci İşleri Yardımcı Robotu",
        "category": "Yazılım ve Uygulama Geliştirme",
        "description": "Öğrencilerin üniversite hayatıyla ilgili sıkça sorduğu sorulara anında cevap verebilen fiziki robot",
        "features": [
            "Öğrenci İşleri binasına konumlandırılacak",
            "Üzerinde ekran, hoparlör ve mikrofon barındıracak", 
            "Sesli ve yazılı soru alma özelliği",
            "AI destekli chatbot entegrasyonu",
            "GPT, Claude, Mistral gibi büyük dil modelleri kullanımı"
        ],
        "purpose": "Öğrencilere hızlı bilgi sağlarken dikkat çekici ve inovatif deneyim sunmak",
        "topics": ["ders programı", "akademik takvim", "sınav tarihleri", "belge işlemleri"]
    },
    "web_tasarim_atolyesi": {
        "name": "Web Sitesi Geliştirme Atölyesi", 
        "category": "Eğitim ve Gelişim Atölyeleri",
        "description": "Katılımcıların sıfırdan web sitesi oluşturduğu atölye çalışması",
        "technologies": ["HTML", "CSS", "JavaScript"],
        "level": "Başlangıç seviyesi",
        "format": "Uygulamalı atölye"
    },
    "obs_yoklama": {
        "name": "OBS QR Kod ile Yoklama Sistemi",
        "category": "Yazılım ve Uygulama Geliştirme", 
        "description": "OBS ile entegre çalışan ve derslerde QR kod okutularak yoklama alınmasını sağlayan sistem",
        "integration": "OBS sistemi",
        "method": "QR kod okutma"
    },
    "okul_karti_sistemi": {
        "name": "Okul Kartı Entegrasyon Sistemi",
        "category": "Yazılım ve Uygulama Geliştirme",
        "status": "Düşünülme aşamasında",
        "description": "Kampüs içi yemekhane, ulaşım, kütüphane gibi alanlarda kullanılabilecek akıllı kart sistemi",
        "areas": ["yemekhane", "ulaşım", "kütüphane"],
        "phase": "Araştırma/prototipleme"
    },
    "siber_guvenlik_yarismasi": {
        "name": "Siber Güvenlik Yarışması (CTF)",
        "category": "Yarışmalar ve Hackathon Etkinlikleri",
        "description": "Katılımcıların bir web sitesi üzerindeki şifreleri çözmeye çalıştığı temel siber güvenlik yarışması",
        "type": "CTF (Capture The Flag)",
        "level": "Temel seviye"
    },
    "llm_hackathon": {
        "name": "LLM Hackathon",
        "category": "Yarışmalar ve Hackathon Etkinlikleri", 
        "description": "Büyük dil modelleri kullanılarak yaratıcı çözümlerin geliştirileceği hackathon",
        "models": ["ChatGPT", "Claude", "Mistral"],
        "focus": "Yaratıcı çözüm geliştirme"
    },
    "excel_101": {
        "name": "Excel 101 Eğitimi",
        "category": "Eğitim ve Gelişim Atölyeleri",
        "description": "Excel başlangıç eğitimi",
        "topics": ["temel tablo işlemleri", "formüller", "veri düzenleme"],
        "level": "Başlangıç"
    },
    "github_101": {
        "name": "GitHub 101 Eğitimi", 
        "category": "Eğitim ve Gelişim Atölyeleri",
        "description": "Git ve GitHub platformu temel eğitimi",
        "topics": ["versiyon kontrol", "Git kullanımı", "GitHub'a proje yükleme"],
        "level": "Başlangıç"
    },
    "python_101": {
        "name": "Python 101 Eğitimi",
        "category": "Eğitim ve Gelişim Atölyeleri", 
        "description": "Python programlama dili başlangıç eğitimi",
        "topics": ["değişkenler", "döngüler", "koşullar", "temel Python yapıları"],
        "level": "Başlangıç"
    },
    "linkedin_101": {
        "name": "LinkedIn 101 Eğitimi",
        "category": "Eğitim ve Gelişim Atölyeleri",
        "description": "LinkedIn kullanımı ve kariyer gelişimi eğitimi", 
        "topics": ["profil oluşturma", "etkili içerik paylaşımı", "kariyer ağı kurma"],
        "type": "Farkındalık eğitimi"
    },
    "teknofest_2025": {
        "name": "TEKNOFEST 2025 Yarışma Hedefleri",
        "category": "TEKNOFEST",
        "description": "TEKNOFEST yarışmalarına aktif katılım ile teknoloji alanındaki yetkinlikleri sergileme",
        "categories": [
            {
                "name": "İnsansız Kara Aracı Yarışması",
                "focus": ["otonom sürüş sistemleri", "sensör entegrasyonu", "navigasyon teknolojileri"]
            },
            {
                "name": "Tarım Teknolojileri Yarışması", 
                "focus": ["IoT tabanlı sistemler", "drone destekli tarım çözümleri", "akıllı sulama sistemleri"]
            },
            {
                "name": "TEKNOFEST Robolig Yarışması",
                "focus": ["görev odaklı robotik sistemler", "insan-robot etkileşimi"]
            },
            {
                "name": "Sağlıkta Yapay Zeka Yarışması",
                "focus": ["sağlık sektörü AI uygulamaları", "teşhis destekli sistemler", "hasta takip çözümleri"]
            },
            {
                "name": "Hava Savunma Yarışması", 
                "focus": ["hava savunma sistemleri", "radar teknolojileri", "tehdit tespit algoritmaları"]
            },
            {
                "name": "Dikey İniş Yarışması",
                "focus": ["dikey kalkış/iniş hava araçları", "stabilizasyon sistemleri", "otonom uçuş kontrol"]
            },
            {
                "name": "Helikopter Tasarım Yarışması",
                "focus": ["helikopter aerodinamiği", "rotor tasarımı", "kontrol sistemleri"]
            }
        ],
        "strategy": "Her kategori için ayrı başvuru, ön eleme hazırlığı, ekip oluşturma, detaylı planlama"
    }
}

def get_club_info(info_type):
    """Kulüp hakkında statik bilgileri getirir"""
    
    if info_type == "genel":
        return f"""
        HUGIP - Girişimcilik ve Pazarlama Kulübü
        • Hakkinda: {CLUB_INFO['kulup_hakkinda']}
        • Başkan: {CLUB_INFO['baskan']}
        • Başkan Yardımcısı: {CLUB_INFO['baskan_yardimcisi']} 
        • Kuruluş Yılı: {CLUB_INFO['kurulus_yili']}
        • Üye Sayısı: {CLUB_INFO['uye_sayisi']} kişi
        • Toplantı: {CLUB_INFO['toplanti_gunleri']}
        """
    
    elif info_type == "yonetim":
        return f"""
        Yönetim Kurulu:
        • Başkan: {CLUB_INFO['baskan']}
        • Başkan Yardımcısı: {CLUB_INFO['baskan_yardimcisi']}
        """
        
    elif info_type == "projeler":
        projeler = '\n'.join([f"• {p}" for p in CLUB_INFO['projeler']])
        return f"Aktif Projelerimiz:\n{projeler}"
        
    elif info_type == "etkinlikler":
        etkinlikler = '\n'.join([f"• {e}" for e in CLUB_INFO['etkinlikler']])
        return f"Düzenlediğimiz Etkinlikler:\n{etkinlikler}"
        
    elif info_type == "iletisim":
        return f"""
        İletişim Bilgileri:
        • E-posta: {CLUB_INFO['iletisim']['email']}
        • Telefon: {CLUB_INFO['iletisim']['telefon']}
        • Adres: {CLUB_INFO['iletisim']['adres']}
        • Instagram: {CLUB_INFO['sosyal_medya']['instagram']}
        • LinkedIn: {CLUB_INFO['sosyal_medya']['linkedin']}
        """
        
    elif info_type == "uyeler":
        uyeler = ', '.join(CLUB_INFO['uyeler'])
        return f"Aktif Üyelerimizden Bazıları: {uyeler}"
        
    else:
        return "Bu konuda elimde bilgi yok."


def get_event_details(event_key):
    """Spesifik bir etkinlik hakkında detaylı bilgi getirir"""
    
    event_map = {
        "welcomefest": "WelcomeFest",
        "welcome": "WelcomeFest",
        "social_media": "Social Media Talks",
        "social": "Social Media Talks",
        "talks": "Social Media Talks",
        "hugip_akademi": "Hugip Akademi",
        "akademi": "Hugip Akademi",
        "digitalmag": "Digitalmag",
        "digital": "Digitalmag",
        "festup": "FestUp",
        "fest": "FestUp",
        "startup": "FestUp"
    }
    
    # Etkinlik anahtarını bul
    event_key_lower = event_key.lower()
    actual_key = event_map.get(event_key_lower, event_key)
    
    if actual_key not in EVENT_DETAILS:
        return "Bu etkinlik hakkında detaylı bilgi bulunamadı."
    
    event = EVENT_DETAILS[actual_key]
    
    # Etkinlik detaylarını formatla
    details = f"🎉 **{event['name']}**\n"
    details += f"📅 Tarih: {event['date']}\n"
    details += f"🕐 Saat: {event['time']}\n"
    details += f"📍 Yer: {event['location']}\n\n"
    details += f"📝 Açıklama:\n{event['description'].strip()}\n"
    
    return details


def get_project_details(project_key):
    """Spesifik bir proje hakkında detaylı bilgi getirir"""
    
    project_map = {
        "ogrenci_isleri": "ogrenci_isleri_robotu",
        "robot": "ogrenci_isleri_robotu", 
        "chatbot": "ogrenci_isleri_robotu",
        "web_tasarim": "web_tasarim_atolyesi",
        "web": "web_tasarim_atolyesi",
        "html": "web_tasarim_atolyesi",
        "obs": "obs_yoklama",
        "yoklama": "obs_yoklama", 
        "qr": "obs_yoklama",
        "okul_karti": "okul_karti_sistemi",
        "akilli_kart": "okul_karti_sistemi",
        "siber_guvenlik": "siber_guvenlik_yarismasi",
        "ctf": "siber_guvenlik_yarismasi",
        "hackathon": "llm_hackathon",
        "llm": "llm_hackathon",
        "excel": "excel_101",
        "github": "github_101",
        "git": "github_101",
        "python": "python_101",
        "linkedin": "linkedin_101",
        "teknofest": "teknofest_2025"
    }
    
    # Proje anahtarını bul
    project_key_lower = project_key.lower()
    actual_key = project_map.get(project_key_lower, project_key_lower)
    
    if actual_key not in PROJECT_DETAILS:
        return "Bu proje hakkında detaylı bilgi bulunamadı."
    
    project = PROJECT_DETAILS[actual_key]
    
    # Proje detaylarını formatla
    details = f"📋 **{project['name']}**\n"
    details += f"🏷️ Kategori: {project['category']}\n"
    details += f"📝 Açıklama: {project['description']}\n\n"
    
    # Özel alanları ekle
    if 'features' in project:
        details += "✨ Özellikler:\n"
        for feature in project['features']:
            details += f"• {feature}\n"
        details += "\n"
    
    if 'topics' in project:
        details += "📚 Kapsadığı Konular:\n"
        for topic in project['topics']:
            details += f"• {topic}\n"
        details += "\n"
            
    if 'technologies' in project:
        details += f"💻 Teknolojiler: {', '.join(project['technologies'])}\n"
        
    if 'level' in project:
        details += f"📊 Seviye: {project['level']}\n"
        
    if 'purpose' in project:
        details += f"🎯 Amaç: {project['purpose']}\n"
        
    if 'status' in project:
        details += f"📍 Durum: {project['status']}\n"
        
    if 'categories' in project:  # TEKNOFEST için
        details += "🏆 Hedef Kategoriler:\n"
        for cat in project['categories']:
            details += f"• **{cat['name']}**: {', '.join(cat['focus'])}\n"
        details += f"\n📋 Strateji: {project['strategy']}\n"
    
    return details

# OpenAI Function tanımları
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_club_info",
            "description": "HUGIP kulübü hakkında statik bilgileri getirir",
            "parameters": {
                "type": "object",
                "properties": {
                    "info_type": {
                        "type": "string",
                        "enum": ["genel", "yonetim", "projeler", "etkinlikler", "iletisim", "uyeler"],
                        "description": "Hangi bilgi türü: genel, yonetim, projeler, etkinlikler, iletisim, uyeler"
                    }
                },
                "required": ["info_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_event_details",
            "description": "Spesifik bir etkinlik hakkında detaylı bilgi getirir", 
            "parameters": {
                "type": "object",
                "properties": {
                    "event_key": {
                        "type": "string",
                        "description": "Etkinlik anahtarı: welcomefest, social_media, hugip_akademi, digitalmag, festup, etc."
                    }
                },
                "required": ["event_key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_project_details", 
            "description": "Spesifik bir proje hakkında detaylı bilgi getirir",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Proje anahtarı: ogrenci_isleri, web_tasarim, obs, hackathon, llm, excel, github, python, linkedin, teknofest, robot, chatbot, etc."
                    }
                },
                "required": ["project_key"]
            }
        }
    }
]

system_message = """
Sen HUGIP (Girişimcilik ve Pazarlama Kulübü)'nin AI asistanısın.

Görevlerin:
- Kulübün statik bilgileri için get_club_info fonksiyonunu kullan
- Proje detayları için get_project_details fonksiyonunu kullan  
- Kısa, kibar ve resmi cevaplar ver
- Türkçe karakter kullan
- Eğer fonksiyonlarla bulunamayan bir bilgi sorulursa 'Bu konuda elimde bilgi yok.' de

get_club_info fonksiyonunu şu durumlarda kullan:
- Başkan, yönetim kurulu sorularında → "yonetim"
- Projeler listesi hakkında → "projeler" 
- Etkinlikler hakkında → "etkinlikler"
- İletişim, adres, telefon → "iletisim"
- Üyeler hakkında → "uyeler" 
- Genel bilgi → "genel"

get_project_details fonksiyonunu şu durumlarda kullan:
- Spesifik bir proje hakkında detay istendiğinde
- "robot", "chatbot", "öğrenci işleri" → "ogrenci_isleri"
- "web tasarım", "HTML", "CSS" → "web_tasarim"  
- "OBS", "yoklama", "QR kod" → "obs"
- "hackathon", "LLM" → "hackathon"
- "Excel", "GitHub", "Python", "LinkedIn" → ilgili eğitim
- "TEKNOFEST" → "teknofest"

get_event_details fonksiyonunu şu durumlarda kullan:
- Spesifik bir etkinlik hakkında detay istendiğinde
- "WelcomeFest", "welcome" → "welcomefest"
- "Social Media Talks", "social" → "social_media"
- "Hugip Akademi", "akademi" → "hugip_akademi"
- "Digitalmag", "digital" → "digitalmag"
- "FestUp", "startup festival" → "festup"

Kullanıcı bir projenin detaylarını isterse kesinlikle get_project_details fonksiyonunu kullan.
"""

# HTML Template - Düzeltilmiş versiyon
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HUGIP AI Assistant</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            text-align: center;
            background: linear-gradient(135deg, #007bff, #0056b3);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .chat-container { 
            border: 1px solid #ddd; 
            height: 400px; 
            overflow-y: scroll; 
            padding: 15px; 
            margin-bottom: 10px;
            background: white;
            border-radius: 10px;
        }
        .message { 
            margin-bottom: 15px; 
            padding: 10px;
            border-radius: 8px;
        }
        .user { 
            background-color: #e3f2fd;
            text-align: right;
        }
        .assistant { 
            background-color: #f1f8e9;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        input[type="text"] { 
            flex: 1;
            padding: 12px; 
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button { 
            padding: 12px 24px; 
            background: #007bff; 
            color: white; 
            border: none; 
            cursor: pointer;
            border-radius: 5px;
            font-size: 16px;
        }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 HUGIP AI Assistant</h1>
        <p>Girişimcilik ve Pazarlama Kulübü</p>
    </div>
    
    <div id="chatContainer" class="chat-container">
        <div class="message assistant">
            <strong>Assistant:</strong> Merhaba! HUGIP kulübü hakkında sorularınızı yanıtlamaya hazırım. 
            Başkan, projeler, etkinlikler, iletişim bilgileri hakkında ne öğrenmek istersiniz?
        </div>
    </div>
    
    <div class="input-container">
        <input type="text" id="messageInput" placeholder="Mesajınızı yazın...">
        <button onclick="sendMessage()" id="sendButton">Gönder</button>
    </div>

    <script>
        function sendMessage() {
            var messageInput = document.getElementById('messageInput');
            var sendButton = document.getElementById('sendButton');
            var message = messageInput.value.trim();
            
            if (!message) return;

            addMessage('Sen', message, 'user');
            messageInput.value = '';
            sendButton.disabled = true;
            sendButton.textContent = 'Gönderiliyor...';

            // Önce normal fetch deneyelim
            fetch('/ask', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                addMessage('Assistant', data.answer, 'assistant');
            })
            .catch(function(error) {
                addMessage('Hata', 'Bir hata oluştu. Lütfen tekrar deneyin.', 'assistant');
            })
            .finally(function() {
                sendButton.disabled = false;
                sendButton.textContent = 'Gönder';
                messageInput.focus();
            });
        }

        function addMessage(sender, message, type) {
            var chatContainer = document.getElementById('chatContainer');
            var messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + type;
            messageDiv.innerHTML = '<strong>' + sender + ':</strong> ' + message.replace(/\\n/g, '<br>');
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            return messageDiv;
        }

        // Enter tuşu için event listener
        document.addEventListener('DOMContentLoaded', function() {
            var messageInput = document.getElementById('messageInput');
            messageInput.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            });
            messageInput.focus();
        });
    </script>
</body>
</html>
"""
@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/ask_stream")
def ask_stream():
    user_message = request.args.get("message", "")
    
    def generate():
        try:
            # OpenAI'ye streaming ile istek gönder
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                tools=tools,
                tool_choice="auto",
                stream=True
            )
            
            collected_messages = []
            tool_calls = []
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    collected_messages.append(content)
                    yield f"data: {json.dumps({'content': content})}\n\n"
                
                # Tool call varsa topla
                if chunk.choices[0].delta.tool_calls:
                    tool_calls.extend(chunk.choices[0].delta.tool_calls)
            
            # Eğer tool call varsa işle
            if tool_calls:
                try:
                    # Tool'u çalıştır
                    function_name = tool_calls[0].function.name
                    function_args = json.loads(tool_calls[0].function.arguments)
                    
                    if function_name == "get_club_info":
                        function_response = get_club_info(function_args.get("info_type"))
                    elif function_name == "get_project_details":
                        function_response = get_project_details(function_args.get("project_key"))
                    elif function_name == "get_event_details":
                        function_response = get_event_details(function_args.get("event_key"))
                    else:
                        function_response = "Bu konuda elimde bilgi yok."
                    
                    # Tool sonucunu streaming ile döndür
                    import time
                    words = function_response.split()
                    for word in words:
                        yield f"data: {json.dumps({'content': word + ' '})}\n\n"
                        time.sleep(0.05)  # Yazma hızını ayarla
                        
                except Exception as e:
                    yield f"data: {json.dumps({'content': 'Bir hata oluştu.'})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'content': 'Üzgünüm, bir hata oluştu.'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    user_message = data.get("message", "")
    
    try:
        # OpenAI'ye tools ile birlikte istek gönder
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Eğer AI bir tool çağırmak istiyorsa
        if response_message.tool_calls:
            # Tool'u çalıştır
            tool_call = response_message.tool_calls[0]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name == "get_club_info":
                function_response = get_club_info(function_args.get("info_type"))
            elif function_name == "get_project_details":
                function_response = get_project_details(function_args.get("project_key"))
            elif function_name == "get_event_details":
                function_response = get_event_details(function_args.get("event_key"))
            else:
                function_response = "Bu konuda elimde bilgi yok."
                
            # Tool sonucunu tekrar OpenAI'ye gönder
            second_response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message},
                    response_message,
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response
                    }
                ]
            )
            answer = second_response.choices[0].message.content
        else:
            answer = response_message.content
            
    except Exception as e:
        print(f"Hata: {e}")
        answer = "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin."
    
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)