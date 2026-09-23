function job(o) {
  return Object.assign({
    id: 1, title: 'Cím', featured: false, remote_work_possible: 0, is_junior: false,
    degree_level_name: 'nem szükséges végzettség', student_status_name: 'szükséges',
    work_hours: 25, salary: null, salary_formatted: null, salary_period_name: null,
    salary_type_name: null, location: 'Budapest, Magyarország',
    job_end_date_name: 'határozatlan', job_start_date_name: 'amint lehet',
    fields: [], languages: [], skills: [], publishes: [{ start_at: '2026-09-14 10:00:00' }],
    job_type: { name: 'Gyakornoki állás' }, company: { name: 'Cég' },
    avatar: { presets: { avatar: '/uploads/avatar/x.webp' } },
    url: 'https://zyntern.com/job/1-cim', description: '<div>Leírás</div>'
  }, o);
}

const data = [
  job({ id: 22049, title: 'ESG gyakornok', featured: true, salary: 2400, salary_formatted: '2 400 Ft',
    salary_period_name: ' / óra', salary_type_name: 'bruttó', location: 'Budapest, V. kerület, Magyarország',
    fields: [{ name: 'Környezet & energia' }], company: { name: 'OTP Bank' },
    languages: [{ name: 'Magyar', level_name: 'Anyanyelvi' }],
    publishes: [{ start_at: '2026-09-15 09:35:05' }] }),
  job({ id: 22060, title: 'Junior Auditor (budapesti lokáció)', is_junior: true, work_hours: 40,
    job_type: { name: 'Junior, 1-3 év tapasztalat' }, student_status_name: 'nem szükséges',
    fields: [{ name: 'Pénzügy & számvitel' }], company: { name: 'PwC Magyarország' },
    languages: [{ name: 'Magyar', level_name: 'Anyanyelvi' }, { name: 'Angol', level_name: 'Limitált tárgyalási szint' }],
    skills: [{ name: 'Elemzőkészség' }, { name: 'Számvitel' }, { name: 'Microsoft Excel' }],
    publishes: [{ start_at: '2026-09-08 17:56:38' }] }),
  job({ id: 22058, title: 'Finance gyakornok', salary: 2145, salary_formatted: '2 145 Ft',
    salary_period_name: ' / óra', salary_type_name: 'bruttó', work_hours: 20,
    location: 'Budapest, Váci út 96, 1133 Magyarország',
    fields: [{ name: 'Értékesítés & kereskedelem' }, { name: 'Pénzügy & számvitel' }, { name: 'Adminisztratív' }],
    company: { name: 'Mercedes-Benz Hungária Kft.' },
    languages: [{ name: 'Magyar', level_name: 'Anyanyelvi' }, { name: 'Angol', level_name: 'Felsőfokú tárgyalási szint' }],
    skills: [{ name: 'Pénzügyi elemzés' }, { name: 'Számvitel' }, { name: 'Adatelemzés' }],
    publishes: [{ start_at: '2026-09-07 15:54:56' }] }),
  job({ id: 22038, title: '2026 Kockázatkezelési gyakornoki program – Quantitative',
    remote_work_possible: 1, work_hours: 20, location: 'Budapest, Lechner Ödön fasor 8, 1095 Hungary',
    fields: [{ name: 'Pénzügy & számvitel' }, { name: 'Business & Data Analyst' }],
    company: { name: 'Morgan Stanley' },
    languages: [{ name: 'Angol', level_name: 'Limitált tárgyalási szint' }],
    publishes: [{ start_at: '2026-08-31 14:19:38' }] }),
  job({ id: 21873, title: 'Méréstechnológus gyakornok', salary: 2500, salary_formatted: '2 500 Ft',
    salary_period_name: ' / óra', salary_type_name: 'nettó', work_hours: 24,
    location: 'Sóskút, 2038 Magyarország', fields: [{ name: 'Gépészmérnök' }, { name: 'Mechatronikai mérnök' }],
    company: { name: 'TopiWork Iskolaszövetkezet' },
    languages: [{ name: 'Magyar', level_name: 'Anyanyelvi' }],
    publishes: [{ start_at: '2026-08-25 14:23:35' }] })
];


module.exports = data;
