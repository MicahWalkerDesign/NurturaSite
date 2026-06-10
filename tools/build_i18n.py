#!/usr/bin/env python3
"""
build_i18n.py — generates localized copies of index.html.

Source of truth = the `STRINGS` dict below. Each language entry has the
same keys; the script substitutes {{key}} placeholders in
`tools/index.template.html` and writes the result to {lang}/index.html.

Re-run any time after editing STRINGS or the template:

    python3 tools/build_i18n.py

The script also emits sitemap.xml with one URL per locale (root +
privacy + support; privacy/support are English-only for now, so they
are listed once, not per-locale).

Translation quality: written without a native reviewer. Marketing copy
is faithful to the English intent but a native pass will sharpen
nuance — this is a starting point, not the final version.
"""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / 'tools' / 'index.template.html'

# Order = order they appear in the language switcher. English first.
LANGUAGES = ['en', 'es', 'fr', 'it', 'pt-br', 'ja', 'nl', 'zh-cn', 'ko', 'de']

LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'it': 'Italiano',
    'pt-br': 'Português (BR)',
    'ja': '日本語',
    'nl': 'Nederlands',
    'zh-cn': '简体中文',
    'ko': '한국어',
    'de': 'Deutsch',
}

HREFLANG = {
    'en': 'en',
    'es': 'es',
    'fr': 'fr',
    'it': 'it',
    'pt-br': 'pt-BR',
    'ja': 'ja',
    'nl': 'nl',
    'zh-cn': 'zh-Hans',
    'ko': 'ko',
    'de': 'de',
}

# ─── Strings (the localization dictionary) ─────────────────────────────────

STRINGS: dict[str, dict[str, str]] = {
    # Page-level meta
    'title': {
        'en': "Nurtura — Understand every leap of your baby's development",
        'es': 'Nurtura — Entiende cada salto del desarrollo de tu bebé',
        'fr': 'Nurtura — Comprenez chaque étape du développement de votre bébé',
        'it': 'Nurtura — Capisci ogni fase dello sviluppo del tuo bambino',
        'pt-br': 'Nurtura — Entenda cada salto do desenvolvimento do seu bebê',
        'ja': 'Nurtura — 赤ちゃんの発達の飛躍を理解する',
        'nl': "Nurtura — Begrijp elke ontwikkelingssprong van je baby",
        'zh-cn': 'Nurtura — 读懂宝宝发展的每一次飞跃',
        'ko': 'Nurtura — 아기의 모든 발달 도약을 이해하세요',
        'de': 'Nurtura — Verstehen Sie jeden Entwicklungssprung Ihres Babys',
    },
    'description': {
        'en': "Calm baby tracker for sleep, feeds, milestones and developmental leaps — from pregnancy onwards. AI insights, weekly reports, partner sharing. 1 week free, then €3.99/month. Cancel any time.",
        'es': 'Seguimiento sereno para sueño, tomas, hitos y saltos del desarrollo — desde el embarazo. Análisis con IA, informes semanales, compartir con tu pareja. 1 semana gratis, luego 3,99 €/mes. Cancela cuando quieras.',
        'fr': "Suivi serein du sommeil, des repas, des étapes et des bonds du développement — dès la grossesse. Analyses IA, rapports hebdomadaires, partage avec votre partenaire. 1 semaine gratuite, puis 3,99 €/mois. Résiliable à tout moment.",
        'it': 'Tracker sereno per sonno, pasti, traguardi e salti dello sviluppo — dalla gravidanza in poi. Analisi AI, report settimanali, condivisione con il partner. 1 settimana gratis, poi 3,99 €/mese. Annulla quando vuoi.',
        'pt-br': 'Acompanhamento tranquilo para sono, mamadas, marcos e saltos de desenvolvimento — desde a gravidez. Insights de IA, relatórios semanais, compartilhamento com o parceiro. 1 semana grátis, depois R$ 19,90/mês. Cancele quando quiser.',
        'ja': '妊娠期から始まる、睡眠・授乳・マイルストーン・発達飛躍の穏やかなトラッカー。AIによる気づき、週次レポート、パートナー共有。1週間無料、その後月額500円。いつでも解約可能。',
        'nl': "Rustige tracker voor slaap, voedingen, mijlpalen en ontwikkelingssprongen — vanaf de zwangerschap. AI-inzichten, weekrapporten, delen met je partner. 1 week gratis, daarna €3,99/maand. Altijd opzegbaar.",
        'zh-cn': '从孕期开始，平静地记录宝宝的睡眠、喂养、里程碑与发展飞跃。AI 洞察、每周报告、与伴侣共享。免费 1 周，之后每月 ¥29.9，随时取消。',
        'ko': '임신부터 시작되는 차분한 트래커 — 수면, 수유, 마일스톤, 발달 도약. AI 인사이트, 주간 리포트, 파트너 공유. 1주 무료, 이후 월 5,500원. 언제든지 해지 가능.',
        'de': "Ruhiger Tracker für Schlaf, Mahlzeiten, Meilensteine und Entwicklungssprünge — ab der Schwangerschaft. KI-Einblicke, Wochenberichte, Teilen mit dem Partner. 1 Woche gratis, danach 3,99 €/Monat. Jederzeit kündbar.",
    },

    # Nav
    'nav_features': {'en': 'Features', 'es': 'Funciones', 'fr': 'Fonctions', 'it': 'Funzioni', 'pt-br': 'Recursos', 'ja': '機能', 'nl': 'Functies', 'zh-cn': '功能', 'ko': '기능', 'de': 'Funktionen'},
    'nav_pregnancy': {'en': 'Pregnancy', 'es': 'Embarazo', 'fr': 'Grossesse', 'it': 'Gravidanza', 'pt-br': 'Gravidez', 'ja': '妊娠', 'nl': 'Zwangerschap', 'zh-cn': '孕期', 'ko': '임신', 'de': 'Schwangerschaft'},
    'nav_premium': {'en': 'Premium', 'es': 'Premium', 'fr': 'Premium', 'it': 'Premium', 'pt-br': 'Premium', 'ja': 'プレミアム', 'nl': 'Premium', 'zh-cn': '高级版', 'ko': '프리미엄', 'de': 'Premium'},
    'nav_privacy': {'en': 'Privacy', 'es': 'Privacidad', 'fr': 'Confidentialité', 'it': 'Privacy', 'pt-br': 'Privacidade', 'ja': 'プライバシー', 'nl': 'Privacy', 'zh-cn': '隐私', 'ko': '개인정보', 'de': 'Datenschutz'},
    'nav_cta': {'en': 'Get the app', 'es': 'Obtener la app', 'fr': "Télécharger l'app", 'it': "Scarica l'app", 'pt-br': 'Baixe o app', 'ja': 'アプリを入手', 'nl': 'Download de app', 'zh-cn': '获取应用', 'ko': '앱 받기', 'de': 'App holen'},

    # Hero
    'hero_badge': {'en': 'nurtura ✦ baby insights', 'es': 'nurtura ✦ insights del bebé', 'fr': 'nurtura ✦ insights bébé', 'it': 'nurtura ✦ insight del bebè', 'pt-br': 'nurtura ✦ insights do bebê', 'ja': 'nurtura ✦ ベビーインサイト', 'nl': 'nurtura ✦ baby-inzichten', 'zh-cn': 'nurtura ✦ 宝宝洞察', 'ko': 'nurtura ✦ 베이비 인사이트', 'de': 'nurtura ✦ baby-insights'},
    'hero_title_line1': {'en': 'Every baby develops in leaps.', 'es': 'Cada bebé se desarrolla a saltos.', 'fr': 'Chaque bébé évolue par bonds.', 'it': 'Ogni bambino cresce a salti.', 'pt-br': 'Todo bebê se desenvolve em saltos.', 'ja': 'すべての赤ちゃんは飛躍的に成長します。', 'nl': 'Elke baby ontwikkelt in sprongen.', 'zh-cn': '每个宝宝都是跳跃式成长。', 'ko': '모든 아기는 도약으로 자랍니다.', 'de': 'Jedes Baby entwickelt sich in Sprüngen.'},
    'hero_title_line2': {'en': 'Understand yours.', 'es': 'Entiende los del tuyo.', 'fr': 'Comprenez ceux du vôtre.', 'it': 'Capisci quelli del tuo.', 'pt-br': 'Entenda os do seu.', 'ja': 'あなたの赤ちゃんを理解しましょう。', 'nl': 'Begrijp die van jou.', 'zh-cn': '读懂你家宝宝。', 'ko': '우리 아이의 도약을 이해하세요.', 'de': 'Verstehen Sie die Ihres Kindes.'},
    'hero_sub': {
        'en': 'Calm baby tracker for sleep, feeds & milestones — from pregnancy onwards. AI insights, weekly reports & partner sharing. 1 week free, then €3.99/month. Cancel any time.',
        'es': 'Seguimiento sereno para sueño, tomas e hitos — desde el embarazo. Análisis con IA, informes semanales y compartir con tu pareja. 1 semana gratis, luego 3,99 €/mes. Cancela cuando quieras.',
        'fr': "Suivi serein du sommeil, des repas et des étapes — dès la grossesse. Analyses IA, rapports hebdomadaires et partage avec votre partenaire. 1 semaine gratuite, puis 3,99 €/mois. Résiliable à tout moment.",
        'it': "Tracker sereno per sonno, pasti e traguardi — dalla gravidanza in poi. Analisi AI, report settimanali e condivisione con il partner. 1 settimana gratis, poi 3,99 €/mese. Annulla quando vuoi.",
        'pt-br': 'Acompanhamento tranquilo para sono, mamadas e marcos — desde a gravidez. Insights de IA, relatórios semanais e compartilhamento com o parceiro. 1 semana grátis, depois R$ 19,90/mês. Cancele quando quiser.',
        'ja': '妊娠期から始まる、睡眠・授乳・マイルストーンの穏やかなトラッカー。AIインサイト、週次レポート、パートナー共有。1週間無料、その後月額500円。いつでも解約可能。',
        'nl': "Rustige tracker voor slaap, voedingen en mijlpalen — vanaf de zwangerschap. AI-inzichten, weekrapporten en delen met je partner. 1 week gratis, daarna €3,99/maand. Altijd opzegbaar.",
        'zh-cn': '从孕期开始，平静地记录宝宝的睡眠、喂养与里程碑。AI 洞察、每周报告、与伴侣共享。免费 1 周，之后每月 ¥29.9，随时取消。',
        'ko': '임신부터 시작되는 차분한 트래커 — 수면, 수유, 마일스톤. AI 인사이트, 주간 리포트, 파트너 공유. 1주 무료, 이후 월 5,500원. 언제든지 해지 가능.',
        'de': "Ruhiger Tracker für Schlaf, Mahlzeiten und Meilensteine — ab der Schwangerschaft. KI-Einblicke, Wochenberichte und Teilen mit dem Partner. 1 Woche gratis, danach 3,99 €/Monat. Jederzeit kündbar.",
    },
    'cta_eyebrow': {'en': 'Download on the', 'es': 'Descarga en', 'fr': 'Télécharger sur', 'it': 'Scarica su', 'pt-br': 'Baixe na', 'ja': '入手:', 'nl': 'Downloaden in de', 'zh-cn': '下载于', 'ko': '다운로드:', 'de': 'Laden im'},
    'cta_main': {'en': 'App Store', 'es': 'App Store', 'fr': 'App Store', 'it': 'App Store', 'pt-br': 'App Store', 'ja': 'App Store', 'nl': 'App Store', 'zh-cn': 'App Store', 'ko': 'App Store', 'de': 'App Store'},
    'cta_secondary': {'en': 'See what it does →', 'es': 'Ver qué hace →', 'fr': 'Voir comment ça marche →', 'it': 'Scopri cosa fa →', 'pt-br': 'Veja o que faz →', 'ja': '機能を見る →', 'nl': 'Zien wat het doet →', 'zh-cn': '查看功能 →', 'ko': '기능 보기 →', 'de': 'Sehen, was es kann →'},
    'hero_trust': {
        'en': 'Your data stays on your device. No account required. Pregnancy mode is always free.',
        'es': 'Tus datos se quedan en tu dispositivo. Sin cuenta. El modo embarazo es siempre gratis.',
        'fr': 'Vos données restent sur votre appareil. Aucun compte requis. Le mode grossesse est toujours gratuit.',
        'it': 'I tuoi dati restano sul tuo dispositivo. Nessun account richiesto. La modalità gravidanza è sempre gratuita.',
        'pt-br': 'Seus dados ficam no seu dispositivo. Sem conta. O modo gravidez é sempre grátis.',
        'ja': 'データはあなたのデバイスに保存されます。アカウント不要。妊娠モードは常に無料です。',
        'nl': 'Je gegevens blijven op je apparaat. Geen account nodig. Zwangerschapsmodus is altijd gratis.',
        'zh-cn': '您的数据保留在设备本地，无需账户。孕期模式始终免费。',
        'ko': '데이터는 기기에만 저장됩니다. 계정 불필요. 임신 모드는 언제나 무료입니다.',
        'de': 'Ihre Daten bleiben auf Ihrem Gerät. Kein Konto erforderlich. Schwangerschaftsmodus ist immer kostenlos.',
    },

    # Value props
    'value1_title': {'en': "See the current leap", 'es': 'Ve el salto actual', 'fr': 'Voyez le bond du moment', 'it': 'Vedi il salto in corso', 'pt-br': 'Veja o salto atual', 'ja': '今の発達飛躍を見る', 'nl': 'Zie de huidige sprong', 'zh-cn': '查看当前飞跃阶段', 'ko': '현재 도약 보기', 'de': 'Aktuellen Sprung sehen'},
    'value1_body': {
        'en': "Know which developmental phase your baby is in right now — and why they're acting the way they are.",
        'es': 'Sabe en qué fase del desarrollo está tu bebé ahora mismo — y por qué se comporta así.',
        'fr': 'Sachez dans quelle phase de développement votre bébé se trouve maintenant — et pourquoi il agit ainsi.',
        'it': 'Scopri in quale fase di sviluppo è ora il tuo bambino — e perché si comporta in questo modo.',
        'pt-br': 'Saiba em qual fase de desenvolvimento seu bebê está agora — e por que ele está agindo assim.',
        'ja': '赤ちゃんが今どの発達段階にいるか、なぜそんな様子なのかが分かります。',
        'nl': "Weet in welke ontwikkelingsfase je baby nu zit — en waarom hij zich zo gedraagt.",
        'zh-cn': '了解宝宝现在处于哪个发展阶段——以及为什么会有那些表现。',
        'ko': '우리 아기가 지금 어떤 발달 단계에 있는지, 왜 그렇게 행동하는지 알아보세요.',
        'de': "Wissen Sie, in welcher Entwicklungsphase Ihr Baby gerade ist — und warum es sich so verhält.",
    },
    'value2_title': {'en': "Understand what you're seeing", 'es': 'Entiende lo que ves', 'fr': 'Comprenez ce que vous voyez', 'it': 'Capisci quello che vedi', 'pt-br': 'Entenda o que está vendo', 'ja': '見ていることを理解する', 'nl': 'Begrijp wat je ziet', 'zh-cn': '读懂你看到的一切', 'ko': '지금 보이는 것을 이해하세요', 'de': 'Verstehen, was Sie sehen'},
    'value2_body': {
        'en': 'Fussiness, sleep disruption, clinginess — each leap has a signature. Nurtura maps behaviour to research.',
        'es': 'Irritabilidad, sueño alterado, apego — cada salto tiene su firma. Nurtura conecta el comportamiento con la investigación.',
        'fr': "Pleurs, sommeil perturbé, besoin de proximité — chaque bond a sa signature. Nurtura relie le comportement à la recherche.",
        'it': 'Nervosismo, sonno disturbato, attaccamento — ogni salto ha la sua firma. Nurtura collega il comportamento alla ricerca.',
        'pt-br': 'Manha, sono interrompido, apego — cada salto tem uma assinatura. Nurtura conecta o comportamento à pesquisa.',
        'ja': 'ぐずり、睡眠の乱れ、人見知り — それぞれの飛躍にはサインがあります。Nurturaは行動を研究と結びつけます。',
        'nl': "Gehuil, slaapverstoring, aanhankelijkheid — elke sprong heeft een signatuur. Nurtura koppelt gedrag aan onderzoek.",
        'zh-cn': '哭闹、睡眠紊乱、黏人——每次飞跃都有特征。Nurtura 将行为与研究对应起来。',
        'ko': '보챔, 수면 방해, 매달림 — 각 도약에는 고유한 신호가 있습니다. Nurtura가 행동을 연구와 연결해드립니다.',
        'de': "Quengeln, gestörter Schlaf, Anhänglichkeit — jeder Sprung hat eine Signatur. Nurtura verbindet Verhalten mit Forschung.",
    },
    'value3_title': {'en': 'Know exactly what to do', 'es': 'Sabe exactamente qué hacer', 'fr': 'Sachez exactement quoi faire', 'it': 'Sai esattamente cosa fare', 'pt-br': 'Saiba exatamente o que fazer', 'ja': '何をすべきか分かる', 'nl': 'Weet precies wat te doen', 'zh-cn': '知道该怎么做', 'ko': '무엇을 해야 할지 알 수 있어요', 'de': 'Wissen Sie, was zu tun ist'},
    'value3_body': {
        'en': "Age-specific activities & tips matched to your baby's phase — adapting as you log what you're seeing.",
        'es': 'Actividades y consejos específicos para la edad y la fase de tu bebé — se adaptan a lo que vas registrando.',
        'fr': "Activités et conseils adaptés à l'âge et à la phase de votre bébé — qui s'adaptent à ce que vous notez.",
        'it': "Attività e consigli su misura per l'età e la fase del tuo bambino — si adattano a ciò che registri.",
        'pt-br': "Atividades e dicas específicas para a idade e fase do seu bebê — adaptam-se ao que você registra.",
        'ja': '赤ちゃんの年齢と段階に合わせたアクティビティとヒント — 記録に応じて適応します。',
        'nl': "Leeftijdsgerichte activiteiten en tips afgestemd op de fase van je baby — passen zich aan op wat je registreert.",
        'zh-cn': '针对宝宝当前年龄和发展阶段的活动与建议——随你的记录自动调整。',
        'ko': "아기의 연령과 단계에 맞춘 활동 및 팁 — 기록한 내용에 따라 자동으로 조정됩니다.",
        'de': "Altersspezifische Aktivitäten und Tipps passend zur Phase Ihres Babys — angepasst an das, was Sie protokollieren.",
    },

    # Features section
    'features_eyebrow': {'en': 'FEATURES', 'es': 'FUNCIONES', 'fr': 'FONCTIONS', 'it': 'FUNZIONI', 'pt-br': 'RECURSOS', 'ja': '機能', 'nl': 'FUNCTIES', 'zh-cn': '功能', 'ko': '기능', 'de': 'FUNKTIONEN'},
    'features_title': {
        'en': 'A calm companion for the first 1,000 days.',
        'es': 'Un acompañante sereno para los primeros 1.000 días.',
        'fr': 'Un compagnon serein pour les 1 000 premiers jours.',
        'it': 'Un compagno sereno per i primi 1.000 giorni.',
        'pt-br': 'Um companheiro tranquilo para os primeiros 1.000 dias.',
        'ja': '最初の1000日のための、穏やかな寄り添い。',
        'nl': 'Een rustige metgezel voor de eerste 1.000 dagen.',
        'zh-cn': '陪伴你度过宝宝最初的 1,000 天。',
        'ko': '첫 1,000일을 함께하는 차분한 동반자.',
        'de': 'Ein ruhiger Begleiter für die ersten 1.000 Tage.',
    },
    'features_lead': {
        'en': 'Built for tired hands and busy minds. One-minute check-ins, evidence-based insights, and a timeline that grows with your baby.',
        'es': 'Hecho para manos cansadas y mentes ocupadas. Registros de un minuto, análisis con evidencia y una línea de tiempo que crece con tu bebé.',
        'fr': 'Conçu pour des mains fatiguées et des esprits occupés. Suivi en une minute, analyses fondées sur des preuves, et une chronologie qui grandit avec votre bébé.',
        'it': 'Pensato per mani stanche e menti occupate. Check-in di un minuto, analisi basate sull\'evidenza e una timeline che cresce con il tuo bambino.',
        'pt-br': 'Feito para mãos cansadas e mentes ocupadas. Check-ins de um minuto, insights baseados em evidências e uma linha do tempo que cresce com seu bebê.',
        'ja': '疲れた手と忙しい頭のために設計されました。1分の記録、根拠に基づくインサイト、赤ちゃんと共に育つタイムライン。',
        'nl': 'Gemaakt voor moe handen en drukke hoofden. Check-ins van een minuut, op bewijs gebaseerde inzichten en een tijdlijn die met je baby meegroeit.',
        'zh-cn': '为疲惫的双手与繁忙的大脑而设计。一分钟记录、循证洞察、与宝宝一同成长的时间轴。',
        'ko': '지친 손과 바쁜 마음을 위한 앱입니다. 1분 체크인, 근거 기반 인사이트, 아기와 함께 자라는 타임라인.',
        'de': 'Entwickelt für müde Hände und beschäftigte Köpfe. Ein-Minuten-Check-ins, evidenzbasierte Einblicke und eine Zeitleiste, die mit Ihrem Baby wächst.',
    },
    'feature1_title': {'en': 'Daily check-in in seconds', 'es': 'Registro diario en segundos', 'fr': 'Check-in quotidien en quelques secondes', 'it': 'Check-in quotidiano in pochi secondi', 'pt-br': 'Check-in diário em segundos', 'ja': '数秒で完了する毎日の記録', 'nl': 'Dagelijkse check-in in seconden', 'zh-cn': '几秒钟完成每日记录', 'ko': '몇 초면 끝나는 매일 체크인', 'de': 'Tägliches Check-in in Sekunden'},
    'feature1_body': {
        'en': 'Tap the big "All good today" button for routine days. Or capture sleep, fussiness, clinginess, and appetite with three-tap sliders. A streak counter celebrates consistency.',
        'es': 'Pulsa el botón "Todo bien hoy" para días normales. O registra sueño, irritabilidad, apego y apetito con deslizadores de tres toques. Un contador de racha celebra la constancia.',
        'fr': "Touchez « Tout va bien aujourd'hui » pour les journées ordinaires. Ou enregistrez sommeil, pleurs, attachement et appétit en trois touches. Un compteur de série célèbre la régularité.",
        'it': 'Tocca "Tutto bene oggi" per le giornate normali. Oppure registra sonno, nervosismo, attaccamento e appetito con slider a tre tap. Un contatore di serie celebra la costanza.',
        'pt-br': 'Toque em "Tudo bem hoje" para dias rotineiros. Ou registre sono, manha, apego e apetite com sliders de três toques. Um contador de sequência celebra a constância.',
        'ja': 'いつもの日は「今日は順調」ボタンを1タップ。睡眠、ぐずり、人見知り、食欲も3タップで記録。継続日数カウンターが習慣化を後押しします。',
        'nl': 'Tik op "Vandaag alles goed" voor gewone dagen. Of leg slaap, gehuil, aanhankelijkheid en eetlust vast met sliders van drie tikken. Een reeks-teller viert consistentie.',
        'zh-cn': '日常用一键「今天一切都好」记录。或用三键滑块捕捉睡眠、烦躁、黏人与食欲。连续天数计数让习惯更稳。',
        'ko': '평범한 날은 "오늘 좋아요" 한 번이면 끝. 수면, 보챔, 매달림, 식욕은 3-탭 슬라이더로 기록하세요. 연속 일수 카운터로 꾸준함을 응원합니다.',
        'de': 'Tippen Sie auf "Heute alles gut" für gewöhnliche Tage. Oder erfassen Sie Schlaf, Unruhe, Anhänglichkeit und Appetit mit Drei-Tipp-Slidern. Ein Streak-Zähler feiert Beständigkeit.',
    },
    'feature2_title': {'en': 'AI insights, personalised', 'es': 'Análisis con IA, personalizados', 'fr': 'Analyses IA personnalisées', 'it': 'Analisi AI personalizzate', 'pt-br': 'Insights de IA, personalizados', 'ja': 'パーソナライズされたAIインサイト', 'nl': 'AI-inzichten, persoonlijk', 'zh-cn': '个性化 AI 洞察', 'ko': '맞춤형 AI 인사이트', 'de': 'KI-Einblicke, persönlich'},
    'feature2_body': {
        'en': 'Nurtura turns your logs into clear insights with confidence and evidence cues — no scary charts, no medical jargon.',
        'es': 'Nurtura convierte tus registros en análisis claros con indicadores de confianza y evidencia — sin gráficos intimidantes ni jerga médica.',
        'fr': "Nurtura transforme vos enregistrements en analyses claires avec indices de confiance et de preuves — sans graphiques effrayants ni jargon médical.",
        'it': 'Nurtura trasforma i tuoi log in analisi chiare con indicatori di affidabilità e evidenza — senza grafici spaventosi né gergo medico.',
        'pt-br': 'A Nurtura transforma seus registros em insights claros com indicadores de confiança e evidência — sem gráficos assustadores nem jargão médico.',
        'ja': 'Nurturaは記録を、信頼度と根拠を伴う分かりやすいインサイトに変えます。怖いグラフや専門用語はありません。',
        'nl': "Nurtura zet je logs om in heldere inzichten met betrouwbaarheids- en bewijsindicatoren — geen enge grafieken, geen medisch jargon.",
        'zh-cn': 'Nurtura 将你的记录化为带有可信度和证据提示的清晰洞察——没有吓人的图表，也没有医学行话。',
        'ko': 'Nurtura는 기록을 신뢰도와 근거가 포함된 명확한 인사이트로 바꿔드립니다. 무서운 차트도, 의학 용어도 없어요.',
        'de': "Nurtura macht aus Ihren Logs klare Einblicke mit Konfidenz- und Evidenzhinweisen — keine furchteinflößenden Diagramme, kein medizinischer Jargon.",
    },
    'feature3_title': {'en': 'The full leap journey', 'es': 'El viaje completo de los saltos', 'fr': 'Le parcours complet des bonds', 'it': "L'intero viaggio dei salti", 'pt-br': 'Toda a jornada de saltos', 'ja': '飛躍の全旅路', 'nl': 'De volledige sprongreis', 'zh-cn': '完整的飞跃旅程', 'ko': '도약의 전체 여정', 'de': 'Die ganze Sprung-Reise'},
    'feature3_body': {
        'en': 'See every developmental phase from newborn to toddler, with sources and activity packs you can do today.',
        'es': 'Ve cada fase del desarrollo desde recién nacido hasta los primeros pasos, con fuentes y packs de actividades para hoy.',
        'fr': "Visualisez chaque phase de développement, du nouveau-né au tout-petit, avec sources et packs d'activités pour aujourd'hui.",
        'it': 'Vedi ogni fase di sviluppo dal neonato al bambino piccolo, con fonti e pacchetti di attività da fare oggi.',
        'pt-br': 'Veja cada fase de desenvolvimento, do recém-nascido aos primeiros passos, com fontes e pacotes de atividades para hoje.',
        'ja': '新生児から幼児期までのすべての発達段階を、出典と今日できるアクティビティパックと共に。',
        'nl': "Zie elke ontwikkelingsfase van pasgeboren tot peuter, met bronnen en activiteitenpakketten voor vandaag.",
        'zh-cn': '从新生儿到学步期的每一个发展阶段，附带研究来源和今日活动包。',
        'ko': '신생아부터 유아기까지 모든 발달 단계를, 근거 자료와 오늘 할 수 있는 활동 팩과 함께 보세요.',
        'de': "Sehen Sie jede Entwicklungsphase vom Neugeborenen bis zum Kleinkind — mit Quellen und Aktivitätspaketen für heute.",
    },
    'feature4_title': {'en': 'Partner sharing', 'es': 'Compartir con la pareja', 'fr': 'Partage avec le partenaire', 'it': 'Condivisione con il partner', 'pt-br': 'Compartilhamento com o parceiro', 'ja': 'パートナー共有', 'nl': 'Delen met je partner', 'zh-cn': '与伴侣共享', 'ko': '파트너 공유', 'de': 'Partner-Sharing'},
    'feature4_body': {
        'en': 'Invite your partner or any caregiver with a 6-character code. Same timeline, same insights — everyone on the same page.',
        'es': 'Invita a tu pareja o a cualquier cuidador con un código de 6 caracteres. Misma línea de tiempo, mismos análisis — todos coordinados.',
        'fr': 'Invitez votre partenaire ou tout autre soignant avec un code à 6 caractères. Même chronologie, mêmes analyses — tout le monde sur la même longueur d\'onde.',
        'it': 'Invita il partner o qualsiasi caregiver con un codice di 6 caratteri. Stessa timeline, stessi insight — tutti allineati.',
        'pt-br': 'Convide o parceiro ou qualquer cuidador com um código de 6 caracteres. Mesma linha do tempo, mesmos insights — todos no mesmo lugar.',
        'ja': '6文字のコードで、パートナーや育児に関わる人を招待。同じタイムライン、同じインサイトで全員が同じ視点に。',
        'nl': "Nodig je partner of een verzorger uit met een 6-cijferige code. Dezelfde tijdlijn, dezelfde inzichten — iedereen op één lijn.",
        'zh-cn': '用 6 位邀请码邀请伴侣或其他照护者。同一时间轴、同一洞察——全家步调一致。',
        'ko': '6자리 코드로 파트너나 보호자를 초대하세요. 같은 타임라인, 같은 인사이트로 모두가 한 페이지에.',
        'de': "Laden Sie Ihren Partner oder eine Betreuungsperson mit einem 6-stelligen Code ein. Gleiche Zeitleiste, gleiche Einblicke — alle auf demselben Stand.",
    },
    'feature5_title': {'en': 'Local-first & private', 'es': 'Local primero y privado', 'fr': 'Local d\'abord, privé', 'it': 'Locale prima di tutto, e privato', 'pt-br': 'Local primeiro, e privado', 'ja': 'ローカルファースト、プライバシー重視', 'nl': 'Lokaal eerst, privé', 'zh-cn': '本地优先，隐私至上', 'ko': '로컬 우선, 개인정보 보호', 'de': 'Lokal zuerst, privat'},
    'feature5_body': {
        'en': 'Your data stays on your device by default. No account required to use Nurtura. Optional cloud sync when you sign in.',
        'es': 'Tus datos se quedan en tu dispositivo por defecto. No hace falta cuenta para usar Nurtura. Sincronización en la nube opcional al iniciar sesión.',
        'fr': "Vos données restent par défaut sur votre appareil. Aucun compte requis pour utiliser Nurtura. Synchronisation cloud optionnelle à la connexion.",
        'it': 'I tuoi dati restano sul dispositivo per impostazione predefinita. Nessun account necessario per usare Nurtura. Sincronizzazione cloud opzionale al login.',
        'pt-br': 'Seus dados ficam no seu dispositivo por padrão. Sem conta para usar a Nurtura. Sincronização na nuvem opcional ao entrar.',
        'ja': 'デフォルトでデータはデバイスに残ります。Nurturaの利用にアカウントは不要。サインイン時にクラウド同期も選択できます。',
        'nl': "Je gegevens blijven standaard op je apparaat. Geen account nodig om Nurtura te gebruiken. Optionele cloudsynchronisatie als je inlogt.",
        'zh-cn': '默认情况下，您的数据保留在设备本地。使用 Nurtura 无需账户。登录后可选择云同步。',
        'ko': '기본적으로 데이터는 기기에 머뭅니다. Nurtura를 사용하는 데 계정이 필요 없습니다. 로그인 시 선택적 클라우드 동기화도 가능합니다.',
        'de': "Ihre Daten bleiben standardmäßig auf Ihrem Gerät. Kein Konto erforderlich. Optionale Cloud-Synchronisierung beim Anmelden.",
    },

    # Pregnancy section
    'preg_eyebrow': {'en': 'FROM PREGNANCY ONWARDS', 'es': 'DESDE EL EMBARAZO EN ADELANTE', 'fr': "DÈS LA GROSSESSE", 'it': 'DALLA GRAVIDANZA IN POI', 'pt-br': 'DESDE A GRAVIDEZ', 'ja': '妊娠期からずっと', 'nl': 'VANAF DE ZWANGERSCHAP', 'zh-cn': '从孕期开始', 'ko': '임신부터 시작해', 'de': 'AB DER SCHWANGERSCHAFT'},
    'preg_title_line1': {'en': 'Start before birth.', 'es': 'Empieza antes del nacimiento.', 'fr': 'Commencez avant la naissance.', 'it': 'Inizia prima della nascita.', 'pt-br': 'Comece antes do nascimento.', 'ja': '出産前から始めましょう。', 'nl': 'Begin voor de geboorte.', 'zh-cn': '从分娩前开始。', 'ko': '출산 전부터 시작하세요.', 'de': 'Beginnen Sie vor der Geburt.'},
    'preg_title_line2': {'en': 'Stay through every leap.', 'es': 'Acompaña en cada salto.', 'fr': 'Restez à chaque bond.', 'it': 'Resta in ogni salto.', 'pt-br': 'Acompanhe em cada salto.', 'ja': 'すべての飛躍に寄り添います。', 'nl': 'Blijf bij elke sprong.', 'zh-cn': '陪伴每次飞跃。', 'ko': '모든 도약 곁에 함께합니다.', 'de': 'Bleiben Sie bei jedem Sprung.'},
    'preg_lead': {
        'en': "Most apps make you pick a side — pregnancy or baby. Nurtura follows you through both. Track fetal growth, weekly milestones, and fruit-size comparisons before birth. Switch to newborn mode the day baby arrives.",
        'es': "La mayoría de apps te obliga a elegir — embarazo o bebé. Nurtura te acompaña en los dos. Sigue el crecimiento fetal, los hitos semanales y las comparaciones de tamaño con frutas antes del parto. Cambia al modo recién nacido el día que llegue.",
        'fr': "La plupart des apps vous font choisir — grossesse ou bébé. Nurtura vous suit dans les deux. Suivez la croissance fœtale, les étapes hebdomadaires et les comparaisons à des fruits avant la naissance. Passez en mode nouveau-né le jour de la naissance.",
        'it': "La maggior parte delle app ti fa scegliere — gravidanza o bambino. Nurtura ti segue in entrambe. Monitora la crescita fetale, i traguardi settimanali e i confronti con i frutti prima della nascita. Passa alla modalità neonato il giorno del parto.",
        'pt-br': "A maioria dos apps faz você escolher um lado — gravidez ou bebê. A Nurtura acompanha os dois. Acompanhe o crescimento fetal, marcos semanais e comparações de tamanho com frutas antes do parto. Mude para o modo recém-nascido no dia do nascimento.",
        'ja': "ほとんどのアプリは妊娠と育児のどちらかを選ばせます。Nurturaは両方を通してあなたに寄り添います。出産前は胎児の成長、週ごとのマイルストーン、果物との大きさ比較を記録。誕生の日に新生児モードに自動で切り替わります。",
        'nl': "De meeste apps laten je kiezen — zwangerschap of baby. Nurtura volgt je in beide. Volg foetale groei, wekelijkse mijlpalen en vergelijkingen met fruit voor de geboorte. Schakel naar pasgeborenmodus op de dag dat de baby er is.",
        'zh-cn': "大多数应用让你二选一——孕期或宝宝。Nurtura 陪伴你度过两个阶段。在出生前追踪胎儿生长、每周里程碑、水果大小对照；宝宝出生当日自动切换到新生儿模式。",
        'ko': "대부분 앱은 임신과 육아 중 하나를 골라야 합니다. Nurtura는 두 시기를 모두 함께합니다. 출산 전에는 태아 성장, 주간 마일스톤, 과일 크기 비교를 기록하고, 출산 당일 신생아 모드로 전환됩니다.",
        'de': "Die meisten Apps zwingen Sie zur Wahl — Schwangerschaft oder Baby. Nurtura begleitet Sie durch beides. Verfolgen Sie fetales Wachstum, wöchentliche Meilensteine und Größenvergleiche mit Früchten vor der Geburt. Wechseln Sie am Geburtstag in den Neugeborenenmodus.",
    },
    'preg_check1': {'en': 'Weekly fetal milestones from conception', 'es': 'Hitos fetales semanales desde la concepción', 'fr': 'Étapes fœtales hebdomadaires dès la conception', 'it': 'Traguardi fetali settimanali dal concepimento', 'pt-br': 'Marcos fetais semanais desde a concepção', 'ja': '受胎から始まる週ごとの胎児マイルストーン', 'nl': 'Wekelijkse foetale mijlpalen vanaf de bevruchting', 'zh-cn': '从受孕起的每周胎儿里程碑', 'ko': '수정부터의 주간 태아 마일스톤', 'de': 'Wöchentliche fetale Meilensteine ab der Empfängnis'},
    'preg_check2': {'en': 'Fruit-size comparisons (the calmer ones)', 'es': 'Comparaciones de tamaño con frutas (las más amables)', 'fr': 'Comparaisons avec des fruits (les plus douces)', 'it': 'Confronti con i frutti (i più tranquilli)', 'pt-br': 'Comparações com frutas (as mais calmas)', 'ja': '果物との大きさ比較（やさしい比較）', 'nl': 'Vergelijkingen met fruit (de rustigere)', 'zh-cn': '水果大小对照（更平和的版本）', 'ko': '과일과의 크기 비교 (편안한 표현으로)', 'de': 'Größenvergleiche mit Früchten (die ruhigeren)'},
    'preg_check3': {'en': 'Movement, scan, and appointment logging', 'es': 'Registro de movimientos, ecografías y citas', 'fr': 'Suivi des mouvements, échographies et rendez-vous', 'it': 'Registrazione di movimenti, ecografie e appuntamenti', 'pt-br': 'Registro de movimentos, ultrassons e consultas', 'ja': '胎動・健診・予約の記録', 'nl': 'Registratie van bewegingen, echo\'s en afspraken', 'zh-cn': '记录胎动、产检和预约', 'ko': '태동, 검진, 예약 기록', 'de': 'Erfassung von Bewegungen, Ultraschall und Terminen'},
    'preg_check4': {'en': 'Automatic handover to newborn mode at birth', 'es': 'Cambio automático al modo recién nacido al nacer', 'fr': "Bascule automatique vers le mode nouveau-né à la naissance", 'it': 'Passaggio automatico alla modalità neonato alla nascita', 'pt-br': 'Transição automática para o modo recém-nascido no nascimento', 'ja': '出産時の新生児モードへの自動切替', 'nl': 'Automatische overgang naar pasgeborenmodus bij de geboorte', 'zh-cn': '出生当日自动切换到新生儿模式', 'ko': '출산 시 신생아 모드 자동 전환', 'de': 'Automatischer Wechsel in den Neugeborenenmodus bei der Geburt'},

    # Premium section
    'premium_eyebrow': {'en': 'PREMIUM', 'es': 'PREMIUM', 'fr': 'PREMIUM', 'it': 'PREMIUM', 'pt-br': 'PREMIUM', 'ja': 'プレミアム', 'nl': 'PREMIUM', 'zh-cn': '高级版', 'ko': '프리미엄', 'de': 'PREMIUM'},
    'premium_title': {'en': '1 week free, then €3.99/month.', 'es': '1 semana gratis, luego 3,99 €/mes.', 'fr': '1 semaine gratuite, puis 3,99 €/mois.', 'it': '1 settimana gratis, poi 3,99 €/mese.', 'pt-br': '1 semana grátis, depois R$ 19,90/mês.', 'ja': '1週間無料、その後月額500円。', 'nl': '1 week gratis, daarna €3,99/maand.', 'zh-cn': '免费 1 周，之后每月 ¥29.9。', 'ko': '1주 무료, 이후 월 5,500원.', 'de': '1 Woche gratis, danach 3,99 €/Monat.'},
    'premium_sub': {
        'en': 'Cancel any time. Pregnancy mode stays free, always.',
        'es': 'Cancela cuando quieras. El modo embarazo siempre es gratis.',
        'fr': "Résiliable à tout moment. Le mode grossesse reste toujours gratuit.",
        'it': 'Annulla quando vuoi. La modalità gravidanza è sempre gratuita.',
        'pt-br': 'Cancele quando quiser. O modo gravidez é sempre grátis.',
        'ja': 'いつでも解約可能。妊娠モードは常に無料です。',
        'nl': 'Altijd opzegbaar. Zwangerschapsmodus blijft altijd gratis.',
        'zh-cn': '可随时取消。孕期模式始终免费。',
        'ko': '언제든지 해지 가능. 임신 모드는 언제나 무료.',
        'de': 'Jederzeit kündbar. Schwangerschaftsmodus bleibt immer kostenlos.',
    },
    'pf1_title': {'en': 'AI-detected patterns', 'es': 'Patrones detectados con IA', 'fr': 'Schémas détectés par IA', 'it': 'Pattern rilevati con AI', 'pt-br': 'Padrões detectados por IA', 'ja': 'AIが見つけるパターン', 'nl': 'AI-gedetecteerde patronen', 'zh-cn': 'AI 识别的规律', 'ko': 'AI가 찾아내는 패턴', 'de': 'KI-erkannte Muster'},
    'pf1_body': {
        'en': 'Personalised insights that surface what your logs are saying.',
        'es': 'Análisis personalizados que muestran lo que dicen tus registros.',
        'fr': "Analyses personnalisées qui font émerger ce que vos enregistrements disent.",
        'it': 'Insight personalizzati che fanno emergere ciò che dicono i tuoi log.',
        'pt-br': 'Insights personalizados que mostram o que seus registros estão dizendo.',
        'ja': 'あなたの記録から見える、パーソナルなインサイト。',
        'nl': 'Persoonlijke inzichten die laten zien wat je logs zeggen.',
        'zh-cn': '从你的记录中提炼专属洞察。',
        'ko': '기록에서 드러나는 맞춤 인사이트.',
        'de': 'Personalisierte Einblicke, die zeigen, was Ihre Logs sagen.',
    },
    'pf2_title': {'en': "\"What's coming\" predictions", 'es': 'Predicciones de "lo que viene"', 'fr': 'Prédictions « Ce qui arrive »', 'it': 'Previsioni "Cosa sta arrivando"', 'pt-br': 'Previsões "O que vem aí"', 'ja': '「次に来ること」の予測', 'nl': 'Voorspellingen voor wat komt', 'zh-cn': '「接下来会怎样」预测', 'ko': '"앞으로 올 것"에 대한 예측', 'de': '"Was kommt"-Vorhersagen'},
    'pf2_body': {
        'en': 'See the trend ahead — fussiness peaks, sleep dips, settling windows.',
        'es': 'Ve la tendencia que viene — picos de irritabilidad, bajones de sueño, ventanas de calma.',
        'fr': "Anticipez les tendances — pics de pleurs, baisses de sommeil, fenêtres d'apaisement.",
        'it': 'Vedi la tendenza in arrivo — picchi di nervosismo, cali di sonno, finestre di calma.',
        'pt-br': 'Veja a tendência adiante — picos de manha, quedas de sono, janelas de calma.',
        'ja': 'ぐずりのピーク、睡眠の落ち込み、落ち着きの兆しを先回り。',
        'nl': 'Zie de trend vooraf — pieken in huilen, dips in slaap, kalme momenten.',
        'zh-cn': '提前看到趋势——烦躁高峰、睡眠低谷、平稳期。',
        'ko': '앞으로의 흐름을 미리 — 보챔 정점, 수면 저점, 안정 구간.',
        'de': 'Sehen Sie den Trend voraus — Unruhe-Spitzen, Schlaf-Dellen, ruhige Phasen.',
    },
    'pf3_title': {'en': 'Weekly Nurtura report', 'es': 'Informe semanal Nurtura', 'fr': 'Rapport hebdomadaire Nurtura', 'it': 'Report settimanale Nurtura', 'pt-br': 'Relatório semanal Nurtura', 'ja': '週次Nurturaレポート', 'nl': 'Wekelijks Nurtura-rapport', 'zh-cn': '每周 Nurtura 报告', 'ko': '주간 Nurtura 리포트', 'de': 'Wöchentlicher Nurtura-Bericht'},
    'pf3_body': {
        'en': "A clear summary of your baby's week, delivered with calm.",
        'es': 'Un resumen claro de la semana de tu bebé, con calma.',
        'fr': "Un résumé clair de la semaine de votre bébé, livré avec sérénité.",
        'it': 'Un riassunto chiaro della settimana del tuo bambino, con calma.',
        'pt-br': 'Um resumo claro da semana do seu bebê, com calma.',
        'ja': '赤ちゃんの1週間の、穏やかなまとめ。',
        'nl': 'Een helder overzicht van de week van je baby, rustig gebracht.',
        'zh-cn': '宝宝这一周的清晰小结，平静呈现。',
        'ko': '우리 아기의 한 주를 차분하게 요약해드립니다.',
        'de': "Eine klare Zusammenfassung der Woche Ihres Babys, ruhig vermittelt.",
    },
    'pf4_title': {'en': 'Partner sharing', 'es': 'Compartir con la pareja', 'fr': 'Partage avec le partenaire', 'it': 'Condivisione con il partner', 'pt-br': 'Compartilhamento com o parceiro', 'ja': 'パートナー共有', 'nl': 'Delen met je partner', 'zh-cn': '与伴侣共享', 'ko': '파트너 공유', 'de': 'Partner-Sharing'},
    'pf4_body': {
        'en': 'Co-parent on the same timeline, with the same context.',
        'es': 'Co-crianza en la misma línea de tiempo, con el mismo contexto.',
        'fr': 'Co-parenter sur la même chronologie, avec le même contexte.',
        'it': 'Co-genitorialità sulla stessa timeline, con lo stesso contesto.',
        'pt-br': 'Co-parentalidade na mesma linha do tempo, com o mesmo contexto.',
        'ja': '同じタイムラインと文脈で、共に子育てを。',
        'nl': 'Co-ouderschap op dezelfde tijdlijn, met dezelfde context.',
        'zh-cn': '与伴侣共用同一时间轴，看到同样的上下文。',
        'ko': '같은 타임라인, 같은 맥락으로 함께 육아하세요.',
        'de': 'Co-Elternschaft auf derselben Zeitleiste, mit demselben Kontext.',
    },
    'pf5_title': {'en': 'Pediatrician PDF report', 'es': 'Informe en PDF para el pediatra', 'fr': 'Rapport PDF pour le pédiatre', 'it': 'Report PDF per il pediatra', 'pt-br': 'Relatório em PDF para o pediatra', 'ja': '小児科向けPDFレポート', 'nl': 'PDF-rapport voor de kinderarts', 'zh-cn': '儿科医生 PDF 报告', 'ko': '소아과의용 PDF 리포트', 'de': 'Kinderarzt-PDF-Bericht'},
    'pf5_body': {
        'en': 'A 1-page summary you can hand your doctor at the next visit.',
        'es': 'Un resumen de 1 página que puedes dar a tu médico en la próxima visita.',
        'fr': 'Un résumé d\'une page à remettre à votre médecin lors du prochain rendez-vous.',
        'it': 'Un riassunto di 1 pagina da consegnare al medico alla prossima visita.',
        'pt-br': 'Um resumo de 1 página para entregar ao médico na próxima consulta.',
        'ja': '次の診察で医師に渡せる、1枚にまとめたサマリー。',
        'nl': "Een samenvatting van 1 pagina die je je arts kunt geven bij het volgende bezoek.",
        'zh-cn': '1 页摘要，下次就诊时可直接交给医生。',
        'ko': '다음 진료 때 의사에게 건넬 수 있는 1페이지 요약.',
        'de': "Eine 1-seitige Zusammenfassung, die Sie Ihrem Arzt beim nächsten Besuch geben können.",
    },
    'always_free_label': {'en': 'Always free, forever:', 'es': 'Siempre gratis, para siempre:', 'fr': 'Toujours gratuit, pour toujours :', 'it': 'Sempre gratis, per sempre:', 'pt-br': 'Sempre grátis, para sempre:', 'ja': 'ずっと無料:', 'nl': 'Altijd gratis, voor altijd:', 'zh-cn': '永远免费：', 'ko': '항상 무료:', 'de': 'Immer kostenlos, für immer:'},
    'always_free_body': {
        'en': 'daily logging, phase timeline, activity packs, memories, and the entire pregnancy journey.',
        'es': 'registro diario, línea de tiempo de fases, packs de actividades, recuerdos y todo el viaje del embarazo.',
        'fr': 'enregistrement quotidien, chronologie des phases, packs d\'activités, souvenirs et tout le parcours de grossesse.',
        'it': 'registrazione quotidiana, timeline delle fasi, pacchetti di attività, ricordi e tutto il percorso della gravidanza.',
        'pt-br': 'registro diário, linha do tempo de fases, pacotes de atividades, memórias e toda a jornada da gravidez.',
        'ja': '毎日の記録、段階のタイムライン、アクティビティパック、思い出、そして妊娠期のすべて。',
        'nl': 'dagelijks loggen, fase-tijdlijn, activiteitenpakketten, herinneringen en de hele zwangerschapsreis.',
        'zh-cn': '每日记录、阶段时间轴、活动包、回忆，以及整个孕期旅程。',
        'ko': '매일 기록, 단계별 타임라인, 활동 팩, 추억, 그리고 임신 여정 전체.',
        'de': 'tägliches Loggen, Phasen-Zeitleiste, Aktivitätspakete, Erinnerungen und die gesamte Schwangerschaftsreise.',
    },
    'premium_cta': {'en': 'Try free for 7 days →', 'es': 'Prueba gratis 7 días →', 'fr': '7 jours gratuits →', 'it': 'Prova gratis per 7 giorni →', 'pt-br': 'Experimente grátis por 7 dias →', 'ja': '7日間無料で試す →', 'nl': '7 dagen gratis proberen →', 'zh-cn': '免费试用 7 天 →', 'ko': '7일 무료 체험 →', 'de': '7 Tage gratis testen →'},

    # Privacy strip
    'privacy_title': {'en': 'Built privately by design.', 'es': 'Privado por diseño.', 'fr': 'Privé par conception.', 'it': 'Privato per scelta progettuale.', 'pt-br': 'Privado por design.', 'ja': '設計からプライベート。', 'nl': 'Privé door ontwerp.', 'zh-cn': '隐私始于设计。', 'ko': '설계 단계부터 프라이버시.', 'de': 'Privat per Design.'},
    'privacy_body': {
        'en': 'Logs are stored locally on your device first. No tracking pixels, no third-party analytics on parent or baby data, no account required to use the core app. Cloud sync is opt-in and end-to-end protected.',
        'es': 'Los registros se guardan primero en tu dispositivo. Sin píxeles de rastreo, sin analítica de terceros sobre datos del padre/madre o del bebé, sin cuenta para usar la app principal. La sincronización en la nube es opcional y protegida de extremo a extremo.',
        'fr': "Les enregistrements sont stockés d'abord localement sur votre appareil. Pas de pixels de tracking, pas d'analytics tiers sur les données parent ou bébé, aucun compte requis pour l'app principale. La synchronisation cloud est optionnelle et protégée de bout en bout.",
        'it': 'I log sono salvati prima localmente sul tuo dispositivo. Niente pixel di tracking, niente analytics di terze parti sui dati di genitore o bambino, nessun account richiesto per l\'app principale. La sincronizzazione cloud è opzionale e protetta end-to-end.',
        'pt-br': 'Os registros são salvos primeiro no seu dispositivo. Sem pixels de rastreamento, sem analytics de terceiros sobre dados do pai/mãe ou bebê, sem conta para usar o app principal. A sincronização na nuvem é opcional e protegida de ponta a ponta.',
        'ja': '記録はまずあなたのデバイスにローカル保存されます。トラッキングピクセルなし、保護者や赤ちゃんのデータに対する第三者分析なし、コア機能の利用にアカウント不要。クラウド同期は任意かつエンドツーエンドで保護されています。',
        'nl': 'Logs worden eerst lokaal op je apparaat opgeslagen. Geen trackingpixels, geen externe analytics op ouder- of babygegevens, geen account vereist voor de kern-app. Cloudsync is opt-in en end-to-end beschermd.',
        'zh-cn': '记录首先保存在您的设备上。无追踪像素，不对家长或宝宝的数据使用第三方分析，使用核心功能无需账户。云同步可选，端到端加密保护。',
        'ko': '기록은 먼저 기기에 로컬로 저장됩니다. 추적 픽셀 없음, 부모/아기 데이터에 대한 외부 분석 없음, 핵심 기능 사용에 계정 불필요. 클라우드 동기화는 선택이며 종단간 보호됩니다.',
        'de': 'Logs werden zuerst lokal auf Ihrem Gerät gespeichert. Keine Tracking-Pixel, keine Drittanbieter-Analytics auf Eltern- oder Babydaten, kein Konto für die Kern-App nötig. Cloud-Sync ist optional und Ende-zu-Ende geschützt.',
    },
    'privacy_link': {'en': 'Read the full privacy policy →', 'es': 'Lee la política de privacidad completa →', 'fr': 'Lire la politique de confidentialité complète →', 'it': "Leggi l'informativa completa sulla privacy →", 'pt-br': 'Leia a política de privacidade completa →', 'ja': 'プライバシーポリシー全文を読む →', 'nl': 'Lees het volledige privacybeleid →', 'zh-cn': '阅读完整隐私政策 →', 'ko': '전체 개인정보 처리방침 보기 →', 'de': 'Vollständige Datenschutzerklärung lesen →'},

    # Footer
    'footer_app_store': {'en': 'App Store', 'es': 'App Store', 'fr': 'App Store', 'it': 'App Store', 'pt-br': 'App Store', 'ja': 'App Store', 'nl': 'App Store', 'zh-cn': 'App Store', 'ko': 'App Store', 'de': 'App Store'},
    'footer_privacy': {'en': 'Privacy', 'es': 'Privacidad', 'fr': 'Confidentialité', 'it': 'Privacy', 'pt-br': 'Privacidade', 'ja': 'プライバシー', 'nl': 'Privacy', 'zh-cn': '隐私', 'ko': '개인정보', 'de': 'Datenschutz'},
    'footer_support': {'en': 'Support', 'es': 'Soporte', 'fr': 'Support', 'it': 'Supporto', 'pt-br': 'Suporte', 'ja': 'サポート', 'nl': 'Ondersteuning', 'zh-cn': '支持', 'ko': '지원', 'de': 'Support'},
    'footer_contact': {'en': 'Contact', 'es': 'Contacto', 'fr': 'Contact', 'it': 'Contatti', 'pt-br': 'Contato', 'ja': 'お問い合わせ', 'nl': 'Contact', 'zh-cn': '联系', 'ko': '문의', 'de': 'Kontakt'},
    'footer_copy': {
        'en': '© 2026 Micah John Walker · Nurtura is not a medical device and does not diagnose, treat, or replace professional advice.',
        'es': '© 2026 Micah John Walker · Nurtura no es un dispositivo médico y no diagnostica, trata ni sustituye el consejo profesional.',
        'fr': "© 2026 Micah John Walker · Nurtura n'est pas un dispositif médical et ne diagnostique, ne traite ni ne remplace un avis professionnel.",
        'it': "© 2026 Micah John Walker · Nurtura non è un dispositivo medico e non diagnostica, tratta o sostituisce il parere professionale.",
        'pt-br': '© 2026 Micah John Walker · Nurtura não é um dispositivo médico e não diagnostica, trata ou substitui orientação profissional.',
        'ja': '© 2026 Micah John Walker · Nurturaは医療機器ではなく、診断・治療・専門家のアドバイスの代わりにはなりません。',
        'nl': "© 2026 Micah John Walker · Nurtura is geen medisch hulpmiddel en stelt geen diagnose, behandelt niet en vervangt geen professioneel advies.",
        'zh-cn': '© 2026 Micah John Walker · Nurtura 不是医疗设备，不进行诊断、治疗，也不替代专业建议。',
        'ko': '© 2026 Micah John Walker · Nurtura는 의료 기기가 아니며 진단·치료·전문가 조언을 대체하지 않습니다.',
        'de': "© 2026 Micah John Walker · Nurtura ist kein Medizinprodukt und ersetzt keine Diagnose, Behandlung oder professionelle Beratung.",
    },
}


def render_template(template: str, lang: str) -> str:
    """Substitute {{key}} in `template` with STRINGS[key][lang]."""
    def repl(m: re.Match[str]) -> str:
        key = m.group(1).strip()
        try:
            return STRINGS[key][lang]
        except KeyError as e:
            raise KeyError(f"Missing translation for key '{key}' in '{lang}'") from e
    return re.sub(r'\{\{\s*([\w_]+)\s*\}\}', repl, template)


def render_language_switcher(current_lang: str) -> str:
    """Build the language picker dropdown HTML for a given current locale."""
    options = []
    for lang in LANGUAGES:
        # 'en' lives at the site root; everything else lives under /{lang}/
        url = '/' if lang == 'en' else f'/{lang}/'
        selected = ' selected' if lang == current_lang else ''
        options.append(f'      <option value="{url}"{selected}>{LANGUAGE_NAMES[lang]}</option>')
    return '\n'.join(options)


def render_hreflang() -> str:
    """Build alternate-hreflang link tags for the <head>."""
    parts = []
    for lang in LANGUAGES:
        url = 'https://micahwalkerdesign.github.io/NurturaSite/' if lang == 'en' else f'https://micahwalkerdesign.github.io/NurturaSite/{lang}/'
        parts.append(f'  <link rel="alternate" hreflang="{HREFLANG[lang]}" href="{url}" />')
    parts.append('  <link rel="alternate" hreflang="x-default" href="https://micahwalkerdesign.github.io/NurturaSite/" />')
    return '\n'.join(parts)


def build():
    template = TEMPLATE.read_text()

    for lang in LANGUAGES:
        # Pre-substitute the top-level placeholders that aren't in STRINGS,
        # BEFORE the {{key}} regex sweep — otherwise render_template will
        # see them and throw KeyError.
        html = template
        html = html.replace('{{LANG_ATTR}}', HREFLANG[lang])
        html = html.replace('{{ASSET_PREFIX}}', '' if lang == 'en' else '../')
        html = html.replace('{{LANG_SWITCHER}}', render_language_switcher(lang))
        html = html.replace('{{HREFLANG}}', render_hreflang())
        html = render_template(html, lang)

        if lang == 'en':
            out = ROOT / 'index.html'
        else:
            out = ROOT / lang / 'index.html'
            out.parent.mkdir(parents=True, exist_ok=True)

        out.write_text(html)
        print(f'  wrote {out.relative_to(ROOT)}')

    # Build the sitemap with one URL per locale + the two English-only pages
    write_sitemap()
    print('\nDone.')


def write_sitemap():
    today = '2026-06-09'
    base = 'https://micahwalkerdesign.github.io/NurturaSite'

    urls = []
    # Localized index pages — alternate links for each locale
    for lang in LANGUAGES:
        loc = f'{base}/' if lang == 'en' else f'{base}/{lang}/'
        alternates = ''.join(
            f'    <xhtml:link rel="alternate" hreflang="{HREFLANG[l]}" href="{base}/' + ('' if l == 'en' else f'{l}/') + '" />\n'
            for l in LANGUAGES
        )
        urls.append(
            f'  <url>\n'
            f'    <loc>{loc}</loc>\n'
            f'    <lastmod>{today}</lastmod>\n'
            f'    <changefreq>monthly</changefreq>\n'
            f'    <priority>{"1.0" if lang == "en" else "0.9"}</priority>\n'
            f'{alternates}'
            f'  </url>'
        )

    # English-only pages
    urls.append(f'  <url>\n    <loc>{base}/privacy.html</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>yearly</changefreq>\n    <priority>0.4</priority>\n  </url>')
    urls.append(f'  <url>\n    <loc>{base}/support.html</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.5</priority>\n  </url>')

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + '\n'.join(urls)
        + '\n</urlset>\n'
    )
    (ROOT / 'sitemap.xml').write_text(sitemap)


if __name__ == '__main__':
    build()
