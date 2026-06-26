
// mock-data.ts
// Données de test réalistes pour initialiser les composants Angular/React
// Basées sur le marché tech africain (Cameroun, Côte d'Ivoire, Sénégal

// ─────────────────────────────────────────────
//  Types
// ─────────────────────────────────────────────

export interface Company {
  companyName: string;
  companyDescription: string;
  companyLocation: string;
  companyWebsite: string;
  companyLogo: string;
}

export interface JobSearch {
  company: Company;
  jobTitle: string;
  jobDescription: string;
  jobLocation: string;
  jobType: 'CDI' | 'CDD' | 'STAGE' | 'FREELANCE' | '';
  status: 'open' | 'closed' | '';
  remote: boolean;
  experienceRequired: number;
  educationLevelRequired: string;
  skillsRequired: string[];
  salaryMin: number;
  salaryMax: number;
  deadline: Date;
  post_at: Date;
  created_at: Date;
}

// ─────────────────────────────────────────────
//  Entreprises fictives
// ─────────────────────────────────────────────

export const MOCK_COMPANIES: Company[] = [
  {
    companyName: 'TechAfrik Solutions',
    companyDescription:
      'Entreprise spécialisée dans le développement de solutions digitales pour les PME africaines. Nous accompagnons nos clients dans leur transformation numérique avec des outils adaptés au contexte local.',
    companyLocation: 'Yaoundé, Cameroun',
    companyWebsite: 'https://techafrik.cm',
    companyLogo: 'https://ui-avatars.com/api/?name=TechAfrik&background=4f46e5&color=fff&size=128',
  },
  {
    companyName: 'DigitalHub Dakar',
    companyDescription:
      'Hub technologique sénégalais dédié à l\'innovation. Nous développons des applications mobiles et web pour les secteurs de la finance, de la santé et de l\'agriculture.',
    companyLocation: 'Dakar, Sénégal',
    companyWebsite: 'https://digitalhub.sn',
    companyLogo: 'https://ui-avatars.com/api/?name=DigitalHub&background=0ea5e9&color=fff&size=128',
  },
  {
    companyName: 'InnovateCI',
    companyDescription:
      'Leader ivoirien du conseil en transformation digitale. Nos 120 collaborateurs accompagnent les grandes entreprises et institutions dans leurs projets SI.',
    companyLocation: 'Abidjan, Côte d\'Ivoire',
    companyWebsite: 'https://innovateci.com',
    companyLogo: 'https://ui-avatars.com/api/?name=InnovateCi&background=f59e0b&color=fff&size=128',
  },
  {
    companyName: 'Kali Tech',
    companyDescription:
      'Startup camerounaise spécialisée en cybersécurité et infrastructure cloud. Nous sécurisons les systèmes informatiques des banques et opérateurs télécoms.',
    companyLocation: 'Douala, Cameroun',
    companyWebsite: 'https://kalitech.cm',
    companyLogo: 'https://ui-avatars.com/api/?name=Kali+Tech&background=10b981&color=fff&size=128',
  },
];

// ─────────────────────────────────────────────
//  Offres d'emploi fictives
// ─────────────────────────────────────────────

export const MOCK_JOBS: JobSearch[] = [
  // ── 1. Développeur Full Stack ──────────────
  {
    company: MOCK_COMPANIES[0],
    jobTitle: 'Développeur Full Stack Django / Angular',
    jobDescription: `Nous recherchons un développeur Full Stack passionné pour rejoindre notre équipe produit.

**Missions :**
- Développer et maintenir les APIs REST avec Django REST Framework
- Intégrer les interfaces Angular avec les services backend
- Participer aux revues de code et aux réunions d'architecture
- Optimiser les performances des requêtes PostgreSQL

**Environnement technique :**
Django · DRF · Angular 17 · PostgreSQL · Redis · Docker · GitLab CI`,
    jobLocation: 'Yaoundé, Cameroun',
    jobType: 'CDI',
    status: 'open',
    remote: true,
    experienceRequired: 3,
    educationLevelRequired: 'bac+3',
    skillsRequired: ['Django', 'Angular', 'PostgreSQL', 'Docker', 'REST API'],
    salaryMin: 450000,
    salaryMax: 700000,
    deadline: new Date('2025-08-15'),
    post_at: new Date('2025-06-01'),
    created_at: new Date('2025-06-01'),
  },

  // ── 2. Data Scientist ──────────────────────
  {
    company: MOCK_COMPANIES[1],
    jobTitle: 'Data Scientist — Agriculture & FinTech',
    jobDescription: `Dans le cadre du développement de notre division Data, nous recrutons un Data Scientist expérimenté.

**Missions :**
- Construire des modèles prédictifs pour l'analyse de risque crédit
- Développer des pipelines de données avec Apache Airflow
- Produire des dashboards BI pour les équipes métiers
- Collaborer avec les équipes produit pour industrialiser les modèles

**Stack :** Python · Scikit-learn · TensorFlow · Airflow · BigQuery · Looker`,
    jobLocation: 'Dakar, Sénégal',
    jobType: 'CDI',
    status: 'open',
    remote: false,
    experienceRequired: 4,
    educationLevelRequired: 'bac+5',
    skillsRequired: ['Python', 'Machine Learning', 'SQL', 'TensorFlow', 'Airflow'],
    salaryMin: 600000,
    salaryMax: 900000,
    deadline: new Date('2025-07-30'),
    post_at: new Date('2025-05-20'),
    created_at: new Date('2025-05-20'),
  },

  // ── 3. Stage Développeur Mobile ───────────
  {
    company: MOCK_COMPANIES[2],
    jobTitle: 'Stage — Développeur Mobile Flutter (6 mois)',
    jobDescription: `Rejoins notre équipe mobile pour un stage de fin d'études enrichissant !

**Missions :**
- Développer de nouvelles fonctionnalités sur notre app Flutter (50 000 utilisateurs)
- Écrire des tests unitaires et d'intégration
- Participer aux sprints Agile (Scrum, 2 semaines)
- Rédiger la documentation technique

**Profil recherché :**
Étudiant en dernière année de licence ou master en informatique.
Connaissance de Flutter/Dart appréciée, motivation et curiosité requises.`,
    jobLocation: 'Abidjan, Côte d\'Ivoire',
    jobType: 'STAGE',
    status: 'open',
    remote: false,
    experienceRequired: 0,
    educationLevelRequired: 'bac+3',
    skillsRequired: ['Flutter', 'Dart', 'Firebase', 'Git'],
    salaryMin: 80000,
    salaryMax: 120000,
    deadline: new Date('2025-07-01'),
    post_at: new Date('2025-06-10'),
    created_at: new Date('2025-06-10'),
  },

  // ── 4. DevOps Engineer ────────────────────
  {
    company: MOCK_COMPANIES[3],
    jobTitle: 'Ingénieur DevOps / Cloud',
    jobDescription: `Kali Tech renforce son équipe infrastructure pour accompagner sa forte croissance.

**Missions :**
- Gérer et sécuriser l'infrastructure cloud (AWS / Azure)
- Mettre en place et maintenir les pipelines CI/CD
- Administrer les clusters Kubernetes en production
- Implémenter les politiques de sécurité (IAM, WAF, VPN)
- Assurer la supervision avec Prometheus / Grafana

**Certifications appréciées :** AWS Solutions Architect, CKA`,
    jobLocation: 'Douala, Cameroun',
    jobType: 'CDI',
    status: 'open',
    remote: true,
    experienceRequired: 5,
    educationLevelRequired: 'bac+5',
    skillsRequired: ['Kubernetes', 'Docker', 'AWS', 'Terraform', 'CI/CD', 'Linux'],
    salaryMin: 800000,
    salaryMax: 1200000,
    deadline: new Date('2025-09-01'),
    post_at: new Date('2025-06-05'),
    created_at: new Date('2025-06-05'),
  },

  // ── 5. Freelance UX Designer ──────────────
  {
    company: MOCK_COMPANIES[0],
    jobTitle: 'Designer UX/UI — Mission Freelance (3 mois)',
    jobDescription: `Nous cherchons un designer UX/UI freelance pour repenser l'expérience utilisateur de notre plateforme SaaS.

**Livrables attendus :**
- Audit UX de la plateforme existante
- Wireframes et prototypes interactifs sur Figma
- Design system complet (couleurs, typographie, composants)
- Accompagnement des développeurs lors de l'intégration

**Rythme :** 3 jours/semaine, full remote.`,
    jobLocation: 'Remote',
    jobType: 'FREELANCE',
    status: 'open',
    remote: true,
    experienceRequired: 3,
    educationLevelRequired: 'bac+3',
    skillsRequired: ['Figma', 'UX Research', 'Design System', 'Prototypage'],
    salaryMin: 300000,
    salaryMax: 500000,
    deadline: new Date('2025-07-15'),
    post_at: new Date('2025-06-12'),
    created_at: new Date('2025-06-12'),
  },
];

// ─────────────────────────────────────────────
//  Valeur vide (reset de formulaire)
// ─────────────────────────────────────────────

export const EMPTY_JOB_SEARCH: JobSearch = {
  company: {
    companyName: '',
    companyDescription: '',
    companyLocation: '',
    companyWebsite: '',
    companyLogo: '',
  },
  jobTitle: '',
  jobDescription: '',
  jobLocation: '',
  jobType: '',
  status: '',
  remote: false,
  experienceRequired: 0,
  educationLevelRequired: '',
  skillsRequired: [],
  salaryMin: 0,
  salaryMax: 0,
  deadline: new Date(),
  post_at: new Date(),
  created_at: new Date(),
};

// ─────────────────────────────────────────────
//  Constantes utiles pour les selects
// ─────────────────────────────────────────────

export const JOB_TYPES = [
  { value: 'CDI',       label: 'CDI — Contrat à durée indéterminée' },
  { value: 'CDD',       label: 'CDD — Contrat à durée déterminée' },
  { value: 'STAGE',     label: 'Stage' },
  { value: 'FREELANCE', label: 'Freelance / Mission' },
];

export const EDUCATION_LEVELS = [
  { value: 'bac',   label: 'Baccalauréat' },
  { value: 'bac+2', label: 'Bac+2 (BTS / DUT)' },
  { value: 'bac+3', label: 'Bac+3 (Licence)' },
  { value: 'bac+5', label: 'Bac+5 (Master / Ingénieur)' },
  { value: 'bac+8', label: 'Bac+8 (Doctorat)' },
  { value: 'other', label: 'Autre' },
];

export const POPULAR_SKILLS = [
  'Python', 'Django', 'JavaScript', 'TypeScript', 'Angular', 'React',
  'Flutter', 'Dart', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
  'Docker', 'Kubernetes', 'AWS', 'Azure', 'Linux', 'Git',
  'Machine Learning', 'TensorFlow', 'Figma', 'REST API', 'GraphQL',
];