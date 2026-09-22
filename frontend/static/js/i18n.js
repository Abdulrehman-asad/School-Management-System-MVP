/**
 * Lightweight i18n engine for the public site.
 *
 * Every translatable element carries data-i18n="some.key" (for textContent).
 * The hero title, which mixes plain and emphasized text, uses
 * data-i18n-pre / data-i18n-em / data-i18n-post instead.
 *
 * setLanguage() walks the DOM once and swaps everything, then flips
 * <html dir/lang> and lets CSS ([dir="rtl"] rules in main.css) handle the
 * Urdu font and layout changes.
 *
 * Language choice is kept in memory only (no localStorage/sessionStorage),
 * so it resets to English on reload — intentional for this static demo page.
 */

const translations = {
  en: {
    "nav.about": "About",
    "nav.academics": "Academics",
    "nav.news": "News",
    "nav.gallery": "Gallery",
    "nav.teachers": "Teachers",
    "nav.faq": "FAQ",
    "nav.contact": "Contact",
    "nav.login": "Login",
    "nav.apply": "Apply Now",

    "hero.eyebrow": "Est. 1998 \u00b7 Lahore, Pakistan",
    "hero.title.pre": "Where every girl learns to ",
    "hero.title.em": "soar",
    "hero.title.post": ".",
    "hero.lead": "Shaheen Model Girls High School blends academic rigour with genuine care \u2014 helping students build the confidence, character, and curiosity to rise beyond what's expected of them.",
    "hero.cta.apply": "Apply for Admission",
    "hero.cta.tour": "Explore the Campus",

    "stats.students.num": "1,240+",
    "stats.students.label": "Students Enrolled",
    "stats.teachers.num": "68",
    "stats.teachers.label": "Qualified Faculty",
    "stats.passrate.num": "97%",
    "stats.passrate.label": "Matric Pass Rate",
    "stats.years.num": "27",
    "stats.years.label": "Years of Excellence",

    "about.eyebrow": "About Us",
    "about.title": "A school built on self-belief",
    "about.p1": "Founded in 1998, Shaheen Model Girls High School takes its name and spirit from the shaheen \u2014 the mountain falcon that Allama Iqbal made a symbol of ambition, independence, and flying higher than the flock. That idea still shapes how we teach.",
    "about.p2": "From Montessori through Matriculation, our teachers focus as much on character and confidence as they do on the syllabus \u2014 because an educated girl who believes in herself changes more than her own future.",
    "about.quote": "\u201cTeach her to fly, not just to follow.\u201d",

    "principal.eyebrow": "From the Principal's Desk",
    "principal.quote": "\u201cEvery girl who walks through our gates carries a quiet kind of courage. Our task is simply to give it room to grow \u2014 through rigorous academics, honest mentorship, and the belief that ambition is not immodest, it's necessary.\u201d",
    "principal.name": "Mrs. Sadia Farooq",
    "principal.role": "Principal, Shaheen Model Girls High School",

    "vm.vision.title": "Our Vision",
    "vm.vision.text": "To be a school where every student leaves not only prepared for examinations, but equipped to lead \u2014 in her home, her career, and her community.",
    "vm.mission.title": "Our Mission",
    "vm.mission.text": "To deliver a rigorous, values-based education that balances academic excellence with character, curiosity, and confidence \u2014 in an environment where every girl feels safe to be ambitious.",

    "why.eyebrow": "Why Choose Us",
    "why.title": "What sets Shaheen apart",
    "why.f1.title": "Qualified Faculty",
    "why.f1.text": "Every teacher is subject-qualified and trained in modern, student-centred pedagogy.",
    "why.f2.title": "Modern Science Labs",
    "why.f2.text": "Fully equipped physics, chemistry, biology, and computer labs from Middle School onward.",
    "why.f3.title": "Safe, Girls-Only Campus",
    "why.f3.text": "A secure, CCTV-monitored campus with dedicated transport and female staff throughout.",
    "why.f4.title": "Digital Learning (ERP)",
    "why.f4.text": "Parents and students track attendance, homework, and results through our school ERP.",
    "why.f5.title": "Co-Curricular Life",
    "why.f5.text": "Debate, robotics, art, and sport clubs that build confidence outside the classroom.",
    "why.f6.title": "Individual Attention",
    "why.f6.text": "Small section sizes so no student's questions \u2014 or ambitions \u2014 go unnoticed.",

    "academics.eyebrow": "Academic Programs",
    "academics.title": "A clear path, stage by stage",
    "academics.s1.stage": "Stage 01",
    "academics.s1.title": "Montessori & Prep",
    "academics.s1.text": "Play-based early learning building language, numeracy, and social confidence.",
    "academics.s2.stage": "Stage 02",
    "academics.s2.title": "Primary (I\u2013V)",
    "academics.s2.text": "A strong foundation in core subjects, English fluency, and independent study habits.",
    "academics.s3.stage": "Stage 03",
    "academics.s3.title": "Middle (VI\u2013VIII)",
    "academics.s3.text": "Science labs, computer studies, and Islamiat/Urdu alongside a widening curriculum.",
    "academics.s4.stage": "Stage 04",
    "academics.s4.title": "Matriculation (IX\u2013X)",
    "academics.s4.text": "Science, Arts, and Computer Science groups, preparing students for board examinations.",

    "news.eyebrow": "Latest News",
    "news.title": "What's happening on campus",
    "news.n1.date": "July 18, 2026",
    "news.n1.tag": "Results",
    "news.n1.title": "Matric Class of 2026 Achieves 97% Pass Rate",
    "news.n1.text": "Twelve students secured A+ grades across Science and Computer Science groups this year.",
    "news.n2.date": "July 02, 2026",
    "news.n2.tag": "Event",
    "news.n2.title": "Annual Science Exhibition Opens Registrations",
    "news.n2.text": "Students from Grades VI\u2013X are invited to submit projects for this year's exhibition.",
    "news.n3.date": "June 20, 2026",
    "news.n3.tag": "Admissions",
    "news.n3.title": "Admissions Open for Academic Year 2026\u201327",
    "news.n3.text": "Applications for Montessori through Grade IX are now open; seats are limited.",
    "news.readmore": "Read more",

    "gallery.eyebrow": "Gallery",
    "gallery.title": "Moments from campus life",
    "gallery.g1": "Annual Sports Day",
    "gallery.g2": "Science Exhibition",
    "gallery.g3": "Independence Day",
    "gallery.g4": "Annual Convocation",
    "gallery.g5": "Art & Craft Week",
    "gallery.g6": "Robotics Club",
    "gallery.modal.close": "Close",

    "teachers.eyebrow": "Our Faculty",
    "teachers.title": "Teachers who teach beyond the syllabus",
    "teachers.t1.name": "Ms. Ayesha Raza",
    "teachers.t1.subject": "Mathematics",
    "teachers.t1.bio": "M.Phil Mathematics \u00b7 14 years teaching Middle & Matric classes.",
    "teachers.t2.name": "Ms. Hina Malik",
    "teachers.t2.subject": "Biology",
    "teachers.t2.bio": "M.Sc Zoology \u00b7 Leads the Science Exhibition every year.",
    "teachers.t3.name": "Ms. Nimra Sheikh",
    "teachers.t3.subject": "English",
    "teachers.t3.bio": "M.A. English Literature \u00b7 Coaches the debate team.",
    "teachers.t4.name": "Ms. Farah Iqbal",
    "teachers.t4.subject": "Computer Science",
    "teachers.t4.bio": "B.S. Computer Science \u00b7 Runs the Robotics Club.",

    "testimonials.eyebrow": "Testimonials",
    "testimonials.title": "What families say",
    "testimonials.q1": "My daughter came in shy and left ready to argue her point in front of anyone. That's the Shaheen difference.",
    "testimonials.n1": "Ahmed Raza",
    "testimonials.r1": "Parent, Grade IX",
    "testimonials.q2": "The teachers actually know my name \u2014 and my weak subjects. That kind of attention is rare.",
    "testimonials.n2": "Zoya Tariq",
    "testimonials.r2": "Alumna, Class of 2024",
    "testimonials.q3": "The ERP portal means I never have to wonder about attendance or fee status. Everything is one login away.",
    "testimonials.n3": "Saima Khalid",
    "testimonials.r3": "Parent, Grade VI",

    "faq.eyebrow": "FAQ",
    "faq.title": "Common questions",
    "faq.q1": "How do I apply for admission?",
    "faq.a1": "Visit the Admissions Office with the student's birth certificate, previous school records (if any), and two passport photographs. Applications for 2026\u201327 are open now through August.",
    "faq.q2": "What is the fee structure?",
    "faq.a2": "Fees vary by grade level and are billed monthly. Contact the school office or log in to the parent portal for an exact breakdown for your daughter's class.",
    "faq.q3": "Is transport available?",
    "faq.a3": "Yes \u2014 school vans cover most areas of Lahore. Ask the office for the route nearest your home.",
    "faq.q4": "What is the school uniform?",
    "faq.a4": "Navy shalwar kameez with the school crest, white dupatta, and black shoes. Uniforms can be purchased through the school's approved tailor.",
    "faq.q5": "What are school timings?",
    "faq.a5": "Montessori: 8:00 AM \u2013 12:00 PM. Primary\u2013Matric: 7:45 AM \u2013 2:15 PM, Monday through Saturday (half-day Saturday).",
    "faq.q6": "How do I access the school ERP?",
    "faq.a6": "Parents and students receive login credentials at admission. Use the Login button above to sign in to your dashboard.",

    "contact.eyebrow": "Contact Us",
    "contact.title": "We'd love to hear from you",
    "contact.text": "Whether it's an admissions question or a chance to visit campus, our office is happy to help.",
    "contact.form.name": "Full Name",
    "contact.form.email": "Email Address",
    "contact.form.subject": "Subject",
    "contact.form.message": "Message",
    "contact.form.submit": "Send Message",
    "contact.address.label": "Address",
    "contact.address.text": "123 Iqbal Road, Gulberg III, Lahore, Punjab, Pakistan",
    "contact.phone.label": "Phone",
    "contact.email.label": "Email",
    "contact.hours.label": "Office Hours",
    "contact.hours.text": "Mon\u2013Sat, 8:00 AM \u2013 3:00 PM",
    "contact.toast": "Thank you! Your message has been sent \u2014 we'll respond within one business day.",

    "footer.about.title": "Shaheen Model Girls High School",
    "footer.about.text": "An institution devoted to raising confident, capable young women since 1998.",
    "footer.links.title": "Quick Links",
    "footer.programs.title": "Programs",
    "footer.contact.title": "Contact",
    "footer.rights": "\u00a9 2026 Shaheen Model Girls High School. All rights reserved.",
    "footer.credit": "Built with care, for every girl who dares to soar.",
  },

  ur: {
    "nav.about": "ہمارے بارے میں",
    "nav.academics": "تعلیمی نصاب",
    "nav.news": "خبریں",
    "nav.gallery": "تصاویر",
    "nav.teachers": "اساتذہ",
    "nav.faq": "عام سوالات",
    "nav.contact": "رابطہ کریں",
    "nav.login": "لاگ ان",
    "nav.apply": "ابھی داخلہ لیں",

    "hero.eyebrow": "قیام: 1998 - لاہور، پاکستان",
    "hero.title.pre": "جہاں ہر بیٹی اڑنا سیکھتی ہے",
    "hero.title.em": "بلندیوں کی طرف",
    "hero.title.post": "۔",
    "hero.lead": "شاہین ماڈل گرلز ہائی اسکول تعلیمی معیار کو حقیقی خیال رکھنے کے ساتھ جوڑتا ہے — طالبات میں اعتماد، کردار اور تجسس پیدا کرتے ہوئے، تاکہ وہ توقعات سے بڑھ کر آگے بڑھ سکیں۔",
    "hero.cta.apply": "داخلے کے لیے درخواست دیں",
    "hero.cta.tour": "کیمپس دیکھیں",

    "stats.students.num": "1,240+",
    "stats.students.label": "زیرِ تعلیم طالبات",
    "stats.teachers.num": "68",
    "stats.teachers.label": "اہل اساتذہ",
    "stats.passrate.num": "97%",
    "stats.passrate.label": "میٹرک کامیابی کی شرح",
    "stats.years.num": "27",
    "stats.years.label": "برسوں کی عمدگی",

    "about.eyebrow": "ہمارے بارے میں",
    "about.title": "خود اعتمادی پر قائم ایک ادارہ",
    "about.p1": "1998 میں قائم ہونے والا شاہین ماڈل گرلز ہائی اسکول اپنا نام اور روح شاہین سے لیتا ہے — وہ پہاڑی باز جسے علامہ اقبال نے عزم، خودمختاری اور جھنڈ سے بلند اڑان کی علامت بنایا۔ یہی سوچ آج بھی ہماری تدریس کی بنیاد ہے۔",
    "about.p2": "مونٹیسری سے لے کر میٹرک تک، ہمارے اساتذہ نصاب کے ساتھ ساتھ کردار اور اعتماد پر بھی اتنی ہی توجہ دیتے ہیں — کیونکہ خود پر بھروسہ رکھنے والی تعلیم یافتہ بیٹی صرف اپنا نہیں بلکہ اپنے پورے گھرانے کا مستقبل بدل دیتی ہے۔",
    "about.quote": "\u201cاسے اڑنا سکھائیں، صرف پیروی کرنا نہیں۔\u201d",

    "principal.eyebrow": "پرنسپل کے پیغام سے",
    "principal.quote": "\u201cہمارے دروازے سے گزرنے والی ہر بیٹی اپنے اندر ایک خاموش حوصلہ رکھتی ہے۔ ہمارا کام بس اتنا ہے کہ اسے بڑھنے کا موقع دیں — سخت تعلیمی محنت، مخلص رہنمائی، اور اس یقین کے ساتھ کہ عزم کوئی بے جا بات نہیں بلکہ ایک ضرورت ہے۔\u201d",
    "principal.name": "محترمہ ثنا ثاقب",
    "principal.role": "پرنسپل، شاہین ماڈل گرلز ہائی اسکول",

    "vm.vision.title": "ہمارا وژن",
    "vm.vision.text": "ایک ایسا اسکول جہاں ہر طالبہ صرف امتحانات کے لیے نہیں بلکہ رہنمائی کے لیے تیار ہو کر نکلے — اپنے گھر، اپنے کیریئر اور اپنے معاشرے میں۔",
    "vm.mission.title": "ہمارا مشن",
    "vm.mission.text": "ایک مضبوط، اقدار پر مبنی تعلیم فراہم کرنا جو تعلیمی معیار کو کردار، تجسس اور اعتماد کے ساتھ متوازن رکھے — ایسے ماحول میں جہاں ہر بیٹی بلند عزائم رکھنے میں محفوظ محسوس کرے۔",

    "why.eyebrow": "ہمیں کیوں منتخب کریں",
    "why.title": "شاہین کو خاص بنانے والی باتیں",
    "why.f1.title": "اہل اساتذہ",
    "why.f1.text": "ہر استاد اپنے مضمون میں تربیت یافتہ اور جدید، طالب علم مرکوز تدریسی طریقوں سے آگاہ ہے۔",
    "why.f2.title": "جدید سائنس لیبارٹریاں",
    "why.f2.text": "مڈل کلاس سے آگے کے لیے مکمل طور پر لیس فزکس، کیمسٹری، بیالوجی اور کمپیوٹر لیبز۔",
    "why.f3.title": "محفوظ، صرف بچیوں کا کیمپس",
    "why.f3.text": "سی سی ٹی وی نگرانی، مخصوص ٹرانسپورٹ اور خاتون عملہ کے ساتھ مکمل محفوظ کیمپس۔",
    "why.f4.title": "ڈیجیٹل تعلیم (ای آر پی)",
    "why.f4.text": "والدین اور طالبات اسکول کے نظام کے ذریعے حاضری، ہوم ورک اور نتائج دیکھ سکتے ہیں۔",
    "why.f5.title": "ہم نصابی سرگرمیاں",
    "why.f5.text": "مباحثہ، روبوٹکس، آرٹ اور کھیلوں کی سرگرمیاں جو کلاس روم سے باہر اعتماد پیدا کرتی ہیں۔",
    "why.f6.title": "انفرادی توجہ",
    "why.f6.text": "چھوٹے سیکشنز تاکہ کسی بھی طالبہ کا سوال یا عزم نظرانداز نہ ہو۔",

    "academics.eyebrow": "تعلیمی نصاب",
    "academics.title": "ہر مرحلے پر واضح راستہ",
    "academics.s1.stage": "مرحلہ 01",
    "academics.s1.title": "مونٹیسری اور پریپ",
    "academics.s1.text": "کھیل پر مبنی ابتدائی تعلیم جو زبان، حساب اور معاشرتی اعتماد پیدا کرتی ہے۔",
    "academics.s2.stage": "مرحلہ 02",
    "academics.s2.title": "پرائمری (اول تا پنجم)",
    "academics.s2.text": "بنیادی مضامین، انگریزی روانی اور خودمختار مطالعے کی عادت میں مضبوط بنیاد۔",
    "academics.s3.stage": "مرحلہ 03",
    "academics.s3.title": "مڈل (چھٹی تا آٹھویں)",
    "academics.s3.text": "سائنس لیبز، کمپیوٹر اسٹڈیز اور اسلامیات/اردو کے ساتھ وسیع تر نصاب۔",
    "academics.s4.stage": "مرحلہ 04",
    "academics.s4.title": "میٹرک (نویں و دسویں)",
    "academics.s4.text": "سائنس، آرٹس اور کمپیوٹر سائنس گروپس، بورڈ امتحانات کی مکمل تیاری۔",

    "news.eyebrow": "تازہ خبریں",
    "news.title": "کیمپس میں کیا ہو رہا ہے",
    "news.n1.date": "18 جولائی 2026",
    "news.n1.tag": "نتائج",
    "news.n1.title": "میٹرک 2026 نے 97% کامیابی کی شرح حاصل کی",
    "news.n1.text": "اس سال بارہ طالبات نے سائنس اور کمپیوٹر سائنس گروپس میں A+ گریڈ حاصل کیے۔",
    "news.n2.date": "02 جولائی 2026",
    "news.n2.tag": "تقریب",
    "news.n2.title": "سالانہ سائنس نمائش کے لیے رجسٹریشن کھل گئی",
    "news.n2.text": "چھٹی سے دسویں جماعت کی طالبات اس سال کی نمائش کے لیے پراجیکٹس جمع کروا سکتی ہیں۔",
    "news.n3.date": "20 جون 2026",
    "news.n3.tag": "داخلہ",
    "news.n3.title": "تعلیمی سال 2026-27 کے لیے داخلے کھل گئے",
    "news.n3.text": "مونٹیسری سے نویں جماعت تک داخلہ جاری ہے؛ نشستیں محدود ہیں۔",
    "news.readmore": "مزید پڑھیں",

    "gallery.eyebrow": "تصاویر",
    "gallery.title": "کیمپس کی یادگار جھلکیاں",
    "gallery.g1": "سالانہ اسپورٹس ڈے",
    "gallery.g2": "سائنس نمائش",
    "gallery.g3": "یومِ آزادی",
    "gallery.g4": "سالانہ تقریبِ جشن",
    "gallery.g5": "آرٹ اینڈ کرافٹ ہفتہ",
    "gallery.g6": "روبوٹکس کلب",
    "gallery.modal.close": "بند کریں",

    "teachers.eyebrow": "ہمارے اساتذہ",
    "teachers.title": "اساتذہ جو نصاب سے بڑھ کر سکھاتے ہیں",
    "teachers.t1.name": "محترمہ عائشہ رضا",
    "teachers.t1.subject": "ریاضی",
    "teachers.t1.bio": "ایم فل ریاضی - 14 سال کا تدریسی تجربہ۔",
    "teachers.t2.name": "محترمہ حنا ملک",
    "teachers.t2.subject": "حیاتیات",
    "teachers.t2.bio": "ایم ایس سی زوالوجی - ہر سال سائنس نمائش کی رہنمائی کرتی ہیں۔",
    "teachers.t3.name": "محترمہ نمرہ شیخ",
    "teachers.t3.subject": "انگریزی",
    "teachers.t3.bio": "ایم اے انگریزی ادب - مباحثہ ٹیم کی کوچ۔",
    "teachers.t4.name": "محترمہ فرح اقبال",
    "teachers.t4.subject": "کمپیوٹر سائنس",
    "teachers.t4.bio": "بی ایس کمپیوٹر سائنس - روبوٹکس کلب چلاتی ہیں۔",

    "testimonials.eyebrow": "تاثرات",
    "testimonials.title": "خاندانوں کی رائے",
    "testimonials.q1": "میری بیٹی شرمیلی تھی اور اب ہر کسی کے سامنے اپنی بات پیش کرتی ہے۔ یہی شاہین کا فرق ہے۔",
    "testimonials.n1": "احمد رضا",
    "testimonials.r1": "والد، جماعت نہم",
    "testimonials.q2": "اساتذہ واقعی میرا نام جانتے ہیں — اور میرے کمزور مضامین بھی۔ ایسی توجہ کم ہی ملتی ہے۔",
    "testimonials.n2": "زویا طارق",
    "testimonials.r2": "سابقہ طالبہ، بیچ 2024",
    "testimonials.q3": "ای آر پی پورٹل کی وجہ سے مجھے حاضری یا فیس کی صورتحال کے بارے میں فکر نہیں کرنی پڑتی۔ سب کچھ ایک لاگ ان کی دوری پر ہے۔",
    "testimonials.n3": "ثمیہ خالد",
    "testimonials.r3": "والدہ، جماعت ششم",

    "faq.eyebrow": "عام سوالات",
    "faq.title": "عام سوالات",
    "faq.q1": "داخلہ کیسے کروں؟",
    "faq.a1": "طالبہ کا پیدائشی سرٹیفکیٹ، سابقہ اسکول ریکارڈ (اگر ہو) اور دو پاسپورٹ تصاویر لے کر داخلہ دفتر تشریف لائیں۔ 2026-27 کے لیے داخلے اگست تک کھلے ہیں۔",
    "faq.q2": "فیس کا ڈھانچہ کیا ہے؟",
    "faq.a2": "فیس جماعت کے حساب سے مختلف ہوتی ہے اور ماہانہ وصول کی جاتی ہے۔ تفصیلات کے لیے اسکول دفتر سے رابطہ کریں یا پیرنٹ پورٹل میں لاگ ان کریں۔",
    "faq.q3": "کیا ٹرانسپورٹ دستیاب ہے؟",
    "faq.a3": "جی ہاں — اسکول وینز لاہور کے زیادہ تر علاقوں کا احاطہ کرتی ہیں۔ اپنے گھر کے قریب ترین روٹ کے لیے دفتر سے پوچھیں۔",
    "faq.q4": "اسکول یونیفارم کیا ہے؟",
    "faq.a4": "اسکول کرسٹ کے ساتھ نیوی شلوار قمیض، سفید دوپٹہ اور کالے جوتے۔ یونیفارم اسکول کے منظور شدہ درزی سے خریدا جا سکتا ہے۔",
    "faq.q5": "اسکول کا وقت کیا ہے؟",
    "faq.a5": "مونٹیسری: صبح 8 بجے تا دوپہر 12 بجے۔ پرائمری تا میٹرک: صبح 7:45 تا دوپہر 2:15، پیر تا ہفتہ (ہفتہ کو آدھا دن)۔",
    "faq.q6": "اسکول کے ای آر پی تک رسائی کیسے حاصل کروں؟",
    "faq.a6": "والدین اور طالبات کو داخلے کے وقت لاگ ان کی تفصیلات دی جاتی ہیں۔ اوپر لاگ ان بٹن سے اپنے ڈیش بورڈ میں داخل ہوں۔",

    "contact.eyebrow": "رابطہ کریں",
    "contact.title": "ہمیں آپ سے سن کر خوشی ہوگی",
    "contact.text": "داخلے کا سوال ہو یا کیمپس دیکھنے کی خواہش، ہمارا دفتر حاضر ہے۔",
    "contact.form.name": "پورا نام",
    "contact.form.email": "ای میل ایڈریس",
    "contact.form.subject": "موضوع",
    "contact.form.message": "پیغام",
    "contact.form.submit": "پیغام بھیجیں",
    "contact.address.label": "پتہ",
    "contact.address.text": "123 اقبال روڈ، گلبرگ III، لاہور، پنجاب، پاکستان",
    "contact.phone.label": "فون",
    "contact.email.label": "ای میل",
    "contact.hours.label": "اوقاتِ کار",
    "contact.hours.text": "پیر تا ہفتہ، صبح 8 بجے تا سہ پہر 3 بجے",
    "contact.toast": "شکریہ! آپ کا پیغام بھیج دیا گیا ہے — ہم ایک کاروباری دن کے اندر جواب دیں گے۔",

    "footer.about.title": "شاہین ماڈل گرلز ہائی اسکول",
    "footer.about.text": "1998 سے پراعتماد اور قابل بیٹیوں کی تربیت کے لیے وقف ادارہ۔",
    "footer.links.title": "فوری روابط",
    "footer.programs.title": "نصاب",
    "footer.contact.title": "رابطہ",
    "footer.rights": "© 2026 شاہین ماڈل گرلز ہائی اسکول۔ تمام حقوق محفوظ ہیں۔",
    "footer.credit": "ہر اس بیٹی کے لیے جو پرواز بھرنے کی جرات رکھتی ہے۔",
  },
};

let currentLang = "en";

function applyTranslations(lang) {
  const dict = translations[lang] || translations.en;

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key] !== undefined) el.textContent = dict[key];
  });

  document.querySelectorAll("[data-i18n-pre]").forEach((el) => {
    const preKey = el.getAttribute("data-i18n-pre");
    const emKey = el.getAttribute("data-i18n-em");
    const postKey = el.getAttribute("data-i18n-post");
    el.innerHTML =
      (dict[preKey] || "") +
      "<em>" + (dict[emKey] || "") + "</em>" +
      (dict[postKey] || "");
  });

  document.documentElement.lang = lang === "ur" ? "ur" : "en";
  document.documentElement.dir = lang === "ur" ? "rtl" : "ltr";

  document.querySelectorAll(".lang-switch button").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-lang") === lang);
  });

  currentLang = lang;
}

function setLanguage(lang) {
  if (lang !== "en" && lang !== "ur") return;
  applyTranslations(lang);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".lang-switch [data-lang]").forEach((btn) => {
    btn.addEventListener("click", () => setLanguage(btn.getAttribute("data-lang")));
  });
  applyTranslations(currentLang);
});
