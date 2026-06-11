#!/usr/bin/env python3
"""
build_legal_i18n.py — generates localized privacy + support pages.

Same templating approach as build_i18n.py but for the longer legal
pages. Per-language pages live at:
    {lang}/privacy.html
    {lang}/support.html

The English originals stay at the site root unchanged.

Re-run any time:

    python3 tools/build_legal_i18n.py

Translation quality: written without a native reviewer. Legal-text
accuracy was prioritised over stylistic polish — a native pass should
review BEFORE relying on these for ANY regulated jurisdiction (GDPR
representations etc).
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LANGUAGES = ['es', 'fr', 'it', 'pt-br', 'ja', 'nl', 'zh-cn', 'ko', 'de']

HREFLANG = {
    'en': 'en', 'es': 'es', 'fr': 'fr', 'it': 'it', 'pt-br': 'pt-BR',
    'ja': 'ja', 'nl': 'nl', 'zh-cn': 'zh-Hans', 'ko': 'ko', 'de': 'de',
}

# ─── Per-page section strings ────────────────────────────────────────────────
# Keys are SECTION-grouped to keep the dict manageable. Each language gets
# the same key set. The template references {{key}} placeholders.

# fmt: off

PRIVACY = {
    'page_title': {
        'en': 'Privacy — Nurtura',
        'es': 'Privacidad — Nurtura',
        'fr': 'Confidentialité — Nurtura',
        'it': 'Privacy — Nurtura',
        'pt-br': 'Privacidade — Nurtura',
        'ja': 'プライバシー — Nurtura',
        'nl': 'Privacy — Nurtura',
        'zh-cn': '隐私 — Nurtura',
        'ko': '개인정보 — Nurtura',
        'de': 'Datenschutz — Nurtura',
    },
    'meta_desc': {
        'en': "Nurtura's privacy policy. Local-first by default. No tracking. No third-party analytics on parent or baby data.",
        'es': 'Política de privacidad de Nurtura. Local primero por defecto. Sin rastreo. Sin analítica de terceros sobre datos del padre/madre o del bebé.',
        'fr': "Politique de confidentialité de Nurtura. Local d'abord par défaut. Pas de tracking. Pas d'analytics tiers sur les données parent ou bébé.",
        'it': "Informativa sulla privacy di Nurtura. Locale per impostazione predefinita. Nessun tracking. Nessuna analitica di terze parti sui dati di genitori o bambini.",
        'pt-br': "Política de privacidade da Nurtura. Local por padrão. Sem rastreamento. Sem analytics de terceiros sobre dados de pais ou bebês.",
        'ja': 'Nurturaのプライバシーポリシー。デフォルトでローカルファースト。トラッキングなし。保護者と赤ちゃんのデータに対する第三者分析なし。',
        'nl': "Privacybeleid van Nurtura. Standaard lokaal eerst. Geen tracking. Geen externe analytics op ouder- of babygegevens.",
        'zh-cn': 'Nurtura 隐私政策。默认本地优先。无追踪。不对家长或宝宝数据使用第三方分析。',
        'ko': 'Nurtura 개인정보 처리방침. 기본적으로 로컬 우선. 추적 없음. 부모와 아기 데이터에 대한 외부 분석 없음.',
        'de': "Datenschutzerklärung von Nurtura. Standardmäßig lokal zuerst. Kein Tracking. Keine Drittanbieter-Analytics auf Eltern- oder Babydaten.",
    },
    'eyebrow': {
        'en': 'PRIVACY POLICY', 'es': 'POLÍTICA DE PRIVACIDAD', 'fr': 'POLITIQUE DE CONFIDENTIALITÉ',
        'it': 'INFORMATIVA SULLA PRIVACY', 'pt-br': 'POLÍTICA DE PRIVACIDADE', 'ja': 'プライバシーポリシー',
        'nl': 'PRIVACYBELEID', 'zh-cn': '隐私政策', 'ko': '개인정보 처리방침', 'de': 'DATENSCHUTZERKLÄRUNG',
    },
    'title': {
        'en': 'Your data stays yours.',
        'es': 'Tus datos siguen siendo tuyos.',
        'fr': 'Vos données restent les vôtres.',
        'it': 'I tuoi dati restano tuoi.',
        'pt-br': 'Seus dados continuam seus.',
        'ja': 'あなたのデータは、あなたのものです。',
        'nl': 'Je gegevens blijven van jou.',
        'zh-cn': '您的数据，始终属于您。',
        'ko': '데이터는 여러분의 것입니다.',
        'de': 'Ihre Daten bleiben Ihre.',
    },
    'updated': {
        'en': 'Last updated: June 2026',
        'es': 'Última actualización: junio 2026',
        'fr': 'Dernière mise à jour : juin 2026',
        'it': 'Ultimo aggiornamento: giugno 2026',
        'pt-br': 'Última atualização: junho de 2026',
        'ja': '最終更新: 2026年6月',
        'nl': 'Laatst bijgewerkt: juni 2026',
        'zh-cn': '最近更新：2026 年 6 月',
        'ko': '최종 업데이트: 2026년 6월',
        'de': 'Zuletzt aktualisiert: Juni 2026',
    },
    'section_short_title': {
        'en': 'The short version', 'es': 'En resumen', 'fr': 'En bref', 'it': 'In breve',
        'pt-br': 'Versão curta', 'ja': '簡単な要約', 'nl': 'In het kort', 'zh-cn': '简短版本',
        'ko': '간단히 말하면', 'de': 'Kurzfassung',
    },
    'short_li1': {
        'en': 'Nurtura is <strong>local-first</strong>. Your logs, photos, and child profiles are stored on your device by default.',
        'es': 'Nurtura es <strong>local primero</strong>. Tus registros, fotos y perfiles del bebé se guardan en tu dispositivo por defecto.',
        'fr': "Nurtura est <strong>local d'abord</strong>. Vos enregistrements, photos et profils enfants sont stockés par défaut sur votre appareil.",
        'it': "Nurtura è <strong>locale prima di tutto</strong>. I tuoi log, foto e profili del bambino sono salvati per impostazione predefinita sul tuo dispositivo.",
        'pt-br': "Nurtura é <strong>local primeiro</strong>. Seus registros, fotos e perfis do bebê ficam no seu dispositivo por padrão.",
        'ja': 'Nurturaは<strong>ローカルファースト</strong>。記録、写真、子どものプロフィールはデフォルトでデバイスに保存されます。',
        'nl': "Nurtura is <strong>lokaal eerst</strong>. Je logs, foto's en kindprofielen worden standaard op je apparaat opgeslagen.",
        'zh-cn': 'Nurtura 是<strong>本地优先</strong>的。您的记录、照片和宝宝档案默认保存在设备上。',
        'ko': 'Nurtura는 <strong>로컬 우선</strong>입니다. 기록, 사진, 아이 프로필은 기본적으로 기기에 저장됩니다.',
        'de': "Nurtura ist <strong>lokal zuerst</strong>. Logs, Fotos und Kinderprofile werden standardmäßig auf Ihrem Gerät gespeichert.",
    },
    'short_li2': {
        'en': "You can use the app without creating an account.",
        'es': 'Puedes usar la app sin crear una cuenta.',
        'fr': "Vous pouvez utiliser l'app sans créer de compte.",
        'it': "Puoi usare l'app senza creare un account.",
        'pt-br': 'Você pode usar o app sem criar conta.',
        'ja': 'アカウントを作成しなくてもアプリを利用できます。',
        'nl': 'Je kunt de app gebruiken zonder account.',
        'zh-cn': '无需账户即可使用应用。',
        'ko': '계정을 만들지 않고도 앱을 사용할 수 있습니다.',
        'de': 'Sie können die App ohne Konto verwenden.',
    },
    'short_li3': {
        'en': "Optional cloud sync (via Supabase) keeps your data accessible across devices when you sign in with an email.",
        'es': 'La sincronización opcional en la nube (a través de Supabase) mantiene tus datos accesibles entre dispositivos cuando inicias sesión con un email.',
        'fr': "La synchronisation cloud optionnelle (via Supabase) garde vos données accessibles sur tous vos appareils lorsque vous vous connectez avec un email.",
        'it': "La sincronizzazione cloud opzionale (tramite Supabase) mantiene i tuoi dati accessibili tra dispositivi quando accedi con un'email.",
        'pt-br': "A sincronização opcional na nuvem (via Supabase) mantém seus dados acessíveis entre dispositivos quando você entra com e-mail.",
        'ja': 'オプションのクラウド同期（Supabase経由）により、メールでサインインすればデバイス間でデータにアクセスできます。',
        'nl': "Optionele cloudsynchronisatie (via Supabase) houdt je gegevens toegankelijk op meerdere apparaten als je met een e-mailadres inlogt.",
        'zh-cn': '可选的云同步（通过 Supabase）让您在登录后跨设备访问数据。',
        'ko': '이메일로 로그인하면 선택적 클라우드 동기화(Supabase 기반)를 통해 여러 기기에서 데이터에 접근할 수 있습니다.',
        'de': "Optionale Cloud-Synchronisierung (via Supabase) hält Ihre Daten geräteübergreifend verfügbar, wenn Sie sich mit einer E-Mail-Adresse anmelden.",
    },
    'short_li4': {
        'en': "We don't sell your data. We don't use third-party analytics on parent or baby data.",
        'es': 'No vendemos tus datos. No usamos analítica de terceros sobre datos del padre/madre o del bebé.',
        'fr': "Nous ne vendons pas vos données. Nous n'utilisons pas d'analytics tiers sur les données parent ou bébé.",
        'it': "Non vendiamo i tuoi dati. Non usiamo analitica di terze parti sui dati di genitore o bambino.",
        'pt-br': "Não vendemos seus dados. Não usamos analytics de terceiros sobre dados de pais ou bebês.",
        'ja': 'データを販売しません。保護者や赤ちゃんのデータに第三者分析を使用しません。',
        'nl': "We verkopen je gegevens niet. We gebruiken geen externe analytics op ouder- of babygegevens.",
        'zh-cn': '我们不出售您的数据，也不对家长或宝宝数据使用第三方分析。',
        'ko': '저희는 데이터를 판매하지 않습니다. 부모나 아기 데이터에 외부 분석을 사용하지 않습니다.',
        'de': "Wir verkaufen Ihre Daten nicht. Wir nutzen keine Drittanbieter-Analytics auf Eltern- oder Babydaten.",
    },
    'short_li5': {
        'en': "You can delete everything by removing the app.",
        'es': 'Puedes borrar todo desinstalando la app.',
        'fr': "Vous pouvez tout supprimer en désinstallant l'app.",
        'it': "Puoi cancellare tutto disinstallando l'app.",
        'pt-br': 'Você pode apagar tudo removendo o app.',
        'ja': 'アプリを削除すれば、すべて消去できます。',
        'nl': "Je kunt alles verwijderen door de app te verwijderen.",
        'zh-cn': '卸载应用即可删除所有数据。',
        'ko': '앱을 삭제하면 모든 데이터가 제거됩니다.',
        'de': "Sie können alles löschen, indem Sie die App entfernen.",
    },
    'section_collect_title': {
        'en': "What we collect", 'es': 'Qué recopilamos', 'fr': 'Ce que nous collectons',
        'it': 'Cosa raccogliamo', 'pt-br': 'O que coletamos', 'ja': '収集する情報',
        'nl': 'Wat we verzamelen', 'zh-cn': '我们收集什么', 'ko': '수집하는 정보', 'de': 'Was wir erfassen',
    },
    'collect_lead': {
        'en': "Only what's needed to make the app work:",
        'es': 'Solo lo necesario para que la app funcione:',
        'fr': "Uniquement ce qui est nécessaire au fonctionnement de l'app :",
        'it': "Solo ciò che serve per far funzionare l'app:",
        'pt-br': 'Apenas o necessário para o app funcionar:',
        'ja': 'アプリの動作に必要な情報のみ:',
        'nl': "Alleen wat nodig is om de app te laten werken:",
        'zh-cn': '只收集让应用运作所需的信息：',
        'ko': '앱 동작에 필요한 정보만 수집합니다:',
        'de': "Nur was zum Betrieb der App nötig ist:",
    },
    'collect_li1': {
        'en': "<strong>Child profile data</strong> (name, date of birth, due date, life stage) — entered by you, stored locally.",
        'es': "<strong>Datos del perfil del bebé</strong> (nombre, fecha de nacimiento, fecha estimada, etapa) — introducidos por ti, guardados localmente.",
        'fr': "<strong>Profil de l'enfant</strong> (prénom, date de naissance, date prévue, étape de vie) — saisi par vous, stocké localement.",
        'it': "<strong>Dati del profilo del bambino</strong> (nome, data di nascita, data prevista, fase di vita) — inseriti da te, salvati localmente.",
        'pt-br': "<strong>Dados do perfil do bebê</strong> (nome, data de nascimento, data prevista, fase de vida) — inseridos por você, salvos localmente.",
        'ja': '<strong>お子さまのプロフィール</strong>（名前、生年月日、出産予定日、ライフステージ）— ご本人が入力、ローカルに保存。',
        'nl': "<strong>Kindprofielgegevens</strong> (naam, geboortedatum, uitgerekende datum, levensfase) — door jou ingevoerd, lokaal opgeslagen.",
        'zh-cn': '<strong>宝宝档案数据</strong>（姓名、出生日期、预产期、生命阶段）——由您输入，本地保存。',
        'ko': '<strong>아이 프로필 정보</strong>(이름, 생년월일, 예정일, 생애 단계) — 직접 입력, 로컬에 저장.',
        'de': "<strong>Kinderprofildaten</strong> (Name, Geburtsdatum, errechneter Termin, Lebensphase) — von Ihnen eingegeben, lokal gespeichert.",
    },
    'collect_li2': {
        'en': "<strong>Daily logs</strong> (sleep, fussiness, clinginess, appetite scores; optional notes; optional MCQ signals) — entered by you, stored locally.",
        'es': "<strong>Registros diarios</strong> (sueño, irritabilidad, apego, apetito; notas opcionales; señales MCQ opcionales) — introducidos por ti, guardados localmente.",
        'fr': "<strong>Logs quotidiens</strong> (sommeil, pleurs, attachement, appétit ; notes optionnelles ; signaux QCM optionnels) — saisis par vous, stockés localement.",
        'it': "<strong>Log giornalieri</strong> (sonno, nervosismo, attaccamento, appetito; note opzionali; segnali MCQ opzionali) — inseriti da te, salvati localmente.",
        'pt-br': "<strong>Registros diários</strong> (sono, manha, apego, apetite; notas opcionais; sinais de questionário opcionais) — inseridos por você, salvos localmente.",
        'ja': '<strong>毎日の記録</strong>（睡眠、ぐずり、人見知り、食欲のスコア。任意のメモ、任意のMCQシグナル）— ご本人が入力、ローカルに保存。',
        'nl': "<strong>Dagelijkse logs</strong> (slaap, gehuil, aanhankelijkheid, eetlust; optionele notities; optionele MCQ-signalen) — door jou ingevoerd, lokaal opgeslagen.",
        'zh-cn': '<strong>每日记录</strong>（睡眠、烦躁、黏人、食欲分数；可选备注；可选 MCQ 信号）——由您输入，本地保存。',
        'ko': '<strong>일일 기록</strong>(수면, 보챔, 매달림, 식욕 점수; 선택 메모; 선택 객관식 신호) — 직접 입력, 로컬에 저장.',
        'de': "<strong>Tägliche Logs</strong> (Schlaf, Unruhe, Anhänglichkeit, Appetit; optionale Notizen; optionale MCQ-Signale) — von Ihnen eingegeben, lokal gespeichert.",
    },
    'collect_li3': {
        'en': "<strong>Memories</strong> (photos, captions, optional milestone labels) — image files stored locally on your device.",
        'es': "<strong>Recuerdos</strong> (fotos, descripciones, etiquetas de hito opcionales) — archivos de imagen guardados localmente.",
        'fr': "<strong>Souvenirs</strong> (photos, légendes, étiquettes de jalons optionnelles) — fichiers image stockés localement.",
        'it': "<strong>Ricordi</strong> (foto, didascalie, etichette di traguardi opzionali) — file immagine salvati localmente.",
        'pt-br': "<strong>Memórias</strong> (fotos, legendas, marcos opcionais) — arquivos de imagem salvos localmente.",
        'ja': '<strong>思い出</strong>（写真、キャプション、任意のマイルストーンラベル）— 画像はローカルに保存。',
        'nl': "<strong>Herinneringen</strong> (foto's, bijschriften, optionele mijlpaal-labels) — beeldbestanden lokaal opgeslagen.",
        'zh-cn': '<strong>回忆</strong>（照片、说明、可选里程碑标签）——图像文件保存在设备本地。',
        'ko': '<strong>추억</strong>(사진, 설명, 선택 마일스톤 라벨) — 이미지 파일은 기기에 로컬 저장.',
        'de': "<strong>Erinnerungen</strong> (Fotos, Bildunterschriften, optionale Meilenstein-Tags) — Bilddateien lokal gespeichert.",
    },
    'collect_li4': {
        'en': "<strong>Account email</strong> — only if you choose to enable cloud sync.",
        'es': '<strong>Email de cuenta</strong> — solo si decides activar la sincronización en la nube.',
        'fr': "<strong>Email du compte</strong> — uniquement si vous activez la synchronisation cloud.",
        'it': "<strong>Email account</strong> — solo se scegli di attivare la sincronizzazione cloud.",
        'pt-br': "<strong>E-mail da conta</strong> — apenas se você optar pela sincronização na nuvem.",
        'ja': '<strong>アカウントのメールアドレス</strong> — クラウド同期を有効化した場合のみ。',
        'nl': "<strong>Account-e-mail</strong> — alleen als je cloudsync aanzet.",
        'zh-cn': '<strong>账户邮箱</strong>——仅当您选择启用云同步时。',
        'ko': '<strong>계정 이메일</strong> — 클라우드 동기화를 사용할 때만.',
        'de': "<strong>Konto-E-Mail</strong> — nur wenn Sie Cloud-Sync aktivieren.",
    },
    'collect_li5': {
        'en': "<strong>Purchase status</strong> — held by RevenueCat (our purchase processor) and Apple, tied to your Apple ID.",
        'es': "<strong>Estado de la compra</strong> — gestionado por RevenueCat (nuestro procesador de compras) y Apple, vinculado a tu Apple ID.",
        'fr': "<strong>Statut d'achat</strong> — géré par RevenueCat (notre processeur d'achats) et Apple, lié à votre identifiant Apple.",
        'it': "<strong>Stato dell'acquisto</strong> — gestito da RevenueCat (il nostro processore) e Apple, collegato al tuo ID Apple.",
        'pt-br': "<strong>Status da compra</strong> — gerido pela RevenueCat (nosso processador) e pela Apple, vinculado ao seu ID Apple.",
        'ja': '<strong>購入ステータス</strong> — RevenueCat（決済処理事業者）とAppleが保持し、Apple IDに紐付きます。',
        'nl': "<strong>Aankoopstatus</strong> — beheerd door RevenueCat (onze betalingsverwerker) en Apple, gekoppeld aan je Apple ID.",
        'zh-cn': '<strong>购买状态</strong>——由 RevenueCat（我们的支付处理方）和 Apple 保管，与您的 Apple ID 关联。',
        'ko': '<strong>구매 상태</strong> — RevenueCat(저희 결제 처리 업체)과 Apple이 보유하며 Apple ID와 연결됩니다.',
        'de': "<strong>Kaufstatus</strong> — gehalten von RevenueCat (unserem Zahlungsdienstleister) und Apple, verknüpft mit Ihrer Apple-ID.",
    },
    'section_not_title': {
        'en': "What we don't collect", 'es': 'Lo que NO recopilamos', 'fr': 'Ce que nous ne collectons pas',
        'it': 'Cosa NON raccogliamo', 'pt-br': 'O que NÃO coletamos', 'ja': '収集しない情報',
        'nl': 'Wat we NIET verzamelen', 'zh-cn': '我们不收集什么', 'ko': '수집하지 않는 정보', 'de': 'Was wir NICHT erfassen',
    },
    'not_li1': {
        'en': "No browsing history, advertising IDs, or device fingerprints.",
        'es': 'Sin historial de navegación, IDs publicitarios ni huellas de dispositivo.',
        'fr': "Pas d'historique de navigation, d'identifiants publicitaires ou d'empreintes d'appareil.",
        'it': "Nessuna cronologia di navigazione, ID pubblicitari o impronte del dispositivo.",
        'pt-br': "Sem histórico de navegação, IDs de anúncio ou impressões digitais de dispositivo.",
        'ja': '閲覧履歴、広告ID、デバイスフィンガープリントは収集しません。',
        'nl': "Geen browsegeschiedenis, advertentie-ID's of device fingerprints.",
        'zh-cn': '不收集浏览记录、广告 ID 或设备指纹。',
        'ko': '브라우징 기록, 광고 ID, 기기 지문을 수집하지 않습니다.',
        'de': "Kein Browserverlauf, keine Werbe-IDs, keine Geräte-Fingerprints.",
    },
    'not_li2': {
        'en': "No third-party analytics SDKs on the parent-facing app.",
        'es': 'Sin SDK de analítica de terceros en la app del padre/madre.',
        'fr': "Aucun SDK d'analytics tiers dans l'app destinée aux parents.",
        'it': "Nessun SDK di analitica di terze parti nell'app per genitori.",
        'pt-br': "Sem SDKs de analytics de terceiros no app voltado aos pais.",
        'ja': '保護者向けアプリに第三者分析SDKは入っていません。',
        'nl': "Geen externe analytics-SDK's in de oudergerichte app.",
        'zh-cn': '面向家长的应用没有第三方分析 SDK。',
        'ko': '부모용 앱에 외부 분석 SDK가 없습니다.',
        'de': "Keine Drittanbieter-Analytics-SDKs in der eltern-orientierten App.",
    },
    'not_li3': {
        'en': "No location data.",
        'es': 'Sin datos de ubicación.',
        'fr': "Aucune donnée de localisation.",
        'it': "Nessun dato di posizione.",
        'pt-br': "Sem dados de localização.",
        'ja': '位置情報は取得しません。',
        'nl': "Geen locatiegegevens.",
        'zh-cn': '不收集位置数据。',
        'ko': '위치 데이터를 수집하지 않습니다.',
        'de': "Keine Standortdaten.",
    },
    'not_li4': {
        'en': "No microphone or contacts access.",
        'es': 'Sin acceso al micrófono ni a los contactos.',
        'fr': "Pas d'accès au microphone ni aux contacts.",
        'it': "Nessun accesso a microfono o contatti.",
        'pt-br': "Sem acesso ao microfone ou aos contatos.",
        'ja': 'マイクや連絡先へのアクセスはありません。',
        'nl': "Geen toegang tot microfoon of contacten.",
        'zh-cn': '不访问麦克风或通讯录。',
        'ko': '마이크나 연락처에 접근하지 않습니다.',
        'de': "Kein Zugriff auf Mikrofon oder Kontakte.",
    },
    'section_sync_title': {
        'en': 'Cloud sync (optional)', 'es': 'Sincronización en la nube (opcional)',
        'fr': 'Synchronisation cloud (optionnelle)', 'it': 'Sincronizzazione cloud (opzionale)',
        'pt-br': 'Sincronização na nuvem (opcional)', 'ja': 'クラウド同期（任意）',
        'nl': 'Cloudsynchronisatie (optioneel)', 'zh-cn': '云同步（可选）',
        'ko': '클라우드 동기화(선택)', 'de': 'Cloud-Synchronisierung (optional)',
    },
    'sync_body1': {
        'en': "When you sign in with an email address, your child profile, logs, and insights are mirrored to <a href=\"https://supabase.com\" class=\"link\" rel=\"noopener\">Supabase</a> so they're available on any device you sign in to. Photos and memories remain local-only.",
        'es': "Cuando inicias sesión con un email, el perfil del bebé, los registros y los análisis se replican en <a href=\"https://supabase.com\" class=\"link\" rel=\"noopener\">Supabase</a> para estar disponibles en cualquier dispositivo. Las fotos y recuerdos quedan solo en local.",
        'fr': "Lorsque vous vous connectez avec un email, le profil de l'enfant, les logs et les analyses sont répliqués sur <a href=\"https://supabase.com\" class=\"link\" rel=\"noopener\">Supabase</a> pour être disponibles sur tous vos appareils. Les photos et souvenirs restent uniquement en local.",
        'it': "Quando accedi con un'email, profilo del bambino, log e insight vengono replicati su <a href=\"https://supabase.com\" class=\"link\" rel=\"noopener\">Supabase</a> per essere disponibili su qualsiasi dispositivo. Foto e ricordi restano solo in locale.",
        'pt-br': "Ao entrar com e-mail, o perfil do bebê, os registros e os insights são replicados na <a href=\"https://supabase.com\" class=\"link\" rel=\"noopener\">Supabase</a> para ficarem disponíveis em qualquer dispositivo. Fotos e memórias permanecem somente no dispositivo.",
        'ja': 'メールでサインインすると、お子さまのプロフィール、記録、インサイトが<a href="https://supabase.com" class="link" rel="noopener">Supabase</a>に同期され、サインインしたどのデバイスからもアクセスできます。写真と思い出はローカル限定です。',
        'nl': "Wanneer je met een e-mailadres inlogt, worden je kindprofiel, logs en inzichten gespiegeld naar <a href=\"https://supabase.com\" class=\"link\" rel=\"noopener\">Supabase</a> zodat ze op elk apparaat beschikbaar zijn. Foto's en herinneringen blijven alleen lokaal.",
        'zh-cn': '当您使用邮箱登录后，宝宝档案、记录与洞察会同步到 <a href="https://supabase.com" class="link" rel="noopener">Supabase</a>，可在任何登录的设备上访问。照片与回忆仍仅保存在本地。',
        'ko': '이메일로 로그인하면 아이 프로필, 기록, 인사이트가 <a href="https://supabase.com" class="link" rel="noopener">Supabase</a>에 동기화되어 로그인한 어떤 기기에서도 접근할 수 있습니다. 사진과 추억은 로컬에만 남습니다.',
        'de': "Wenn Sie sich mit einer E-Mail anmelden, werden Kinderprofil, Logs und Einblicke auf <a href=\"https://supabase.com\" class=\"link\" rel=\"noopener\">Supabase</a> gespiegelt, sodass sie auf jedem angemeldeten Gerät verfügbar sind. Fotos und Erinnerungen bleiben lokal.",
    },
    'sync_body2': {
        'en': "You can disable sync at any time in Profile → Cloud sync.",
        'es': 'Puedes desactivar la sincronización en cualquier momento en Perfil → Sincronización en la nube.',
        'fr': "Vous pouvez désactiver la synchronisation à tout moment dans Profil → Synchronisation cloud.",
        'it': "Puoi disattivare la sincronizzazione in qualsiasi momento da Profilo → Sincronizzazione cloud.",
        'pt-br': "Você pode desativar a sincronização a qualquer momento em Perfil → Sincronização na nuvem.",
        'ja': '同期はいつでもプロフィール → クラウド同期から無効化できます。',
        'nl': "Je kunt synchronisatie altijd uitzetten via Profiel → Cloudsync.",
        'zh-cn': '您可以随时在「档案 → 云同步」中停用同步。',
        'ko': '동기화는 프로필 → 클라우드 동기화에서 언제든 끌 수 있습니다.',
        'de': "Sie können die Synchronisierung jederzeit unter Profil → Cloud-Sync deaktivieren.",
    },
    'section_partner_title': {
        'en': 'Partner sharing', 'es': 'Compartir con la pareja', 'fr': 'Partage avec le partenaire',
        'it': 'Condivisione con il partner', 'pt-br': 'Compartilhamento com o parceiro',
        'ja': 'パートナー共有', 'nl': 'Delen met je partner', 'zh-cn': '与伴侣共享',
        'ko': '파트너 공유', 'de': 'Partner-Sharing',
    },
    'partner_body': {
        'en': "If you invite a partner with a sharing code, they get read access to your child's timeline, recent logs, and insights. The code is single-use and can be revoked at any time. No partner data leaves Nurtura's servers.",
        'es': 'Si invitas a una pareja con un código, esa persona obtiene acceso de solo lectura a la línea de tiempo, registros recientes e insights del bebé. El código es de un solo uso y se puede revocar en cualquier momento. Ningún dato de la pareja sale de los servidores de Nurtura.',
        'fr': "Si vous invitez un partenaire avec un code de partage, il obtient un accès en lecture à la chronologie, aux logs récents et aux insights de votre enfant. Le code est à usage unique et peut être révoqué à tout moment. Aucune donnée du partenaire ne quitte les serveurs de Nurtura.",
        'it': "Se inviti un partner con un codice di condivisione, otterrà accesso in lettura alla timeline, ai log recenti e agli insight del tuo bambino. Il codice è monouso e revocabile in qualsiasi momento. Nessun dato del partner esce dai server di Nurtura.",
        'pt-br': "Se você convidar um parceiro com um código de compartilhamento, ele terá acesso de leitura à linha do tempo, aos registros recentes e aos insights do seu bebê. O código é de uso único e pode ser revogado a qualquer momento. Nenhum dado do parceiro sai dos servidores da Nurtura.",
        'ja': '共有コードでパートナーを招待すると、そのパートナーはお子さまのタイムライン、最近の記録、インサイトに読み取り専用でアクセスできます。コードは一度限りで、いつでも無効化できます。パートナーのデータがNurturaのサーバーから外に出ることはありません。',
        'nl': "Als je een partner uitnodigt met een deelcode, krijgt deze leestoegang tot de tijdlijn, recente logs en inzichten van je kind. De code is eenmalig en kan altijd worden ingetrokken. Er verlaten geen partnergegevens de servers van Nurtura.",
        'zh-cn': '如果您用分享码邀请伴侣，对方会获得宝宝时间轴、近期记录与洞察的只读访问权限。分享码仅可使用一次，可随时撤销。伴侣的数据不会离开 Nurtura 的服务器。',
        'ko': '공유 코드로 파트너를 초대하면 파트너는 아이의 타임라인, 최근 기록, 인사이트에 읽기 전용으로 접근할 수 있습니다. 코드는 일회용이며 언제든지 취소할 수 있습니다. 파트너 데이터는 Nurtura 서버를 떠나지 않습니다.',
        'de': "Wenn Sie einen Partner mit einem Freigabecode einladen, erhält dieser Lesezugriff auf die Zeitleiste, kürzlich erfasste Logs und Einblicke Ihres Kindes. Der Code ist einmalig und jederzeit widerrufbar. Partnerdaten verlassen die Server von Nurtura nicht.",
    },
    'section_perm_title': {
        'en': 'Permissions we request', 'es': 'Permisos que solicitamos',
        'fr': 'Permissions demandées', 'it': 'Autorizzazioni richieste',
        'pt-br': 'Permissões que pedimos', 'ja': '要求する権限',
        'nl': 'Toestemmingen die we vragen', 'zh-cn': '我们请求的权限',
        'ko': '요청하는 권한', 'de': 'Berechtigungen, die wir anfordern',
    },
    'perm_li1': {
        'en': "<strong>Notifications</strong> — to send the optional daily log reminder. You control this in Profile or in iOS Settings.",
        'es': "<strong>Notificaciones</strong> — para enviar el recordatorio diario opcional. Lo controlas en Perfil o en los Ajustes de iOS.",
        'fr': "<strong>Notifications</strong> — pour envoyer le rappel quotidien optionnel. Vous le contrôlez dans Profil ou dans les Réglages iOS.",
        'it': "<strong>Notifiche</strong> — per inviare il promemoria giornaliero opzionale. Lo controlli da Profilo o dalle Impostazioni iOS.",
        'pt-br': "<strong>Notificações</strong> — para enviar o lembrete diário opcional. Você controla isso em Perfil ou nas Configurações do iOS.",
        'ja': '<strong>通知</strong> — オプションの毎日のログリマインダー用。プロフィールまたはiOS設定から制御できます。',
        'nl': "<strong>Meldingen</strong> — om de optionele dagelijkse log-herinnering te sturen. Beheer dit in Profiel of in iOS-instellingen.",
        'zh-cn': '<strong>通知</strong>——用于发送可选的每日记录提醒。可在「档案」或 iOS「设置」中管理。',
        'ko': '<strong>알림</strong> — 선택적 일일 기록 알림을 위해. 프로필 또는 iOS 설정에서 관리할 수 있습니다.',
        'de': "<strong>Benachrichtigungen</strong> — für die optionale tägliche Log-Erinnerung. Sie steuern dies im Profil oder in den iOS-Einstellungen.",
    },
    'perm_li2': {
        'en': "<strong>Photo library</strong> — only when you tap \"Add a memory\" → \"Choose from library\". We don't browse your library otherwise.",
        'es': "<strong>Galería de fotos</strong> — solo cuando pulsas \"Añadir recuerdo\" → \"Elegir de la galería\". No accedemos a tu galería en ningún otro momento.",
        'fr': "<strong>Photothèque</strong> — uniquement quand vous touchez \"Ajouter un souvenir\" → \"Choisir depuis la bibliothèque\". Nous n'y accédons pas autrement.",
        'it': "<strong>Libreria foto</strong> — solo quando tocchi \"Aggiungi un ricordo\" → \"Scegli dalla libreria\". Altrimenti non sfogliamo la tua libreria.",
        'pt-br': "<strong>Biblioteca de fotos</strong> — apenas quando você toca em \"Adicionar memória\" → \"Escolher da biblioteca\". Não acessamos sua biblioteca em outras situações.",
        'ja': '<strong>写真ライブラリ</strong> — 「思い出を追加」→「ライブラリから選ぶ」をタップしたときのみ。それ以外は閲覧しません。',
        'nl': "<strong>Fotobibliotheek</strong> — alleen als je op \"Herinnering toevoegen\" → \"Kies uit bibliotheek\" tikt. Verder kijken we niet in je bibliotheek.",
        'zh-cn': '<strong>照片库</strong>——仅当您点击「添加回忆」→「从图库选择」时。其他时间不会浏览您的图库。',
        'ko': '<strong>사진 보관함</strong> — "추억 추가" → "보관함에서 선택"을 누를 때만. 그 외에는 보관함을 보지 않습니다.',
        'de': "<strong>Fotobibliothek</strong> — nur wenn Sie auf \"Erinnerung hinzufügen\" → \"Aus Bibliothek wählen\" tippen. Sonst greifen wir nicht zu.",
    },
    'perm_li3': {
        'en': "<strong>Camera</strong> — only when you tap \"Add a memory\" → \"Take photo\".",
        'es': "<strong>Cámara</strong> — solo cuando pulsas \"Añadir recuerdo\" → \"Hacer foto\".",
        'fr': "<strong>Appareil photo</strong> — uniquement quand vous touchez \"Ajouter un souvenir\" → \"Prendre une photo\".",
        'it': "<strong>Fotocamera</strong> — solo quando tocchi \"Aggiungi un ricordo\" → \"Scatta foto\".",
        'pt-br': "<strong>Câmera</strong> — apenas quando você toca em \"Adicionar memória\" → \"Tirar foto\".",
        'ja': '<strong>カメラ</strong> — 「思い出を追加」→「写真を撮る」をタップしたときのみ。',
        'nl': "<strong>Camera</strong> — alleen als je op \"Herinnering toevoegen\" → \"Foto maken\" tikt.",
        'zh-cn': '<strong>相机</strong>——仅当您点击「添加回忆」→「拍照」时。',
        'ko': '<strong>카메라</strong> — "추억 추가" → "사진 찍기"를 누를 때만.',
        'de': "<strong>Kamera</strong> — nur wenn Sie auf \"Erinnerung hinzufügen\" → \"Foto aufnehmen\" tippen.",
    },
    'section_rights_title': {
        'en': 'Your rights', 'es': 'Tus derechos', 'fr': 'Vos droits', 'it': 'I tuoi diritti',
        'pt-br': 'Seus direitos', 'ja': 'あなたの権利', 'nl': 'Je rechten', 'zh-cn': '您的权利',
        'ko': '여러분의 권리', 'de': 'Ihre Rechte',
    },
    'rights_body': {
        'en': "You can request a copy of your data, or deletion of your cloud-stored data, by emailing <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>. Local data can be removed at any time by deleting the app.",
        'es': "Puedes solicitar una copia de tus datos, o la eliminación de los datos guardados en la nube, escribiendo a <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>. Los datos locales se pueden eliminar en cualquier momento desinstalando la app.",
        'fr': "Vous pouvez demander une copie de vos données ou la suppression de vos données stockées dans le cloud en écrivant à <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>. Les données locales peuvent être supprimées à tout moment en désinstallant l'app.",
        'it': "Puoi richiedere una copia dei tuoi dati, o la cancellazione dei dati salvati in cloud, scrivendo a <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>. I dati locali possono essere rimossi in qualsiasi momento disinstallando l'app.",
        'pt-br': "Você pode solicitar uma cópia dos seus dados, ou a exclusão dos dados armazenados na nuvem, escrevendo para <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>. Os dados locais podem ser removidos a qualquer momento excluindo o app.",
        'ja': 'データのコピーやクラウド保存データの削除は<a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>までご連絡ください。ローカルデータはアプリを削除することでいつでも消去できます。',
        'nl': "Je kunt een kopie van je gegevens of verwijdering van je in de cloud opgeslagen gegevens aanvragen via <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>. Lokale gegevens kun je altijd verwijderen door de app te wissen.",
        'zh-cn': '如需获取数据副本或删除云端数据，请联系 <a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>。本地数据可随时通过卸载应用删除。',
        'ko': '데이터 사본이나 클라우드 데이터 삭제 요청은 <a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>로 보내주세요. 로컬 데이터는 앱을 삭제하면 언제든 제거됩니다.',
        'de': "Sie können eine Kopie Ihrer Daten oder die Löschung Ihrer in der Cloud gespeicherten Daten per E-Mail an <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> anfordern. Lokale Daten lassen sich jederzeit durch Löschen der App entfernen.",
    },
    'section_contact_title': {
        'en': 'Contact', 'es': 'Contacto', 'fr': 'Contact', 'it': 'Contatti',
        'pt-br': 'Contato', 'ja': 'お問い合わせ', 'nl': 'Contact', 'zh-cn': '联系我们',
        'ko': '연락처', 'de': 'Kontakt',
    },
    'contact_body': {
        'en': "Questions, requests, or concerns: <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>",
        'es': "Preguntas, solicitudes o dudas: <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>",
        'fr': "Questions, demandes ou préoccupations : <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>",
        'it': "Domande, richieste o dubbi: <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>",
        'pt-br': "Dúvidas, solicitações ou preocupações: <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>",
        'ja': 'ご質問、リクエスト、ご不明点は<a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>まで。',
        'nl': "Vragen, verzoeken of zorgen: <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>",
        'zh-cn': '问题、请求或疑虑：<a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>',
        'ko': '문의, 요청, 우려 사항: <a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>',
        'de': "Fragen, Anfragen oder Bedenken: <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a>",
    },
    'footer_note': {
        'en': "Nurtura is not a medical device and does not diagnose, treat, or replace professional advice.",
        'es': 'Nurtura no es un dispositivo médico y no diagnostica, trata ni sustituye el consejo profesional.',
        'fr': "Nurtura n'est pas un dispositif médical et ne diagnostique, ne traite ni ne remplace un avis professionnel.",
        'it': "Nurtura non è un dispositivo medico e non diagnostica, tratta o sostituisce il parere professionale.",
        'pt-br': "Nurtura não é um dispositivo médico e não diagnostica, trata ou substitui orientação profissional.",
        'ja': 'Nurturaは医療機器ではなく、診断・治療・専門家のアドバイスの代わりにはなりません。',
        'nl': "Nurtura is geen medisch hulpmiddel en stelt geen diagnose, behandelt niet en vervangt geen professioneel advies.",
        'zh-cn': 'Nurtura 不是医疗设备，不进行诊断、治疗，也不替代专业建议。',
        'ko': 'Nurtura는 의료 기기가 아니며 진단·치료·전문가 조언을 대체하지 않습니다.',
        'de': "Nurtura ist kein Medizinprodukt und ersetzt keine Diagnose, Behandlung oder professionelle Beratung.",
    },
    'nav_features': {
        'en': 'Features', 'es': 'Funciones', 'fr': 'Fonctions', 'it': 'Funzioni', 'pt-br': 'Recursos',
        'ja': '機能', 'nl': 'Functies', 'zh-cn': '功能', 'ko': '기능', 'de': 'Funktionen',
    },
    'nav_premium': {
        'en': 'Premium', 'es': 'Premium', 'fr': 'Premium', 'it': 'Premium', 'pt-br': 'Premium',
        'ja': 'プレミアム', 'nl': 'Premium', 'zh-cn': '高级版', 'ko': '프리미엄', 'de': 'Premium',
    },
    'nav_support': {
        'en': 'Support', 'es': 'Soporte', 'fr': 'Support', 'it': 'Supporto', 'pt-br': 'Suporte',
        'ja': 'サポート', 'nl': 'Ondersteuning', 'zh-cn': '支持', 'ko': '지원', 'de': 'Support',
    },
    'nav_cta': {
        'en': 'Get the app', 'es': 'Obtener la app', 'fr': "Télécharger l'app", 'it': "Scarica l'app",
        'pt-br': 'Baixe o app', 'ja': 'アプリを入手', 'nl': 'Download de app',
        'zh-cn': '获取应用', 'ko': '앱 받기', 'de': 'App holen',
    },
    'footer_home': {
        'en': 'Home', 'es': 'Inicio', 'fr': 'Accueil', 'it': 'Home', 'pt-br': 'Início',
        'ja': 'ホーム', 'nl': 'Home', 'zh-cn': '首页', 'ko': '홈', 'de': 'Startseite',
    },
    'footer_privacy': {
        'en': 'Privacy', 'es': 'Privacidad', 'fr': 'Confidentialité', 'it': 'Privacy', 'pt-br': 'Privacidade',
        'ja': 'プライバシー', 'nl': 'Privacy', 'zh-cn': '隐私', 'ko': '개인정보', 'de': 'Datenschutz',
    },
    'footer_support': {
        'en': 'Support', 'es': 'Soporte', 'fr': 'Support', 'it': 'Supporto', 'pt-br': 'Suporte',
        'ja': 'サポート', 'nl': 'Ondersteuning', 'zh-cn': '支持', 'ko': '지원', 'de': 'Support',
    },
    'footer_contact': {
        'en': 'Contact', 'es': 'Contacto', 'fr': 'Contact', 'it': 'Contatti', 'pt-br': 'Contato',
        'ja': 'お問い合わせ', 'nl': 'Contact', 'zh-cn': '联系', 'ko': '문의', 'de': 'Kontakt',
    },
    'footer_copy': {
        'en': '© 2026 Micah John Walker', 'es': '© 2026 Micah John Walker', 'fr': '© 2026 Micah John Walker',
        'it': '© 2026 Micah John Walker', 'pt-br': '© 2026 Micah John Walker',
        'ja': '© 2026 Micah John Walker', 'nl': '© 2026 Micah John Walker',
        'zh-cn': '© 2026 Micah John Walker', 'ko': '© 2026 Micah John Walker', 'de': '© 2026 Micah John Walker',
    },
}

# fmt: on


SUPPORT = {
    'page_title': {
        'en': 'Support — Nurtura', 'es': 'Soporte — Nurtura', 'fr': 'Support — Nurtura',
        'it': 'Supporto — Nurtura', 'pt-br': 'Suporte — Nurtura', 'ja': 'サポート — Nurtura',
        'nl': 'Ondersteuning — Nurtura', 'zh-cn': '支持 — Nurtura', 'ko': '지원 — Nurtura', 'de': 'Support — Nurtura',
    },
    'meta_desc': {
        'en': "Help with Nurtura — common questions, how to restore purchases, how to share with a partner, and how to contact support.",
        'es': 'Ayuda con Nurtura: preguntas comunes, restaurar compras, compartir con la pareja y cómo contactar.',
        'fr': "Aide pour Nurtura — questions fréquentes, restauration d'achats, partage avec un partenaire, contact.",
        'it': "Aiuto per Nurtura — domande comuni, come ripristinare gli acquisti, condividere con il partner e contattare l'assistenza.",
        'pt-br': "Ajuda da Nurtura — perguntas comuns, restauração de compras, compartilhamento e contato.",
        'ja': 'Nurturaのヘルプ — よくある質問、購入の復元、パートナー共有、サポートへの連絡方法。',
        'nl': "Hulp bij Nurtura — veelgestelde vragen, aankopen herstellen, delen met je partner en contact opnemen.",
        'zh-cn': 'Nurtura 帮助 — 常见问题、恢复购买、与伴侣共享、联系支持。',
        'ko': 'Nurtura 도움말 — 자주 묻는 질문, 구매 복원, 파트너 공유, 지원 문의.',
        'de': "Hilfe zu Nurtura — häufige Fragen, Käufe wiederherstellen, mit Partner teilen und Support kontaktieren.",
    },
    'eyebrow': {
        'en': 'SUPPORT', 'es': 'SOPORTE', 'fr': 'SUPPORT', 'it': 'SUPPORTO', 'pt-br': 'SUPORTE',
        'ja': 'サポート', 'nl': 'ONDERSTEUNING', 'zh-cn': '支持', 'ko': '지원', 'de': 'SUPPORT',
    },
    'title': {
        'en': 'How can we help?', 'es': '¿Cómo podemos ayudar?', 'fr': 'Comment pouvons-nous aider ?',
        'it': 'Come possiamo aiutarti?', 'pt-br': 'Como podemos ajudar?', 'ja': 'お手伝いできることは?',
        'nl': 'Hoe kunnen we helpen?', 'zh-cn': '我们能怎么帮您？', 'ko': '어떻게 도와드릴까요?', 'de': 'Wie können wir helfen?',
    },
    'updated': {
        'en': 'Email <a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a> — we reply within 1 business day.',
        'es': 'Escribe a <a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a> — respondemos en 1 día hábil.',
        'fr': "Envoyez un email à <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> — nous répondons sous 1 jour ouvré.",
        'it': "Scrivi a <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> — rispondiamo entro 1 giorno lavorativo.",
        'pt-br': "Envie um e-mail para <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> — respondemos em 1 dia útil.",
        'ja': '<a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>までメールでお問い合わせください — 1営業日以内にお返事します。',
        'nl': "Mail naar <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> — we antwoorden binnen 1 werkdag.",
        'zh-cn': '请发送邮件至 <a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>，我们将在 1 个工作日内回复。',
        'ko': '<a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>로 이메일 보내주세요 — 영업일 기준 1일 내에 답변드립니다.',
        'de': "E-Mail an <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> — Antwort innerhalb von 1 Werktag.",
    },
    'section_faq_title': {
        'en': 'Common questions', 'es': 'Preguntas frecuentes', 'fr': 'Questions fréquentes',
        'it': 'Domande comuni', 'pt-br': 'Perguntas comuns', 'ja': 'よくある質問',
        'nl': 'Veelgestelde vragen', 'zh-cn': '常见问题', 'ko': '자주 묻는 질문', 'de': 'Häufige Fragen',
    },
    'q1': {
        'en': 'How do I restore a previous purchase?',
        'es': '¿Cómo restauro una compra anterior?',
        'fr': "Comment restaurer un achat précédent ?",
        'it': 'Come ripristino un acquisto precedente?',
        'pt-br': 'Como restauro uma compra anterior?',
        'ja': '以前の購入を復元するには?',
        'nl': 'Hoe herstel ik een eerdere aankoop?',
        'zh-cn': '如何恢复之前的购买？',
        'ko': '이전 구매를 어떻게 복원하나요?',
        'de': 'Wie stelle ich einen früheren Kauf wieder her?',
    },
    'a1': {
        'en': "Open the paywall (Profile → Subscribe) and tap <strong>Restore purchase</strong>. Make sure you're signed in with the same Apple ID you used to subscribe.",
        'es': "Abre el muro de pago (Perfil → Suscribirse) y pulsa <strong>Restaurar compra</strong>. Asegúrate de iniciar sesión con el mismo Apple ID que usaste para suscribirte.",
        'fr': "Ouvrez le paywall (Profil → S'abonner) et touchez <strong>Restaurer l'achat</strong>. Assurez-vous d'être connecté avec le même identifiant Apple utilisé lors de l'abonnement.",
        'it': "Apri il paywall (Profilo → Sottoscrivi) e tocca <strong>Ripristina acquisto</strong>. Assicurati di aver effettuato l'accesso con lo stesso ID Apple usato per l'abbonamento.",
        'pt-br': "Abra o paywall (Perfil → Assinar) e toque em <strong>Restaurar compra</strong>. Verifique se você está conectado com o mesmo ID Apple usado na assinatura.",
        'ja': 'ペイウォール（プロフィール → 登録）を開き、<strong>購入を復元</strong>をタップします。登録時と同じApple IDでサインインしていることを確認してください。',
        'nl': "Open de paywall (Profiel → Abonneren) en tik op <strong>Aankoop herstellen</strong>. Zorg dat je bent ingelogd met dezelfde Apple ID waarmee je je hebt geabonneerd.",
        'zh-cn': '打开付费墙（档案 → 订阅），点击「<strong>恢复购买</strong>」。请确认使用与订阅时相同的 Apple ID 登录。',
        'ko': '결제 화면(프로필 → 구독)을 열고 <strong>구매 복원</strong>을 누르세요. 구독에 사용한 Apple ID로 로그인했는지 확인하세요.',
        'de': "Öffnen Sie die Paywall (Profil → Abonnieren) und tippen Sie auf <strong>Kauf wiederherstellen</strong>. Stellen Sie sicher, dass Sie mit der gleichen Apple-ID angemeldet sind, mit der Sie abonniert haben.",
    },
    'q2': {
        'en': "What's included in the 7-day free trial?",
        'es': '¿Qué incluye la prueba gratuita de 7 días?',
        'fr': "Qu'est-ce qui est inclus dans l'essai gratuit de 7 jours ?",
        'it': "Cosa include la prova gratuita di 7 giorni?",
        'pt-br': 'O que está incluso no teste gratuito de 7 dias?',
        'ja': '7日間の無料トライアルには何が含まれていますか?',
        'nl': "Wat zit er in de 7-daagse gratis proefperiode?",
        'zh-cn': '7 天免费试用包含什么？',
        'ko': '7일 무료 체험에는 무엇이 포함되나요?',
        'de': "Was ist in der 7-tägigen Testphase enthalten?",
    },
    'a2': {
        'en': "Everything. Personalised insights, \"What's coming\" predictions, partner sharing, and the Pediatrician PDF report. No payment is taken during the trial. You can cancel any time before day 7 with no charge.",
        'es': "Todo. Análisis personalizados, predicciones \"lo que viene\", compartir con la pareja y el informe PDF para el pediatra. No se cobra nada durante la prueba. Puedes cancelar antes del día 7 sin coste.",
        'fr': "Tout. Analyses personnalisées, prédictions « Ce qui arrive », partage avec le partenaire et rapport PDF pour le pédiatre. Aucun paiement n'est prélevé pendant l'essai. Vous pouvez annuler avant le jour 7 sans frais.",
        'it': "Tutto. Insight personalizzati, previsioni \"Cosa sta arrivando\", condivisione con il partner e report PDF per il pediatra. Nessun pagamento durante la prova. Puoi annullare prima del giorno 7 senza addebiti.",
        'pt-br': "Tudo. Insights personalizados, previsões \"O que vem aí\", compartilhamento com o parceiro e relatório PDF para o pediatra. Nenhuma cobrança durante o teste. Você pode cancelar antes do dia 7 sem custos.",
        'ja': 'すべて。パーソナルなインサイト、「次に来ること」予測、パートナー共有、小児科向けPDFレポート。トライアル中の支払いはありません。7日目までであれば、無料でいつでも解約できます。',
        'nl': "Alles. Persoonlijke inzichten, \"What's coming\"-voorspellingen, delen met je partner en het pdf-rapport voor de kinderarts. Tijdens de proefperiode wordt niets afgeschreven. Je kunt vóór dag 7 zonder kosten opzeggen.",
        'zh-cn': '全部。包括个性化洞察、「接下来会怎样」预测、与伴侣共享、儿科医生 PDF 报告。试用期间不会收费。可在第 7 天之前免费取消。',
        'ko': "모든 기능을 사용할 수 있습니다. 맞춤 인사이트, \"앞으로 올 것\" 예측, 파트너 공유, 소아과의용 PDF 리포트 포함. 체험 기간 동안 결제되지 않으며, 7일째 전까지 언제든 무료로 해지할 수 있습니다.",
        'de': "Alles. Personalisierte Einblicke, „Was kommt\"-Vorhersagen, Partner-Sharing und den Kinderarzt-PDF-Bericht. Während des Tests wird nichts abgebucht. Sie können vor Tag 7 jederzeit kostenfrei kündigen.",
    },
    'q3': {
        'en': 'How do I share with a partner?',
        'es': '¿Cómo comparto con mi pareja?',
        'fr': 'Comment partager avec mon partenaire ?',
        'it': 'Come condivido con il mio partner?',
        'pt-br': 'Como compartilho com meu parceiro?',
        'ja': 'パートナーと共有するには?',
        'nl': 'Hoe deel ik met mijn partner?',
        'zh-cn': '怎么和伴侣共享？',
        'ko': '파트너와 어떻게 공유하나요?',
        'de': 'Wie teile ich mit meinem Partner?',
    },
    'a3': {
        'en': "Profile → Partner sharing → Invite a caregiver. Share the 6-character code via Messages, WhatsApp, or however suits. Your partner enters the code in their copy of Nurtura to join your timeline.",
        'es': "Perfil → Compartir con la pareja → Invitar a un cuidador. Comparte el código de 6 caracteres por Mensajes, WhatsApp o como prefieras. Tu pareja lo introduce en su copia de Nurtura para unirse a tu línea de tiempo.",
        'fr': "Profil → Partage avec le partenaire → Inviter un soignant. Partagez le code à 6 caractères par Messages, WhatsApp ou autre. Votre partenaire saisit le code dans sa copie de Nurtura pour rejoindre votre chronologie.",
        'it': "Profilo → Condivisione con il partner → Invita un caregiver. Condividi il codice di 6 caratteri tramite Messaggi, WhatsApp o come preferisci. Il tuo partner inserisce il codice nella sua copia di Nurtura per unirsi alla tua timeline.",
        'pt-br': "Perfil → Compartilhamento com o parceiro → Convidar cuidador. Compartilhe o código de 6 caracteres por Mensagens, WhatsApp ou onde preferir. O parceiro insere o código no Nurtura dele para entrar na sua linha do tempo.",
        'ja': 'プロフィール → パートナー共有 → 育児パートナーを招待。6文字のコードをメッセージ、WhatsAppなどでパートナーに送ります。パートナーは自分のNurturaにそのコードを入力するとタイムラインに参加できます。',
        'nl': "Profiel → Delen met je partner → Verzorger uitnodigen. Stuur de code van 6 tekens via Berichten, WhatsApp of een ander kanaal. Je partner voert de code in zijn/haar Nurtura in om bij je tijdlijn te komen.",
        'zh-cn': '档案 → 与伴侣共享 → 邀请照护者。把 6 位邀请码通过「信息」「WhatsApp」等发给对方。对方在自己的 Nurtura 中输入邀请码即可加入您的时间轴。',
        'ko': '프로필 → 파트너 공유 → 보호자 초대. 6자리 코드를 메시지, WhatsApp 등으로 공유하세요. 파트너가 자신의 Nurtura에서 코드를 입력하면 타임라인에 함께할 수 있습니다.',
        'de': "Profil → Partner-Sharing → Betreuungsperson einladen. Teilen Sie den 6-stelligen Code per Nachrichten, WhatsApp oder wie Sie möchten. Ihr Partner gibt den Code in seiner Nurtura-Installation ein, um Ihrer Zeitleiste beizutreten.",
    },
    'q4': {
        'en': 'How do I export logs for my pediatrician?',
        'es': '¿Cómo exporto los registros para el pediatra?',
        'fr': 'Comment exporter les logs pour mon pédiatre ?',
        'it': 'Come esporto i log per il pediatra?',
        'pt-br': 'Como exporto registros para o pediatra?',
        'ja': '小児科医に渡すためにログをエクスポートするには?',
        'nl': 'Hoe exporteer ik logs voor mijn kinderarts?',
        'zh-cn': '怎么导出记录给儿科医生？',
        'ko': '소아과의에게 보여줄 기록은 어떻게 내보내나요?',
        'de': 'Wie exportiere ich Logs für meinen Kinderarzt?',
    },
    'a4': {
        'en': "Profile → Share with your doctor → Pediatrician report. Generates a 1-page PDF of the last 14 days of logs and opens the system share sheet so you can email, AirDrop, or save to Files. Premium-only.",
        'es': "Perfil → Compartir con tu médico → Informe del pediatra. Genera un PDF de 1 página con los últimos 14 días de registros y abre la hoja para compartir del sistema (email, AirDrop, Archivos). Solo en premium.",
        'fr': "Profil → Partager avec votre médecin → Rapport pédiatre. Génère un PDF d'une page avec les 14 derniers jours de logs et ouvre la feuille de partage système (email, AirDrop, Fichiers). Premium uniquement.",
        'it': "Profilo → Condividi con il medico → Report pediatra. Genera un PDF di 1 pagina con gli ultimi 14 giorni di log e apre il foglio di condivisione di sistema (email, AirDrop, File). Solo premium.",
        'pt-br': "Perfil → Compartilhe com o médico → Relatório do pediatra. Gera um PDF de 1 página com os últimos 14 dias de registros e abre o menu de compartilhamento do sistema (e-mail, AirDrop, Arquivos). Somente premium.",
        'ja': 'プロフィール → 医師と共有 → 小児科レポート。直近14日分のログを1ページPDFで生成し、システムの共有シートを開きます（メール、AirDrop、ファイルなど）。プレミアム限定。',
        'nl': "Profiel → Delen met je arts → Kinderarts-rapport. Genereert een 1-pagina pdf met de laatste 14 dagen logs en opent het systeemdelen-blad (e-mail, AirDrop, Bestanden). Alleen premium.",
        'zh-cn': '档案 → 与医生分享 → 儿科医生报告。生成最近 14 天日志的 1 页 PDF，并打开系统分享面板（邮件、隔空投送、文件 App）。仅限高级版。',
        'ko': "프로필 → 의사와 공유 → 소아과 리포트. 최근 14일의 기록을 1페이지 PDF로 만들고 시스템 공유 시트를 열어 이메일, AirDrop, 파일 앱 등으로 보낼 수 있습니다. 프리미엄 전용.",
        'de': "Profil → Mit Ihrem Arzt teilen → Kinderarzt-Bericht. Erzeugt ein 1-seitiges PDF der letzten 14 Tage und öffnet das System-Teilen-Sheet (E-Mail, AirDrop, Dateien). Nur Premium.",
    },
    'q5': {
        'en': 'Will my logs sync between my phone and iPad?',
        'es': '¿Mis registros se sincronizan entre mi iPhone e iPad?',
        'fr': 'Mes logs sont-ils synchronisés entre mon téléphone et mon iPad ?',
        'it': 'I miei log si sincronizzano tra telefono e iPad?',
        'pt-br': 'Meus registros sincronizam entre celular e iPad?',
        'ja': 'iPhoneとiPadでログは同期されますか?',
        'nl': "Worden mijn logs gesynchroniseerd tussen mijn telefoon en iPad?",
        'zh-cn': '手机和 iPad 之间会同步记录吗？',
        'ko': '아이폰과 아이패드 사이에 기록이 동기화되나요?',
        'de': 'Werden meine Logs zwischen Handy und iPad synchronisiert?',
    },
    'a5': {
        'en': "Yes, if you sign in with an email address. Cloud sync is opt-in; without sign-in your logs stay on the device they were created on.",
        'es': 'Sí, si inicias sesión con un email. La sincronización es opcional; sin iniciar sesión, los registros se quedan en el dispositivo donde se crearon.',
        'fr': "Oui, si vous vous connectez avec un email. La synchronisation est optionnelle ; sans connexion, vos logs restent sur l'appareil où ils ont été créés.",
        'it': "Sì, se accedi con un'email. La sincronizzazione è opzionale; senza login i log restano sul dispositivo dove sono stati creati.",
        'pt-br': "Sim, se você entrar com e-mail. A sincronização é opcional; sem login os registros ficam no dispositivo onde foram criados.",
        'ja': 'はい、メールアドレスでサインインすれば同期されます。クラウド同期はオプトイン式で、サインインしない場合は作成したデバイスにのみ残ります。',
        'nl': "Ja, als je met een e-mailadres inlogt. Cloudsync is opt-in; zonder inloggen blijven je logs op het apparaat waar ze gemaakt zijn.",
        'zh-cn': '会，前提是您使用邮箱登录。云同步是可选的，未登录时记录只保留在创建它的设备上。',
        'ko': '이메일로 로그인하면 동기화됩니다. 클라우드 동기화는 선택이며, 로그인하지 않으면 기록은 생성된 기기에만 남습니다.',
        'de': "Ja, wenn Sie sich mit einer E-Mail anmelden. Cloud-Sync ist opt-in; ohne Anmeldung bleiben Ihre Logs auf dem Gerät, auf dem sie erstellt wurden.",
    },
    'q6': {
        'en': "How do I confirm my baby's birth date after pregnancy?",
        'es': '¿Cómo confirmo la fecha de nacimiento del bebé después del embarazo?',
        'fr': "Comment confirmer la date de naissance après la grossesse ?",
        'it': "Come confermo la data di nascita del bambino dopo la gravidanza?",
        'pt-br': 'Como confirmo a data de nascimento do bebê depois da gravidez?',
        'ja': '出産後に生年月日を確定するには?',
        'nl': "Hoe bevestig ik de geboortedatum van mijn baby na de zwangerschap?",
        'zh-cn': '生产后如何确认宝宝的出生日期？',
        'ko': '출산 후 아기의 생일은 어떻게 확정하나요?',
        'de': 'Wie bestätige ich nach der Schwangerschaft das Geburtsdatum?',
    },
    'a6': {
        'en': "Profile → Child → \"Baby has been born\". Enter the actual birth date and Nurtura switches from pregnancy mode to newborn mode automatically.",
        'es': "Perfil → Bebé → \"El bebé ha nacido\". Introduce la fecha real y Nurtura cambia automáticamente del modo embarazo al modo recién nacido.",
        'fr': "Profil → Enfant → « Bébé est né ». Saisissez la date réelle de naissance et Nurtura passe automatiquement du mode grossesse au mode nouveau-né.",
        'it': "Profilo → Bambino → \"Il bambino è nato\". Inserisci la data effettiva e Nurtura passa automaticamente dalla modalità gravidanza a quella neonato.",
        'pt-br': "Perfil → Bebê → \"O bebê nasceu\". Informe a data real do nascimento e a Nurtura troca automaticamente do modo gravidez para o modo recém-nascido.",
        'ja': 'プロフィール → お子さま → 「赤ちゃんが生まれました」を選択。実際の生年月日を入力すると、妊娠モードから新生児モードに自動で切り替わります。',
        'nl': "Profiel → Kind → \"Baby is geboren\". Voer de echte geboortedatum in; Nurtura schakelt automatisch van zwangerschapsmodus naar pasgeborenmodus.",
        'zh-cn': '档案 → 宝宝 → 「宝宝已出生」。输入实际出生日期，Nurtura 会自动从孕期模式切换到新生儿模式。',
        'ko': "프로필 → 아이 → \"아기가 태어났어요\". 실제 생년월일을 입력하면 Nurtura가 임신 모드에서 신생아 모드로 자동 전환됩니다.",
        'de': "Profil → Kind → „Baby ist geboren\". Geben Sie das tatsächliche Geburtsdatum ein und Nurtura wechselt automatisch vom Schwangerschafts- in den Neugeborenenmodus.",
    },
    'q7': {
        'en': 'I logged the wrong day — how do I edit?',
        'es': 'Registré el día equivocado — ¿cómo lo edito?',
        'fr': "J'ai enregistré le mauvais jour — comment modifier ?",
        'it': 'Ho registrato il giorno sbagliato — come lo modifico?',
        'pt-br': 'Registrei o dia errado — como edito?',
        'ja': '間違った日付で記録してしまいました。編集するには?',
        'nl': "Ik heb de verkeerde dag gelogd — hoe pas ik dat aan?",
        'zh-cn': '我记错了日期，怎么修改？',
        'ko': '잘못된 날짜로 기록했어요. 어떻게 수정하나요?',
        'de': 'Ich habe den falschen Tag geloggt — wie ändere ich das?',
    },
    'a7': {
        'en': "Go to the Log tab and re-submit for the same date. Your previous entry will be updated, not duplicated.",
        'es': 'Ve a la pestaña Registro y vuelve a guardar para esa fecha. La entrada anterior se actualizará, no se duplicará.',
        'fr': "Allez dans l'onglet Log et renvoyez le formulaire pour la même date. L'entrée précédente sera mise à jour, pas dupliquée.",
        'it': "Vai alla scheda Log e invia di nuovo per la stessa data. La voce precedente sarà aggiornata, non duplicata.",
        'pt-br': "Vá para a aba Registro e envie novamente para a mesma data. O registro anterior será atualizado, não duplicado.",
        'ja': 'ログタブで同じ日付に再度保存してください。以前の記録は重複せず更新されます。',
        'nl': "Ga naar het tabblad Log en sla opnieuw op voor dezelfde datum. Je vorige invoer wordt bijgewerkt, niet gedupliceerd.",
        'zh-cn': '前往「记录」标签页，对同一日期再次提交。原记录会被更新，不会重复。',
        'ko': '기록 탭으로 가서 같은 날짜로 다시 저장하세요. 이전 기록이 덮어쓰여 갱신됩니다.',
        'de': "Gehen Sie zum Log-Tab und senden Sie für denselben Tag erneut ab. Der vorherige Eintrag wird aktualisiert, nicht dupliziert.",
    },
    'q8': {
        'en': 'How do I turn off the daily reminder?',
        'es': '¿Cómo desactivo el recordatorio diario?',
        'fr': 'Comment désactiver le rappel quotidien ?',
        'it': 'Come disattivo il promemoria giornaliero?',
        'pt-br': 'Como desativo o lembrete diário?',
        'ja': '毎日のリマインダーをオフにするには?',
        'nl': "Hoe schakel ik de dagelijkse herinnering uit?",
        'zh-cn': '怎么关闭每日提醒？',
        'ko': '매일 알림은 어떻게 끄나요?',
        'de': 'Wie schalte ich die tägliche Erinnerung aus?',
    },
    'a8': {
        'en': "Profile → Notifications → toggle off \"Daily log reminder\". Or disable Nurtura notifications in iOS Settings.",
        'es': "Perfil → Notificaciones → desactiva \"Recordatorio diario\". O desactiva las notificaciones de Nurtura en los Ajustes de iOS.",
        'fr': "Profil → Notifications → désactivez « Rappel quotidien ». Ou désactivez les notifications de Nurtura dans les Réglages iOS.",
        'it': "Profilo → Notifiche → disattiva \"Promemoria giornaliero\". Oppure disabilita le notifiche di Nurtura nelle Impostazioni iOS.",
        'pt-br': "Perfil → Notificações → desligue \"Lembrete diário\". Ou desative as notificações da Nurtura nas Configurações do iOS.",
        'ja': 'プロフィール → 通知 → 「毎日のログリマインダー」をオフ。またはiOSの設定からNurturaの通知を無効化できます。',
        'nl': "Profiel → Meldingen → schakel \"Dagelijkse logherinnering\" uit. Of zet Nurtura-meldingen uit in iOS-instellingen.",
        'zh-cn': '档案 → 通知 → 关闭「每日记录提醒」。或在 iOS「设置」中关闭 Nurtura 通知。',
        'ko': "프로필 → 알림 → \"매일 기록 알림\"을 끄세요. 또는 iOS 설정에서 Nurtura 알림을 꺼도 됩니다.",
        'de': "Profil → Benachrichtigungen → schalten Sie „Tägliche Log-Erinnerung\" aus. Oder deaktivieren Sie Nurtura-Benachrichtigungen in den iOS-Einstellungen.",
    },
    'q9': {
        'en': 'Is Nurtura medical advice?',
        'es': '¿Nurtura es consejo médico?',
        'fr': 'Nurtura est-il un avis médical ?',
        'it': 'Nurtura è un parere medico?',
        'pt-br': 'A Nurtura é orientação médica?',
        'ja': 'Nurturaは医学的アドバイスですか?',
        'nl': 'Is Nurtura medisch advies?',
        'zh-cn': 'Nurtura 是医疗建议吗？',
        'ko': 'Nurtura가 의학적 조언인가요?',
        'de': 'Ist Nurtura medizinischer Rat?',
    },
    'a9': {
        'en': "No. Nurtura helps you notice patterns and feel prepared, but it's not a medical device and doesn't diagnose, treat, or replace professional advice. If anything concerns you, talk to your pediatrician.",
        'es': "No. Nurtura te ayuda a detectar patrones y sentirte preparado/a, pero no es un dispositivo médico ni diagnostica, trata o sustituye el consejo profesional. Si algo te preocupa, habla con tu pediatra.",
        'fr': "Non. Nurtura vous aide à repérer des schémas et à vous sentir préparé(e), mais ce n'est pas un dispositif médical et ne diagnostique, ne traite ni ne remplace un avis professionnel. En cas d'inquiétude, parlez-en à votre pédiatre.",
        'it': "No. Nurtura ti aiuta a notare pattern e sentirti preparato/a, ma non è un dispositivo medico e non diagnostica, tratta o sostituisce il parere professionale. Se qualcosa ti preoccupa, parlane con il pediatra.",
        'pt-br': "Não. A Nurtura ajuda você a notar padrões e se sentir preparado/a, mas não é um dispositivo médico e não diagnostica, trata ou substitui orientação profissional. Se algo preocupar você, fale com o/a pediatra.",
        'ja': 'いいえ。Nurturaはパターンに気づき備えるための助けですが、医療機器ではなく、診断・治療・専門家のアドバイスの代わりにはなりません。気になることがあれば小児科医にご相談ください。',
        'nl': "Nee. Nurtura helpt je patronen op te merken en je voorbereid te voelen, maar het is geen medisch hulpmiddel en stelt geen diagnose, behandelt niet en vervangt geen professioneel advies. Maak je je zorgen, neem dan contact op met je kinderarts.",
        'zh-cn': '不是。Nurtura 帮助您发现规律并做好准备，但不是医疗设备，不诊断、不治疗、也不替代专业建议。如有担忧，请咨询儿科医生。',
        'ko': "아닙니다. Nurtura는 패턴을 발견하고 준비할 수 있도록 도와주지만, 의료 기기가 아니며 진단·치료·전문가 조언을 대체하지 않습니다. 걱정되는 점이 있다면 소아과의와 상담하세요.",
        'de': "Nein. Nurtura hilft Ihnen, Muster zu erkennen und sich vorbereitet zu fühlen, ist aber kein Medizinprodukt und ersetzt keine Diagnose, Behandlung oder professionelle Beratung. Wenn Sie sich Sorgen machen, sprechen Sie mit Ihrem Kinderarzt.",
    },
    'section_stuck_title': {
        'en': 'Still stuck?', 'es': '¿Aún con problemas?', 'fr': 'Toujours bloqué ?',
        'it': 'Ancora bloccato?', 'pt-br': 'Ainda travado?', 'ja': 'まだ解決しませんか?',
        'nl': 'Nog steeds vast?', 'zh-cn': '还没解决？', 'ko': '여전히 막혔나요?', 'de': 'Weiterhin festgefahren?',
    },
    'stuck_body': {
        'en': "Email <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> with a description of what you're seeing and what device you're on (e.g. iPhone 15, iOS 26). Screenshots help a lot.",
        'es': "Escribe a <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> describiendo lo que ves y en qué dispositivo (p. ej. iPhone 15, iOS 26). Las capturas ayudan mucho.",
        'fr': "Écrivez à <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> en décrivant ce que vous voyez et votre appareil (ex. iPhone 15, iOS 26). Les captures d'écran aident beaucoup.",
        'it': "Scrivi a <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> descrivendo cosa vedi e quale dispositivo usi (es. iPhone 15, iOS 26). Gli screenshot aiutano molto.",
        'pt-br': "Escreva para <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> descrevendo o que está vendo e em qual dispositivo (ex. iPhone 15, iOS 26). Capturas de tela ajudam muito.",
        'ja': '<a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>まで、何が起きているか、お使いの端末（例: iPhone 15、iOS 26）をご記載ください。スクリーンショットがあると非常に助かります。',
        'nl': "Stuur een mail naar <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> met een omschrijving van wat je ziet en op welk apparaat (bv. iPhone 15, iOS 26). Screenshots helpen enorm.",
        'zh-cn': '请发送邮件至 <a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>，描述您看到的内容和所用设备（例如 iPhone 15、iOS 26）。截图非常有帮助。',
        'ko': '<a href="mailto:support@nurtura.app" class="link">support@nurtura.app</a>으로 어떤 문제가 발생했고 어떤 기기에서 사용 중인지(예: iPhone 15, iOS 26) 알려주세요. 스크린샷이 큰 도움이 됩니다.',
        'de': "Mailen Sie an <a href=\"mailto:support@nurtura.app\" class=\"link\">support@nurtura.app</a> mit einer Beschreibung dessen, was Sie sehen, und Ihrem Gerät (z. B. iPhone 15, iOS 26). Screenshots helfen sehr.",
    },
    # Reuse the same nav/footer keys as Privacy. Easier than re-duplicating.
}

# Carry the nav/footer keys from PRIVACY into SUPPORT so both pages share them.
for k in ('footer_note', 'nav_features', 'nav_premium', 'nav_support', 'nav_cta',
          'footer_home', 'footer_privacy', 'footer_support', 'footer_contact', 'footer_copy'):
    SUPPORT[k] = PRIVACY[k]


def render_hreflang(page: str) -> str:
    """page is 'privacy' or 'support' — used in the hreflang URLs."""
    parts = []
    for lang, code in HREFLANG.items():
        if lang == 'en':
            url = f'https://micahwalkerdesign.github.io/NurturaSite/{page}.html'
        else:
            url = f'https://micahwalkerdesign.github.io/NurturaSite/{lang}/{page}.html'
        parts.append(f'  <link rel="alternate" hreflang="{code}" href="{url}" />')
    parts.append(f'  <link rel="alternate" hreflang="x-default" href="https://micahwalkerdesign.github.io/NurturaSite/{page}.html" />')
    return '\n'.join(parts)


def render_template(template: str, strings: dict, lang: str) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1).strip()
        try:
            return strings[key][lang]
        except KeyError as e:
            raise KeyError(f"Missing key '{key}' in '{lang}'") from e
    return re.sub(r'\{\{\s*([\w_]+)\s*\}\}', repl, template)


def build_page(page: str, strings: dict):
    template_path = ROOT / 'tools' / f'{page}.template.html'
    template = template_path.read_text()
    for lang in LANGUAGES:
        html = template
        html = html.replace('{{LANG_ATTR}}', HREFLANG[lang])
        html = html.replace('{{ASSET_PREFIX}}', '../')
        html = html.replace('{{ROOT_PREFIX}}', '../')  # home link goes to root
        html = html.replace('{{HREFLANG}}', render_hreflang(page))
        html = render_template(html, strings, lang)
        out = ROOT / lang / f'{page}.html'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
        print(f'  {out.relative_to(ROOT)}')


def main():
    print('Privacy:')
    build_page('privacy', PRIVACY)
    print('\nSupport:')
    build_page('support', SUPPORT)
    print('\nDone.')


if __name__ == '__main__':
    main()
