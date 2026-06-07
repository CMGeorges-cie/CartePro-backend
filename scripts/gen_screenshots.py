#!/usr/bin/env python3
"""Génère des mockups PNG des écrans CartePro Pro (mobile + API)."""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = "/home/user/CartePro-backend/screenshots"
os.makedirs(OUT, exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
PRIMARY   = (26,  86, 219)   # #1A56DB
SECONDARY = (14, 159, 110)   # #0E9F6E
DANGER    = (224, 36,  36)   # #E02424
WARNING   = (255, 136,   0)  # #FF8800
SURFACE   = (249, 250, 251)  # #F9FAFB
WHITE     = (255, 255, 255)
GRAY_100  = (243, 244, 246)
GRAY_200  = (229, 231, 235)
GRAY_400  = (156, 163, 175)
GRAY_600  = (107, 114, 128)
GRAY_900  = ( 17,  24,  40)
DARK      = ( 17,  24,  40)  # textPrimary

W, H = 390, 844   # iPhone 14 Pro viewport

def font(size, bold=False):
    """Fallback to default if Inter not available."""
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf".format("-Bold" if bold else "")
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0,y0,x1,y1 = xy
    draw.rounded_rectangle([x0,y0,x1,y1], radius=radius, fill=fill, outline=outline, width=width)

def status_bar(draw, dark=False):
    c = WHITE if dark else DARK
    draw.text((20, 14), "9:41", font=font(14, True), fill=c)
    for i,w in enumerate([22,16,10]):
        draw.rounded_rectangle([W-50+i*8, 18, W-50+i*8+6, 18+w], radius=2, fill=c)
    draw.ellipse([W-20, 17, W-8, 29], outline=c, width=2)
    draw.rounded_rectangle([W-18,20,W-10,26], radius=1, fill=c)

def nav_bar(img, draw, selected=0):
    """Bottom nav bar."""
    bar_y = H - 90
    draw.rectangle([0, bar_y, W, H], fill=WHITE)
    draw.line([0, bar_y, W, bar_y], fill=GRAY_200, width=1)
    tabs = [("🏠","Accueil"),("💳","Ma carte"),("👥","CRM"),("✓","Tâches"),("⚙","Réglages")]
    tab_w = W // len(tabs)
    for i,(icon,label) in enumerate(tabs):
        cx = i*tab_w + tab_w//2
        color = PRIMARY if i == selected else GRAY_400
        draw.text((cx, bar_y+10), icon, font=font(22), fill=color, anchor="mt")
        draw.text((cx, bar_y+38), label, font=font(10), fill=color, anchor="mt")
        if i == selected:
            draw.rounded_rectangle([cx-20, bar_y+3, cx+20, bar_y+6], radius=3, fill=PRIMARY)

def gradient_rect(draw, x0, y0, x1, y1, c1, c2):
    """Horizontal gradient approximation."""
    steps = x1 - x0
    for i in range(steps):
        r = int(c1[0] + (c2[0]-c1[0]) * i/steps)
        g = int(c1[1] + (c2[1]-c1[1]) * i/steps)
        b = int(c1[2] + (c2[2]-c1[2]) * i/steps)
        draw.line([(x0+i, y0),(x0+i, y1)], fill=(r,g,b))

def card_shadow(draw, x0,y0,x1,y1,r=16):
    for i in range(6,0,-1):
        alpha = 255 - i*30
        shadow = (0,0,0,max(0,alpha))
        draw.rounded_rectangle([x0-i,y0+i,x1+i,y1+i], radius=r+i,
            fill=(180,180,180,max(20,25-i*3)))

# ══════════════════════════════════════════════════════════════════════════════
# 1. LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def draw_login():
    img = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(img)
    status_bar(draw)

    # Logo
    logo_x, logo_y = W//2-100, 90
    rounded_rect(draw, [logo_x, logo_y, logo_x+48, logo_y+48], 12, fill=PRIMARY)
    draw.text((logo_x+24, logo_y+24), "💳", font=font(24), fill=WHITE, anchor="mm")
    draw.text((logo_x+60, logo_y+14), "CartePro", font=font(22, True), fill=PRIMARY)
    draw.text((logo_x+60, logo_y+36), "Pro", font=font(14), fill=GRAY_600)

    # Heading
    draw.text((24, 168), "Connexion", font=font(26, True), fill=DARK)
    draw.text((24, 200), "Connectez-vous à votre compte", font=font(14), fill=GRAY_600)

    # Fields
    for i,(label,placeholder,y) in enumerate([
        ("Nom d'utilisateur","jean_peintre",248),
        ("Mot de passe","••••••••",320),
    ]):
        draw.text((24, y-18), label, font=font(12), fill=GRAY_600)
        rounded_rect(draw, [24, y, W-24, y+44], 10, fill=WHITE, outline=GRAY_200, width=1)
        draw.text((44, y+12), placeholder, font=font(14), fill=GRAY_400)

    # Button
    rounded_rect(draw, [24, 390, W-24, 440], 10, fill=PRIMARY)
    draw.text((W//2, 415), "Se connecter", font=font(15, True), fill=WHITE, anchor="mm")

    # Link
    draw.text((W//2-65, 462), "Pas encore de compte ?", font=font(13), fill=GRAY_600)
    draw.text((W//2+52, 462), "S'inscrire", font=font(13, True), fill=PRIMARY)

    img.save(f"{OUT}/01_login.png")
    print("✓ 01_login.png")

# ══════════════════════════════════════════════════════════════════════════════
# 2. DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def draw_dashboard():
    img = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(img)
    status_bar(draw)

    # App bar
    draw.rectangle([0, 40, W, 90], fill=WHITE)
    draw.text((20, 56), "Tableau de bord", font=font(18, True), fill=DARK)
    draw.text((W-36, 56), "↺", font=font(20), fill=GRAY_600)

    # Greeting card
    gradient_rect(draw, 16, 100, W-16, 170, PRIMARY, (37,99,235))
    rounded_rect(draw, [16,100,W-16,170], 16, outline=None)
    draw.text((32, 116), "Bon après-midi, jean_peintre !", font=font(15, True), fill=WHITE)
    draw.text((32, 138), "Voici votre résumé CartePro Pro", font=font(13), fill=(200,220,255))
    draw.text((W-56, 122), "💳", font=font(36), fill=WHITE)

    # Stat cards row 1
    for i,(val,label,color) in enumerate([(3,"Contacts",PRIMARY),(0.0,"Conversion",SECONDARY)]):
        x = 16 + i*(W//2-20) + i*8
        rounded_rect(draw, [x, 186, x+W//2-24, 256], 12, fill=WHITE, outline=GRAY_200)
        dot = "👥" if i==0 else "📈"
        draw.text((x+14,198), dot, font=font(20), fill=color)
        draw.text((x+14,222), str(val) if i==0 else "0.0%", font=font(24,True), fill=color)
        draw.text((x+14,248), label, font=font(10), fill=GRAY_600)

    # Stat cards row 2
    for i,(val,label,color) in enumerate([(1,"Tâches auj.",WARNING),(0,"Clients gagnés",SECONDARY)]):
        x = 16 + i*(W//2-20) + i*8
        rounded_rect(draw, [x, 272, x+W//2-24, 342], 12, fill=WHITE, outline=GRAY_200)
        draw.text((x+14,284), "✓" if i==1 else "📋", font=font(20), fill=color)
        draw.text((x+14,308), str(val), font=font(24,True), fill=color)
        draw.text((x+14,334), label, font=font(10), fill=GRAY_600)

    # Pipeline section
    draw.text((20, 360), "Entonnoir de vente", font=font(16, True), fill=DARK)
    rounded_rect(draw, [16, 386, W-16, 530], 12, fill=WHITE, outline=GRAY_200)
    stages = [("Nouveau",0,GRAY_600),("Contacté",1,PRIMARY),("Soumission",0,WARNING),("Gagné",0,SECONDARY),("Perdu",0,DANGER)]
    for i,(label,count,color) in enumerate(stages):
        y = 400 + i*26
        draw.ellipse([28,y+2,38,y+12], fill=color)
        draw.text((50, y), label, font=font(13), fill=DARK)
        draw.text((W-32, y), str(count), font=font(13,True), fill=color, anchor="ra")

    # Quick actions
    draw.text((20, 548), "Accès rapide", font=font(16, True), fill=DARK)
    actions = [("➕\nContact","",""),("📊\nPipeline","",""),("💳\nMa carte","","")]
    aw = (W-48)//3
    for i,(label,_,__) in enumerate(actions):
        x = 16 + i*(aw+8)
        rounded_rect(draw, [x, 574, x+aw, 634], 12, fill=WHITE, outline=GRAY_200)
        lines = label.split("\n")
        draw.text((x+aw//2, 592), lines[0], font=font(20), fill=PRIMARY, anchor="mt")
        draw.text((x+aw//2, 614), lines[1] if len(lines)>1 else "", font=font(10,True), fill=DARK, anchor="mt")

    nav_bar(img, draw, selected=0)
    img.save(f"{OUT}/02_dashboard.png")
    print("✓ 02_dashboard.png")

# ══════════════════════════════════════════════════════════════════════════════
# 3. CARTE NUMÉRIQUE
# ══════════════════════════════════════════════════════════════════════════════
def draw_card():
    img = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(img)
    status_bar(draw)
    draw.rectangle([0,40,W,90], fill=WHITE)
    draw.text((20,56), "Ma carte numérique", font=font(18,True), fill=DARK)
    draw.text((W-50,56), "✏️", font=font(18), fill=PRIMARY)

    # Digital card
    gradient_rect(draw, 16, 100, W-16, 310, PRIMARY, (30,64,175))
    rounded_rect(draw, [16,100,W-16,310], 20, outline=None)

    # Avatar circle
    draw.ellipse([30,118,90,178], fill=(255,255,255,50))
    draw.text((60,148), "JT", font=font(22,True), fill=WHITE, anchor="mm")

    draw.text((102,122), "Jean Tremblay", font=font(18,True), fill=WHITE)
    draw.text((102,144), "Maître Peintre", font=font(13), fill=(200,220,255))
    draw.text((102,162), "Peinture résidentielle", font=font(11), fill=(180,210,255))

    # Active badge
    rounded_rect(draw, [W-86,118,W-24,136], 10, fill=SECONDARY)
    draw.text((W-55,127), "Active", font=font(10,True), fill=WHITE, anchor="mm")

    draw.line([30,192,W-30,192], fill=(255,255,255,60))

    for i,(icon,text) in enumerate([
        ("✉","jean@peinture.ca"),
        ("☎","514-555-0101"),
        ("🌐","jeanpeinture.ca"),
        ("📍","Montréal et Rive-Sud"),
    ]):
        y = 204 + i*22
        draw.text((34,y), icon, font=font(14), fill=(200,220,255))
        draw.text((54,y), text, font=font(13), fill=WHITE)

    draw.text((30,296), "15 ans d'expérience en peinture résidentielle.", font=font(11), fill=(180,210,255))

    # QR section
    rounded_rect(draw, [16,326,W-16,496], 12, fill=WHITE, outline=GRAY_200)
    draw.text((W//2,342), "QR Code de votre carte", font=font(14,True), fill=DARK, anchor="mt")
    draw.text((W//2,360), "Partagez ce code pour recevoir des contacts", font=font(11), fill=GRAY_600, anchor="mt")

    # QR placeholder
    qr_x, qr_y = W//2-70, 374
    qr_size = 140
    draw.rectangle([qr_x,qr_y,qr_x+qr_size,qr_y+qr_size], fill=WHITE)
    # Draw QR-like pattern
    cell = qr_size // 7
    for row in range(7):
        for col in range(7):
            if (row<3 or row>3) and (col<3 or col>3):
                if (row+col) % 2 == 0:
                    draw.rectangle([qr_x+col*cell+1,qr_y+row*cell+1,
                                    qr_x+col*cell+cell-1,qr_y+row*cell+cell-1], fill=DARK)
    # Corner squares
    for (cx,cy) in [(qr_x,qr_y),(qr_x+qr_size-3*cell,qr_y),(qr_x,qr_y+qr_size-3*cell)]:
        draw.rectangle([cx,cy,cx+3*cell,cy+3*cell], fill=DARK)
        draw.rectangle([cx+cell//2,cy+cell//2,cx+3*cell-cell//2,cy+3*cell-cell//2], fill=WHITE)
        draw.rectangle([cx+cell,cy+cell,cx+2*cell,cy+2*cell], fill=PRIMARY)

    rounded_rect(draw, [W//2-60,476,W//2+60,498], 8, fill=GRAY_100)
    draw.text((W//2,487), "📋  Copier le lien", font=font(12,True), fill=PRIMARY, anchor="mm")

    # Social links
    rounded_rect(draw, [16,510,W-16,570], 12, fill=WHITE, outline=GRAY_200)
    draw.text((30,524), "Réseaux & liens", font=font(13,True), fill=DARK)
    chips = ["⭐ Google Avis","💬 WhatsApp","📸 Instagram"]
    x = 30
    for chip in chips:
        w = len(chip)*7+16
        rounded_rect(draw, [x,540,x+w,562], 10, fill=GRAY_100, outline=GRAY_200)
        draw.text((x+w//2,551), chip, font=font(11), fill=DARK, anchor="mm")
        x += w + 8

    nav_bar(img, draw, selected=1)
    img.save(f"{OUT}/03_carte.png")
    print("✓ 03_carte.png")

# ══════════════════════════════════════════════════════════════════════════════
# 4. CONTACTS CRM
# ══════════════════════════════════════════════════════════════════════════════
def draw_contacts():
    img = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(img)
    status_bar(draw)
    draw.rectangle([0,40,W,90], fill=WHITE)
    draw.text((20,56), "Contacts CRM", font=font(18,True), fill=DARK)
    draw.text((W-44,56), "⬆", font=font(18), fill=GRAY_600)

    # Search bar
    rounded_rect(draw, [16,98,W-16,134], 10, fill=WHITE, outline=GRAY_200)
    draw.text((34,116), "🔍", font=font(16), fill=GRAY_400)
    draw.text((58,116), "Rechercher un contact…", font=font(14), fill=GRAY_400, anchor="lm")

    # Stage filters
    filters = [("Tous",True,None),("Nouveau",False,GRAY_600),("Contacté",False,PRIMARY),("Soumission",False,WARNING),("Gagné",False,SECONDARY)]
    x = 16
    for label,selected,color in filters:
        w = len(label)*7+16
        c = color or PRIMARY
        rounded_rect(draw, [x,142,x+w,162], 10, fill=c if selected else WHITE, outline=c if not selected else None)
        draw.text((x+w//2,152), label, font=font(11,True), fill=WHITE if selected else GRAY_400, anchor="mm")
        x += w+6

    # Contact cards
    contacts = [
        ("MC","Marie Côté","Résidences MC","450-555-0202","Laval","contacted",PRIMARY),
        ("JT","Jean Tremblay","Peinture JT","514-555-0101","Montréal","new",GRAY_600),
        ("PL","Paul Lavoie","Électro PL","418-555-0303","Québec","quote_sent",WARNING),
        ("SD","Sophie Dubois","Rénov. SD","438-555-0404","Longueuil","won",SECONDARY),
    ]
    stage_labels = {"new":"Nouveau","contacted":"Contacté","quote_sent":"Soumission","won":"Gagné","lost":"Perdu"}
    for i,(init,name,company,phone,city,stage,color) in enumerate(contacts):
        y = 176 + i*88
        rounded_rect(draw, [16,y,W-16,y+80], 12, fill=WHITE, outline=GRAY_200)
        draw.ellipse([28,y+16,68,y+56], fill=(*PRIMARY,20))
        draw.text((48,y+36), init, font=font(14,True), fill=PRIMARY, anchor="mm")
        draw.text((80,y+18), name, font=font(14,True), fill=DARK)
        draw.text((80,y+36), company, font=font(11), fill=GRAY_600)
        draw.text((80,y+52), phone, font=font(11), fill=GRAY_600)
        # Stage badge
        lbl = stage_labels.get(stage,stage)
        bw = len(lbl)*6+12
        rounded_rect(draw, [W-bw-24,y+18,W-24,y+36], 8, fill=(*color,25))
        draw.text((W-24-bw//2,y+27), lbl, font=font(9,True), fill=color, anchor="mm")
        # City
        draw.text((80,y+62), f"📍 {city}", font=font(10), fill=GRAY_400)

    # FAB
    draw.ellipse([W-68,H-164,W-20,H-116], fill=PRIMARY)
    draw.text((W-44,H-140), "👤+", font=font(18), fill=WHITE, anchor="mm")

    nav_bar(img, draw, selected=2)
    img.save(f"{OUT}/04_contacts.png")
    print("✓ 04_contacts.png")

# ══════════════════════════════════════════════════════════════════════════════
# 5. PIPELINE KANBAN
# ══════════════════════════════════════════════════════════════════════════════
def draw_pipeline():
    img = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(img)
    status_bar(draw)
    draw.rectangle([0,40,W,90], fill=WHITE)
    draw.text((20,56), "Pipeline de vente", font=font(18,True), fill=DARK)
    draw.text((W-44,56), "↺", font=font(20), fill=GRAY_600)

    # Horizontal scroll hint
    draw.text((20,95), "← Faites glisser pour voir toutes les étapes →", font=font(10), fill=GRAY_400)

    # Show 2 full columns + peek of third
    col_w = 190
    cols = [
        ("Contacté",1,PRIMARY,[("MC","Marie Côté","Résidences MC","Laval"),]),
        ("Soumission",2,WARNING,[("PL","Paul Lavoie","Électro PL","Québec"),("SD","Sophie Dubois","Rénov. SD","Longueuil")]),
        ("Gagné",0,SECONDARY,[]),
    ]
    for ci,(label,count,color,cards) in enumerate(cols):
        cx = 16 + ci*(col_w+10)
        col_h = 680
        rounded_rect(draw, [cx,112,cx+col_w,112+col_h], 14, fill=WHITE, outline=GRAY_200)

        # Column header
        rounded_rect(draw, [cx,112,cx+col_w,148], 14, fill=(*color,30))
        draw.ellipse([cx+12,122,cx+22,132], fill=color)
        draw.text((cx+28,128), label, font=font(13,True), fill=color, anchor="lm")
        rounded_rect(draw, [cx+col_w-32,118,cx+col_w-12,142], 10, fill=(*color,40))
        draw.text((cx+col_w-22,130), str(count), font=font(11,True), fill=color, anchor="mm")

        # Cards in column
        for j,(init,name,company,city) in enumerate(cards):
            cy = 158 + j*96
            rounded_rect(draw, [cx+8,cy,cx+col_w-8,cy+88], 10, fill=WHITE, outline=GRAY_200)
            draw.ellipse([cx+16,cy+10,cx+40,cy+34], fill=(*PRIMARY,20))
            draw.text((cx+28,cy+22), init, font=font(11,True), fill=PRIMARY, anchor="mm")
            draw.text((cx+48,cy+12), name, font=font(12,True), fill=DARK)
            draw.text((cx+48,cy+28), company, font=font(10), fill=GRAY_600)
            draw.text((cx+16,cy+48), f"📍 {city}", font=font(10), fill=GRAY_600)
            draw.text((cx+16,cy+66), "☎ Voir détails →", font=font(9), fill=PRIMARY)

        if not cards:
            draw.text((cx+col_w//2,300), "Glissez un\ncontact ici", font=font(12), fill=(*color,80), anchor="mm")

    nav_bar(img, draw, selected=2)
    img.save(f"{OUT}/05_pipeline.png")
    print("✓ 05_pipeline.png")

# ══════════════════════════════════════════════════════════════════════════════
# 6. TÂCHES
# ══════════════════════════════════════════════════════════════════════════════
def draw_tasks():
    img = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(img)
    status_bar(draw)
    draw.rectangle([0,40,W,90], fill=WHITE)
    draw.text((20,56), "Tâches", font=font(18,True), fill=DARK)

    # Tabs
    tabs = [("À faire",True),("Aujourd'hui",False),("En retard",False),("Terminées",False)]
    tab_w = W//len(tabs)
    draw.rectangle([0,90,W,128], fill=WHITE)
    draw.line([0,128,W,128], fill=GRAY_200)
    for i,(label,sel) in enumerate(tabs):
        cx = i*tab_w + tab_w//2
        draw.text((cx,106), label, font=font(12, sel), fill=PRIMARY if sel else GRAY_600, anchor="mm")
        if sel:
            draw.rounded_rectangle([i*tab_w+8,124,i*tab_w+tab_w-8,128], radius=2, fill=PRIMARY)

    # Task items
    tasks = [
        ("Rappeler Marie Côté","Confirmer RDV peinture","haute",WARNING,"06/05",""),
        ("Envoyer soumission Paul","Soumission électricité salon","haute",WARNING,"06/07",""),
        ("Relancer Sophie","Suivi rénovations cuisine","moyenne",PRIMARY,"06/10",""),
        ("Acheter peinture","Home Depot St-Hubert","basse",GRAY_400,"06/15","✓"),
    ]
    for i,(title,desc,prio,pcolor,date,done) in enumerate(tasks):
        y = 142 + i*88
        rounded_rect(draw, [16,y,W-16,y+80], 12, fill=WHITE, outline=GRAY_200)

        # Checkbox
        rounded_rect(draw, [28,y+18,52,y+42], 6, fill=GRAY_100 if not done else SECONDARY, outline=GRAY_400 if not done else SECONDARY)
        if done:
            draw.text((40,y+30), "✓", font=font(14,True), fill=WHITE, anchor="mm")

        # Text
        col = GRAY_400 if done else DARK
        draw.text((62,y+18), title, font=font(13,True), fill=col)
        draw.text((62,y+34), desc, font=font(11), fill=GRAY_600)

        # Priority badge
        pw = len(prio)*7+12
        rounded_rect(draw, [62,y+52,62+pw,y+66], 6, fill=(*pcolor,20))
        draw.text((62+pw//2,y+59), prio, font=font(9,True), fill=pcolor, anchor="mm")

        # Date
        date_color = DANGER if i==0 else GRAY_600
        draw.text((62+pw+10,y+59), f"📅 {date}", font=font(10), fill=date_color, anchor="lm")
        if i==0:
            draw.text((62+pw+80,y+59), "EN RETARD", font=font(8,True), fill=DANGER, anchor="lm")

    # FAB
    draw.ellipse([W-68,H-164,W-20,H-116], fill=PRIMARY)
    draw.text((W-44,H-140), "✓+", font=font(18,True), fill=WHITE, anchor="mm")

    nav_bar(img, draw, selected=3)
    img.save(f"{OUT}/06_taches.png")
    print("✓ 06_taches.png")

# ══════════════════════════════════════════════════════════════════════════════
# 7. RÉGLAGES + ABONNEMENT
# ══════════════════════════════════════════════════════════════════════════════
def draw_settings():
    img = Image.new("RGB", (W, H), SURFACE)
    draw = ImageDraw.Draw(img)
    status_bar(draw)
    draw.rectangle([0,40,W,90], fill=WHITE)
    draw.text((20,56), "Réglages", font=font(18,True), fill=DARK)

    # Profile card
    rounded_rect(draw, [16,100,W-16,196], 16, fill=WHITE, outline=GRAY_200)
    draw.ellipse([32,116,92,176], fill=(*PRIMARY,15))
    draw.text((62,146), "JT", font=font(26,True), fill=PRIMARY, anchor="mm")
    draw.text((104,122), "jean_peintre", font=font(16,True), fill=DARK)
    draw.text((104,142), "jean@peinture.ca", font=font(12), fill=GRAY_600)
    rounded_rect(draw, [104,160,196,178], 10, fill=(*GRAY_400,20))
    draw.text((150,169), "Gratuit", font=font(10,True), fill=GRAY_600, anchor="mm")

    # Subscription card
    draw.text((20,210), "ABONNEMENT", font=font(10,True), fill=GRAY_400)
    rounded_rect(draw, [16,228,W-16,390], 12, fill=WHITE, outline=GRAY_200)
    draw.text((30,244), "⭐", font=font(22), fill=WARNING)
    draw.text((60,246), "Passer à CartePro Pro", font=font(14,True), fill=DARK)
    features = ["• Photos avant/après travaux","• CRM complet (contacts, pipeline, tâches)","• QR premium & stats de scan"]
    for i,f in enumerate(features):
        draw.text((32,274+i*18), f, font=font(12), fill=GRAY_600)

    # Buttons
    rounded_rect(draw, [32,334,W//2-4,362], 8, fill=WHITE, outline=PRIMARY)
    draw.text((W//4+16,348), "15 $/mois", font=font(13,True), fill=PRIMARY, anchor="mm")
    rounded_rect(draw, [W//2+4,334,W-32,362], 8, fill=PRIMARY)
    draw.text((W*3//4-8,348), "120 $/an", font=font(13,True), fill=WHITE, anchor="mm")
    draw.text((W//2,374), "Économisez 60 $ avec le plan annuel ✓", font=font(10), fill=SECONDARY, anchor="mm")

    # Settings list
    draw.text((20,404), "APPLICATION", font=font(10,True), fill=GRAY_400)
    items = [("💳","Ma carte numérique"),("👥","Mes contacts CRM"),("✓","Mes tâches")]
    for i,(icon,label) in enumerate(items):
        y = 422 + i*52
        rounded_rect(draw, [16,y,W-16,y+44], 10, fill=WHITE, outline=GRAY_200)
        draw.text((32,y+22), icon, font=font(18), fill=PRIMARY, anchor="lm")
        draw.text((62,y+22), label, font=font(14), fill=DARK, anchor="lm")
        draw.text((W-32,y+22), "›", font=font(18), fill=GRAY_400, anchor="rm")

    # Logout
    y = 580
    rounded_rect(draw, [16,y,W-16,y+48], 10, fill=WHITE, outline=DANGER)
    draw.text((W//2,y+24), "🚪  Se déconnecter", font=font(14,True), fill=DANGER, anchor="mm")

    nav_bar(img, draw, selected=4)
    img.save(f"{OUT}/07_reglages.png")
    print("✓ 07_reglages.png")

# ══════════════════════════════════════════════════════════════════════════════
# 8. API ENDPOINTS SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
def draw_api():
    W2, H2 = 900, 1400
    img = Image.new("RGB", (W2, H2), (15,23,42))   # dark bg
    draw = ImageDraw.Draw(img)

    # Header
    gradient_rect(draw, 0, 0, W2, 80, PRIMARY, (30,64,175))
    draw.text((32,22), "CartePro Pro — API REST", font=font(22,True), fill=WHITE)
    draw.text((32,50), "v4.0  ·  Flask 3.1  ·  63 tests  ·  Render-ready", font=font(13), fill=(200,220,255))
    draw.text((W2-120,22), "🏥 /health", font=font(13), fill=(200,220,255))
    draw.text((W2-120,42), "→ {status:ok}", font=font(11), fill=SECONDARY)

    groups = [
        ("🔐 Authentification", "/auth", PRIMARY, [
            ("POST","/register","Créer un compte (min 8 cars)"),
            ("POST","/login","Connexion (cookie de session)"),
            ("GET", "/me","Profil utilisateur connecté"),
            ("PUT", "/password","Changer mot de passe"),
            ("POST","/logout","Déconnexion"),
        ]),
        ("💳 Cartes numériques", "/api/v1/cards", (99,102,241), [
            ("GET", "/","Liste des cartes (paginée)"),
            ("POST","/","Créer une carte pro"),
            ("GET", "/:id","Détail carte"),
            ("PUT", "/:id","Modifier carte"),
            ("DELETE","/:id","Supprimer (soft delete)"),
            ("POST","/:id/scan","Enregistrer un scan QR"),
            ("GET", "/:id/scans","Statistiques de scans"),
            ("POST","/api/v1/qr/generate","Générer QR code PNG"),
            ("POST","/:id/photos","Ajouter photo avant/après"),
            ("POST","/:id/quote","Demande de soumission (public)"),
        ]),
        ("📊 CRM", "/api/v1/crm", SECONDARY, [
            ("GET", "/dashboard","Stats pipeline + tâches du jour"),
            ("GET", "/pipeline","Vue kanban (contacts par étape)"),
            ("GET", "/contacts","Liste + search + filtre étape"),
            ("POST","/contacts","Créer contact"),
            ("PUT", "/contacts/:id","Modifier contact"),
            ("PATCH","/contacts/:id/stage","Changer étape pipeline"),
            ("DELETE","/contacts/:id","Supprimer contact"),
            ("POST","/contacts/from-quote/:id","Soumission → Contact"),
            ("POST","/contacts/import","Import CSV FR/EN"),
            ("GET", "/contacts/export","Export CSV"),
            ("POST","/contacts/:id/notes","Ajouter note"),
            ("DELETE","/notes/:id","Supprimer note"),
            ("GET", "/tasks","Tâches (filtres multiples)"),
            ("POST","/tasks","Créer tâche"),
            ("PATCH","/tasks/:id/done","Toggle tâche faite/à faire"),
        ]),
        ("💰 Stripe", "/api/v1/stripe", WARNING, [
            ("GET", "/config","Clé publique + price IDs"),
            ("POST","/create-checkout","Session paiement (monthly/annual)"),
            ("GET", "/portal","Portail facturation client"),
            ("POST","/webhook","Webhooks Stripe"),
        ]),
    ]

    y = 96
    method_colors = {"GET":SECONDARY,"POST":PRIMARY,"PUT":WARNING,"DELETE":DANGER,"PATCH":(168,85,247)}

    for group_label,prefix,gcolor,endpoints in groups:
        # Group header
        draw.rectangle([0,y,W2,y+36], fill=(*gcolor,30))
        draw.text((24,y+10), group_label, font=font(14,True), fill=gcolor)
        draw.text((W2-120,y+10), prefix, font=font(12), fill=(*gcolor,180))
        y += 36

        for method,path,desc in endpoints:
            mc = method_colors.get(method,GRAY_400)
            draw.rectangle([0,y,W2,y+30], fill=(22,33,55) if (endpoints.index((method,path,desc))%2==0) else (18,28,48))
            # Method badge
            mw = len(method)*7+10
            rounded_rect(draw, [24,y+6,24+mw,y+24], 4, fill=(*mc,40))
            draw.text((24+mw//2,y+15), method, font=font(10,True), fill=mc, anchor="mm")
            draw.text((34+mw,y+15), path, font=font(11), fill=WHITE, anchor="lm")
            draw.text((W2-24,y+15), desc, font=font(11), fill=GRAY_400, anchor="rm")
            y += 30

        y += 8

    # Footer
    draw.rectangle([0,y+4,W2,H2], fill=(10,15,30))
    draw.text((24,y+16), "Base URL · Render: https://cartepro-api.onrender.com  ·  Local: http://localhost:5000", font=font(12), fill=GRAY_600)
    draw.text((24,y+36), "Auth: Cookie Flask-Login (SameSite=Lax)  ·  Rate limiting: Flask-Limiter + Redis", font=font(12), fill=GRAY_600)

    img.save(f"{OUT}/08_api_endpoints.png")
    print("✓ 08_api_endpoints.png")

# ══════════════════════════════════════════════════════════════════════════════
# 9. GIF animé (démo)
# ══════════════════════════════════════════════════════════════════════════════
def make_gif():
    frames = []
    screen_files = ["01_login.png","02_dashboard.png","03_carte.png","04_contacts.png","05_pipeline.png","06_taches.png","07_reglages.png"]
    captions = ["🔐 Connexion","📊 Tableau de bord","💳 Carte numérique","👥 CRM Contacts","📈 Pipeline Kanban","✅ Tâches","⚙ Réglages & Stripe"]

    for fname,caption in zip(screen_files, captions):
        path = f"{OUT}/{fname}"
        if not os.path.exists(path):
            continue
        src = Image.open(path).convert("RGB")
        # Scale to 260x564 for GIF (manageable size)
        src = src.resize((260,564), Image.LANCZOS)
        # Add caption bar
        frame = Image.new("RGB",(300,620),(30,41,59))
        frame.paste(src,(20,40))
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle([0,0,300,36],radius=0,fill=(26,86,219))
        d.text((150,18),caption,font=font(13,True),fill=(255,255,255),anchor="mm")
        # Repeat frame for display duration
        for _ in range(4):   # 4 × 0.5s = 2s per screen
            frames.append(frame.copy())

    if frames:
        frames[0].save(
            f"{OUT}/demo_cartepro.gif",
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=500,
            loop=0,
        )
        print("✓ demo_cartepro.gif")

# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Génération des mockups CartePro Pro…")
    draw_login()
    draw_dashboard()
    draw_card()
    draw_contacts()
    draw_pipeline()
    draw_tasks()
    draw_settings()
    draw_api()
    print("GIF animé…")
    make_gif()
    print(f"\nTout sauvegardé dans {OUT}/")
