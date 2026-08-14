if ("scrollRestoration" in history) {
  history.scrollRestoration = "manual";
}

window.addEventListener("pageshow", () => {
  window.scrollTo({ top: 0, left: 0, behavior: "auto" });
});

const operations = {
  privacy: {
    label: "Yüzleri anonimleştir",
    description: "Fotoğraf veya videodaki yüzleri otomatik olarak algılar ve gizler.",
    result: "anonimlestirilmis-goruntu",
  },
  people_blur: {
    label: "Kişileri bulanıklaştır",
    description: "Kişileri vücut şekillerine uygun biçimde algılar ve bulanıklaştırır.",
    result: "kisileri-bulaniklastirilmis-goruntu",
  },
  people_remove: {
    label: "Kişileri kaldır",
    description: "Kişileri görüntüden kaldırır ve boşalan alanı çevreye göre tamamlar.",
    result: "kisileri-kaldirilmis-goruntu",
  },
  forklift: {
    label: "Depo nesnelerini tespit et",
    description: "Forklift, kişi, palet ve palet taşıma araçlarını bulup işaretler.",
    result: "depo-nesne-analizi",
  },
  pose: {
    label: "Vücut duruşunu analiz et",
    description: "Kişilerin omuz, dirsek, kalça, diz ve diğer vücut noktalarını gösterir.",
    result: "vucut-durusu-analizi",
  },
};

const englishOperations = {
  privacy: {
    label: "Anonymize faces",
    description: "Detects and protects faces in photos or videos.",
  },
  people_blur: {
    label: "Blur people",
    description: "Detects people and blurs only their body masks.",
  },
  people_remove: {
    label: "Remove people",
    description: "Removes people and reconstructs the cleared area.",
  },
  forklift: {
    label: "Track warehouse objects",
    description: "Detects and tracks forklifts, people and pallets with ByteTrack.",
  },
  pose: {
    label: "Analyze body pose",
    description: "Visualizes body joints and keypoints.",
  },
};

const uiTranslations = {
  tr: {
    intro_eyebrow: "Güvenli görüntü analizi",
    intro_title: "Görüntünüzü güvenle analiz edin.",
    intro_description: "Bir araç seçin; fotoğraf, video veya canlı kamera görüntüsünü aynı ekranda işleyin.",
    how_to: "Nasıl kullanılır?",
    three_steps: "3 kısa adım",
    step_tool: "Aracı seçin",
    step_source: "Görüntüyü ekleyin",
    step_result: "Sonucu alın",
    brand_tagline: "Güvenli görüntü analizi",
    dashboard: "Kontrol paneli",
    help: "Yardım",
    api_docs: "API dokümanı",
    system_ready: "Sistem kullanıma hazır",
    system_warming: "Sistem hazırlanıyor",
    system_error: "Model kontrolü gerekli",
    analysis_tools: "Analiz araçları",
    five_tools: "5 araç",
    choose_operation: "Yapmak istediğiniz işlemi seçin",
    selected_tool: "Seçili araç",
    no_storage: "Kalıcı kayıt yok",
    upload_file: "Dosya yükle",
    use_camera: "Kameradan çek",
    try_demo: "Örnek videoyla dene",
    drop_files: "Dosyalarınızı buraya bırakın",
    upload_limit: "En fazla 10 fotoğrafı birlikte veya tek bir videoyu seçebilirsiniz.",
    choose_file: "Dosya seç",
    supported_files: "JPG, PNG, WebP · MP4, MOV, AVI, WebM · Çoklu seçim desteklenir",
    camera_off: "Kamera kapalı",
    camera_permission: "Başlattığınızda tarayıcınız kamera izni isteyecektir.",
    open_camera: "Kamerayı aç",
    close_camera: "Kamerayı kapat",
    take_photo: "Fotoğraf çek",
    start_live: "Canlı analizi başlat",
    stop_live: "Canlı analizi durdur",
    models_warming: "Modeller hazırlanıyor",
    models_warming_detail: "Analiz araçları arka planda başlatılıyor.",
    models_ready: "Tüm modeller hazır",
    models_ready_detail: "Analize hemen başlayabilirsiniz.",
    models_error: "Bazı modeller hazırlanamadı",
    models_error_detail: "İlgili aracı açtığınızda tekrar denenecek.",
    demo_preparing: "Demo hazırlanıyor…",
    demo_analyzing: "Demo analiz ediliyor…",
    replace_file: "Dosyayı değiştir",
    privacy_method_title: "Yüzlerin nasıl gizleneceğini seçin",
    privacy_method_help: "Bu ayar yalnızca yüz anonimleştirme işleminde kullanılır.",
    blur: "Bulanıklaştır",
    mosaic: "Mozaik uygula",
    color_shield: "Renkle kapat",
    gesture_control: "El hareketiyle kontrol",
    gesture_control_help: "Canlı kamerada sıkıştırma hareketiyle blur'u açıp kapatın.",
    gesture_ready: "Kapalı",
    gesture_waiting: "El hareketi bekleniyor",
    gesture_blur_on: "Blur açık",
    gesture_blur_off: "Blur kapalı",
    gesture_unavailable: "El algılama bileşeni kullanılamıyor",
    advanced_settings: "Gelişmiş ayarlar",
    advanced_help: "Canlı analiz akıcılığı",
    no_file: "Henüz dosya seçilmedi",
    file_limits: "Fotoğraf en fazla 10 MB, video en fazla 250 MB olabilir.",
    analysis_complete: "Analiz tamamlandı",
    result_ready: "Sonucunuz hazır",
    result_help: "İşlenmiş görüntüyü kontrol edebilir veya cihazınıza indirebilirsiniz.",
    processed_result: "İşlenmiş sonuç",
    secure_preview: "Güvenli önizleme",
    applied_operation: "Uygulanan işlem",
    content_type: "İçerik türü",
    analysis_summary: "Analiz özeti",
    processing_details: "İşlem ayrıntıları",
    completed_securely: "Güvenli biçimde tamamlandı",
    total_duration: "Toplam süre",
    model_duration: "Model süresi",
    sensitivity: "Hassasiyet",
    file_size: "Dosya boyutu",
    applied_mode: "Uygulanan mod",
    processing_speed: "İşleme hızı",
    download_result: "Sonucu indir",
    new_analysis: "Yeni analiz başlat",
    light_theme: "Açık tema",
    dark_theme: "Koyu tema",
    sensitivity: "Algılama hassasiyeti",
    sensitivity_help: "Düşük değer daha çok nesne bulur; yanlış tespit ihtimali artabilir.",
    live_performance: "Canlı analiz akıcılığı",
    live_performance_help: "Düşük donanımlı cihazlarda “Ekonomik” seçeneğini kullanın.",
    eco: "Ekonomik",
    balanced: "Dengeli",
    detailed: "Detaylı",
    faq_eyebrow: "Merak edilenler",
    faq_title: "Sık sorulan sorular",
    faq_intro: "Kullanım ve gizlilik hakkında kısa cevaplar.",
    faq_storage_q: "Görüntülerim kalıcı olarak saklanıyor mu?",
    faq_storage_a: "Hayır. İşlem dosyaları sonuç üretildikten sonra temizlenir; tamamlanan video işleri de süre sonunda otomatik kaldırılır.",
    faq_video_q: "Fotoğraf dışında video kullanabilir miyim?",
    faq_video_a: "Evet. MP4, MOV, AVI ve WebM videolarını yükleyebilir veya hazır demo videolarıyla sistemi deneyebilirsiniz.",
    faq_camera_q: "Canlı kamera analizi ne işe yarar?",
    faq_camera_a: "Kameradan gelen görüntüyü seçili araçla aralıklı olarak işler ve sonucu canlı şekilde gösterir.",
    faq_security_q: "Yüklenen dosyalar nasıl güvenli tutuluyor?",
    faq_security_a: "Dosya türü, gerçek içerik imzası, boyut, çözünürlük ve video süresi sunucuda doğrulanır. Geçici dosyalar rastgele adlandırılır ve süre sonunda silinir.",
    faq_api_q: "API kötüye kullanıma karşı korunuyor mu?",
    faq_api_a: "İstek hızı ve eşzamanlı video işleri sınırlandırılır. İnternete açık kullanımda ayrıca API anahtarı etkinleştirilebilir.",
    no_recording: "Görüntü kaydı yok",
    no_recording_help: "Ham dosyanız kalıcı olarak saklanmaz.",
    kvkk_design: "KVKK odaklı tasarım",
    kvkk_design_help: "Kişisel verileri korumaya öncelik verir.",
    one_screen: "Tek ekranda kullanım",
    one_screen_help: "Teknik bilgi gerektirmeden sonuç alın.",
    verified_upload: "Doğrulanmış yükleme",
    verified_upload_help: "Tür, boyut, çözünürlük ve süre sunucuda kontrol edilir.",
    footer_copy: "© 2026 · Güvenli görüntü analizi için geliştirildi.",
    welcome: "Hoş geldiniz",
    welcome_title: "İlk analizinizi üç adımda tamamlayın",
    welcome_intro: "Bir araç seçin, kendi görüntünüzü ekleyin veya örnek videoyu kullanın. Ham dosyanız kalıcı olarak saklanmaz.",
    welcome_tool: "Analiz aracını seçin",
    welcome_tool_help: "İhtiyacınıza uygun beş araçtan birini kullanın.",
    welcome_media: "Görüntüyü ekleyin",
    welcome_media_help: "Dosya yükleyin, kamerayı açın veya hazır demoyu seçin.",
    welcome_result: "Sonucu kontrol edin",
    welcome_result_help: "İşlenmiş çıktıyı görüntüleyin ve indirin.",
    start_analysis: "Analize başla",
    live_analysis: "Canlı analiz",
    progress_video: "Video işleniyor",
    progress_frames: "Kareler analiz ediliyor…",
    progress_preparing: "Dosya hazırlanıyor",
    cancel: "İşlemi iptal et",
    batch: "Toplu işlem",
    batch_ready: "Dosyalarınız hazır",
    tool_guide: "Araç rehberi",
    tool_guide_title: "Hangi araç ne işe yarar?",
    privacy_guide: "Kimliği belli eden yüz bölgelerini bulanıklaştırır, mozaikler veya renkle kapatır.",
    blur_guide: "Yalnızca yüzü değil, kişinin bütün vücudunu gizler.",
    remove_guide: "Kişiyi görüntüden siler. Karmaşık arka planlarda sonuç değişebilir.",
    removal_target_title: "Kim kaldırılacak?",
    removal_target_all_help: "Videodaki tüm kişiler kaldırılır.",
    remove_everyone: "Tüm kişileri kaldır",
    remove_selected: "Bir kişi seç",
    forklift_guide: "Forklift, kişi ve paletleri bulur; videoda nesneleri ByteTrack ile takip eder.",
    pose_guide: "Vücut eklemlerini görselleştirir; tıbbi değerlendirme amacı taşımaz.",
    local_dashboard: "Yerel kontrol paneli",
    dashboard_summary: "Analiz özeti",
    dashboard_privacy: "Bu bilgiler yalnızca bu tarayıcıda tutulur; görüntüler geçmişe kaydedilmez.",
    total_analysis: "Toplam analiz",
    today_analysis: "Bugünkü analiz",
    video_analysis: "Video analizi",
    tool_usage: "Araç kullanımı",
    recent_analysis: "Son analizler",
    clear_history: "Geçmişi temizle",
    learn_eyebrow: "Sistemi tanıyın",
    learn_title: "Sistem hakkında kısa bilgiler",
    learn_intro: "Merak ettiğiniz konuya dokunarak ayrıntıları görüntüleyin.",
    learn_privacy: "Gizlilik nasıl korunuyor?",
    learn_privacy_short: "Yüz ve kişi gizleme yöntemlerini öğrenin.",
    learn_live: "Canlı analiz nasıl çalışıyor?",
    learn_live_short: "FPS, gecikme ve kamera akışını anlayın.",
    learn_models: "Hangi araç ne zaman seçilmeli?",
    learn_models_short: "Beş analiz aracını doğru işle eşleştirin.",
    learn_more: "Bilgi al →",
    close_info: "Anladım",
    about_eyebrow: "Proje hakkında",
    about_title: "Gizliliği önceliklendiren görüntü analizi",
    company_label: "Şirket",
    company_description: "Vispection AI, görüntü analizini erişilebilir ve gizlilik odaklı hale getiren araçlar geliştirir.",
    developer_label: "Geliştirici",
    developer_role: "Proje geliştiricisi",
    contact: "İletişime geç",
    view_github: "GitHub projesini görüntüle",
  },
  en: {
    intro_eyebrow: "Secure visual analysis",
    intro_title: "Analyze your media securely.",
    intro_description: "Choose a tool and process photos, videos or a live camera in one workspace.",
    how_to: "How to use",
    three_steps: "3 quick steps",
    step_tool: "Choose a tool",
    step_source: "Add your media",
    step_result: "Get the result",
    brand_tagline: "Secure visual analysis",
    dashboard: "Dashboard",
    help: "Help",
    api_docs: "API docs",
    system_ready: "System ready",
    system_warming: "System preparing",
    system_error: "Model check required",
    analysis_tools: "Analysis tools",
    five_tools: "5 tools",
    choose_operation: "Choose what you want to do",
    selected_tool: "Selected tool",
    no_storage: "No permanent storage",
    upload_file: "Upload file",
    use_camera: "Use camera",
    try_demo: "Try a sample video",
    drop_files: "Drop your files here",
    upload_limit: "Select up to 10 photos together or one video.",
    choose_file: "Choose file",
    supported_files: "JPG, PNG, WebP · MP4, MOV, AVI, WebM · Multiple photos supported",
    camera_off: "Camera is off",
    camera_permission: "Your browser will request camera permission when you start.",
    open_camera: "Open camera",
    close_camera: "Close camera",
    take_photo: "Take photo",
    start_live: "Start live analysis",
    stop_live: "Stop live analysis",
    models_warming: "Preparing models",
    models_warming_detail: "Analysis tools are starting in the background.",
    models_ready: "All models are ready",
    models_ready_detail: "You can start analyzing immediately.",
    models_error: "Some models are not ready",
    models_error_detail: "They will retry when you open the related tool.",
    demo_preparing: "Preparing demo…",
    demo_analyzing: "Analyzing demo…",
    replace_file: "Replace file",
    privacy_method_title: "Choose how faces should be protected",
    privacy_method_help: "This setting appears only for face anonymization.",
    blur: "Blur",
    mosaic: "Apply mosaic",
    color_shield: "Cover with color",
    gesture_control: "Hand gesture control",
    gesture_control_help: "Pinch in the live camera to turn face blur on or off.",
    gesture_ready: "Off",
    gesture_waiting: "Waiting for a hand gesture",
    gesture_blur_on: "Blur on",
    gesture_blur_off: "Blur off",
    gesture_unavailable: "Hand detection component is unavailable",
    advanced_settings: "Advanced settings",
    advanced_help: "Live analysis performance",
    no_file: "No file selected yet",
    file_limits: "Photos can be up to 10 MB and videos up to 250 MB.",
    analysis_complete: "Analysis complete",
    result_ready: "Your result is ready",
    result_help: "Review the processed media or download it to your device.",
    processed_result: "Processed result",
    secure_preview: "Secure preview",
    applied_operation: "Applied operation",
    content_type: "Content type",
    analysis_summary: "Analysis summary",
    processing_details: "Processing details",
    completed_securely: "Completed securely",
    total_duration: "Total duration",
    model_duration: "Model time",
    sensitivity: "Sensitivity",
    file_size: "File size",
    applied_mode: "Applied mode",
    processing_speed: "Processing speed",
    download_result: "Download result",
    new_analysis: "Start a new analysis",
    light_theme: "Light mode",
    dark_theme: "Dark mode",
    sensitivity: "Detection sensitivity",
    sensitivity_help: "A lower value finds more objects but may increase false detections.",
    live_performance: "Live analysis performance",
    live_performance_help: "Use “Eco” on lower-powered devices.",
    eco: "Eco",
    balanced: "Balanced",
    detailed: "Detailed",
    faq_eyebrow: "Common questions",
    faq_title: "Frequently asked questions",
    faq_intro: "Short answers about usage and privacy.",
    faq_storage_q: "Are my images stored permanently?",
    faq_storage_a: "No. Processing files are cleared after results are produced, and completed video jobs are removed automatically after their retention period.",
    faq_video_q: "Can I use video as well as photos?",
    faq_video_a: "Yes. Upload MP4, MOV, AVI or WebM files, or try the system with the included sample videos.",
    faq_camera_q: "What does live camera analysis do?",
    faq_camera_a: "It periodically processes camera frames with the selected tool and displays the result live.",
    faq_security_q: "How are uploaded files protected?",
    faq_security_a: "The server validates file type, content signature, size, resolution and video duration. Temporary files use random names and are deleted automatically.",
    faq_api_q: "Is the API protected against abuse?",
    faq_api_a: "Request rates and concurrent video jobs are limited. An API key can also be enabled for internet-facing use.",
    no_recording: "No image archive",
    no_recording_help: "Your raw file is not stored permanently.",
    kvkk_design: "Privacy-focused design",
    kvkk_design_help: "Prioritizes the protection of personal data.",
    one_screen: "One-screen workflow",
    one_screen_help: "Get results without technical knowledge.",
    verified_upload: "Validated uploads",
    verified_upload_help: "Type, size, resolution and duration are checked server-side.",
    footer_copy: "© 2026 · Built for secure visual analysis.",
    welcome: "Welcome",
    welcome_title: "Complete your first analysis in three steps",
    welcome_intro: "Choose a tool, add your own media or use a sample video. Your raw file is not stored permanently.",
    welcome_tool: "Choose an analysis tool",
    welcome_tool_help: "Use one of five tools for your task.",
    welcome_media: "Add your media",
    welcome_media_help: "Upload a file, open the camera or select a sample.",
    welcome_result: "Review the result",
    welcome_result_help: "Preview and download the processed output.",
    start_analysis: "Start analyzing",
    live_analysis: "Live analysis",
    progress_video: "Processing video",
    progress_frames: "Analyzing frames…",
    progress_preparing: "Preparing file",
    cancel: "Cancel",
    batch: "Batch processing",
    batch_ready: "Your files are ready",
    tool_guide: "Tool guide",
    tool_guide_title: "What does each tool do?",
    privacy_guide: "Blurs, mosaics or covers identifiable face regions.",
    blur_guide: "Protects the person's full body, not only the face.",
    remove_guide: "Removes the person from the image. Results may vary on complex backgrounds.",
    removal_target_title: "Who should be removed?",
    removal_target_all_help: "Every detected person in the video will be removed.",
    remove_everyone: "Remove everyone",
    remove_selected: "Select one person",
    forklift_guide: "Finds forklifts, people and pallets, and tracks objects in video with ByteTrack.",
    pose_guide: "Visualizes body joints; it is not intended for medical assessment.",
    local_dashboard: "Local dashboard",
    dashboard_summary: "Analysis summary",
    dashboard_privacy: "This information stays in this browser; images are not added to history.",
    total_analysis: "Total analyses",
    today_analysis: "Today's analyses",
    video_analysis: "Video analyses",
    tool_usage: "Tool usage",
    recent_analysis: "Recent analyses",
    clear_history: "Clear history",
    learn_eyebrow: "Explore the system",
    learn_title: "Quick information about the system",
    learn_intro: "Select a topic to view more details.",
    learn_privacy: "How is privacy protected?",
    learn_privacy_short: "Learn about face and person protection methods.",
    learn_live: "How does live analysis work?",
    learn_live_short: "Understand FPS, latency and the camera stream.",
    learn_models: "Which tool should I choose?",
    learn_models_short: "Match the five analysis tools to the right task.",
    learn_more: "Learn more →",
    close_info: "Got it",
    about_eyebrow: "About the project",
    about_title: "Visual analysis that prioritizes privacy",
    company_label: "Company",
    company_description: "Vispection AI builds accessible, privacy-focused visual analysis tools.",
    developer_label: "Developer",
    developer_role: "Project developer",
    contact: "Get in touch",
    view_github: "View the GitHub project",
  },
};

const infoTopics = {
  tr: {
    privacy: {
      badge: "Gizlilik",
      title: "Görüntünüz üzerinde kontrol sizde kalır",
      description: "Sistem, seçtiğiniz gizleme yöntemini yalnızca işlenen görüntüye uygular.",
      points: [
        "Yüz anonimleştirme; bulanıklaştırma, mozaik veya renk kalkanı kullanabilir.",
        "Kişi bulanıklaştırma yalnızca algılanan insan maskesini hedefler.",
        "Ham dosyalar kalıcı bir kullanıcı arşivine eklenmez.",
      ],
    },
    live: {
      badge: "Canlı analiz",
      title: "Akıcılık ve ayrıntı arasında seçim yapabilirsiniz",
      description: "Kamera kareleri sırayla işlenir; arayüz aynı anda birden fazla ağır istek göndermez.",
      points: [
        "FPS değeri saniyede görüntülenen işlenmiş kare sayısını gösterir.",
        "Gecikme, bir karenin analiz edilip ekrana dönme süresidir.",
        "Ekonomik profil düşük donanımda daha akıcı bir deneyim sağlar.",
      ],
    },
    models: {
      badge: "Araç seçimi",
      title: "Her işlem kendi analiz bileşenini kullanır",
      description: "İhtiyacınıza en yakın aracı seçmek hem sonucu hem işlem süresini iyileştirir.",
      points: [
        "Kimliği gizlemek için yüz anonimleştirmeyi veya kişi bulanıklaştırmayı seçin.",
        "Depo sahnelerinde forklift analizi ByteTrack ile nesne kimliklerini takip eder.",
        "Eklem noktaları için vücut duruşu analizini kullanın.",
      ],
    },
  },
  en: {
    privacy: {
      badge: "Privacy",
      title: "You remain in control of your media",
      description: "The system applies your selected protection method only to the processed output.",
      points: [
        "Face anonymization can use blur, mosaic or a solid color shield.",
        "Person blur targets only the detected human mask.",
        "Raw files are not added to a permanent user archive.",
      ],
    },
    live: {
      badge: "Live analysis",
      title: "Choose between smoothness and detail",
      description: "Camera frames are processed in sequence so the interface does not send overlapping heavy requests.",
      points: [
        "FPS shows the number of processed frames displayed each second.",
        "Latency is the time required to analyze and return one frame.",
        "Eco mode provides a smoother experience on lower-powered hardware.",
      ],
    },
    models: {
      badge: "Tool selection",
      title: "Each task uses its own analysis component",
      description: "Choosing the closest tool for your need improves both results and processing time.",
      points: [
        "Choose face anonymization or person blur to protect identities.",
        "For warehouse scenes, forklift analysis tracks object IDs with ByteTrack.",
        "Use body pose analysis when you need joint keypoints.",
      ],
    },
  },
};

const sampleVideos = {
  privacy: {
    url: "/static/samples/face-privacy-demo.mp4",
    filename: "yuz-anonimlestirme-demo.mp4",
    description: "Yüz gizleme aracını hazır bir insan videosunda deneyin.",
  },
  people_blur: {
    url: "/static/samples/people-blur-demo.mp4",
    filename: "kisi-bulaniklastirma-demo.mp4",
    description: "Kişi bulanıklaştırmayı hazır bir insan videosunda deneyin.",
  },
  people_remove: {
    url: "/static/samples/people-remove-demo.mp4",
    filename: "kisi-kaldirma-demo.mp4",
    description: "Kişi kaldırmayı hazır bir insan videosunda deneyin.",
  },
  forklift: {
    url: "/static/samples/warehouse-demo.mp4?v=20260803-2",
    filename: "depo-analizi-demo.mp4",
    description: "Tamamı kadrajda görünen hareketli forklifti ByteTrack ile analiz edin.",
  },
  pose: {
    url: "/static/samples/multi-person-pose-demo.mp4?v=20260803-2",
    filename: "vucut-durusu-demo.mp4",
    description: "Günlük kıyafetlerle yürüyen üç kişinin duruş ve hareketlerini analiz edin.",
  },
};

const state = {
  language: localStorage.getItem("vispection_language") || "tr",
  operation: "privacy",
  mode: "soft_blur",
  source: "file",
  file: null,
  files: [],
  mediaType: null,
  previewUrl: null,
  resultUrl: null,
  removalTarget: "all",
  selectedPersonPoint: null,
  batchActive: false,
  processing: false,
  batchIndex: 0,
  batchStatuses: [],
  batchResults: [],
  progressTimer: null,
  confidence: {
    privacy: 0.30,
    people_blur: 0.20,
    people_remove: 0.20,
    forklift: 0.15,
    pose: 0.25,
  },
  liveProfile: "balanced",
  liveDelay: 450,
  liveMaxWidth: 384,
  liveJpegQuality: 0.48,
  liveRequestTimeoutMs: 2500,
  liveCaptureCanvas: document.createElement("canvas"),
  liveCaptureContext: null,
  liveDisplayContext: null,
  liveLoopTimer: null,
  liveInFlight: false,
  liveGeneration: 0,
  liveConsecutiveErrors: 0,
  liveAdaptiveWidth: 320,
  liveStableFrames: 0,
  cameraStream: null,
  cameraStartGeneration: 0,
  cameraWatchdogTimer: null,
  cameraRecoveryTimer: null,
  cameraRecoveryAttempts: 0,
  cameraPreferredDeviceId: null,
  cameraLastVideoTime: 0,
  cameraStalledChecks: 0,
  currentJobId: null,
  liveAnalysis: false,
  liveAbortController: null,
  liveSessionId: null,
  liveFrames: 0,
  liveFps: 0,
  liveLatency: 0,
  liveDroppedFrames: 0,
  liveLastFrameAt: null,
  liveExpectedFrameMs: 1000 / 30,
  liveAlerts: 0,
  liveStartedAt: null,
  liveQualityProbeCounter: 0,
  liveQualityMetrics: null,
  livePreviousQualitySample: null,
  liveQualityCandidate: null,
  liveQualityCandidateFrames: 0,
  liveQualityClearFrames: 0,
  liveQualityIssue: null,
  liveMissingTargetFrames: 0,
  liveLastQualityToastAt: 0,
  gestureControl: false,
  gesturePrivacyEnabled: true,
  modelHealth: { status: "pending", ready: 0, total: 4 },
  modelPollTimer: null,
  lastResultDetails: null,
};

const $ = (selector) => document.querySelector(selector);
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
let themeAnimationTimer = null;
let themeTransitionTimer = null;
const elements = {
  operationCards: document.querySelectorAll(".operation-card"),
  modeButtons: document.querySelectorAll(".mode-button"),
  sourceButtons: document.querySelectorAll(".source-button"),
  sampleVideoButton: $("#sample-video-button"),
  sampleVideoDescription: $("#sample-video-description"),
  sampleVideoPreview: $("#sample-video-preview"),
  privacyOptions: $("#privacy-options"),
  dropzone: $("#dropzone"),
  uploadQueue: $("#upload-queue"),
  cameraPanel: $("#camera-panel"),
  fileInput: $("#file-input"),
  chooseButton: $("#choose-button"),
  emptyUpload: $("#empty-upload"),
  previewWrap: $("#preview-wrap"),
  previewImage: $("#preview-image"),
  previewVideo: $("#preview-video"),
  resultCanvas: $("#result-canvas"),
  previewProgress: $("#preview-progress"),
  previewProgressDetail: $("#preview-progress-detail"),
  previewProgressValue: $("#preview-progress-value"),
  previewProgressTrack: $("#preview-progress-track"),
  previewProgressBar: $("#preview-progress-bar"),
  previewCancelJobButton: $("#preview-cancel-job-button"),
  removalTargetOptions: $("#removal-target-options"),
  removalTargetButtons: document.querySelectorAll("[data-removal-target]"),
  removalTargetHelp: $("#removal-target-help"),
  personSelectionOverlay: $("#person-selection-overlay"),
  personSelectionHint: $("#person-selection-hint"),
  personSelectionMarker: $("#person-selection-marker"),
  removeButton: $("#remove-button"),
  cameraVideo: $("#camera-video"),
  cameraCanvas: $("#camera-canvas"),
  liveStatus: $("#live-status"),
  liveFrameCount: $("#live-frame-count"),
  cameraQualityAlert: $("#camera-quality-alert"),
  cameraQualityAlertText: $("#camera-quality-alert-text"),
  cameraEmpty: $("#camera-empty"),
  cameraSelect: $("#camera-select"),
  startCameraButton: $("#start-camera-button"),
  captureButton: $("#capture-button"),
  liveAnalysisButton: $("#live-analysis-button"),
  gestureControlRow: $("#gesture-control-row"),
  gestureControlToggle: $("#gesture-control-toggle"),
  gestureStatus: $("#gesture-status"),
  advancedToggle: $("#advanced-toggle"),
  advancedPanel: $("#advanced-panel"),
  confidenceRange: $("#confidence-range"),
  confidenceValue: $("#confidence-value"),
  profileButtons: document.querySelectorAll("[data-profile]"),
  processButton: $("#process-button"),
  buttonLabel: $(".button-label"),
  activeOperationTitle: $("#active-operation-title"),
  activeOperationDescription: $("#active-operation-description"),
  fileMeta: $("#file-meta"),
  message: $("#message"),
  resultSection: $("#result-section"),
  resultSummary: $("#result-summary"),
  resultOperation: $("#result-operation"),
  resultMediaType: $("#result-media-type"),
  resultMetric: $("#result-metric"),
  resultDuration: $("#result-duration"),
  resultServerTime: $("#result-server-time"),
  resultConfidence: $("#result-confidence"),
  resultFileSize: $("#result-file-size"),
  resultMode: $("#result-mode"),
  resultThroughput: $("#result-throughput"),
  resultPreviewImage: $("#result-preview-image"),
  resultPreviewVideo: $("#result-preview-video"),
  detectionList: $("#detection-list"),
  downloadButton: $("#download-button"),
  newButton: $("#new-button"),
  progressPanel: $("#progress-panel"),
  progressTitle: $("#progress-title"),
  progressDetail: $("#progress-detail"),
  progressValue: $("#progress-value"),
  progressBar: $("#progress-bar"),
  progressTrack: $("#progress-track"),
  progressIcon: $("#progress-icon"),
  progressFile: $("#progress-file"),
  cancelJobButton: $("#cancel-job-button"),
  batchResults: $("#batch-results"),
  batchResultCount: $("#batch-result-count"),
  batchResultList: $("#batch-result-list"),
  dashboardButton: $("#dashboard-button"),
  helpButton: $("#help-button"),
  toolInfoButton: $("#tool-info-button"),
  welcomeDialog: $("#welcome-dialog"),
  welcomeStartButton: $("#welcome-start-button"),
  toolDialog: $("#tool-dialog"),
  infoDetailDialog: $("#info-detail-dialog"),
  infoDetailBadge: $("#info-detail-badge"),
  infoDetailTitle: $("#info-detail-title"),
  infoDetailDescription: $("#info-detail-description"),
  infoDetailList: $("#info-detail-list"),
  dashboardDialog: $("#dashboard-dialog"),
  clearHistoryButton: $("#clear-history-button"),
  operationChart: $("#operation-chart"),
  historyList: $("#history-list"),
  toast: $("#toast"),
  toastIcon: $("#toast-icon"),
  toastTitle: $("#toast-title"),
  toastMessage: $("#toast-message"),
  themeButton: $("#theme-button"),
  themeIcon: $("#theme-icon"),
  themeLabel: $("#theme-label"),
  languageSelect: $("#language-select"),
  systemHealth: $(".system-health"),
  headerStatus: $("#header-status"),
  headerStatusText: $("#header-status-text"),
  modelStatusTitle: $("#model-status-title"),
  modelStatusDetail: $("#model-status-detail"),
  modelStatusCount: $("#model-status-count"),
};

function operationLabel(operation) {
  return state.language === "en"
    ? englishOperations[operation].label
    : operations[operation].label;
}

function operationDescription(operation) {
  return state.language === "en"
    ? englishOperations[operation].description
    : operations[operation].description;
}

function replayMotion(element, className) {
  if (!element || prefersReducedMotion) return;
  element.classList.remove(className);
  void element.offsetWidth;
  element.classList.add(className);
}

function applyLanguage(language) {
  state.language = language === "en" ? "en" : "tr";
  localStorage.setItem("vispection_language", state.language);
  document.documentElement.lang = state.language;
  elements.languageSelect.value = state.language;
  const copy = uiTranslations[state.language];
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const value = copy[element.dataset.i18n];
    if (value) element.textContent = value;
  });
  elements.operationCards.forEach((card) => {
    const operation = card.dataset.operation;
    card.querySelector("strong").textContent = operationLabel(operation);
    card.querySelector("small").textContent = operationDescription(operation);
  });
  document.querySelectorAll("[data-operation-copy]").forEach((element) => {
    element.textContent = operationLabel(element.dataset.operationCopy);
  });
  elements.activeOperationTitle.textContent = operationLabel(state.operation);
  elements.activeOperationDescription.textContent = operationDescription(state.operation);
  elements.sampleVideoDescription.textContent = state.language === "en"
    ? {
        privacy: "Try face anonymization with a ready-made people video.",
        people_blur: "Try person-only blur with a ready-made people video.",
        people_remove: "Try removing people from a ready-made video.",
        forklift: "Track a fully visible moving forklift with ByteTrack.",
        pose: "Analyze the pose and movement of three casually dressed people walking together.",
      }[state.operation]
    : sampleVideos[state.operation].description;
  if (!state.file) {
    elements.fileMeta.innerHTML = `
      <strong>${copy.no_file}</strong>
      <span>${copy.file_limits}</span>
    `;
  } else if (state.files.length === 1) {
    elements.fileMeta.innerHTML = `
      <strong>${escapeHtml(state.file.name)}</strong>
      <span>${state.mediaType === "image" ? (state.language === "en" ? "Photo" : "Fotoğraf") : "Video"} · ${formatBytes(state.file.size)}</span>
    `;
  }
  elements.startCameraButton.textContent = state.cameraStream
    ? copy.close_camera
    : copy.open_camera;
  elements.liveAnalysisButton.textContent = state.liveAnalysis
    ? copy.stop_live
    : copy.start_live;
  updateGestureStatus(elements.gestureStatus.dataset.status || "ready");
  applyTheme(document.documentElement.dataset.theme || "light");
  updateActionLabel();
  updatePersonSelectionUi();
  refreshModelStatus();
  if (!elements.resultSection.hidden) updateResultTechnicalDetails();
}

function selectOperation(operation) {
  if (state.processing) return;
  if (state.liveAnalysis) stopLiveAnalysis();
  const operationChanged = state.operation !== operation;
  state.operation = operation;
  if (operationChanged && state.file) resetUpload();
  elements.operationCards.forEach((card) => {
    const selected = card.dataset.operation === operation;
    card.classList.toggle("selected", selected);
    card.setAttribute("aria-checked", String(selected));
  });
  elements.buttonLabel.textContent = operationLabel(operation);
  elements.activeOperationTitle.textContent = operationLabel(operation);
  elements.activeOperationDescription.textContent = operationDescription(operation);
  replayMotion(document.querySelector(".work-header"), "selection-change");
  const confidencePercent = Math.round(state.confidence[operation] * 100);
  elements.confidenceRange.value = String(confidencePercent);
  elements.confidenceValue.textContent = `${confidencePercent}%`;
  elements.sampleVideoDescription.textContent = state.language === "en"
    ? {
        privacy: "Try face anonymization with a ready-made people video.",
        people_blur: "Try person-only blur with a ready-made people video.",
        people_remove: "Try removing people from a ready-made video.",
        forklift: "Track a fully visible moving forklift with ByteTrack.",
        pose: "Analyze the pose and movement of three casually dressed people walking together.",
      }[operation]
    : sampleVideos[operation].description;
  if (elements.sampleVideoPreview.getAttribute("src") !== sampleVideos[operation].url) {
    elements.sampleVideoPreview.src = sampleVideos[operation].url;
    elements.sampleVideoPreview.load();
  }
  clearBatchResults();
  resetProgress();
  updateActionLabel();
  updateContextualOptions();
  clearResult();
}

function selectMode(mode) {
  if (state.processing) return;
  state.mode = mode;
  elements.modeButtons.forEach((button) => {
    const selected = button.dataset.mode === mode;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
}

function updateGestureStatus(status = "ready") {
  const copy = uiTranslations[state.language];
  const labels = {
    ready: copy.gesture_ready,
    waiting: copy.gesture_waiting,
    enabled: copy.gesture_blur_on,
    disabled: copy.gesture_blur_off,
    unavailable: copy.gesture_unavailable,
  };
  elements.gestureStatus.textContent = labels[status] || labels.ready;
  elements.gestureStatus.dataset.status = status;
}

function toggleAdvancedSettings() {
  const expanded = elements.advancedToggle.getAttribute("aria-expanded") === "true";
  elements.advancedToggle.setAttribute("aria-expanded", String(!expanded));
  elements.advancedPanel.hidden = expanded;
}

function selectLiveProfile(profile) {
  const profiles = {
    eco: { delay: 180, maxWidth: 256, jpegQuality: 0.38, timeoutMs: 2400 },
    balanced: { delay: 120, maxWidth: 288, jpegQuality: 0.42, timeoutMs: 3000 },
    detail: { delay: 150, maxWidth: 352, jpegQuality: 0.50, timeoutMs: 3800 },
  };
  const selectedProfile = profiles[profile] || profiles.balanced;
  state.liveProfile = profile in profiles ? profile : "balanced";
  state.liveDelay = selectedProfile.delay;
  state.liveMaxWidth = selectedProfile.maxWidth;
  state.liveJpegQuality = selectedProfile.jpegQuality;
  state.liveRequestTimeoutMs = selectedProfile.timeoutMs;
  state.liveAdaptiveWidth = selectedProfile.maxWidth;
  state.liveStableFrames = 0;
  elements.profileButtons.forEach((button) => {
    const selected = button.dataset.profile === state.liveProfile;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
}

function selectSource(source) {
  if (state.processing) return;
  if (source === "camera" && state.source !== "camera") resetUpload();
  state.source = source;
  elements.sourceButtons.forEach((button) => {
    const selected = button.dataset.source === source;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
  elements.dropzone.hidden = source !== "file";
  elements.cameraPanel.hidden = source !== "camera";
  replayMotion(source === "file" ? elements.dropzone : elements.cameraPanel, "source-change");
  if (source !== "camera") stopCamera();
  showMessage("");
}

async function loadSampleVideo() {
  if (state.processing || elements.sampleVideoButton.disabled) return;
  const sample = sampleVideos[state.operation];
  const originalLabel = elements.sampleVideoButton.querySelector("strong").textContent;
  elements.sampleVideoButton.disabled = true;
  elements.sampleVideoButton.querySelector("strong").textContent =
    uiTranslations[state.language].demo_preparing;

  try {
    const response = await fetch(sample.url);
    if (!response.ok) throw new Error("Örnek video yüklenemedi.");
    const blob = await response.blob();
    const file = new File([blob], sample.filename, { type: "video/mp4" });
    selectSource("file");
    setFiles([file]);
    if (state.operation === "people_remove") {
      elements.previewVideo.pause();
      elements.previewVideo.currentTime = 0;
      showMessage(
        state.language === "en"
          ? "Choose Remove everyone or Select one person directly on the video, then start processing."
          : "Videonun üzerinden ‘Tüm kişileri kaldır’ veya ‘Bir kişi seç’ seçeneğini belirleyip işlemi başlatın.",
      );
      return;
    }
    elements.sampleVideoButton.querySelector("strong").textContent =
      uiTranslations[state.language].demo_analyzing;
    await delay(120);
    await processSelection();
  } catch (error) {
    showMessage(error.message || "Örnek video yüklenemedi.");
  } finally {
    elements.sampleVideoButton.disabled = false;
    elements.sampleVideoButton.querySelector("strong").textContent = originalLabel;
  }
}

function validateFile(file) {
  const imageTypes = ["image/jpeg", "image/png", "image/webp"];
  const videoTypes = ["video/mp4", "video/quicktime", "video/x-msvideo", "video/webm"];
  const isImage = imageTypes.includes(file.type);
  const isVideo = videoTypes.includes(file.type);
  if (!isImage && !isVideo) {
    return { error: "JPEG, PNG, WebP, MP4, MOV, AVI veya WebM dosyası seçin." };
  }
  const limit = isImage ? 10 * 1024 * 1024 : 250 * 1024 * 1024;
  if (file.size > limit) {
    return {
      error: isImage
        ? `${file.name}: Fotoğraf 10 MB sınırını aşıyor.`
        : `${file.name}: Video 250 MB sınırını aşıyor.`,
    };
  }
  return { isImage, isVideo };
}

function setFiles(fileList) {
  const candidates = Array.from(fileList || []);
  if (!candidates.length) return;
  const validated = candidates.map((file) => ({ file, ...validateFile(file) }));
  const invalid = validated.find((item) => item.error);
  if (invalid) {
    showMessage(invalid.error);
    return;
  }

  const videos = validated.filter((item) => item.isVideo);
  if (videos.length && candidates.length > 1) {
    showMessage("Videolar tek tek işlenir. Çoklu seçim için yalnızca fotoğraf ekleyin.");
    return;
  }
  if (candidates.length > 10) {
    showMessage("Aynı anda en fazla 10 fotoğraf seçebilirsiniz.");
    return;
  }

  clearBatchResults();
  state.files = candidates;
  state.batchStatuses = candidates.map(() => "queued");
  setFile(candidates[0], { preserveQueue: true });
  if (candidates.length > 1) {
    const totalSize = candidates.reduce((sum, file) => sum + file.size, 0);
    const countText = state.language === "en"
      ? `${candidates.length} photos selected`
      : `${candidates.length} fotoğraf seçildi`;
    const queueText = state.language === "en" ? "Will be processed in order" : "Sırayla işlenecek";
    elements.fileMeta.innerHTML = `
      <strong>${countText}</strong>
      <span>${state.language === "en" ? "Total" : "Toplam"} ${formatBytes(totalSize)} · ${queueText}</span>
    `;
  }
  renderUploadQueue();
  updateActionLabel();
}

function setFile(file, { preserveQueue = false } = {}) {
  if (!file) return;
  const validation = validateFile(file);
  if (validation.error) {
    showMessage(validation.error);
    return;
  }
  const { isImage } = validation;
  if (!preserveQueue) {
    clearBatchResults();
    state.files = [file];
    state.batchStatuses = ["queued"];
  }

  cleanupUrl("previewUrl");
  state.file = file;
  state.mediaType = isImage ? "image" : "video";
  clearPersonSelection();
  state.previewUrl = URL.createObjectURL(file);
  elements.emptyUpload.hidden = true;
  elements.previewWrap.hidden = false;
  elements.processButton.disabled = false;
  elements.resultCanvas.hidden = true;

  if (isImage) {
    elements.previewImage.src = state.previewUrl;
    elements.previewImage.hidden = false;
    elements.previewVideo.hidden = true;
    elements.previewVideo.removeAttribute("src");
  } else {
    elements.previewVideo.src = state.previewUrl;
    elements.previewVideo.hidden = false;
    elements.previewImage.hidden = true;
    elements.previewImage.removeAttribute("src");
  }
  elements.fileInput.value = "";
  elements.fileMeta.innerHTML = `
    <strong>${escapeHtml(file.name)}</strong>
    <span>${isImage ? (state.language === "en" ? "Photo" : "Fotoğraf") : "Video"} · ${formatBytes(file.size)}</span>
  `;
  showMessage("");
  updateContextualOptions();
  clearResult();
  if (!state.batchActive) resetProgress();
  updateSteps(2);
  renderUploadQueue();
  updateActionLabel();
}

function resetUpload() {
  cleanupUrl("previewUrl");
  state.file = null;
  state.files = [];
  state.batchStatuses = [];
  state.batchActive = false;
  state.mediaType = null;
  clearPersonSelection();
  elements.previewImage.removeAttribute("src");
  elements.previewVideo.removeAttribute("src");
  elements.emptyUpload.hidden = false;
  elements.previewWrap.hidden = true;
  elements.uploadQueue.hidden = true;
  elements.uploadQueue.innerHTML = "";
  elements.processButton.disabled = true;
  elements.fileMeta.innerHTML = `
    <strong>${uiTranslations[state.language].no_file}</strong>
    <span>${uiTranslations[state.language].file_limits}</span>
  `;
  showMessage("");
  updateContextualOptions();
  clearResult();
  clearBatchResults();
  resetProgress();
  updateSteps(1);
}

function renderUploadQueue() {
  const showQueue = state.files.length > 1;
  elements.uploadQueue.hidden = !showQueue;
  if (!showQueue) {
    elements.uploadQueue.innerHTML = "";
    return;
  }
  elements.uploadQueue.innerHTML = state.files.map((file, index) => {
    const status = state.batchStatuses[index] || "queued";
    const statusText = {
      queued: "Sırada",
      active: "İşleniyor",
      done: "Tamamlandı",
      error: "İşlenemedi",
    }[status];
    return `
      <div class="queue-item ${status}" data-queue-index="${index}">
        <span class="queue-file-icon" aria-hidden="true">◫</span>
        <span class="queue-item-copy">
          <strong>${escapeHtml(file.name)}</strong>
          <small>${formatBytes(file.size)} · ${statusText}</small>
        </span>
        <button class="queue-remove" type="button" data-remove-index="${index}" aria-label="${escapeHtml(file.name)} dosyasını kaldır">×</button>
      </div>
    `;
  }).join("");
  elements.uploadQueue.querySelectorAll(".queue-remove").forEach((button) => {
    button.disabled = state.batchActive;
  });
}

function removeQueuedFile(index) {
  if (state.batchActive || index < 0 || index >= state.files.length) return;
  state.files.splice(index, 1);
  state.batchStatuses.splice(index, 1);
  if (!state.files.length) {
    resetUpload();
    return;
  }
  setFile(state.files[0], { preserveQueue: true });
  renderUploadQueue();
  updateActionLabel();
}

function updateActionLabel() {
  if (state.batchActive) return;
  elements.buttonLabel.textContent = state.files.length > 1
    ? state.language === "en"
      ? `Analyze ${state.files.length} files`
      : `${state.files.length} dosyayı analiz et`
    : operationLabel(state.operation);
}

function setInterfaceBusy(busy) {
  [
    ...elements.operationCards,
    ...elements.modeButtons,
    ...elements.sourceButtons,
    ...elements.profileButtons,
    ...elements.removalTargetButtons,
    elements.advancedToggle,
    elements.sampleVideoButton,
    elements.chooseButton,
    elements.removeButton,
    elements.gestureControlToggle,
  ].forEach((control) => {
    control.disabled = busy;
  });
  elements.confidenceRange.disabled = busy;
}

function updateContextualOptions() {
  elements.privacyOptions.hidden = !(
    state.operation === "privacy"
    && (
      (state.file && state.mediaType)
      || (state.source === "camera" && state.cameraStream)
    )
  );
  elements.gestureControlRow.hidden = !(
    state.operation === "privacy" && state.source === "camera"
  );
  updatePersonSelectionUi();
}

function clearPersonSelection() {
  state.selectedPersonPoint = null;
  elements.personSelectionOverlay?.classList.remove("has-selection");
  if (elements.personSelectionMarker) {
    elements.personSelectionMarker.style.left = "";
    elements.personSelectionMarker.style.top = "";
  }
}

function updatePersonSelectionUi() {
  const available = state.operation === "people_remove" && Boolean(state.file);
  const selecting = available && state.removalTarget === "selected";
  const choosingPerson = selecting && !state.resultUrl;
  elements.removalTargetOptions.hidden = !available;
  elements.personSelectionOverlay.hidden = !choosingPerson || state.processing;
  elements.removalTargetButtons.forEach((button) => {
    const active = button.dataset.removalTarget === state.removalTarget;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
  elements.removalTargetHelp.textContent = selecting
    ? state.selectedPersonPoint
      ? state.language === "en"
        ? "Selected person will be followed with ByteTrack and removed."
        : "Seçilen kişi ByteTrack ile takip edilerek kaldırılacak."
      : state.language === "en"
        ? "Pause on the opening frame, then tap the person you want to remove."
        : "İpucu: Videoyu ilk karede durdurup kişinin gövdesinin ortasına dokunun."
    : state.language === "en"
      ? "Every detected person in the video will be removed."
      : "Videodaki tüm kişiler kaldırılır.";
  elements.personSelectionHint.textContent = state.selectedPersonPoint
    ? state.language === "en" ? "Person selected — tap again to change" : "Kişi seçildi — değiştirmek için tekrar dokunun"
    : state.language === "en" ? "Tip: tap the center of the person’s body" : "İpucu: Kişinin gövdesinin ortasına dokunun";
  if (available && !state.processing) {
    elements.processButton.disabled = selecting && !state.selectedPersonPoint;
  }
}

function setRemovalTarget(target) {
  if (!['all', 'selected'].includes(target) || state.processing) return;
  if (state.resultUrl) clearResult();
  state.removalTarget = target;
  clearPersonSelection();
  if (target === "selected" && state.mediaType === "video") {
    elements.previewVideo.pause();
    elements.previewVideo.currentTime = 0;
  }
  updatePersonSelectionUi();
}

function selectPersonAt(event) {
  event.preventDefault();
  event.stopPropagation();
  const media = state.mediaType === "video" ? elements.previewVideo : elements.previewImage;
  const rect = media.getBoundingClientRect();
  const sourceWidth = state.mediaType === "video" ? media.videoWidth : media.naturalWidth;
  const sourceHeight = state.mediaType === "video" ? media.videoHeight : media.naturalHeight;
  if (!sourceWidth || !sourceHeight || !rect.width || !rect.height) return;

  const scale = Math.min(rect.width / sourceWidth, rect.height / sourceHeight);
  const contentWidth = sourceWidth * scale;
  const contentHeight = sourceHeight * scale;
  const contentLeft = rect.left + (rect.width - contentWidth) / 2;
  const contentTop = rect.top + (rect.height - contentHeight) / 2;
  const x = (event.clientX - contentLeft) / contentWidth;
  const y = (event.clientY - contentTop) / contentHeight;
  if (x < 0 || x > 1 || y < 0 || y > 1) {
    showMessage(state.language === "en" ? "Tap directly on a person in the image." : "Görüntüde doğrudan bir kişinin üzerine dokunun.");
    return;
  }

  state.selectedPersonPoint = { x, y };
  const overlayRect = elements.personSelectionOverlay.getBoundingClientRect();
  elements.personSelectionMarker.style.left = `${event.clientX - overlayRect.left}px`;
  elements.personSelectionMarker.style.top = `${event.clientY - overlayRect.top}px`;
  elements.personSelectionOverlay.classList.add("has-selection");
  showMessage("");
  updatePersonSelectionUi();
}

function clearResult() {
  cleanupUrl("resultUrl");
  state.lastResultDetails = null;
  elements.resultSection.hidden = true;
  elements.resultPreviewImage.removeAttribute("src");
  elements.resultPreviewImage.hidden = true;
  elements.resultPreviewVideo.pause();
  elements.resultPreviewVideo.removeAttribute("src");
  elements.resultPreviewVideo.hidden = true;
  elements.detectionList.hidden = true;
  elements.detectionList.innerHTML = "";
  elements.downloadButton.hidden = false;
  elements.downloadButton.removeAttribute("href");
  elements.resultCanvas.hidden = true;
  if (state.file && state.previewUrl && state.mediaType === "image") {
    elements.previewImage.src = state.previewUrl;
    elements.previewImage.hidden = false;
  }
  if (state.file && state.previewUrl && state.mediaType === "video") {
    elements.previewVideo.src = state.previewUrl;
    elements.previewVideo.hidden = false;
  }
}

function cleanupUrl(key) {
  if (state[key]) {
    URL.revokeObjectURL(state[key]);
    state[key] = null;
  }
}

function showMessage(text, loading = false) {
  elements.message.textContent = text;
  elements.message.classList.toggle("loading", loading);
}

function resetLiveQualityWarning() {
  state.liveQualityProbeCounter = 0;
  state.liveQualityMetrics = null;
  state.livePreviousQualitySample = null;
  state.liveQualityCandidate = null;
  state.liveQualityCandidateFrames = 0;
  state.liveQualityClearFrames = 0;
  state.liveQualityIssue = null;
  state.liveMissingTargetFrames = 0;
  elements.cameraQualityAlert.hidden = true;
  elements.cameraQualityAlertText.textContent = "";
}

function sampleLiveFrameQuality(context, width, height) {
  state.liveQualityProbeCounter += 1;
  if (state.liveQualityProbeCounter % 8 !== 1) return;

  try {
    const pixels = context.getImageData(0, 0, width, height).data;
    const stepX = Math.max(1, Math.floor(width / 24));
    const stepY = Math.max(1, Math.floor(height / 14));
    const sample = [];
    let brightnessTotal = 0;
    for (let y = Math.floor(stepY / 2); y < height; y += stepY) {
      for (let x = Math.floor(stepX / 2); x < width; x += stepX) {
        const offset = (y * width + x) * 4;
        const luminance = (
          pixels[offset] * 0.2126
          + pixels[offset + 1] * 0.7152
          + pixels[offset + 2] * 0.0722
        );
        sample.push(luminance);
        brightnessTotal += luminance;
      }
    }
    let motion = 0;
    if (state.livePreviousQualitySample?.length === sample.length) {
      motion = sample.reduce(
        (total, value, index) => total + Math.abs(value - state.livePreviousQualitySample[index]),
        0,
      ) / sample.length;
    }
    state.livePreviousQualitySample = sample;
    state.liveQualityMetrics = {
      brightness: brightnessTotal / Math.max(sample.length, 1),
      motion,
    };
  } catch {
    // Quality guidance is optional; analysis must continue if pixel reads fail.
  }
}

function missingTargetMessage() {
  const messages = state.language === "en"
    ? {
      privacy: "No face detected. Face the camera or improve the lighting.",
      people_blur: "No person detected. Include the full body in the frame.",
      people_remove: "No person detected. Include the full body in the frame.",
      forklift: "No forklift detected. Keep the entire vehicle in the frame.",
      pose: "No full-body pose detected. Step back from the camera.",
    }
    : {
      privacy: "Yüz algılanamadı. Kameraya dönün veya ışığı artırın.",
      people_blur: "Kişi algılanamadı. Tüm vücudu kadraja alın.",
      people_remove: "Kişi algılanamadı. Tüm vücudu kadraja alın.",
      forklift: "Forklift algılanamadı. Aracın tamamını kadraja alın.",
      pose: "Tam vücut duruşu algılanamadı. Kameradan biraz uzaklaşın.",
    };
  return messages[state.operation];
}

function evaluateLiveQualityWarning(detectionCount, latency) {
  if (Number.isFinite(detectionCount)) {
    state.liveMissingTargetFrames = detectionCount === 0
      ? state.liveMissingTargetFrames + 1
      : 0;
  }

  const metrics = state.liveQualityMetrics;
  let candidate = null;
  if (metrics?.brightness < 46) {
    candidate = {
      key: "low-light",
      text: state.language === "en"
        ? "Low light. Move to a brighter area for more reliable detection."
        : "Işık düşük. Daha güvenilir algılama için ortamı aydınlatın.",
    };
  } else if (latency > 1100) {
    candidate = {
      key: "high-latency",
      text: state.language === "en"
        ? "High delay. Image quality is being adjusted automatically."
        : "Gecikme yüksek. Görüntü kalitesi otomatik ayarlanıyor.",
    };
  } else if (metrics?.motion > 40) {
    candidate = {
      key: "camera-motion",
      text: state.language === "en"
        ? "The camera is moving quickly. Hold it steadier for stable tracking."
        : "Kamera hızlı hareket ediyor. Kararlı takip için daha sabit tutun.",
    };
  } else if (state.liveMissingTargetFrames >= 6) {
    candidate = { key: "missing-target", text: missingTargetMessage() };
  }

  if (!candidate) {
    state.liveQualityCandidate = null;
    state.liveQualityCandidateFrames = 0;
    state.liveQualityClearFrames += 1;
    if (state.liveQualityClearFrames >= 4) {
      state.liveQualityIssue = null;
      elements.cameraQualityAlert.hidden = true;
    }
    return;
  }

  state.liveQualityClearFrames = 0;
  if (state.liveQualityCandidate === candidate.key) {
    state.liveQualityCandidateFrames += 1;
  } else {
    state.liveQualityCandidate = candidate.key;
    state.liveQualityCandidateFrames = 1;
  }
  if (state.liveQualityCandidateFrames < 3) return;

  const changed = state.liveQualityIssue !== candidate.key;
  state.liveQualityIssue = candidate.key;
  elements.cameraQualityAlertText.textContent = candidate.text;
  elements.cameraQualityAlert.hidden = false;
  if (changed) state.liveAlerts += 1;
  if (changed && Date.now() - state.liveLastQualityToastAt > 12_000) {
    state.liveLastQualityToastAt = Date.now();
    showToast(
      state.language === "en" ? "Camera guidance" : "Kamera önerisi",
      candidate.text,
      "warning",
    );
  }
}

function updateSteps(activeStep) {
  document.querySelectorAll(".steps li").forEach((step, index) => {
    step.classList.toggle("active", index + 1 <= activeStep);
    if (index + 1 === activeStep) {
      step.setAttribute("aria-current", "step");
    } else {
      step.removeAttribute("aria-current");
    }
  });
}

function setCameraPlaceholder(title, description) {
  elements.cameraEmpty.querySelector("strong").textContent = title;
  elements.cameraEmpty.querySelector("p").textContent = description;
  elements.cameraEmpty.hidden = false;
}

function resetCameraPlaceholder() {
  setCameraPlaceholder(
    uiTranslations[state.language].camera_off,
    uiTranslations[state.language].camera_permission,
  );
}

function clearCameraWatchdog() {
  window.clearInterval(state.cameraWatchdogTimer);
  state.cameraWatchdogTimer = null;
  state.cameraLastVideoTime = 0;
  state.cameraStalledChecks = 0;
}

function scheduleCameraRecovery(reason = "stalled") {
  if (!state.cameraStream || state.cameraRecoveryTimer || document.hidden) return;
  const nextAttempt = state.cameraRecoveryAttempts + 1;
  if (nextAttempt > 4) {
    stopCamera({ preserveMessage: true });
    setCameraPlaceholder(
      state.language === "en" ? "Camera connection interrupted" : "Kamera bağlantısı kesildi",
      state.language === "en"
        ? "Close other camera apps, then open the camera again."
        : "Kamerayı kullanan başka uygulamaları kapatıp yeniden açın.",
    );
    showMessage(
      state.language === "en"
        ? "The camera stream stopped and could not reconnect automatically."
        : "Kamera akışı durdu ve otomatik olarak yeniden bağlanamadı.",
    );
    return;
  }

  stopLiveAnalysis();
  elements.cameraCanvas.hidden = true;
  elements.cameraVideo.hidden = true;
  setCameraPlaceholder(
    state.language === "en" ? "Reconnecting camera…" : "Kamera yeniden bağlanıyor…",
    state.language === "en"
      ? "The video stream paused. This usually takes a moment."
      : "Görüntü akışı durakladı. Bu işlem genellikle kısa sürer.",
  );
  const preferredDeviceId = state.cameraPreferredDeviceId;
  state.cameraRecoveryTimer = window.setTimeout(() => {
    state.cameraRecoveryTimer = null;
    startCamera(preferredDeviceId, { recoveryAttempt: nextAttempt, reason });
  }, Math.min(4000, 500 * (2 ** (nextAttempt - 1))));
}

function startCameraWatchdog(stream) {
  clearCameraWatchdog();
  const track = stream.getVideoTracks()[0];
  track?.addEventListener("ended", () => {
    if (state.cameraStream === stream) scheduleCameraRecovery("ended");
  });
  track?.addEventListener("mute", () => {
    if (state.cameraStream === stream) {
      state.cameraStalledChecks = Math.max(1, state.cameraStalledChecks);
    }
  });
  track?.addEventListener("unmute", () => {
    if (state.cameraStream !== stream) return;
    state.cameraStalledChecks = 0;
    state.cameraLastVideoTime = elements.cameraVideo.currentTime;
    elements.cameraVideo.play().catch(() => {});
  });

  state.cameraWatchdogTimer = window.setInterval(() => {
    if (state.cameraStream !== stream || document.hidden) return;
    const video = elements.cameraVideo;
    const activeTrack = stream.getVideoTracks()[0];
    const frameAdvanced = video.currentTime > state.cameraLastVideoTime + 0.01;
    const frameReady = video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA && video.videoWidth > 0;
    state.cameraLastVideoTime = video.currentTime;
    state.cameraStalledChecks = frameAdvanced && frameReady ? 0 : state.cameraStalledChecks + 1;
    if (frameAdvanced && frameReady) state.cameraRecoveryAttempts = 0;
    if (video.paused && activeTrack?.readyState === "live") {
      video.play().catch(() => {});
    }
    // A busy browser can temporarily stop painting video frames while the
    // MediaStream track remains healthy. Never stop a live track for that;
    // doing so can make an integrated camera disappear until the driver resets.
    if (activeTrack?.readyState === "ended") scheduleCameraRecovery("ended");
  }, 1000);
}

async function startCamera(deviceId = null, options = {}) {
  const recoveryAttempt = Number(options.recoveryAttempt || 0);
  stopCamera({ keepRecoveryAttempt: recoveryAttempt > 0 });
  state.cameraRecoveryAttempts = recoveryAttempt;
  const startGeneration = state.cameraStartGeneration;
  if (!navigator.mediaDevices?.getUserMedia) {
    showMessage("Bu tarayıcı kamera kullanımını desteklemiyor. Chrome veya Edge ile tekrar deneyin.");
    return;
  }

  try {
    const preferredVideo = {
      // The analysis request is resized to at most 352 px, so opening the
      // physical camera at 720p only adds USB/driver load without model detail.
      width: { ideal: 640 },
      height: { ideal: 480 },
      frameRate: { ideal: 24, max: 30 },
      ...(deviceId
        ? { deviceId: { exact: deviceId } }
        : { facingMode: { ideal: "user" } }),
    };

    let openedStream;
    try {
      openedStream = await navigator.mediaDevices.getUserMedia({
        video: preferredVideo,
        audio: false,
      });
    } catch (preferredCameraError) {
      const canUseDefaultCamera = [
        "NotFoundError",
        "OverconstrainedError",
        "AbortError",
      ].includes(preferredCameraError.name);
      if (!canUseDefaultCamera) throw preferredCameraError;
      // Camera identifiers can change after a browser/driver restart. If the
      // remembered camera no longer exists, retry without the stale exact id.
      openedStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });
    }

    if (startGeneration !== state.cameraStartGeneration) {
      openedStream.getTracks().forEach((track) => track.stop());
      return;
    }
    state.cameraStream = openedStream;
    elements.cameraVideo.srcObject = openedStream;
    openedStream.getVideoTracks().forEach((track) => {
      try {
        if ("contentHint" in track) track.contentHint = "motion";
      } catch {
        // Some mobile browsers expose contentHint but reject assignments.
      }
    });
    await elements.cameraVideo.play();
    state.cameraPreferredDeviceId = openedStream.getVideoTracks()[0]?.getSettings()?.deviceId || deviceId;
    startCameraWatchdog(openedStream);
    elements.cameraVideo.hidden = false;
    elements.cameraEmpty.hidden = true;
    elements.captureButton.hidden = false;
    elements.liveAnalysisButton.hidden = false;
    elements.startCameraButton.textContent =
      uiTranslations[state.language].close_camera;
    await populateCameras();
    updateContextualOptions();
    showMessage("");
  } catch (error) {
    if (startGeneration !== state.cameraStartGeneration) return;
    stopCamera({
      preserveMessage: recoveryAttempt > 0,
      keepRecoveryAttempt: recoveryAttempt > 0,
    });
    let detectedCameraCount = null;
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      detectedCameraCount = devices.filter((device) => device.kind === "videoinput").length;
    } catch {
      // Device enumeration is only used to make the error more specific.
    }
    const messages = state.language === "en"
      ? {
        NotAllowedError: "Camera permission is blocked. Allow it from the camera icon in the address bar.",
        NotFoundError: detectedCameraCount > 0
          ? "The browser sees a camera but cannot open it. Check Windows camera access and close other camera apps."
          : "The browser cannot see a camera. Check Windows camera access and whether the camera is enabled.",
        NotReadableError: "Another app may be using the camera. Close other camera apps and try again.",
        OverconstrainedError: "The selected camera is unavailable. Choose another camera.",
        SecurityError: "The browser could not open the camera because of a security restriction.",
      }
      : {
        NotAllowedError: "Kamera izni engellendi. Adres çubuğundaki kamera simgesinden izni açın.",
        NotFoundError: detectedCameraCount > 0
          ? "Tarayıcı kamerayı görüyor ancak açamıyor. Windows kamera erişimini kontrol edin ve diğer kamera uygulamalarını kapatın."
          : "Tarayıcı kamerayı göremiyor. Windows kamera erişimini ve kameranın etkin olduğunu kontrol edin.",
        NotReadableError: "Kamera başka bir uygulama tarafından kullanılıyor olabilir. Diğer kamera uygulamalarını kapatın.",
        OverconstrainedError: "Seçilen kamera kullanılamıyor. Başka bir kamera seçin.",
        SecurityError: "Tarayıcı güvenlik nedeniyle kamerayı açamadı.",
      };
    const fallback = state.language === "en" ? "Unknown error" : "Bilinmeyen hata";
    const prefix = state.language === "en" ? "Camera could not open" : "Kamera açılamadı";
    const message = messages[error.name] || `${prefix}: ${error.message || fallback}`;
    if (recoveryAttempt > 0 && recoveryAttempt < 4) {
      const nextAttempt = recoveryAttempt + 1;
      const retryDelay = Math.min(4000, 500 * (2 ** (recoveryAttempt - 1)));
      const retryMessage = state.language === "en"
        ? `Camera disconnected. Reconnecting (${nextAttempt}/4)…`
        : `Kamera bağlantısı kesildi. Yeniden bağlanıyor (${nextAttempt}/4)…`;
      showMessage(retryMessage);
      setCameraPlaceholder(
        state.language === "en" ? "Reconnecting camera…" : "Kamera yeniden bağlanıyor…",
        retryMessage,
      );
      state.cameraRecoveryTimer = window.setTimeout(() => {
        state.cameraRecoveryTimer = null;
        startCamera(state.cameraPreferredDeviceId, {
          recoveryAttempt: nextAttempt,
          reason: "device-unavailable",
        });
      }, retryDelay);
    } else {
      showMessage(message);
      if (recoveryAttempt > 0) {
        setCameraPlaceholder(
          state.language === "en" ? "Camera could not reconnect" : "Kamera yeniden bağlanamadı",
          message,
        );
      }
    }
  }
}

function stopCamera(options = {}) {
  state.cameraStartGeneration += 1;
  stopLiveAnalysis();
  state.liveAbortController?.abort();
  state.liveAbortController = null;
  window.clearTimeout(state.liveLoopTimer);
  state.liveLoopTimer = null;
  state.liveInFlight = false;
  clearCameraWatchdog();
  window.clearTimeout(state.cameraRecoveryTimer);
  state.cameraRecoveryTimer = null;
  if (!options.keepRecoveryAttempt) state.cameraRecoveryAttempts = 0;
  elements.cameraCanvas.classList.remove("live-result-overlay");
  elements.cameraCanvas.classList.remove("transparent-detection-overlay");
  elements.cameraVideo.classList.remove("privacy-guard");
  elements.liveStatus.hidden = true;
  resetLiveQualityWarning();
  if (state.cameraStream) {
    state.cameraStream.getTracks().forEach((track) => track.stop());
    state.cameraStream = null;
  }
  elements.cameraVideo.srcObject = null;
  elements.cameraVideo.hidden = true;
  elements.cameraEmpty.hidden = false;
  elements.captureButton.hidden = true;
  elements.liveAnalysisButton.hidden = true;
  elements.cameraCanvas.hidden = true;
  if (!options.preserveMessage) resetCameraPlaceholder();
  elements.startCameraButton.textContent =
    uiTranslations[state.language].open_camera;
  updateContextualOptions();
}

async function populateCameras() {
  const devices = await navigator.mediaDevices.enumerateDevices();
  const cameras = devices.filter((device) => device.kind === "videoinput");
  const activeDeviceId = state.cameraStream
    ?.getVideoTracks()[0]
    ?.getSettings()
    ?.deviceId;
  elements.cameraSelect.innerHTML = "";
  cameras.forEach((camera, index) => {
    const option = document.createElement("option");
    option.value = camera.deviceId;
    option.textContent = friendlyCameraName(camera.label, index, cameras.length);
    option.selected = camera.deviceId === activeDeviceId;
    elements.cameraSelect.appendChild(option);
  });
  elements.cameraSelect.hidden = cameras.length < 2;
}

function friendlyCameraName(label, index, cameraCount) {
  const normalized = label.toLocaleLowerCase("tr-TR");
  if (/(back|rear|environment|arka)/.test(normalized)) {
    return state.language === "en" ? "Back camera" : "Arka kamera";
  }
  if (/(front|user|face|ön)/.test(normalized)) {
    return state.language === "en" ? "Front camera" : "Ön kamera";
  }
  if (cameraCount === 2) {
    return `${state.language === "en" ? "Camera" : "Kamera"} ${index + 1}`;
  }
  return label || `${state.language === "en" ? "Camera" : "Kamera"} ${index + 1}`;
}

function captureCameraFrame() {
  const video = elements.cameraVideo;
  if (!video.videoWidth) return;
  const canvas = elements.cameraCanvas;
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  canvas.toBlob((blob) => {
    if (!blob) return;
    setFile(new File([blob], "kamera-karesi.jpg", { type: "image/jpeg" }));
    selectSource("file");
  }, "image/jpeg", 0.94);
}

function imageEndpointForOperation() {
  const confidence = state.confidence[state.operation];
  if (state.operation === "privacy") {
    if (state.liveAnalysis) {
      const sessionId = encodeURIComponent(state.liveSessionId);
      return `/api/v1/privacy/live?mode=${state.mode}&confidence=${confidence}&session_id=${sessionId}&gesture_control=${state.gestureControl}`;
    }
    return `/api/v1/privacy/anonymize?mode=${state.mode}&confidence=${confidence}&fast=true`;
  }
  if (state.operation === "people_blur" || state.operation === "people_remove") {
    const mode = state.operation === "people_remove" ? "remove" : "blur";
    if (state.liveAnalysis) {
      const sessionId = encodeURIComponent(state.liveSessionId);
      return `/api/v1/people/live?mode=${mode}&confidence=${confidence}&session_id=${sessionId}`;
    }
    return `/api/v1/people/process?mode=${mode}&confidence=${confidence}&fast=true`;
  }
  if (state.operation === "forklift") {
    if (state.liveAnalysis) {
      const sessionId = encodeURIComponent(state.liveSessionId);
      return `/api/v1/forklift/detect?confidence=${confidence}&fast=true&session_id=${sessionId}`;
    }
    return `/api/v1/forklift/detect?confidence=${confidence}&fast=true`;
  }
  if (state.liveAnalysis) {
    const sessionId = encodeURIComponent(state.liveSessionId);
    return `/api/v1/pose/live?confidence=${confidence}&session_id=${sessionId}`;
  }
  return `/api/v1/pose/estimate?confidence=${confidence}&fast=true`;
}

function toggleLiveAnalysis() {
  if (state.liveAnalysis) {
    stopLiveAnalysis();
    return;
  }
  if (!state.cameraStream) {
    showMessage("Canlı analiz için önce kamerayı açın.");
    return;
  }
  state.liveAnalysis = true;
  state.liveGeneration += 1;
  state.liveSessionId = globalThis.crypto?.randomUUID?.()
    || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  state.liveFrames = 0;
  state.liveFps = 0;
  state.liveLatency = 0;
  state.liveDroppedFrames = 0;
  state.liveConsecutiveErrors = 0;
  state.liveAdaptiveWidth = state.liveMaxWidth;
  state.liveStableFrames = 0;
  state.liveInFlight = false;
  state.liveLastFrameAt = null;
  const cameraFrameRate = state.cameraStream
    .getVideoTracks()[0]
    ?.getSettings()
    ?.frameRate;
  state.liveExpectedFrameMs = 1000 / (cameraFrameRate || 30);
  state.liveAlerts = 0;
  state.liveStartedAt = Date.now();
  resetLiveQualityWarning();
  elements.liveAnalysisButton.classList.add("active");
  elements.liveAnalysisButton.textContent =
    uiTranslations[state.language].stop_live;
  elements.captureButton.hidden = true;
  elements.cameraCanvas.hidden = true;
  elements.cameraCanvas.classList.add("live-result-overlay");
  elements.cameraVideo.hidden = false;
  elements.cameraVideo.classList.toggle(
    "privacy-guard",
    state.operation === "privacy",
  );
  elements.liveStatus.hidden = false;
  elements.liveFrameCount.textContent = "Model hazırlanıyor";
  if (state.gestureControl) updateGestureStatus("waiting");
  showToast("Canlı analiz başladı", "Kamera kareleri seçili araçla analiz ediliyor.");
  scheduleLiveFrame(0, state.liveGeneration);
}

function stopLiveAnalysis() {
  if (!state.liveAnalysis) return;
  state.liveAnalysis = false;
  state.liveGeneration += 1;
  window.clearTimeout(state.liveLoopTimer);
  state.liveLoopTimer = null;
  state.liveAbortController?.abort();
  state.liveAbortController = null;
  state.liveInFlight = false;
  elements.liveAnalysisButton.classList.remove("active");
  elements.liveAnalysisButton.textContent =
    uiTranslations[state.language].start_live;
  elements.captureButton.hidden = !state.cameraStream;
  elements.cameraCanvas.hidden = true;
  elements.cameraCanvas.classList.remove("live-result-overlay");
  elements.cameraCanvas.classList.remove("transparent-detection-overlay");
  elements.cameraVideo.hidden = !state.cameraStream;
  elements.cameraVideo.classList.remove("privacy-guard");
  elements.liveStatus.hidden = true;
  resetLiveQualityWarning();
  if (state.gestureControl) updateGestureStatus("waiting");

  if (state.liveFrames > 0) {
    recordHistory({
      operation: state.operation,
      mediaType: "camera",
      durationMs: Date.now() - state.liveStartedAt,
      alerts: state.liveAlerts,
      detail: `${state.liveFrames} canlı kare · ${state.liveFps.toFixed(1)} FPS · ${Math.round(state.liveLatency)} ms`,
    });
  }
}

function scheduleLiveFrame(delayMs = 0, generation = state.liveGeneration) {
  window.clearTimeout(state.liveLoopTimer);
  if (!state.liveAnalysis || generation !== state.liveGeneration) return;
  state.liveLoopTimer = window.setTimeout(() => {
    state.liveLoopTimer = null;
    window.requestAnimationFrame(() => processLiveFrame(generation));
  }, Math.max(0, delayMs));
}

async function processLiveFrame(generation = state.liveGeneration) {
  if (
    !state.liveAnalysis
    || !state.cameraStream
    || state.liveInFlight
    || generation !== state.liveGeneration
  ) return;
  const cycleStartedAt = performance.now();
  const video = elements.cameraVideo;
  const displayCanvas = elements.cameraCanvas;
  const captureCanvas = state.liveCaptureCanvas;
  if (!video.videoWidth) {
    scheduleLiveFrame(100, generation);
    return;
  }

  if (document.hidden) {
    scheduleLiveFrame(300, generation);
    return;
  }

  state.liveInFlight = true;
  const maxWidth = state.liveAdaptiveWidth;
  const scale = Math.min(1, maxWidth / video.videoWidth);
  const frameWidth = Math.round(video.videoWidth * scale);
  const frameHeight = Math.round(video.videoHeight * scale);
  if (!state.liveCaptureContext || captureCanvas.width !== frameWidth || captureCanvas.height !== frameHeight) {
    captureCanvas.width = frameWidth;
    captureCanvas.height = frameHeight;
    state.liveCaptureContext = captureCanvas.getContext("2d", {
      alpha: false,
      desynchronized: true,
    });
  }
  if (!state.liveDisplayContext || displayCanvas.width !== frameWidth || displayCanvas.height !== frameHeight) {
    displayCanvas.width = frameWidth;
    displayCanvas.height = frameHeight;
    state.liveDisplayContext = displayCanvas.getContext("2d", {
      alpha: true,
      desynchronized: true,
    });
  }
  const captureContext = state.liveCaptureContext;
  const displayContext = state.liveDisplayContext;
  let blob;
  try {
    captureContext.drawImage(video, 0, 0, frameWidth, frameHeight);
    sampleLiveFrameQuality(captureContext, frameWidth, frameHeight);
    blob = await new Promise((resolve) => {
      captureCanvas.toBlob(resolve, "image/jpeg", state.liveJpegQuality);
    });
  } catch {
    state.liveInFlight = false;
    state.liveDroppedFrames += 1;
    scheduleLiveFrame(120, generation);
    return;
  }
  if (!blob || !state.liveAnalysis || generation !== state.liveGeneration) {
    state.liveInFlight = false;
    if (state.liveAnalysis && generation === state.liveGeneration) {
      scheduleLiveFrame(80, generation);
    }
    return;
  }

  const data = new FormData();
  data.append("file", new File([blob], "canli-kare.jpg", { type: "image/jpeg" }));
  const abortController = new AbortController();
  state.liveAbortController = abortController;
  let requestTimedOut = false;
  let retryDelay = 0;
  const requestTimeout = window.setTimeout(() => {
    requestTimedOut = true;
    abortController.abort();
  }, state.liveRequestTimeoutMs);
  try {
    const response = await fetch(imageEndpointForOperation(), {
      method: "POST",
      body: data,
      signal: abortController.signal,
    });
    if (response.status === 204 || response.headers.get("X-Frame-Dropped") === "true") {
      const droppedFrame = new Error("A newer camera frame is available.");
      droppedFrame.name = "FrameDropped";
      throw droppedFrame;
    }
    if (!response.ok) throw new Error(await apiError(response));
    if (!state.liveAnalysis || generation !== state.liveGeneration) return;

    if (state.operation === "privacy" && state.gestureControl) {
      const gestureAvailable = response.headers.get("X-Gesture-Control-Available") !== "false";
      if (!gestureAvailable) {
        state.gestureControl = false;
        elements.gestureControlToggle.checked = false;
        updateGestureStatus("unavailable");
        showMessage(uiTranslations[state.language].gesture_unavailable);
      } else {
        state.gesturePrivacyEnabled = response.headers.get("X-Privacy-Enabled") !== "false";
        updateGestureStatus(state.gesturePrivacyEnabled ? "enabled" : "disabled");
        const responseMode = response.headers.get("X-Privacy-Mode");
        if (responseMode && responseMode !== state.mode) selectMode(responseMode);
        const gesture = response.headers.get("X-Gesture");
        if (gesture && gesture !== "none") {
          const gestureLabels = {
            PINCH: state.gesturePrivacyEnabled ? "Blur açıldı" : "Blur kapatıldı",
            FIST: "Blur kapatıldı",
            BLUR: "Bulanıklaştırma seçildi",
            PIXEL: "Mozaik seçildi",
            COLOR: "Renk kalkanı seçildi",
          };
          showToast("El hareketi algılandı", gestureLabels[gesture] || gesture);
        }
      }
    }

    let detectionCount = null;
    if (state.operation === "forklift") {
      const result = await response.json();
      detectionCount = result.detections?.filter(
        (detection) => detection.class_name === "forklift",
      ).length ?? result.detection_count;
      if (!state.liveAnalysis || generation !== state.liveGeneration) return;
      displayContext.clearRect(0, 0, frameWidth, frameHeight);
      drawDetectionOverlay(displayContext, result, frameWidth);
      displayCanvas.classList.add("transparent-detection-overlay");
    } else {
      const countHeader = state.operation === "privacy"
        ? "X-Face-Count"
        : state.operation === "pose"
          ? "X-Pose-Count"
          : "X-Person-Count";
      const countValue = response.headers.get(countHeader);
      const parsedCount = countValue === null ? null : Number(countValue);
      if (Number.isFinite(parsedCount)) detectionCount = parsedCount;
      const transparentOverlay = response.headers.get("X-Live-Overlay") === "true";
      const resultBlob = await response.blob();
      const bitmap = await createImageBitmap(resultBlob);
      if (!state.liveAnalysis || generation !== state.liveGeneration) {
        bitmap.close();
        return;
      }
      displayContext.clearRect(0, 0, frameWidth, frameHeight);
      displayContext.drawImage(bitmap, 0, 0, frameWidth, frameHeight);
      bitmap.close();
      displayCanvas.classList.toggle("transparent-detection-overlay", transparentOverlay);
    }
    elements.cameraCanvas.hidden = false;
    elements.cameraVideo.classList.toggle(
      "privacy-guard",
      state.operation === "privacy",
    );
    state.liveFrames += 1;
    state.liveConsecutiveErrors = 0;
    const completedAt = performance.now();
    const currentLatency = completedAt - cycleStartedAt;
    state.liveLatency = state.liveLatency === 0
      ? currentLatency
      : state.liveLatency * 0.8 + currentLatency * 0.2;
    evaluateLiveQualityWarning(detectionCount, currentLatency);
    if (currentLatency > 700 && state.liveAdaptiveWidth > 256) {
      state.liveAdaptiveWidth = Math.max(256, state.liveAdaptiveWidth - 64);
      state.liveStableFrames = 0;
    } else if (currentLatency < 320) {
      state.liveStableFrames += 1;
      if (state.liveStableFrames >= 12 && state.liveAdaptiveWidth < state.liveMaxWidth) {
        state.liveAdaptiveWidth = Math.min(state.liveMaxWidth, state.liveAdaptiveWidth + 32);
        state.liveStableFrames = 0;
      }
    } else {
      state.liveStableFrames = 0;
    }
    if (state.liveLastFrameAt !== null) {
      const frameGap = completedAt - state.liveLastFrameAt;
      const instantFps = 1000 / Math.max(frameGap, 1);
      state.liveFps = state.liveFps === 0
        ? instantFps
        : state.liveFps * 0.9 + instantFps * 0.1;
      state.liveDroppedFrames += Math.max(
        0,
        Math.round(frameGap / state.liveExpectedFrameMs) - 1,
      );
    }
    state.liveLastFrameAt = completedAt;
    elements.liveFrameCount.textContent = state.liveFrames < 2
      ? "FPS ölçülüyor"
      : `${state.liveFps.toFixed(1)} FPS · ${Math.round(state.liveLatency)} ms`;
  } catch (error) {
    if (!state.liveAnalysis || generation !== state.liveGeneration) return;
    if (error.name === "FrameDropped") {
      state.liveDroppedFrames += 1;
      state.liveConsecutiveErrors = 0;
      retryDelay = 0;
    } else {
      state.liveDroppedFrames += 1;
      state.liveConsecutiveErrors += 1;
      state.liveAdaptiveWidth = Math.max(256, state.liveAdaptiveWidth - 64);
      retryDelay = requestTimedOut
        ? 800
        : Math.min(700, 120 * state.liveConsecutiveErrors);
      if (requestTimedOut) {
        elements.liveFrameCount.textContent = state.language === "en"
          ? "Optimizing the stream…"
          : "Akış optimize ediliyor…";
      } else if (error.name !== "AbortError") {
        elements.liveFrameCount.textContent = state.language === "en"
          ? "Reconnecting…"
          : "Yeniden bağlanıyor…";
      }
      if (state.liveConsecutiveErrors >= 6) {
        showMessage(
          state.language === "en"
            ? "Live analysis could not recover. The camera remains open; you can try again."
            : "Canlı analiz toparlanamadı. Kamera açık kaldı; tekrar deneyebilirsiniz.",
        );
        stopLiveAnalysis();
      }
    }
  } finally {
    window.clearTimeout(requestTimeout);
    if (state.liveAbortController === abortController) {
      state.liveAbortController = null;
    }
    state.liveInFlight = false;
  }
  if (state.liveAnalysis && generation === state.liveGeneration) {
    // Leave a short paint window between model calls. Back-to-back inference
    // can starve the camera element on CPU-only systems and look frozen.
    const nextFrameDelay = Math.max(retryDelay, state.liveDelay);
    scheduleLiveFrame(nextFrameDelay, generation);
  }
}

function endpointForCurrentSelection() {
  const video = state.mediaType === "video";
  const confidence = state.confidence[state.operation];
  let endpoint;
  if (state.operation === "privacy") {
    endpoint = `/api/v1/privacy/${video ? "anonymize-video" : "anonymize"}?mode=${state.mode}`;
  } else if (state.operation === "people_blur" || state.operation === "people_remove") {
    const mode = state.operation === "people_remove" ? "remove" : "blur";
    endpoint = `/api/v1/people/${video ? "process-video" : "process"}?mode=${mode}`;
  } else if (state.operation === "forklift") {
    endpoint = `/api/v1/forklift/${video ? "detect-video" : "detect"}`;
  } else {
    endpoint = `/api/v1/pose/${video ? "estimate-video" : "estimate"}`;
  }
  const separator = endpoint.includes("?") ? "&" : "?";
  const selection = state.operation === "people_remove"
    && state.removalTarget === "selected"
    && state.selectedPersonPoint
    ? `&selection_x=${state.selectedPersonPoint.x.toFixed(5)}&selection_y=${state.selectedPersonPoint.y.toFixed(5)}`
    : "";
  return `${endpoint}${separator}confidence=${confidence}${selection}`;
}

async function processSelection() {
  if (state.processing || state.batchActive) return false;
  if (state.files.length > 1) {
    await processBatch();
    return true;
  }
  return processMedia();
}

async function processMedia({ batchMode = false } = {}) {
  if (!state.file) return false;
  if (!batchMode) {
    state.processing = true;
    setInterfaceBusy(true);
  }
  const startedAt = Date.now();
  elements.processButton.disabled = true;
  elements.processButton.classList.add("is-loading");
  elements.processButton.setAttribute("aria-busy", "true");
  elements.buttonLabel.textContent = state.batchActive
    ? `${state.batchIndex + 1} / ${state.files.length} işleniyor`
    : state.mediaType === "video" ? "Video işleniyor…" : "Görüntü işleniyor…";
  showMessage(
    state.mediaType === "video"
      ? "Videonun her karesi işleniyor. Bu işlem birkaç dakika sürebilir."
      : "Görüntü analiz ediliyor. Lütfen bekleyin.",
    true,
  );
  clearResult();
  beginProgress();
  if (state.mediaType === "image") startSimulatedProgress();

  const data = new FormData();
  data.append("file", state.file);
  try {
    if (state.mediaType === "video") {
      const stats = await processVideoJob(data);
      storeResultDetails(Date.now() - startedAt, null, stats);
      recordHistory({
        operation: state.operation,
        mediaType: "video",
        durationMs: Date.now() - startedAt,
        alerts: 0,
        detail: `${stats.frame_count || 0} kare`,
      });
      completeProgress();
      showCompletedResult(!batchMode);
      if (!batchMode) {
        showToast("Video analizi tamamlandı", "İşlenmiş video görüntülenmeye ve indirilmeye hazır.");
      }
      return true;
    }

    const response = await fetch(endpointForCurrentSelection(), { method: "POST", body: data });
    if (!response.ok) throw new Error(await apiError(response));

    if (state.operation === "forklift" && state.mediaType === "image") {
      const result = await response.json();
      await drawDetections(result);
      elements.resultSummary.textContent = result.detection_count === 0
        ? "Depo nesnesi bulunamadı"
        : `${result.detection_count} nesne bulundu`;
      elements.downloadButton.href = elements.resultCanvas.toDataURL("image/jpeg", 0.92);
      elements.downloadButton.download = "depo-analizi.jpg";
      renderDetectionList(result.detections);
      recordHistory({
        operation: state.operation,
        mediaType: "image",
        durationMs: Date.now() - startedAt,
        alerts: 0,
        detail: `${result.detection_count} nesne`,
      });
    } else {
      await showBlobResult(response);
      recordHistory({
        operation: state.operation,
        mediaType: "image",
        durationMs: Date.now() - startedAt,
        alerts: 0,
        detail: "Görüntü analizi",
      });
    }

    storeResultDetails(
      Date.now() - startedAt,
      Number(response.headers.get("X-Processing-Time-Ms")) || null,
    );
    completeProgress();
    showCompletedResult(!batchMode);
    if (!batchMode) {
      showToast("Analiz tamamlandı", "Sonucunuz görüntülenmeye ve indirilmeye hazır.");
    }
    return true;
  } catch (error) {
    failProgress();
    showMessage(error.message || "İşlem sırasında bir sorun oluştu. Tekrar deneyin.");
    if (!batchMode) {
      showToast("İşlem tamamlanamadı", error.message || "Lütfen tekrar deneyin.", "error");
    }
    return false;
  } finally {
    stopSimulatedProgress();
    if (!state.batchActive) {
      state.processing = false;
      setInterfaceBusy(false);
      elements.processButton.disabled = false;
      elements.processButton.classList.remove("is-loading");
      elements.processButton.setAttribute("aria-busy", "false");
      updateActionLabel();
      updatePersonSelectionUi();
    }
  }
}

async function processBatch() {
  if (state.batchActive || state.files.length < 2) return;
  clearBatchResults();
  state.batchActive = true;
  state.processing = true;
  setInterfaceBusy(true);
  state.batchResults = [];
  state.batchStatuses = state.files.map(() => "queued");
  elements.batchResults.hidden = true;
  elements.processButton.disabled = true;
  elements.processButton.classList.add("is-loading");
  elements.processButton.setAttribute("aria-busy", "true");

  for (let index = 0; index < state.files.length; index += 1) {
    state.batchIndex = index;
    state.batchStatuses[index] = "active";
    renderUploadQueue();
    setFile(state.files[index], { preserveQueue: true });
    const success = await processMedia({ batchMode: true });
    if (success) {
      try {
        const result = await captureBatchResult(state.files[index]);
        state.batchResults.push(result);
        state.batchStatuses[index] = "done";
      } catch {
        state.batchStatuses[index] = "error";
      }
    } else {
      state.batchStatuses[index] = "error";
    }
    renderUploadQueue();
  }

  state.batchActive = false;
  state.processing = false;
  setInterfaceBusy(false);
  renderUploadQueue();
  elements.processButton.disabled = false;
  elements.processButton.classList.remove("is-loading");
  elements.processButton.setAttribute("aria-busy", "false");
  updateActionLabel();
  renderBatchResults();
  setProgress(100, `${state.batchResults.length} dosya tamamlandı`);
  elements.progressPanel.classList.add("complete");
  elements.progressIcon.textContent = "✓";
  elements.progressTitle.textContent = "Toplu analiz tamamlandı";
  elements.cancelJobButton.hidden = true;
  showMessage("");
  showToast(
    "Toplu analiz tamamlandı",
    `${state.batchResults.length} dosya indirilmeye hazır.`,
  );
}

async function captureBatchResult(file) {
  const response = await fetch(elements.downloadButton.href);
  const blob = await response.blob();
  return {
    sourceName: file.name,
    url: URL.createObjectURL(blob),
    filename: elements.downloadButton.download || `sonuc-${file.name}`,
    size: blob.size,
  };
}

function renderBatchResults() {
  elements.batchResults.hidden = state.batchResults.length === 0;
  elements.batchResultCount.textContent = `${state.batchResults.length} sonuç`;
  elements.batchResultList.innerHTML = state.batchResults.map((result) => `
    <article class="batch-result-item">
      <span aria-hidden="true">✓</span>
      <div>
        <strong>${escapeHtml(result.sourceName)}</strong>
        <small>${formatBytes(result.size)}</small>
      </div>
      <a href="${result.url}" download="${escapeHtml(result.filename)}">İndir</a>
    </article>
  `).join("");
  elements.resultSection.hidden = false;
}

function clearBatchResults() {
  state.batchResults.forEach((result) => URL.revokeObjectURL(result.url));
  state.batchResults = [];
  if (elements.batchResults) elements.batchResults.hidden = true;
  if (elements.batchResultList) elements.batchResultList.innerHTML = "";
}

function showCompletedResult(scrollToResult = true) {
  updateResultPresentation();
  updateSteps(3);
  elements.resultSection.hidden = false;
  if (scrollToResult) {
    elements.resultSection.scrollIntoView({
      behavior: prefersReducedMotion ? "auto" : "smooth",
      block: "center",
    });
  }
  showMessage("");
}

function updateResultPresentation() {
  updateResultTechnicalDetails();
  elements.resultOperation.textContent = operationLabel(state.operation);
  elements.resultMediaType.textContent = state.mediaType === "video" ? "Video" : "Fotoğraf";
  elements.resultMetric.textContent = elements.resultSummary.textContent || "Analiz tamamlandı";

  elements.resultPreviewImage.hidden = true;
  elements.resultPreviewVideo.hidden = true;
  if (state.mediaType === "video" && state.resultUrl) {
    elements.resultPreviewVideo.src = state.resultUrl;
    elements.resultPreviewVideo.hidden = false;
    return;
  }

  if (!elements.resultCanvas.hidden) {
    elements.resultPreviewImage.src = elements.resultCanvas.toDataURL("image/jpeg", 0.92);
    elements.resultPreviewImage.hidden = false;
    return;
  }

  if (state.resultUrl) {
    elements.resultPreviewImage.src = state.resultUrl;
    elements.resultPreviewImage.hidden = false;
  }
}

function storeResultDetails(durationMs, serverMs = null, stats = {}) {
  state.lastResultDetails = {
    durationMs: Math.max(0, Number(durationMs) || 0),
    serverMs: serverMs == null ? null : Math.max(0, Number(serverMs) || 0),
    stats: stats || {},
    confidence: state.confidence[state.operation],
    fileSize: state.file?.size || 0,
    operation: state.operation,
    mode: state.mode,
  };
}

function formatResultDuration(milliseconds) {
  if (milliseconds == null) return "—";
  if (milliseconds < 1000) return `${Math.round(milliseconds)} ms`;
  if (milliseconds < 60000) return `${(milliseconds / 1000).toFixed(1)} sn`;
  const minutes = Math.floor(milliseconds / 60000);
  const seconds = Math.round((milliseconds % 60000) / 1000);
  return `${minutes} dk ${seconds} sn`;
}

function resultModeLabel(details) {
  const isEnglish = state.language === "en";
  if (details.operation === "privacy") {
    const labels = isEnglish
      ? { soft_blur: "Natural blur", mosaic: "Mosaic", color_shield: "Color shield" }
      : { soft_blur: "Doğal bulanıklaştırma", mosaic: "Mozaik", color_shield: "Renk kalkanı" };
    return labels[details.mode] || details.mode;
  }
  const labels = isEnglish
    ? {
        people_blur: "Segmentation mask",
        people_remove: "Segmentation + inpainting",
        forklift: "YOLO + ByteTrack",
        pose: "17 keypoints + ByteTrack",
      }
    : {
        people_blur: "Segmentasyon maskesi",
        people_remove: "Segmentasyon + alan tamamlama",
        forklift: "YOLO + ByteTrack",
        pose: "17 eklem + ByteTrack",
      };
  return labels[details.operation] || "—";
}

function updateResultTechnicalDetails() {
  const details = state.lastResultDetails;
  const fields = [
    elements.resultDuration,
    elements.resultServerTime,
    elements.resultConfidence,
    elements.resultFileSize,
    elements.resultMode,
    elements.resultThroughput,
  ];
  if (!details) {
    fields.forEach((element) => { element.textContent = "—"; });
    return;
  }

  const frames = Number(details.stats.frame_count) || 0;
  const seconds = details.durationMs / 1000;
  const throughput = frames > 0 && seconds > 0
    ? `${(frames / seconds).toFixed(1)} ${state.language === "en" ? "frames/s" : "kare/sn"}`
    : details.serverMs != null
      ? `1 ${state.language === "en" ? "frame" : "kare"} / ${formatResultDuration(details.serverMs)}`
      : state.language === "en" ? "Single frame" : "Tek kare";

  elements.resultDuration.textContent = formatResultDuration(details.durationMs);
  elements.resultServerTime.textContent = details.serverMs == null
    ? (state.language === "en" ? "Included in total" : "Toplam süreye dahil")
    : formatResultDuration(details.serverMs);
  elements.resultConfidence.textContent = state.language === "en" ? "Automatic" : "Otomatik";
  elements.resultFileSize.textContent = formatBytes(details.fileSize);
  elements.resultMode.textContent = resultModeLabel(details);
  elements.resultThroughput.textContent = throughput;
}

async function processVideoJob(data) {
  updateJobProgress({ progress: 0, processed_frames: 0, total_frames: 0 });
  const mode = state.operation === "privacy" ? `&mode=${state.mode}` : "";
  const confidence = state.confidence[state.operation];
  const selection = state.operation === "people_remove"
    && state.removalTarget === "selected"
    && state.selectedPersonPoint
    ? `&selection_x=${state.selectedPersonPoint.x.toFixed(5)}&selection_y=${state.selectedPersonPoint.y.toFixed(5)}`
    : "";
  const response = await fetch(
    `/api/v1/jobs/video?operation=${state.operation}${mode}&confidence=${confidence}${selection}`,
    { method: "POST", body: data },
  );
  if (!response.ok) throw new Error(await apiError(response));

  const created = await response.json();
  state.currentJobId = created.id;

  while (state.currentJobId) {
    await delay(600);
    const statusResponse = await fetch(`/api/v1/jobs/${state.currentJobId}`);
    if (!statusResponse.ok) throw new Error(await apiError(statusResponse));
    const job = await statusResponse.json();
    updateJobProgress(job);

    if (job.status === "completed") {
      const resultResponse = await fetch(`/api/v1/jobs/${state.currentJobId}/result`);
      if (!resultResponse.ok) throw new Error(await apiError(resultResponse));
      await showVideoJobResult(resultResponse, job.stats);
      state.currentJobId = null;
      elements.cancelJobButton.hidden = true;
      elements.previewCancelJobButton.hidden = true;
      return job.stats;
    }
    if (job.status === "cancelled") {
      state.currentJobId = null;
      elements.cancelJobButton.hidden = true;
      elements.previewCancelJobButton.hidden = true;
      throw new Error("Video işlemi iptal edildi.");
    }
    if (job.status === "failed") {
      state.currentJobId = null;
      elements.cancelJobButton.hidden = true;
      elements.previewCancelJobButton.hidden = true;
      throw new Error(job.error || "Video işlenemedi.");
    }
  }
  throw new Error("Video işlemi iptal edildi.");
}

function updateJobProgress(job) {
  const progress = Math.max(0, Math.min(100, job.progress || 0));
  const detail = job.total_frames
    ? `${job.processed_frames} / ${job.total_frames} kare işlendi`
    : "Video hazırlanıyor…";
  setProgress(progress, detail);
}

function beginProgress() {
  stopSimulatedProgress();
  const showFloatingVideoProgress = state.mediaType === "video" && !state.batchActive;
  elements.progressPanel.hidden = showFloatingVideoProgress;
  elements.previewProgress.hidden = !showFloatingVideoProgress;
  elements.progressPanel.classList.remove("complete", "error");
  elements.progressPanel.classList.toggle("is-video-progress", showFloatingVideoProgress);
  elements.progressIcon.textContent = "↻";
  elements.progressTitle.textContent = state.batchActive
    ? `${state.batchIndex + 1}. dosya işleniyor`
    : state.mediaType === "video" ? "Video işleniyor" : "Görüntü işleniyor";
  elements.progressFile.textContent = state.file?.name || "Dosya hazırlanıyor";
  elements.cancelJobButton.hidden = state.mediaType !== "video";
  elements.previewCancelJobButton.hidden = !showFloatingVideoProgress;
  setProgress(0, state.mediaType === "video" ? "Video hazırlanıyor…" : "Model hazırlanıyor…");
}

function setProgress(itemProgress, detail) {
  const normalizedItem = Math.max(0, Math.min(100, Math.round(itemProgress)));
  const overall = state.batchActive
    ? Math.round(((state.batchIndex + normalizedItem / 100) / state.files.length) * 100)
    : normalizedItem;
  elements.progressValue.textContent = `${overall}%`;
  elements.progressBar.style.width = `${overall}%`;
  elements.progressTrack.setAttribute("aria-valuenow", String(overall));
  elements.progressDetail.textContent = detail;
  elements.previewProgressValue.textContent = `${overall}%`;
  elements.previewProgressBar.style.width = `${overall}%`;
  elements.previewProgressTrack.setAttribute("aria-valuenow", String(overall));
  elements.previewProgressDetail.textContent = detail;
}

function startSimulatedProgress() {
  let progress = 6;
  setProgress(progress, "Görüntü hazırlanıyor…");
  state.progressTimer = window.setInterval(() => {
    progress = Math.min(90, progress + Math.max(1, Math.round((92 - progress) * 0.12)));
    setProgress(progress, progress < 45 ? "Nesneler aranıyor…" : "Sonuç oluşturuluyor…");
  }, 240);
}

function stopSimulatedProgress() {
  if (state.progressTimer) {
    window.clearInterval(state.progressTimer);
    state.progressTimer = null;
  }
}

function completeProgress() {
  stopSimulatedProgress();
  setProgress(100, "İşlem tamamlandı");
  elements.progressPanel.classList.add("complete");
  elements.progressPanel.classList.remove("is-video-progress");
  elements.progressIcon.textContent = "✓";
  elements.cancelJobButton.hidden = true;
  elements.previewProgress.hidden = true;
  elements.previewCancelJobButton.hidden = true;
}

function failProgress() {
  stopSimulatedProgress();
  elements.progressPanel.hidden = false;
  elements.progressPanel.classList.add("error");
  elements.progressPanel.classList.remove("complete");
  elements.progressPanel.classList.remove("is-video-progress");
  elements.progressIcon.textContent = "!";
  elements.progressTitle.textContent = "İşlem tamamlanamadı";
  elements.progressDetail.textContent = "Dosyayı kontrol edip tekrar deneyin.";
  elements.cancelJobButton.hidden = true;
  elements.previewProgress.hidden = true;
  elements.previewCancelJobButton.hidden = true;
}

function resetProgress() {
  stopSimulatedProgress();
  elements.progressPanel.hidden = true;
  elements.progressPanel.classList.remove("complete", "error", "is-video-progress");
  elements.progressBar.style.width = "0%";
  elements.progressValue.textContent = "0%";
  elements.progressTrack.setAttribute("aria-valuenow", "0");
  elements.previewProgress.hidden = true;
  elements.previewProgressBar.style.width = "0%";
  elements.previewProgressValue.textContent = "0%";
  elements.previewProgressTrack.setAttribute("aria-valuenow", "0");
  elements.previewCancelJobButton.hidden = true;
}

async function cancelCurrentJob() {
  if (!state.currentJobId) return;
  elements.cancelJobButton.disabled = true;
  elements.previewCancelJobButton.disabled = true;
  try {
    elements.progressDetail.textContent = "İptal isteği gönderildi…";
    elements.previewProgressDetail.textContent = "İptal isteği gönderildi…";
    await fetch(`/api/v1/jobs/${state.currentJobId}`, { method: "DELETE" });
  } finally {
    elements.cancelJobButton.disabled = false;
    elements.previewCancelJobButton.disabled = false;
  }
}

async function showVideoJobResult(response, stats) {
  const blob = await response.blob();
  state.resultUrl = URL.createObjectURL(blob);
  elements.previewVideo.src = state.resultUrl;
  elements.previewVideo.hidden = false;
  elements.previewImage.hidden = true;
  elements.downloadButton.href = state.resultUrl;
  elements.downloadButton.download = `${operations[state.operation].result}.mp4`;
  renderVideoStats(stats);

  if (state.operation === "forklift") {
    elements.resultSummary.textContent = `${stats.forklift_count || 0} forklift tespiti`;
  } else if (state.operation === "privacy") {
    elements.resultSummary.textContent = `${stats.frame_count || 0} kare · ${stats.face_count || 0} yüz tespiti`;
  } else if (state.operation === "pose") {
    elements.resultSummary.textContent = `${stats.frame_count || 0} kare · ${stats.pose_count || 0} duruş tespiti`;
  } else {
    elements.resultSummary.textContent = `${stats.frame_count || 0} kare · ${stats.person_count || 0} kişi tespiti`;
  }
}

function renderVideoStats(stats) {
  const common = [
    [state.language === "en" ? "Processed frames" : "İşlenen kare", stats.frame_count || 0],
  ];
  const operationStats = {
    privacy: [
      [state.language === "en" ? "Face detections" : "Yüz tespiti", stats.face_count || 0],
      [state.language === "en" ? "Fail-safe frames" : "Fail-safe kare", stats.fail_safe_frame_count || 0],
    ],
    people_blur: [
      [state.language === "en" ? "Person detections" : "Kişi tespiti", stats.person_count || 0],
    ],
    people_remove: [
      [state.language === "en" ? "Removed detections" : "Kaldırılan kişi tespiti", stats.person_count || 0],
    ],
    pose: [
      [state.language === "en" ? "Pose detections" : "Duruş tespiti", stats.pose_count || 0],
    ],
    forklift: [
      ["Forklift", stats.forklift_count || 0],
      [state.language === "en" ? "People" : "İnsan", stats.person_count || 0],
      [state.language === "en" ? "Pallets" : "Palet", stats.pallet_count || 0],
    ],
  };
  const items = [...common, ...(operationStats[state.operation] || [])];
  elements.detectionList.innerHTML = items.map(([label, value]) => `
    <article class="detection-item">
      <strong>${escapeHtml(String(value))}</strong>
      <span>${escapeHtml(label)}</span>
    </article>
  `).join("");
  elements.detectionList.hidden = false;
}

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function showBlobResult(response) {
  const blob = await response.blob();
  state.resultUrl = URL.createObjectURL(blob);
  const isVideo = state.mediaType === "video";
  if (isVideo) {
    elements.previewVideo.src = state.resultUrl;
    elements.previewVideo.hidden = false;
    elements.previewImage.hidden = true;
  } else {
    elements.previewImage.src = state.resultUrl;
    elements.previewImage.hidden = false;
    elements.previewVideo.hidden = true;
  }

  const summaryHeaders = {
    privacy: ["X-Face-Count", "yüz işlendi"],
    people_blur: ["X-Person-Count", "kişi bulanıklaştırıldı"],
    people_remove: ["X-Person-Count", "kişi kaldırıldı"],
    pose: ["X-Pose-Count", "duruş bulundu"],
    forklift: ["X-Forklift-Count", "forklift tespiti"],
  };
  const [header, label] = summaryHeaders[state.operation];
  const count = response.headers.get(header) || "0";
  if (count === "0") {
    const emptyLabels = {
      privacy: response.headers.get("X-Fail-Safe-Applied") === "true"
        ? "Yüz bulunamadı · görüntünün tamamı korundu"
        : "Yüz bulunamadı",
      people_blur: "Bulanıklaştırılacak kişi bulunamadı",
      people_remove: "Kaldırılacak kişi bulunamadı",
      pose: "Analiz edilebilir vücut duruşu bulunamadı",
      forklift: "Forklift bulunamadı",
    };
    elements.resultSummary.textContent = emptyLabels[state.operation];
  } else {
    elements.resultSummary.textContent = `${count} ${label}`;
  }
  elements.downloadButton.href = state.resultUrl;
  elements.downloadButton.download = `${operations[state.operation].result}.${isVideo ? "mp4" : "jpg"}`;
}

async function drawDetections(result) {
  await elements.previewImage.decode();
  const canvas = elements.resultCanvas;
  canvas.width = result.image_width;
  canvas.height = result.image_height;
  const context = canvas.getContext("2d");
  context.drawImage(elements.previewImage, 0, 0, canvas.width, canvas.height);
  drawDetectionOverlay(context, result, canvas.width);
  elements.previewImage.hidden = true;
  canvas.hidden = false;
}

function drawDetectionOverlay(context, result, canvasWidth) {
  const colors = { forklift: "#238da0", person: "#2d8f68", pallet: "#985fce", pallet_truck: "#3f77c8" };
  const scale = Math.max(1, canvasWidth / 900);
  context.lineWidth = 2 * scale;
  context.font = `600 ${12 * scale}px sans-serif`;

  result.detections.forEach((detection) => {
    const { x1, y1, x2, y2 } = detection.box;
    const color = colors[detection.class_name] || "#238da0";
    const trackLabel = detection.track_id == null ? "" : ` #${detection.track_id}`;
    const label = `${friendlyName(detection.class_name)}${trackLabel} %${Math.round(detection.confidence * 100)}`;
    const labelWidth = context.measureText(label).width + 12 * scale;
    const labelHeight = 21 * scale;
    context.strokeStyle = color;
    context.strokeRect(x1, y1, x2 - x1, y2 - y1);
    context.fillStyle = color;
    context.fillRect(x1, Math.max(0, y1 - labelHeight), labelWidth, labelHeight);
    context.fillStyle = "#fff";
    context.fillText(label, x1 + 6 * scale, Math.max(15 * scale, y1 - 6 * scale));
  });
}

function renderDetectionList(detections) {
  const counts = detections.reduce((summary, item) => {
    summary[item.class_name] = (summary[item.class_name] || 0) + 1;
    return summary;
  }, {});
  elements.detectionList.innerHTML = "";
  Object.entries(counts).forEach(([name, count]) => {
    const item = document.createElement("div");
    item.className = "detection-item";
    item.innerHTML = `<strong>${friendlyName(name)}</strong><span>${count} adet bulundu</span>`;
    elements.detectionList.appendChild(item);
  });
  elements.detectionList.hidden = detections.length === 0;
}

function friendlyName(name) {
  return { forklift: "Forklift", person: "Kişi", pallet: "Palet", pallet_truck: "Palet taşıma aracı" }[name] || name;
}

const HISTORY_KEY = "vispection_analysis_history_v1";
let toastTimer = null;

function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function recordHistory(entry) {
  const history = loadHistory();
  history.unshift({
    id: crypto.randomUUID?.() || `${Date.now()}`,
    createdAt: new Date().toISOString(),
    operation: entry.operation,
    mediaType: entry.mediaType,
    durationMs: entry.durationMs || 0,
    alerts: entry.alerts || 0,
    detail: entry.detail || "",
  });
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 50)));
}

function renderDashboard() {
  const history = loadHistory();
  const today = new Date().toDateString();
  $("#stat-total").textContent = history.length;
  $("#stat-today").textContent = history.filter(
    (item) => new Date(item.createdAt).toDateString() === today,
  ).length;
  $("#stat-video").textContent = history.filter((item) => item.mediaType === "video").length;

  const counts = Object.fromEntries(Object.keys(operations).map((key) => [key, 0]));
  history.forEach((item) => {
    if (item.operation in counts) counts[item.operation] += 1;
  });
  const maximum = Math.max(1, ...Object.values(counts));
  elements.operationChart.innerHTML = Object.entries(counts).map(([key, count]) => `
    <div class="chart-row">
      <span>${escapeHtml(shortOperationName(key))}</span>
      <div class="chart-track"><span style="width:${count / maximum * 100}%"></span></div>
      <strong>${count}</strong>
    </div>
  `).join("");

  if (!history.length) {
    elements.historyList.innerHTML = '<p class="empty-history">Henüz tamamlanmış analiz bulunmuyor.</p>';
    return;
  }
  elements.historyList.innerHTML = history.slice(0, 8).map((item) => {
    const date = new Date(item.createdAt).toLocaleString("tr-TR", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
    const media = { image: "Fotoğraf", video: "Video", camera: "Canlı kamera" }[item.mediaType] || item.mediaType;
    return `
      <article class="history-item">
        <div>
          <strong>${escapeHtml(operations[item.operation]?.label || item.operation)}</strong>
          <span>${date} · ${media} · ${escapeHtml(item.detail || "")}</span>
        </div>
        ${item.alerts ? `<span class="history-alert">${item.alerts} uyarı</span>` : ""}
      </article>
    `;
  }).join("");
}

function shortOperationName(key) {
  return {
    privacy: "Yüz",
    people_blur: "Kişi bulanık.",
    people_remove: "Kişi kaldır.",
    forklift: "Depo",
    pose: "Duruş",
  }[key] || key;
}

function showToast(title, message, type = "success") {
  clearTimeout(toastTimer);
  elements.toast.classList.toggle("error", type === "error");
  elements.toast.classList.toggle("warning", type === "warning");
  elements.toastIcon.textContent = type === "error" || type === "warning" ? "!" : "✓";
  elements.toastTitle.textContent = title;
  elements.toastMessage.textContent = message;
  elements.toast.hidden = false;
  toastTimer = setTimeout(() => {
    elements.toast.hidden = true;
  }, 4800);
}

function openDialog(dialog) {
  if (!dialog.open) dialog.showModal();
}

function openInfoTopic(topic) {
  const content = infoTopics[state.language]?.[topic];
  if (!content) return;
  elements.infoDetailBadge.textContent = content.badge;
  elements.infoDetailTitle.textContent = content.title;
  elements.infoDetailDescription.textContent = content.description;
  elements.infoDetailList.innerHTML = content.points
    .map((point) => `<li>${escapeHtml(point)}</li>`)
    .join("");
  openDialog(elements.infoDetailDialog);
}

function initScrollReveals() {
  const targets = document.querySelectorAll(
    ".learn-section, .about-section, .faq-section, .trust-strip",
  );
  if (prefersReducedMotion || !("IntersectionObserver" in window)) {
    targets.forEach((target) => target.classList.add("is-visible"));
    return;
  }
  targets.forEach((target) => target.classList.add("reveal-on-scroll"));
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12 });
  targets.forEach((target) => observer.observe(target));
}

function applyTheme(theme, animate = false) {
  const root = document.documentElement;
  const commitTheme = () => {
    const dark = theme === "dark";
    const copy = uiTranslations[state.language] || uiTranslations.tr;
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    localStorage.setItem("vispection_theme", dark ? "dark" : "light");
    elements.themeIcon.textContent = dark ? "☀" : "◐";
    elements.themeLabel.textContent = dark ? copy.light_theme : copy.dark_theme;
    elements.themeButton.setAttribute(
      "aria-label",
      dark ? copy.light_theme : copy.dark_theme,
    );
  };

  if (!animate || prefersReducedMotion) {
    commitTheme();
    return;
  }

  root.classList.remove("theme-animating");
  void root.offsetWidth;
  root.classList.add("theme-animating");
  window.clearTimeout(themeAnimationTimer);
  themeAnimationTimer = window.setTimeout(() => {
    root.classList.remove("theme-animating");
  }, 1050);

  if (document.startViewTransition) {
    document.startViewTransition(commitTheme);
    return;
  }
  root.classList.add("theme-transitioning");
  commitTheme();
  window.clearTimeout(themeTransitionTimer);
  themeTransitionTimer = window.setTimeout(() => {
    root.classList.remove("theme-transitioning");
  }, 920);
}

function formatBytes(bytes) {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[character]);
}

async function apiError(response) {
  try {
    const body = await response.json();
    return body.detail || "İşlem tamamlanamadı.";
  } catch {
    return "Sunucuyla iletişim kurulamadı.";
  }
}

function refreshModelStatus() {
  const health = state.modelHealth;
  const copy = uiTranslations[state.language];
  elements.systemHealth.classList.toggle("ready", health.status === "ready");
  elements.systemHealth.classList.toggle("error", health.status === "error");
  elements.headerStatus.classList.toggle("ready", health.status === "ready");
  elements.headerStatus.classList.toggle("warming", !["ready", "error"].includes(health.status));
  elements.headerStatus.classList.toggle("error", health.status === "error");
  if (health.status === "ready") {
    elements.modelStatusTitle.textContent = copy.models_ready;
    elements.modelStatusDetail.textContent = copy.models_ready_detail;
    elements.headerStatusText.textContent = copy.system_ready;
  } else if (health.status === "error") {
    elements.modelStatusTitle.textContent = copy.models_error;
    elements.modelStatusDetail.textContent = copy.models_error_detail;
    elements.headerStatusText.textContent = copy.system_error;
  } else {
    elements.modelStatusTitle.textContent = copy.models_warming;
    elements.modelStatusDetail.textContent = copy.models_warming_detail;
    elements.headerStatusText.textContent = copy.system_warming;
  }
  elements.modelStatusCount.textContent = `${health.ready} / ${health.total}`;
}

async function pollModelStatus() {
  try {
    const response = await fetch("/health/models", { cache: "no-store" });
    if (!response.ok) throw new Error("health");
    state.modelHealth = await response.json();
    refreshModelStatus();
    if (state.modelHealth.status === "ready" && state.modelPollTimer) {
      window.clearInterval(state.modelPollTimer);
      state.modelPollTimer = null;
    }
  } catch {
    state.modelHealth = { status: "error", ready: 0, total: 4 };
    refreshModelStatus();
  }
}

elements.operationCards.forEach((card, index, cards) => {
  card.addEventListener("click", () => selectOperation(card.dataset.operation));
  card.addEventListener("keydown", (event) => {
    if (!["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(event.key)) {
      return;
    }
    event.preventDefault();
    const direction = ["ArrowDown", "ArrowRight"].includes(event.key) ? 1 : -1;
    const nextIndex = (index + direction + cards.length) % cards.length;
    cards[nextIndex].focus();
    selectOperation(cards[nextIndex].dataset.operation);
  });
});
elements.modeButtons.forEach((button) => button.addEventListener("click", () => selectMode(button.dataset.mode)));
elements.sourceButtons.forEach((button) => button.addEventListener("click", () => selectSource(button.dataset.source)));
elements.advancedToggle.addEventListener("click", toggleAdvancedSettings);
elements.confidenceRange.addEventListener("input", () => {
  const value = Number(elements.confidenceRange.value);
  state.confidence[state.operation] = value / 100;
  elements.confidenceValue.textContent = `${value}%`;
});
elements.profileButtons.forEach((button) => {
  button.addEventListener("click", () => selectLiveProfile(button.dataset.profile));
});
elements.removalTargetButtons.forEach((button) => {
  button.addEventListener("click", () => setRemovalTarget(button.dataset.removalTarget));
});
elements.personSelectionOverlay.addEventListener("click", selectPersonAt);
elements.sampleVideoButton.addEventListener("click", (event) => {
  event.preventDefault();
  event.stopPropagation();
  loadSampleVideo();
});
elements.sampleVideoButton.addEventListener("pointerenter", () => {
  if (!prefersReducedMotion) elements.sampleVideoPreview.play().catch(() => {});
});
elements.sampleVideoButton.addEventListener("pointerleave", () => elements.sampleVideoPreview.pause());
elements.sampleVideoButton.addEventListener("focus", () => {
  if (!prefersReducedMotion) elements.sampleVideoPreview.play().catch(() => {});
});
elements.sampleVideoButton.addEventListener("blur", () => elements.sampleVideoPreview.pause());
elements.chooseButton.addEventListener("click", (event) => { event.stopPropagation(); elements.fileInput.click(); });
elements.dropzone.addEventListener("click", (event) => {
  // The processed image/video is rendered inside the dropzone. Interacting
  // with that preview must not be interpreted as a request to replace it.
  if (!elements.previewWrap.hidden || event.target.closest("button, video, a, input, select, canvas")) {
    return;
  }
  elements.fileInput.click();
});
elements.dropzone.addEventListener("keydown", (event) => {
  if (event.key === "Enter" || event.key === " ") { event.preventDefault(); elements.fileInput.click(); }
});
elements.fileInput.addEventListener("change", () => setFiles(elements.fileInput.files));
elements.removeButton.addEventListener("click", (event) => { event.stopPropagation(); resetUpload(); });
elements.uploadQueue.addEventListener("click", (event) => {
  const removeButton = event.target.closest("[data-remove-index]");
  if (removeButton) removeQueuedFile(Number(removeButton.dataset.removeIndex));
});
["dragenter", "dragover"].forEach((name) => elements.dropzone.addEventListener(name, (event) => {
  event.preventDefault(); elements.dropzone.classList.add("dragging");
}));
["dragleave", "drop"].forEach((name) => elements.dropzone.addEventListener(name, (event) => {
  event.preventDefault(); elements.dropzone.classList.remove("dragging");
}));
elements.dropzone.addEventListener("drop", (event) => setFiles(event.dataTransfer.files));
elements.startCameraButton.addEventListener("click", () => state.cameraStream ? stopCamera() : startCamera());
elements.cameraSelect.addEventListener("change", () => startCamera(elements.cameraSelect.value));
elements.captureButton.addEventListener("click", captureCameraFrame);
elements.liveAnalysisButton.addEventListener("click", toggleLiveAnalysis);
elements.cameraVideo.addEventListener("stalled", () => {
  if (state.cameraStream) state.cameraStalledChecks = Math.max(1, state.cameraStalledChecks);
});
elements.cameraVideo.addEventListener("error", () => {
  if (!state.cameraStream) return;
  const track = state.cameraStream.getVideoTracks()[0];
  if (track?.readyState === "ended") {
    scheduleCameraRecovery("video-error");
  } else {
    elements.cameraVideo.play().catch(() => {});
  }
});
document.addEventListener("visibilitychange", () => {
  if (document.hidden || !state.cameraStream) return;
  const track = state.cameraStream.getVideoTracks()[0];
  if (track?.readyState === "ended") {
    scheduleCameraRecovery("ended");
    return;
  }
  state.cameraLastVideoTime = elements.cameraVideo.currentTime;
  elements.cameraVideo.play().catch(() => {
    showMessage(
      state.language === "en"
        ? "The camera is still open. Click the page once to resume the preview."
        : "Kamera açık kaldı. Görüntüyü sürdürmek için sayfaya bir kez tıklayın.",
    );
  });
});
navigator.mediaDevices?.addEventListener?.("devicechange", async () => {
  if (state.source !== "camera") return;
  try {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const cameras = devices.filter((device) => device.kind === "videoinput");
    const preferredStillExists = cameras.some(
      (camera) => camera.deviceId === state.cameraPreferredDeviceId,
    );
    if (!preferredStillExists) state.cameraPreferredDeviceId = null;
    if (state.cameraStream) {
      await populateCameras();
      const activeTrack = state.cameraStream.getVideoTracks()[0];
      if (!activeTrack || activeTrack.readyState === "ended") scheduleCameraRecovery("device-change");
    }
  } catch {
    // Some browsers restrict device enumeration until permission is granted.
  }
});
elements.gestureControlToggle.addEventListener("change", () => {
  state.gestureControl = elements.gestureControlToggle.checked;
  state.gesturePrivacyEnabled = true;
  updateGestureStatus(state.gestureControl ? "waiting" : "ready");
  if (state.liveAnalysis) {
    state.liveSessionId = globalThis.crypto?.randomUUID?.()
      || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }
});
elements.processButton.addEventListener("click", processSelection);
elements.cancelJobButton.addEventListener("click", cancelCurrentJob);
elements.previewCancelJobButton.addEventListener("click", cancelCurrentJob);
elements.newButton.addEventListener("click", () => {
  resetUpload();
  window.scrollTo({ top: 0, behavior: prefersReducedMotion ? "auto" : "smooth" });
});
elements.dashboardButton.addEventListener("click", () => {
  renderDashboard();
  openDialog(elements.dashboardDialog);
});
elements.themeButton.addEventListener("click", () => {
  applyTheme(
    document.documentElement.dataset.theme === "dark" ? "light" : "dark",
    true,
  );
});
elements.languageSelect.addEventListener("change", () => {
  applyLanguage(elements.languageSelect.value);
});
elements.helpButton.addEventListener("click", () => openDialog(elements.welcomeDialog));
elements.toolInfoButton.addEventListener("click", () => openDialog(elements.toolDialog));
document.querySelectorAll("[data-info-topic]").forEach((card) => {
  card.addEventListener("click", () => openInfoTopic(card.dataset.infoTopic));
});
elements.welcomeStartButton.addEventListener("click", () => {
  localStorage.setItem("vispection_welcome_seen", "true");
  elements.welcomeDialog.close();
});
elements.clearHistoryButton.addEventListener("click", () => {
  localStorage.removeItem(HISTORY_KEY);
  renderDashboard();
  showToast("Geçmiş temizlendi", "Yalnızca bu tarayıcıdaki analiz kayıtları silindi.");
});
document.querySelectorAll("[data-close-dialog]").forEach((button) => {
  button.addEventListener("click", () => button.closest("dialog").close());
});
document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
});
window.addEventListener("beforeunload", () => {
  stopCamera();
  clearBatchResults();
  if (state.modelPollTimer) window.clearInterval(state.modelPollTimer);
});

selectOperation("privacy");
selectSource("file");
selectLiveProfile("balanced");
applyTheme(document.documentElement.dataset.theme || "light");
applyLanguage(state.language);
pollModelStatus();
state.modelPollTimer = window.setInterval(pollModelStatus, 2500);
initScrollReveals();
if (!localStorage.getItem("vispection_welcome_seen")) {
  openDialog(elements.welcomeDialog);
}
