"""
SocialPulse Monastir - Ajout de données
=======================================
Script pour ajouter rapidement des données d'entraînement. 


"""

import os
import json

# Chemins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(PROJECT_ROOT, 'data', 'processed', 'training_dataset.json')


def load_data():
    """Charge les données existantes."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_data(data):
    """Sauvegarde les données."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_samples():
    """Interface pour ajouter des échantillons."""
    data = load_data()
    
    print("=" * 60)
    print("SOCIALPULSE - Ajout de données d'entraînement")
    print("=" * 60)
    
    # Compter les données actuelles
    counts = {'positive': 0, 'negative': 0, 'neutral':  0}
    for item in data:
        if item['label'] in counts:
            counts[item['label']] += 1
    
    print("\n📊 Données actuelles:")
    print("   ✅ Positive: " + str(counts['positive']))
    print("   ❌ Negative: " + str(counts['negative']))
    print("   ⚪ Neutral:   " + str(counts['neutral']))
    print("   📁 Total:     " + str(len(data)))
    
    print("\n" + "-" * 60)
    print("Entrez vos données.  Tapez 'quit' pour terminer.")
    print("Format: <label> <texte>")
    print("Labels: p (positive), n (negative), u (neutral)")
    print("-" * 60)
    print("\nExemples:")
    print("  p الجو رائع في المنستير")
    print("  n مشكلة كبيرة في الطرقات")
    print("  u غدوة فما ماتش")
    print()
    
    added = 0
    
    while True:
        try: 
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        
        if line.lower() in ['quit', 'exit', 'q', '']:
            if line.lower() in ['quit', 'exit', 'q']: 
                break
            continue
        
        # Parser l'entrée
        parts = line.split(' ', 1)
        if len(parts) < 2:
            print("   ⚠️ Format invalide.  Utilisez: <label> <texte>")
            continue
        
        label_code = parts[0]. lower()
        text = parts[1].strip()
        
        # Convertir le code en label
        label_map = {
            'p': 'positive', 'pos': 'positive', 'positive': 'positive', '+': 'positive',
            'n': 'negative', 'neg': 'negative', 'negative': 'negative', '-':  'negative',
            'u': 'neutral', 'neu': 'neutral', 'neutral': 'neutral', '0': 'neutral'
        }
        
        if label_code not in label_map:
            print("   ⚠️ Label invalide. Utilisez: p, n, ou u")
            continue
        
        label = label_map[label_code]
        
        # Ajouter
        data.append({
            'text': text,
            'label':  label,
            'source': 'manual'
        })
        added += 1
        
        emoji = {'positive': '✅', 'negative': '❌', 'neutral': '⚪'}[label]
        print("   " + emoji + " Ajouté:  " + label)
    
    # Sauvegarder
    if added > 0:
        save_data(data)
        print("\n" + "=" * 60)
        print("✅ " + str(added) + " échantillons ajoutés!")
        print("📁 Total: " + str(len(data)) + " échantillons")
        print("=" * 60)
    else:
        print("\nAucun échantillon ajouté.")


# Données pré-définies à ajouter
NEW_POSITIVE_DATA = [
    # Arabe
    "الجو رائع اليوم في المنستير",
    "المهرجان كان ممتاز برشا",
    "نحب المنستير وشواطئها",
    "الاكل بنين في المطعم",
    "الناس الكل فرحانين",
    "البحر نظيف وجميل",
    "الفندق خدمة ممتازة",
    "رحلة رائعة للمنستير",
    "المدينة القديمة جميلة",
    "الاجواء ممتازة",
    "فريق المنستير ربح الماتش",
    "الحفلة كانت روعة",
    "الشاطئ نظيف ومرتب",
    "الخدمات متوفرة وممتازة",
    "التنظيم كان في المستوى",
    # Arabizi
    "jaw rawaa barcha lyoum",
    "el mahrejen kaan behii",
    "nheb monastir barcha",
    "el akl bniin yasser",
    "nhar jamil fi monastir",
    "el match kaan rawa3",
    "chate2 monastir propre",
    "service mmtez fel hotel",
    "trip zwin lel monastir",
    "ambiance rawaa",
]

NEW_NEGATIVE_DATA = [
    # Arabe  
    "زحمة كبيرة في الطرقات",
    "الترانسبور خايب برشا",
    "مشكلة في النظافة",
    "البحر وسخ والبلاصة خايبة",
    "الخدمات ضعيفة",
    "الاسعار غالية برشا",
    "الفوضى في كل بلاصة",
    "الانتظار طويل برشا",
    "النقل العمومي سيء",
    "الشوارع مهملة",
    "الفريق خسر الماتش",
    "الحفلة كانت خايبة",
    "الاكل ما عجبنيش",
    "الفندق خدمة سيئة",
    "تنظيم فاشل",
    # Arabizi
    "zahma kbira fel trouq",
    "transport khayeb barcha",
    "mochkla fel nadhafa",
    "el bhar wsekh",
    "les services dhayfin",
    "les prix ghalyin",
    "fawdha fi kol blasa",
    "attente twila barcha",
    "match khayeb yasser",
    "el akl moch behi",
]

NEW_NEUTRAL_DATA = [
    # Arabe
    "غدوة فما ماتش في الملعب",
    "المهرجان يبدأ الاسبوع الجاي",
    "الطقس معتدل اليوم",
    "فما اجتماع في البلدية",
    "المحلات تسكر الساعة ثمنية",
    "الباص يوصل كل نص ساعة",
    "السوق الاحد فتحو",
    "المدرسة تبدأ في سبتمبر",
    "الرحلة تاخذ ساعة",
    "الفندق فيه 50 غرفة",
    "المطعم يفتح من الصباح",
    "الشاطئ على بعد كيلومتر",
    "الماتش يبدأ الساعة خمسة",
    "البلدية نظمت اجتماع",
    "المهرجان فيه فنانين من تونس",
    # Arabizi
    "ghodwa fama match fel stade",
    "el mahrejen yabda el jom3a",
    "el taks maatdel lyoum",
    "fama reunion fel baladiya",
    "el bus yousel kol nos se3a",
    "el souq el a7ad maftou7",
    "el trip tekhou se3a",
    "el hotel fih 50 chambre",
    "el restaurant yeftah 8h",
    "el chate2 3la bo3d km",
]


def add_predefined_data():
    """Ajoute les données pré-définies."""
    data = load_data()
    
    print("=" * 60)
    print("SOCIALPULSE - Ajout de données pré-définies")
    print("=" * 60)
    
    initial_count = len(data)
    
    # Ajouter les positives
    for text in NEW_POSITIVE_DATA: 
        data.append({'text': text, 'label':  'positive', 'source':  'predefined'})
    
    # Ajouter les negatives
    for text in NEW_NEGATIVE_DATA:
        data.append({'text': text, 'label': 'negative', 'source': 'predefined'})
    
    # Ajouter les neutres
    for text in NEW_NEUTRAL_DATA: 
        data.append({'text': text, 'label': 'neutral', 'source': 'predefined'})
    
    # Sauvegarder
    save_data(data)
    
    added = len(data) - initial_count
    
    print("\n✅ " + str(added) + " échantillons ajoutés!")
    print("   ✅ Positive: +" + str(len(NEW_POSITIVE_DATA)))
    print("   ❌ Negative: +" + str(len(NEW_NEGATIVE_DATA)))
    print("   ⚪ Neutral:  +" + str(len(NEW_NEUTRAL_DATA)))
    print("\n📁 Total: " + str(len(data)) + " échantillons")


def main():
    print("\n1. Ajouter des données manuellement")
    print("2. Ajouter des données pré-définies (75 nouveaux échantillons)")
    print("3. Quitter")
    
    choice = input("\nVotre choix (1-3): ").strip()
    
    if choice == '1':
        add_samples()
    elif choice == '2':
        add_predefined_data()
    else:
        print("Au revoir!")


if __name__ == "__main__":
    main()