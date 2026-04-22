// SLIS Teacher Portal — React App (Babel/JSX)
// All pages: Login, Dashboard, Students, Profile, Recommendations, Predict

const API = 'http://127.0.0.1:8000';

// ── Icons (inline SVG snippets) ──────────────────────────────────────────────
const Icon = ({ name, size = 16, color = 'currentColor' }) => {
  const paths = {
    dashboard:   <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></>,
    users:       <><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></>,
    brain:       <><path d="M9.5 2a2.5 2.5 0 0 1 5 0"/><path d="M14.5 2a2.5 2.5 0 0 1 0 5"/><path d="M9.5 2a2.5 2.5 0 0 0 0 5"/><ellipse cx="12" cy="12" rx="3" ry="5"/><path d="M5.5 7a2.5 2.5 0 0 0 0 5"/><path d="M18.5 7a2.5 2.5 0 0 1 0 5"/><path d="M5.5 12a2.5 2.5 0 0 0 0 5"/><path d="M18.5 12a2.5 2.5 0 0 1 0 5"/><path d="M9.5 22a2.5 2.5 0 0 0 5 0"/></>,
    lightbulb:   <><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></>,
    logout:      <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></>,
    search:      <><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></>,
    alert:       <><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></>,
    check:       <><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></>,
    arrowleft:   <><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></>,
    chevron:     <><polyline points="9 18 15 12 9 6"/></>,
    filter:      <><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></>,
    bar:         <><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></>,
    calendar:    <><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></>,
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{flexShrink:0}}>
      {paths[name] || null}
    </svg>
  );
};

// ── Mock Data ────────────────────────────────────────────────────────────────
const MOCK_STATS = {
  total_students: 500, high_risk_count: 87, avg_performance: 68.2, avg_attendance: 79.4,
  risk_distribution: { Low: 231, Medium: 182, High: 87 },
  subject_averages: { Mathematics: 61.4, Physics: 65.8, Chemistry: 67.2, 'Computer Science': 73.1, English: 70.5 },
  top_5_students: [
    {student_id:'STU0341',name:'Ananya Krishnan',avg_score:94.2,risk_level:'Low'},
    {student_id:'STU0088',name:'Rohan Iyer',avg_score:92.7,risk_level:'Low'},
    {student_id:'STU0204',name:'Priya Nair',avg_score:91.1,risk_level:'Low'},
    {student_id:'STU0017',name:'Kiran Das',avg_score:90.8,risk_level:'Low'},
    {student_id:'STU0156',name:'Meera Pillai',avg_score:89.3,risk_level:'Low'},
  ],
};
const MOCK_METRICS = {
  classifier: { model_name:'Random Forest', cv_f1_macro:0.962, test_accuracy:0.92 },
  regressor:  { model_name:'Ridge Regression', cv_rmse:5.02, test_rmse:4.68, test_r2:0.885 },
};
const MOCK_STUDENTS = Array.from({length:20}, (_,i) => ({
  student_id: `STU${String(i+1).padStart(4,'0')}`,
  name: ['Sneha Reddy','Arjun Mehta','Priya Sharma','Rahul Gupta','Anika Singh','Dev Patel','Kavya Rao','Nikhil Kumar','Sanya Joshi','Rohit Verma','Ananya Roy','Vijay Nair','Pooja Iyer','Karan Das','Lavanya Pillai','Aman Bose','Deepa Menon','Suresh Reddy','Tara Sharma','Ajay Kapoor'][i],
  major: ['Computer Science','Electronics','Mathematics','Physics','Chemistry'][i%5],
  avg_score: +(55+Math.sin(i)*25).toFixed(1),
  avg_attendance: +(60+Math.cos(i)*30).toFixed(1),
  gpa_start: +(2.5+Math.sin(i*0.7)*1.3).toFixed(2),
  risk_level: ['Low','Medium','High','Low','Medium'][i%5],
}));
const MOCK_PROFILE = {
  student_id:'STU0001', name:'Sneha Reddy', major:'Computer Science', age:20, gpa_start:3.42,
  avg_attendance:91.2, avg_score:78.4, engagement_score:8.7,
  risk_level:'Low', risk_probabilities:{Low:0.82,Medium:0.13,High:0.05},
  predicted_score:79.1,
  attendance_by_month:[{month:1,attendance_pct:88},{month:2,attendance_pct:94},{month:3,attendance_pct:91},{month:4,attendance_pct:92}],
  scores_by_subject:[
    {subject:'Machine Learning',it1_score:72,it2_score:78,final_score:81,weighted_score:78.5},
    {subject:'Deep Learning',it1_score:68,it2_score:74,final_score:79,weighted_score:75.5},
    {subject:'Python for AI',it1_score:76,it2_score:82,final_score:84,weighted_score:81.5},
    {subject:'Data Structures & Algorithms',it1_score:88,it2_score:91,final_score:93,weighted_score:91.3},
    {subject:'Statistics for AI',it1_score:71,it2_score:73,final_score:75,weighted_score:73.5},
  ],
  activity:{lms_logins_per_week:9.2,forum_posts:14,resources_accessed:42,avg_session_minutes:67},
};
const MOCK_RECS = {
  student_id:'STU0001', student_name:'Sneha Reddy',
  recommendations:[
    {title:'Strengthen Mathematics Foundation',description:'Focus 3 additional hours/week on Mathematics — your lowest subject at 78.5. Work through practice problems systematically before the final exam.',priority:'High'},
    {title:'Maintain LMS Engagement Momentum',description:'Your 9.2 logins/week is strong. Keep consistent daily login habits to maintain access to fresh materials and announcements.',priority:'Low'},
    {title:'Leverage Computer Science Strength',description:'Your 91.3 in Computer Science is excellent. Consider helping peers — teaching reinforces your own understanding significantly.',priority:'Medium'},
    {title:'Sustain Attendance Excellence',description:'91.2% attendance is commendable. Continue this discipline through the final exam period, especially in weaker subjects.',priority:'Low'},
  ],
};

// ── API helpers ──────────────────────────────────────────────────────────────
async function apiFetch(path, fallback) {
  try {
    const r = await fetch(API + path);
    if (!r.ok) throw new Error();
    return await r.json();
  } catch { return fallback; }
}

// ── Risk colour helper ───────────────────────────────────────────────────────
const riskColor = r => r === 'High' ? 'var(--risk-high)' : r === 'Medium' ? 'var(--risk-med)' : 'var(--risk-low)';
const RiskBadge = ({r}) => <span className={`badge badge-${r?.toLowerCase()}`}>{r}</span>;

// ── Sidebar ──────────────────────────────────────────────────────────────────
const NAVITEMS = [
  {id:'dashboard',    label:'Dashboard',       icon:'dashboard'},
  {id:'students',     label:'Students',        icon:'users'},
  {id:'predict',      label:'Custom Predict',  icon:'brain'},
  {id:'upload',       label:'Upload Scores',   icon:'calendar'},
];

function Sidebar({ page, setPage, onLogout }) {
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-brand">SLIS</div>
        <div className="sidebar-sub">Teacher Portal</div>
      </div>
      <div className="sidebar-section">Analytics</div>
      {NAVITEMS.map(n => (
        <div key={n.id} className={`nav-item ${page===n.id?'active':''}`} onClick={() => setPage(n.id)}>
          <Icon name={n.icon} size={15} color={page===n.id ? 'var(--accent)' : 'var(--fg-3)'} />
          {n.label}
        </div>
      ))}
      <div className="sidebar-footer">
        <div className="avatar">TR</div>
        <div>
          <div className="avatar-name">Teacher</div>
          <div className="avatar-role">Admin</div>
        </div>
        <button className="logout-btn" onClick={onLogout} title="Sign out"><Icon name="logout" size={14} /></button>
      </div>
    </div>
  );
}

// ── Login Page ───────────────────────────────────────────────────────────────
function LoginPage({ onLogin }) {
  const [role, setRole] = React.useState('teacher');
  const [user, setUser] = React.useState('');
  const [pass, setPass] = React.useState('');
  const [err, setErr] = React.useState('');

  const submit = e => {
    e.preventDefault();
    if (role === 'teacher' && user.trim().toLowerCase() === 'teacher' && pass === 'slis2024') { onLogin('teacher'); return; }
    if (role === 'student' && user.trim()) { onLogin('student', user.trim().toUpperCase()); return; }
    setErr(role === 'teacher' ? 'Invalid credentials. Try teacher / slis2024' : 'Enter a Student ID e.g. STU0001');
  };

  return (
    <div className="login-page">
      {/* Left panel */}
      <div className="login-left">
        <div className="login-shapes">
          <svg width="100%" height="100%" viewBox="0 0 600 800" fill="none" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
            <circle cx="480" cy="120" r="220" stroke="rgba(79,127,255,0.07)" strokeWidth="1"/>
            <circle cx="480" cy="120" r="160" stroke="rgba(79,127,255,0.05)" strokeWidth="1"/>
            <circle cx="480" cy="120" r="100" stroke="rgba(79,127,255,0.08)" strokeWidth="1"/>
            <circle cx="80"  cy="680" r="180" stroke="rgba(79,127,255,0.05)" strokeWidth="1"/>
            <circle cx="80"  cy="680" r="110" stroke="rgba(79,127,255,0.04)" strokeWidth="1"/>
            <line x1="0" y1="400" x2="600" y2="380" stroke="rgba(255,255,255,0.03)" strokeWidth="1"/>
            <line x1="0" y1="420" x2="600" y2="400" stroke="rgba(255,255,255,0.02)" strokeWidth="1"/>
            <rect x="300" y="300" width="60" height="60" rx="4" stroke="rgba(79,127,255,0.06)" strokeWidth="1" transform="rotate(20 330 330)"/>
            <rect x="150" y="200" width="30" height="30" rx="2" stroke="rgba(79,127,255,0.05)" strokeWidth="1" transform="rotate(-10 165 215)"/>
          </svg>
        </div>
        <div style={{position:'relative',zIndex:1}}>
          <div className="login-brand">SLIS</div>
          <div className="login-tagline">Student Learning Intelligence System — AI-powered academic analytics and risk prediction for modern educators.</div>
        </div>
        <div style={{position:'relative',zIndex:1}}>
          <div className="login-stats">
            <div><div className="login-stat-n">500</div><div className="login-stat-l">Students</div></div>
            <div><div className="login-stat-n">92%</div><div className="login-stat-l">Model Accuracy</div></div>
            <div><div className="login-stat-n">4</div><div className="login-stat-l">AI Recs / Student</div></div>
          </div>
          <div style={{marginTop:24,fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)'}}>Powered by Qwen3-32B · FastAPI · Random Forest</div>
        </div>
      </div>

      {/* Right panel — form */}
      <div className="login-right">
        <div className="login-form">
          <div className="login-heading">Sign in</div>
          <div className="login-sub">Select your role to continue</div>

          <div className="role-toggle">
            {['teacher','student'].map(r => (
              <button key={r} onClick={() => { setRole(r); setErr(''); }} className={`role-btn ${role===r?'active':'inactive'}`}>
                {r === 'teacher' ? 'Teacher' : 'Student'}
              </button>
            ))}
          </div>

          <form onSubmit={submit}>
            <div className="login-field">
              <label className="login-label">{role === 'teacher' ? 'Username' : 'Student ID'}</label>
              <input className="input" style={{width:'100%'}} value={user} onChange={e=>setUser(e.target.value)} placeholder={role==='teacher'?'teacher':'STU0001'} autoFocus />
            </div>
            {role === 'teacher' && (
              <div className="login-field">
                <label className="login-label">Password</label>
                <input className="input" style={{width:'100%'}} type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="••••••••" />
              </div>
            )}
            {err && <div className="login-error">{err}</div>}
            <button type="submit" className="btn btn-primary" style={{width:'100%',marginTop:20,justifyContent:'center',padding:'10px 16px'}}>
              Sign In →
            </button>
          </form>

          <div style={{marginTop:20,padding:'12px 14px',background:'var(--bg-elevated)',borderRadius:8,fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)',lineHeight:1.7}}>
            {role==='teacher' ? 'Demo: username teacher / password slis2024' : 'Demo: any ID like STU0001 through STU0500'}
          </div>

          <div style={{marginTop:16,fontSize:12,color:'var(--fg-3)',textAlign:'center'}}>
            <a href="../student/index.html" style={{color:'var(--accent)',textDecoration:'none'}}>Go to Student Portal →</a>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Dashboard Page ───────────────────────────────────────────────────────────
function DashboardPage({ setPage, setSelectedStudent }) {
  const [stats, setStats] = React.useState(null);
  const [metrics, setMetrics] = React.useState(null);
  React.useEffect(() => {
    apiFetch('/api/dashboard/stats', MOCK_STATS).then(setStats);
    apiFetch('/api/model-metrics', MOCK_METRICS).then(setMetrics);
  }, []);
  if (!stats || !metrics) return <div className="loading">Loading dashboard…</div>;
  const { total_students, high_risk_count, avg_performance, avg_attendance, risk_distribution, subject_averages, top_5_students } = stats;
  const subjectMax = Math.max(...Object.values(subject_averages));
  return (
    <div className="page-body">
      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-label">Total Students</div>
          <div className="stat-value">{total_students}</div>
          <div className="stat-sub">Active cohort</div>
        </div>
        <div className="stat-card" style={{borderColor:'var(--risk-high)'}}>
          <div className="stat-label">High Risk</div>
          <div className="stat-value" style={{color:'var(--risk-high)'}}>{high_risk_count}</div>
          <div className="stat-sub">{((high_risk_count/total_students)*100).toFixed(1)}% of cohort</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Score</div>
          <div className="stat-value">{avg_performance}</div>
          <div className="stat-sub">Predicted weighted</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Attendance</div>
          <div className="stat-value">{avg_attendance}%</div>
          <div className="stat-sub">Across all students</div>
        </div>
      </div>

      <div className="two-col" style={{marginBottom:16}}>
        <div>
          <div className="section-header"><span className="section-title">Risk Distribution</span></div>
          <div style={{background:'var(--bg-surface)',border:'1px solid var(--border)',padding:'16px'}}>
            {Object.entries(risk_distribution).map(([level, count]) => (
              <div key={level} style={{marginBottom:12}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:4}}>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:12,color:'var(--fg-2)'}}>{level} Risk</span>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:12,color:riskColor(level)}}>{count}</span>
                </div>
                <div className="risk-bar-track">
                  <div className="risk-bar-fill" style={{width:`${(count/total_students)*100}%`,background:riskColor(level)}}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div>
          <div className="section-header"><span className="section-title">Model Performance</span></div>
          <div style={{background:'var(--bg-surface)',border:'1px solid var(--border)',padding:'16px'}}>
            <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:10}}>Risk Classifier — {metrics.classifier.model_name}</div>
            <div className="metric-grid" style={{marginBottom:14}}>
              <div className="metric-card"><div className="metric-key">CV F1 Macro</div><div className="metric-val">{(metrics.classifier.cv_f1_macro*100).toFixed(1)}%</div></div>
              <div className="metric-card"><div className="metric-key">Test Accuracy</div><div className="metric-val">{(metrics.classifier.test_accuracy*100).toFixed(0)}%</div></div>
            </div>
            <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:10}}>Performance Predictor — {metrics.regressor.model_name}</div>
            <div className="metric-grid">
              <div className="metric-card"><div className="metric-key">Test RMSE</div><div className="metric-val">{metrics.regressor.test_rmse}</div></div>
              <div className="metric-card"><div className="metric-key">R²</div><div className="metric-val">{metrics.regressor.test_r2}</div></div>
            </div>
          </div>
        </div>
      </div>

      <div className="two-col">
        <div>
          <div className="section-header"><span className="section-title">Subject Averages</span></div>
          <div style={{background:'var(--bg-surface)',border:'1px solid var(--border)',padding:'16px'}}>
            <div className="bar-chart">
              {Object.entries(subject_averages).map(([subj, avg]) => (
                <div key={subj} className="bar-row">
                  <div className="bar-label">{subj.replace('Computer Science','CS')}</div>
                  <div className="bar-track"><div className="bar-fill" style={{width:`${(avg/subjectMax)*100}%`}}></div></div>
                  <div className="bar-val">{avg}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div>
          <div className="section-header"><span className="section-title">Top Performers</span></div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Name</th><th>Score</th><th>Risk</th></tr></thead>
              <tbody>
                {top_5_students.map(s => (
                  <tr key={s.student_id} onClick={() => { setSelectedStudent(s.student_id); setPage('profile'); }}>
                    <td>{s.name}</td>
                    <td><span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.avg_score}</span></td>
                    <td><RiskBadge r={s.risk_level}/></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Students Page ────────────────────────────────────────────────────────────
function StudentsPage({ setPage, setSelectedStudent }) {
  const [students, setStudents] = React.useState([]);
  const [search, setSearch] = React.useState('');
  const [riskFilter, setRiskFilter] = React.useState('');
  const [page, setPageNum] = React.useState(1);
  const [total, setTotal] = React.useState(0);
  const limit = 15;

  React.useEffect(() => {
    const params = new URLSearchParams({ page, limit, ...(riskFilter&&{risk_filter:riskFilter}), ...(search&&{search}) });
    apiFetch(`/api/students?${params}`, { students: MOCK_STUDENTS.filter(s => (!riskFilter||s.risk_level===riskFilter)&&(!search||s.name.toLowerCase().includes(search.toLowerCase())||s.student_id.toLowerCase().includes(search.toLowerCase()))).slice((page-1)*limit,page*limit), total: MOCK_STUDENTS.length })
      .then(d => { setStudents(d.students); setTotal(d.total); });
  }, [search, riskFilter, page]);

  return (
    <div className="page-body">
      <div className="search-row">
        <div style={{position:'relative',flex:1,maxWidth:320}}>
          <svg style={{position:'absolute',left:10,top:'50%',transform:'translateY(-50%)',pointerEvents:'none'}} width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--fg-3)" strokeWidth="1.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          <input className="input" style={{paddingLeft:30}} placeholder="Search by name or ID…" value={search} onChange={e=>{setSearch(e.target.value);setPageNum(1);}} />
        </div>
        <select className="input" style={{width:160}} value={riskFilter} onChange={e=>{setRiskFilter(e.target.value);setPageNum(1);}}>
          <option value="">All Risk Levels</option>
          <option value="High">High Risk</option>
          <option value="Medium">Medium Risk</option>
          <option value="Low">Low Risk</option>
        </select>
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Student ID</th><th>Name</th><th>Major</th><th>Avg Score</th><th>Attendance</th><th>GPA</th><th>Risk</th></tr></thead>
          <tbody>
            {students.map(s => (
              <tr key={s.student_id} onClick={() => { setSelectedStudent(s.student_id); setPage('profile'); }}>
                <td className="id-cell">{s.student_id}</td>
                <td>{s.name}</td>
                <td style={{color:'var(--fg-2)',fontSize:12}}>{s.major}</td>
                <td><span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.avg_score}</span></td>
                <td><span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.avg_attendance}%</span></td>
                <td><span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.gpa_start}</span></td>
                <td><RiskBadge r={s.risk_level}/></td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="pagination">
          <button className="btn btn-secondary btn-sm" onClick={()=>setPageNum(p=>Math.max(1,p-1))} disabled={page===1}>← Prev</button>
          <span>Page {page} of {Math.ceil(total/limit) || 1}</span>
          <button className="btn btn-secondary btn-sm" onClick={()=>setPageNum(p=>p+1)} disabled={page*limit>=total}>Next →</button>
          <span style={{marginLeft:'auto'}}>{total} students</span>
        </div>
      </div>
    </div>
  );
}

// ── Profile Page ─────────────────────────────────────────────────────────────
function ProfilePage({ studentId, setPage, setSelectedStudent }) {
  const [profile, setProfile] = React.useState(null);
  const [recs, setRecs] = React.useState(null);
  const [showRecs, setShowRecs] = React.useState(false);
  const [editSubject, setEditSubject] = React.useState(null);
  const [editVals, setEditVals] = React.useState({});
  const [saving, setSaving] = React.useState(false);
  const [saveMsg, setSaveMsg] = React.useState('');

  React.useEffect(() => {
    apiFetch(`/api/students/${studentId}`, MOCK_PROFILE).then(setProfile);
  }, [studentId]);

  const loadRecs = () => {
    setShowRecs(true);
    if (!recs) apiFetch(`/api/recommendations/${studentId}`, MOCK_RECS).then(setRecs);
  };

  const startEdit = s => {
    setEditSubject(s.subject);
    setEditVals({ it1_score: s.it1_score, it2_score: s.it2_score, final_score: s.final_score });
  };

  const saveEdit = async subject => {
    setSaving(true); setSaveMsg('');
    const params = new URLSearchParams(editVals);
    try {
      const r = await fetch(`${API}/api/students/${studentId}/scores/${encodeURIComponent(subject)}?${params}`, { method:'PUT' });
      const data = await r.json();
      if (r.ok) {
        setSaveMsg('✓ Saved');
        setProfile(p => ({
          ...p,
          scores_by_subject: p.scores_by_subject.map(s =>
            s.subject === subject ? { ...s, ...editVals, weighted_score: data.weighted_score } : s
          ),
        }));
        setEditSubject(null);
      } else { setSaveMsg('Error: ' + (data.detail || 'save failed')); }
    } catch { setSaveMsg('Network error'); }
    setSaving(false);
    setTimeout(() => setSaveMsg(''), 3000);
  };

  if (!profile) return <div className="loading">Loading profile…</div>;

  const { name, student_id, major, age, gpa_start, avg_attendance, avg_score, predicted_score, risk_level, risk_probabilities, scores_by_subject, activity } = profile;

  return (
    <div className="page-body">
      <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:20}}>
        <button className="btn btn-secondary btn-sm" onClick={() => setPage('students')}><Icon name="arrowleft" size={13}/> Students</button>
        <span style={{fontFamily:'var(--font-mono)',fontSize:12,color:'var(--fg-3)'}}>{student_id}</span>
        <RiskBadge r={risk_level}/>
      </div>

      <div className="profile-grid">
        <div style={{display:'flex',flexDirection:'column',gap:12}}>
          <div className="profile-card">
            <div className="profile-name">{name}</div>
            <div className="profile-id">{student_id} · {major} · Age {age}</div>
            <div className="divider"></div>
            <div className="profile-row"><span className="profile-key">GPA (Start)</span><span className="profile-val">{gpa_start}</span></div>
            <div className="profile-row"><span className="profile-key">Avg Score</span><span className="profile-val">{avg_score}</span></div>
            <div className="profile-row"><span className="profile-key">Predicted Score</span><span className="profile-val" style={{color:'var(--accent-text)'}}>{predicted_score}</span></div>
            <div className="profile-row"><span className="profile-key">Attendance</span><span className="profile-val">{avg_attendance}%</span></div>
          </div>
          <div className="profile-card">
            <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:10}}>Risk Confidence</div>
            {Object.entries(risk_probabilities).map(([level, prob]) => (
              <div key={level} style={{marginBottom:8}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:3}}>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-2)'}}>{level}</span>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:11,color:riskColor(level)}}>{(prob*100).toFixed(0)}%</span>
                </div>
                <div className="risk-bar-track"><div className="risk-bar-fill" style={{width:`${prob*100}%`,background:riskColor(level)}}></div></div>
              </div>
            ))}
          </div>
          <div className="profile-card">
            <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:10}}>LMS Activity</div>
            {Object.entries(activity||{}).filter(([k])=>k!=='student_id').map(([k,v]) => (
              <div className="profile-row" key={k}><span className="profile-key">{k.replace(/_/g,' ')}</span><span className="profile-val">{typeof v==='number'?+v.toFixed(1):v}</span></div>
            ))}
          </div>
        </div>

        <div style={{display:'flex',flexDirection:'column',gap:12}}>
          <div>
            <div className="section-header">
              <span className="section-title">Subject Scores</span>
              {saveMsg && <span style={{fontFamily:'var(--font-mono)',fontSize:11,color:saveMsg.startsWith('✓')?'var(--risk-low)':'var(--risk-high)'}}>{saveMsg}</span>}
            </div>
            <div className="table-wrap">
              <table>
                <thead><tr><th>Subject</th><th>IT1</th><th>IT2</th><th>Final</th><th>Weighted</th><th></th></tr></thead>
                <tbody>
                  {(scores_by_subject||[]).map(s => {
                    const isEditing = editSubject === s.subject;
                    const scoreInput = (key) => (
                      <input
                        type="number" min="0" max="100" step="0.1"
                        value={editVals[key] ?? ''}
                        onChange={e => setEditVals(v => ({...v, [key]: parseFloat(e.target.value)||0}))}
                        style={{width:54, fontFamily:'var(--font-mono)', fontSize:12, background:'var(--bg-elevated)', border:'1px solid var(--border-focus)', borderRadius:4, color:'var(--fg-1)', padding:'2px 6px', outline:'none'}}
                      />
                    );
                    return (
                      <tr key={s.subject}>
                        <td style={{fontSize:12}}>{s.subject}</td>
                        <td>{isEditing ? scoreInput('it1_score') : <span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.it1_score}</span>}</td>
                        <td>{isEditing ? scoreInput('it2_score') : <span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.it2_score}</span>}</td>
                        <td>{isEditing ? scoreInput('final_score') : <span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.final_score}</span>}</td>
                        <td><span style={{fontFamily:'var(--font-mono)',fontSize:12,color:'var(--accent-text)',fontWeight:500}}>{isEditing ? (+((editVals.it1_score||0)*0.25+(editVals.it2_score||0)*0.25+(editVals.final_score||0)*0.50)).toFixed(1) : s.weighted_score}</span></td>
                        <td style={{width:80}}>
                          {isEditing
                            ? <><button className="btn btn-primary btn-sm" onClick={()=>saveEdit(s.subject)} disabled={saving} style={{padding:'3px 8px',fontSize:11}}>{saving?'…':'Save'}</button>
                                <button className="btn btn-secondary btn-sm" onClick={()=>setEditSubject(null)} style={{padding:'3px 8px',fontSize:11,marginLeft:4}}>✕</button></>
                            : <button className="btn btn-secondary btn-sm" onClick={()=>startEdit(s)} style={{padding:'3px 8px',fontSize:11}}>Edit</button>
                          }
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          <div>
            <div className="section-header">
              <span className="section-title">AI Recommendations</span>
              {!showRecs && <button className="btn btn-secondary btn-sm" onClick={loadRecs}><Icon name="lightbulb" size={13}/> Load</button>}
            </div>
            {showRecs && !recs && <div className="loading">Generating recommendations…</div>}
            {recs && recs.recommendations.map((r,i) => (
              <div key={i} className="rec-card" style={{borderLeftColor:riskColor(r.priority)}}>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:6}}>
                  <div className="rec-title">{r.title}</div>
                  <span className={`badge badge-${r.priority.toLowerCase()}`}>{r.priority.toUpperCase()}</span>
                </div>
                <div className="rec-desc">{r.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Upload Scores Page ───────────────────────────────────────────────────────
function UploadPage() {
  const [file, setFile] = React.useState(null);
  const [preview, setPreview] = React.useState(null);
  const [result, setResult] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState('');

  const parseCSV = text => {
    const lines = text.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase().replace(/ /g,'_'));
    return lines.slice(1).map(line => {
      const vals = line.split(',');
      const obj = {};
      headers.forEach((h,i) => obj[h] = vals[i]?.trim() || '');
      return obj;
    });
  };

  const onFileChange = e => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f); setResult(null); setError('');
    const reader = new FileReader();
    reader.onload = ev => {
      try {
        const rows = parseCSV(ev.target.result);
        setPreview(rows.slice(0, 10));
      } catch { setError('Could not parse file. Ensure it is a valid CSV.'); }
    };
    reader.readAsText(f);
  };

  const upload = async () => {
    if (!file) return;
    setLoading(true); setError(''); setResult(null);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const r = await fetch(API + '/api/upload/scores', { method:'POST', body: fd });
      const data = await r.json();
      if (!r.ok) { setError(data.detail || 'Upload failed'); }
      else { setResult(data); }
    } catch { setError('Network error — is the backend running?'); }
    setLoading(false);
  };

  const SUBJECTS = ['Machine Learning','Deep Learning','Python for AI','Data Structures & Algorithms','Statistics for AI'];
  const downloadTemplate = () => {
    const header = 'student_id,subject,it1_score,it2_score,final_score';
    const rows = ['STU0001','STU0002'].flatMap(sid =>
      SUBJECTS.map(s => `${sid},${s},0,0,0`)
    );
    const blob = new Blob([[header,...rows].join('\n')], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
    a.download = 'scores_template.csv'; a.click();
  };

  return (
    <div className="page-body" style={{maxWidth:860}}>
      <div style={{marginBottom:20}}>
        <p style={{color:'var(--fg-2)',fontSize:13,marginBottom:12}}>
          Upload a CSV or Excel file with exam scores. Rows are matched by <span style={{fontFamily:'var(--font-mono)',color:'var(--accent-text)'}}>student_id</span> and <span style={{fontFamily:'var(--font-mono)',color:'var(--accent-text)'}}>subject</span>. Scores are updated in memory and saved to disk.
        </p>
        <button className="btn btn-secondary btn-sm" onClick={downloadTemplate}>↓ Download Template CSV</button>
      </div>

      <div style={{marginBottom:20}}>
        <div style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)',textTransform:'uppercase',letterSpacing:'0.06em',marginBottom:8}}>Required columns</div>
        <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
          {['student_id','subject','it1_score','it2_score','final_score'].map(c=>(
            <span key={c} style={{fontFamily:'var(--font-mono)',fontSize:11,padding:'3px 10px',background:'var(--bg-elevated)',border:'1px solid var(--border)',borderRadius:6,color:'var(--accent-text)'}}>{c}</span>
          ))}
        </div>
      </div>

      <div style={{border:'2px dashed var(--border-strong)',borderRadius:12,padding:'32px 28px',textAlign:'center',marginBottom:20,background: file ? 'rgba(79,127,255,0.04)' : 'transparent',transition:'background 200ms'}}>
        <input type="file" accept=".csv,.xlsx,.xls" id="score-file" style={{display:'none'}} onChange={onFileChange} />
        <label htmlFor="score-file" style={{cursor:'pointer'}}>
          <div style={{fontFamily:'var(--font-mono)',fontSize:12,color:'var(--fg-3)',marginBottom:8}}>
            {file ? `📎 ${file.name}` : 'Click to choose file'}
          </div>
          <div style={{fontSize:11,color:'var(--fg-3)'}}>Supports .csv, .xlsx, .xls</div>
        </label>
      </div>

      {error && <div style={{background:'var(--risk-high-dim)',border:'1px solid rgba(255,68,68,0.3)',borderRadius:8,padding:'10px 14px',color:'var(--risk-high)',fontSize:13,marginBottom:16}}>{error}</div>}

      {preview && preview.length > 0 && (
        <div style={{marginBottom:20}}>
          <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:8}}>Preview (first {preview.length} rows)</div>
          <div className="table-wrap" style={{overflowX:'auto'}}>
            <table>
              <thead><tr>{Object.keys(preview[0]).map(k=><th key={k}>{k}</th>)}</tr></thead>
              <tbody>{preview.map((row,i)=><tr key={i}>{Object.values(row).map((v,j)=><td key={j} style={{fontFamily:'var(--font-mono)',fontSize:12}}>{v}</td>)}</tr>)}</tbody>
            </table>
          </div>
        </div>
      )}

      {file && !result && (
        <button className="btn btn-primary" onClick={upload} disabled={loading} style={{marginTop:4}}>
          {loading ? 'Uploading…' : `Upload ${file.name}`}
        </button>
      )}

      {result && (
        <div style={{background:'var(--bg-surface)',border:'1px solid var(--border)',borderRadius:12,padding:20,marginTop:16}}>
          <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:12}}>Upload Result</div>
          <div style={{display:'flex',gap:24,marginBottom:16}}>
            <div><div style={{fontFamily:'var(--font-mono)',fontSize:28,fontWeight:700,color:'var(--risk-low)'}}>{result.updated}</div><div style={{fontSize:11,color:'var(--fg-3)'}}>Rows updated</div></div>
            {result.skipped>0 && <div><div style={{fontFamily:'var(--font-mono)',fontSize:28,fontWeight:700,color:'var(--risk-med)'}}>{result.skipped}</div><div style={{fontSize:11,color:'var(--fg-3)'}}>Skipped (ID not found)</div></div>}
            {result.errors>0  && <div><div style={{fontFamily:'var(--font-mono)',fontSize:28,fontWeight:700,color:'var(--risk-high)'}}>{result.errors}</div><div style={{fontSize:11,color:'var(--fg-3)'}}>Errors</div></div>}
          </div>
          {result.skipped_detail?.length>0 && (
            <div style={{fontSize:12,color:'var(--risk-med)',fontFamily:'var(--font-mono)',marginTop:8}}>
              Unknown IDs: {result.skipped_detail.map(s=>s.student_id).join(', ')}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ── Predict Page ─────────────────────────────────────────────────────────────
function PredictPage() {
  const [form, setForm] = React.useState({ avg_attendance:80, engagement_score:6, gpa_start:3.0, lms_logins_per_week:5, forum_posts:8 });
  const [result, setResult] = React.useState(null);
  const [loading, setLoading] = React.useState(false);

  const submit = async e => {
    e.preventDefault();
    setLoading(true);
    const data = await apiFetch('/api/predict', {
      risk_level: form.avg_attendance < 70 || form.engagement_score < 4 ? 'High' : form.avg_attendance < 80 ? 'Medium' : 'Low',
      risk_probabilities: { Low: 0.2, Medium: 0.3, High: 0.5 },
      predicted_score: +((form.avg_attendance * 0.4 + form.gpa_start * 10 + form.engagement_score * 2)).toFixed(1),
    }).catch(() => null);
    setLoading(false);
    if (data) setResult(data);
  };

  const fields = [
    {key:'avg_attendance',      label:'Avg Attendance (%)',      min:0,   max:100, step:0.1, hint:'0–100'},
    {key:'engagement_score',    label:'Engagement Score',        min:0,   max:20,  step:0.1, hint:'composite LMS metric'},
    {key:'gpa_start',           label:'GPA (Start of semester)', min:0,   max:10,  step:0.1, hint:'0–10'},
    {key:'lms_logins_per_week', label:'LMS Logins / Week',       min:0,   max:30,  step:0.1, hint:'weekly average'},
    {key:'forum_posts',         label:'Forum Posts (total)',      min:0,   max:100, step:1,   hint:'semester total'},
  ];

  return (
    <div className="page-body">
      <div style={{maxWidth:640}}>
        <div style={{marginBottom:20}}>
          <div style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)',marginBottom:4}}>POST /api/predict</div>
          <p style={{color:'var(--fg-2)',fontSize:13}}>Enter custom student metrics to get an instant risk classification and predicted weighted score.</p>
        </div>
        <form onSubmit={submit}>
          <div className="form-grid">
            {fields.map(f => (
              <div key={f.key} className="form-group">
                <label className="form-label">{f.label}</label>
                <input className="input" type="number" min={f.min} max={f.max} step={f.step} value={form[f.key]} onChange={e=>setForm(p=>({...p,[f.key]:parseFloat(e.target.value)||0}))} />
                <span className="form-hint">{f.hint}</span>
              </div>
            ))}
          </div>
          <button type="submit" className="btn btn-primary" style={{marginTop:20}} disabled={loading}>
            {loading ? 'Predicting…' : 'Run Prediction'}
          </button>
        </form>

        {result && (
          <div className="result-panel">
            <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:12}}>Prediction Result</div>
            <div style={{display:'flex',gap:20,alignItems:'flex-start',marginBottom:16}}>
              <div>
                <div style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)',marginBottom:4}}>Risk Level</div>
                <RiskBadge r={result.risk_level}/>
              </div>
              <div>
                <div style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)',marginBottom:4}}>Predicted Score</div>
                <span style={{fontFamily:'var(--font-display)',fontSize:28,fontWeight:700,color:'var(--accent-text)'}}>{result.predicted_score}</span>
              </div>
            </div>
            <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:8}}>Risk Probabilities</div>
            {Object.entries(result.risk_probabilities).map(([level, prob]) => (
              <div key={level} style={{marginBottom:6}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:2}}>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-2)'}}>{level}</span>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:11,color:riskColor(level)}}>{(prob*100).toFixed(0)}%</span>
                </div>
                <div className="risk-bar-track"><div className="risk-bar-fill" style={{width:`${prob*100}%`,background:riskColor(level)}}></div></div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ── App Shell ────────────────────────────────────────────────────────────────
function App() {
  const [auth, setAuth] = React.useState(null);
  const [role, setRole] = React.useState(null);
  const [page, setPage] = React.useState('dashboard');
  const [selectedStudent, setSelectedStudent] = React.useState(null);

  const login = (r, id) => {
    setAuth(true); setRole(r);
    if (id) localStorage.setItem('slis_student_id', id);
  };
  const logout = () => {
    setAuth(null); setRole(null); setPage('dashboard');
    localStorage.removeItem('slis_auth');
  };

  if (!auth) return <LoginPage onLogin={login} />;

  if (role === 'student') {
    return (
      <div style={{height:'100vh',display:'flex',alignItems:'center',justifyContent:'center',flexDirection:'column',gap:16,background:'var(--bg-base)'}}>
        <div style={{fontFamily:'var(--font-display)',fontSize:24,fontWeight:700}}>Signed in as Student</div>
        <div style={{fontFamily:'var(--font-mono)',fontSize:13,color:'var(--fg-2)'}}>Redirecting to Student Portal…</div>
        <a href="../student/index.html" className="btn btn-primary" style={{textDecoration:'none',marginTop:8}}>Open Student Portal →</a>
        <button className="btn btn-secondary" onClick={logout}>Back to Login</button>
      </div>
    );
  }

  const PAGE_TITLES = { dashboard:'Dashboard', students:'Student Directory', profile:'Student Profile', predict:'Custom Prediction', upload:'Upload Scores' };

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={p => { setPage(p); if(p!=='profile') setSelectedStudent(null); }} onLogout={logout} />
      <div className="main-content">
        <div className="topbar">
          <span className="topbar-title">SLIS</span>
          <span className="topbar-sep">·</span>
          <span className="topbar-breadcrumb">{PAGE_TITLES[page] || page}</span>
          {page === 'profile' && selectedStudent && (
            <><span className="topbar-sep">·</span><span className="topbar-breadcrumb" style={{fontFamily:'var(--font-mono)'}}>{selectedStudent}</span></>
          )}
        </div>
        {page === 'dashboard'  && <DashboardPage setPage={setPage} setSelectedStudent={setSelectedStudent} />}
        {page === 'students'   && <StudentsPage setPage={setPage} setSelectedStudent={setSelectedStudent} />}
        {page === 'profile'    && <ProfilePage studentId={selectedStudent} setPage={setPage} setSelectedStudent={setSelectedStudent} />}
        {page === 'predict'    && <PredictPage />}
        {page === 'upload'     && <UploadPage />}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
