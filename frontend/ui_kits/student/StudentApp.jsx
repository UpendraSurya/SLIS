// SLIS Student Portal — React App (Babel/JSX)
// Pages: Login, My Dashboard, My Recommendations, My Performance

const API = 'http://127.0.0.1:8000';

async function apiFetch(path, fallback) {
  try {
    const r = await fetch(API + path);
    if (!r.ok) throw new Error();
    return await r.json();
  } catch { return fallback; }
}

// ── Mock data ────────────────────────────────────────────────────────────────
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
  recommendations:[
    {title:'Strengthen Mathematics Foundation',description:'Focus 3 additional hours/week on Mathematics — your lowest subject at 78.5. Work through practice problems systematically before the final exam.',priority:'High'},
    {title:'Maintain LMS Engagement Momentum',description:'Your 9.2 logins/week is strong. Keep consistent daily login habits to maintain access to fresh materials and announcements.',priority:'Low'},
    {title:'Leverage Computer Science Strength',description:'Your 91.3 in Computer Science is excellent. Consider helping peers — teaching reinforces your own understanding significantly.',priority:'Medium'},
    {title:'Sustain Attendance Excellence',description:'91.2% attendance is commendable. Continue this discipline through the final exam period, especially in weaker subjects.',priority:'Low'},
  ],
};

const riskColor = r => r==='High'?'var(--risk-high)':r==='Medium'?'var(--risk-med)':'var(--risk-low)';
const RiskBadge = ({r}) => <span className={`badge badge-${r?.toLowerCase()}`}>{r}</span>;

// ── Sidebar ──────────────────────────────────────────────────────────────────
const NAVITEMS = [
  {id:'dashboard',     label:'My Dashboard',      icon:'dashboard'},
  {id:'recommendations',label:'My Recommendations',icon:'lightbulb'},
  {id:'performance',   label:'My Performance',    icon:'bar'},
];

const IconSvg = ({name, size=16, color='currentColor'}) => {
  const p = {
    dashboard: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></>,
    lightbulb: <><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/></>,
    bar:       <><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></>,
    logout:    <><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></>,
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{flexShrink:0}}>
      {p[name]}
    </svg>
  );
};

function Sidebar({ page, setPage, studentId, studentName, onLogout }) {
  const initials = studentName ? studentName.split(' ').map(w=>w[0]).join('').slice(0,2) : 'ST';
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-brand">SLIS</div>
        <div className="sidebar-sub">Student Portal</div>
      </div>
      <div className="sidebar-section">My Learning</div>
      {NAVITEMS.map(n => (
        <div key={n.id} className={`nav-item ${page===n.id?'active':''}`} onClick={() => setPage(n.id)}>
          <IconSvg name={n.icon} size={15} color={page===n.id?'var(--accent)':'var(--fg-3)'} />
          {n.label}
        </div>
      ))}
      <div className="sidebar-footer">
        <div className="avatar">{initials}</div>
        <div>
          <div style={{fontSize:13,color:'var(--fg-1)'}}>{studentName || studentId}</div>
          <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)'}}>{studentId}</div>
        </div>
        <button className="logout-btn" onClick={onLogout} title="Sign out">
          <IconSvg name="logout" size={14} />
        </button>
      </div>
    </div>
  );
}

// ── Login ────────────────────────────────────────────────────────────────────
function LoginPage({ onLogin }) {
  const [sid, setSid] = React.useState('');
  const [err, setErr] = React.useState('');
  const submit = e => {
    e.preventDefault();
    const id = sid.trim().toUpperCase();
    if (!id.match(/^STU\d{4}$/)) { setErr('Enter a valid Student ID, e.g. STU0001'); return; }
    onLogin(id);
  };
  return (
    <div className="login-page">
      {/* Left panel */}
      <div className="login-left">
        <div className="login-shapes">
          <svg width="100%" height="100%" viewBox="0 0 600 800" fill="none" preserveAspectRatio="xMidYMid slice">
            <circle cx="500" cy="150" r="240" stroke="rgba(79,127,255,0.07)" strokeWidth="1"/>
            <circle cx="500" cy="150" r="170" stroke="rgba(79,127,255,0.05)" strokeWidth="1"/>
            <circle cx="500" cy="150" r="100" stroke="rgba(79,127,255,0.08)" strokeWidth="1"/>
            <circle cx="60"  cy="660" r="190" stroke="rgba(79,127,255,0.05)" strokeWidth="1"/>
            <circle cx="60"  cy="660" r="120" stroke="rgba(79,127,255,0.04)" strokeWidth="1"/>
            <line x1="0" y1="390" x2="600" y2="370" stroke="rgba(255,255,255,0.025)" strokeWidth="1"/>
            <rect x="260" y="310" width="50" height="50" rx="4" stroke="rgba(79,127,255,0.06)" strokeWidth="1" transform="rotate(15 285 335)"/>
            <rect x="120" y="180" width="28" height="28" rx="2" stroke="rgba(79,127,255,0.05)" strokeWidth="1" transform="rotate(-8 134 194)"/>
          </svg>
        </div>
        <div style={{position:'relative',zIndex:1}}>
          <div className="login-brand">SLIS</div>
          <div className="login-tagline">Your personal academic dashboard — track performance, monitor risk, and get AI-powered study recommendations.</div>
        </div>
        <div style={{position:'relative',zIndex:1}}>
          <div style={{display:'flex',gap:32}}>
            <div><div className="login-stat-n">4</div><div className="login-stat-l">AI Recs</div></div>
            <div><div className="login-stat-n">5</div><div className="login-stat-l">Subjects</div></div>
            <div><div className="login-stat-n">Real-time</div><div className="login-stat-l">Risk Score</div></div>
          </div>
          <div style={{marginTop:24,fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)'}}>Powered by Qwen3-32B · FastAPI</div>
        </div>
      </div>

      {/* Right panel */}
      <div className="login-right">
        <div className="login-form">
          <div className="login-heading">Student Sign In</div>
          <div className="login-sub">Enter your Student ID to access your dashboard</div>
          <form onSubmit={submit}>
            <div className="login-field">
              <label className="login-label">Student ID</label>
              <input className="input" style={{width:'100%'}} value={sid} onChange={e=>setSid(e.target.value)} placeholder="STU0001" autoFocus />
            </div>
            {err && <div className="login-error">{err}</div>}
            <button type="submit" className="btn btn-primary" style={{width:'100%',marginTop:20,justifyContent:'center',padding:'10px 16px'}}>
              Sign In →
            </button>
          </form>
          <div style={{marginTop:20,padding:'12px 14px',background:'var(--bg-elevated)',borderRadius:8,fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)',lineHeight:1.7}}>
            Demo: any ID matching STU0001 – STU0500
          </div>
          <div className="divider"></div>
          <div style={{fontSize:12,color:'var(--fg-3)',textAlign:'center'}}>
            <a href="../teacher/index.html" style={{color:'var(--accent)',textDecoration:'none'}}>Go to Teacher Portal →</a>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── My Dashboard ─────────────────────────────────────────────────────────────
function DashboardPage({ profile }) {
  if (!profile) return <div className="loading">Loading your data…</div>;
  const { name, student_id, major, risk_level, predicted_score, avg_attendance, avg_score, activity, risk_probabilities, attendance_by_month } = profile;
  const maxAtt = Math.max(...(attendance_by_month||[]).map(a=>a.attendance_pct));

  return (
    <div className="page-body">
      {/* Hero banner */}
      <div className="risk-hero">
        <div>
          <div style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',textTransform:'uppercase',letterSpacing:'0.08em',marginBottom:8}}>Risk Level</div>
          <RiskBadge r={risk_level}/>
          <div style={{marginTop:12,display:'flex',flexDirection:'column',gap:4}}>
            {Object.entries(risk_probabilities||{}).map(([level,prob]) => (
              <div key={level} style={{display:'flex',alignItems:'center',gap:8}}>
                <span style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',width:50}}>{level}</span>
                <div className="risk-bar-track" style={{width:80}}><div className="risk-bar-fill" style={{width:`${prob*100}%`,background:riskColor(level)}}></div></div>
                <span style={{fontFamily:'var(--font-mono)',fontSize:10,color:riskColor(level)}}>{(prob*100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
        <div className="risk-sep"></div>
        <div>
          <div className="risk-hero-score" style={{color:'var(--accent-text)'}}>{predicted_score}</div>
          <div className="risk-hero-label">Predicted Weighted Score</div>
        </div>
        <div className="risk-sep"></div>
        <div>
          <div className="risk-hero-score">{avg_attendance}%</div>
          <div className="risk-hero-label">Attendance</div>
        </div>
        <div className="risk-sep"></div>
        <div>
          <div className="risk-hero-score">{avg_score}</div>
          <div className="risk-hero-label">Current Avg Score</div>
        </div>
      </div>

      <div className="two-col">
        {/* Attendance trend */}
        <div>
          <div className="section-header"><span className="section-title">Attendance by Month</span></div>
          <div style={{background:'var(--bg-surface)',border:'1px solid var(--border)',padding:16}}>
            {(attendance_by_month||[]).map(a => (
              <div key={a.month} style={{marginBottom:10}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom:3}}>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-2)'}}>Month {a.month}</span>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:11,color: a.attendance_pct>=85?'var(--risk-low)':a.attendance_pct>=70?'var(--risk-med)':'var(--risk-high)'}}>{a.attendance_pct}%</span>
                </div>
                <div className="risk-bar-track">
                  <div className="risk-bar-fill" style={{width:`${(a.attendance_pct/100)*100}%`,background:a.attendance_pct>=85?'var(--risk-low)':a.attendance_pct>=70?'var(--risk-med)':'var(--risk-high)'}}></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* LMS Activity */}
        <div>
          <div className="section-header"><span className="section-title">LMS Activity</span></div>
          <div style={{background:'var(--bg-surface)',border:'1px solid var(--border)',padding:16}}>
            {[
              {key:'lms_logins_per_week', label:'LMS Logins / Week', good: v=>v>=5},
              {key:'forum_posts',         label:'Forum Posts',        good: v=>v>=10},
              {key:'resources_accessed',  label:'Resources Accessed', good: v=>v>=30},
              {key:'avg_session_minutes', label:'Avg Session (min)',   good: v=>v>=45},
            ].map(({key,label,good}) => {
              const v = activity?.[key] ?? 0;
              const isGood = good(v);
              return (
                <div key={key} style={{display:'flex',justifyContent:'space-between',alignItems:'center',padding:'8px 0',borderBottom:'1px solid var(--border)'}}>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)'}}>{label}</span>
                  <span style={{fontFamily:'var(--font-mono)',fontSize:13,fontWeight:500,color:isGood?'var(--risk-low)':'var(--risk-med)'}}>{+v.toFixed(1)}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── My Recommendations ───────────────────────────────────────────────────────
function RecommendationsPage({ studentId }) {
  const [recs, setRecs] = React.useState(null);
  React.useEffect(() => {
    apiFetch(`/api/recommendations/${studentId}`, MOCK_RECS).then(setRecs);
  }, [studentId]);

  if (!recs) return <div className="loading">Generating your recommendations…</div>;
  const sorted = [...(recs.recommendations||[])].sort((a,b) => {
    const order = {High:0,Medium:1,Low:2};
    return (order[a.priority]??2) - (order[b.priority]??2);
  });

  return (
    <div className="page-body" style={{maxWidth:640}}>
      <div style={{marginBottom:20}}>
        <p style={{color:'var(--fg-2)',fontSize:13}}>Personalised recommendations generated by Qwen3-32B based on your academic profile.</p>
      </div>
      {sorted.map((r,i) => (
        <div key={i} className="rec-card" style={{borderLeftColor:riskColor(r.priority)}}>
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:8}}>
            <div className="rec-title">{r.title}</div>
            <span className={`badge badge-${r.priority.toLowerCase()}`}>{r.priority.toUpperCase()}</span>
          </div>
          <div className="rec-desc">{r.description}</div>
          <div style={{marginTop:10,fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)'}}>
            {i+1} of {sorted.length}
          </div>
        </div>
      ))}
    </div>
  );
}

// ── My Performance ───────────────────────────────────────────────────────────
function PerformancePage({ profile }) {
  if (!profile) return <div className="loading">Loading performance data…</div>;
  const { scores_by_subject } = profile;
  const maxScore = 100;

  const trend = (it1, it2, fin) => {
    if (fin > it2 && it2 > it1) return <span className="trend-up">↑ Improving</span>;
    if (fin < it2 && it2 < it1) return <span className="trend-down">↓ Declining</span>;
    if (fin > it1) return <span className="trend-up">↑ Recovering</span>;
    return <span className="trend-flat">→ Stable</span>;
  };

  return (
    <div className="page-body">
      <div style={{marginBottom:20}}>
        <p style={{color:'var(--fg-2)',fontSize:13}}>IT1 × 0.25 + IT2 × 0.25 + Final × 0.50 = Weighted Score</p>
      </div>

      {/* Score table */}
      <div style={{marginBottom:24}}>
        <div className="section-header"><span className="section-title">Subject Breakdown</span></div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Subject</th><th>IT1</th><th>IT2</th><th>Final</th><th>Weighted</th><th>Trend</th></tr>
            </thead>
            <tbody>
              {(scores_by_subject||[]).map(s => (
                <tr key={s.subject}>
                  <td style={{fontWeight:500}}>{s.subject}</td>
                  <td><span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.it1_score}</span></td>
                  <td><span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.it2_score}</span></td>
                  <td><span style={{fontFamily:'var(--font-mono)',fontSize:12}}>{s.final_score}</span></td>
                  <td><span style={{fontFamily:'var(--font-mono)',fontSize:13,fontWeight:500,color:'var(--accent-text)'}}>{s.weighted_score}</span></td>
                  <td style={{fontSize:12}}>{trend(s.it1_score,s.it2_score,s.final_score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual bars per subject */}
      <div className="section-header"><span className="section-title">Score Comparison</span></div>
      <div style={{background:'var(--bg-surface)',border:'1px solid var(--border)',padding:16}}>
        {(scores_by_subject||[]).map(s => (
          <div key={s.subject} style={{marginBottom:16}}>
            <div style={{display:'flex',justifyContent:'space-between',marginBottom:6}}>
              <span style={{fontFamily:'var(--font-display)',fontSize:13,fontWeight:600}}>{s.subject}</span>
              <span style={{fontFamily:'var(--font-mono)',fontSize:12,color:'var(--accent-text)',fontWeight:500}}>WS: {s.weighted_score}</span>
            </div>
            {[{label:'IT1',val:s.it1_score,col:'var(--fg-3)'},{label:'IT2',val:s.it2_score,col:'var(--accent)'},{label:'Final',val:s.final_score,col:'var(--risk-low)'}].map(({label,val,col}) => (
              <div key={label} style={{display:'flex',alignItems:'center',gap:8,marginBottom:4}}>
                <span style={{fontFamily:'var(--font-mono)',fontSize:10,color:'var(--fg-3)',width:36}}>{label}</span>
                <div className="score-bar-track"><div className="score-bar-fill" style={{width:`${val}%`,background:col}}></div></div>
                <span style={{fontFamily:'var(--font-mono)',fontSize:11,color:col,width:28}}>{val}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── App ──────────────────────────────────────────────────────────────────────
function App() {
  const [studentId, setStudentId] = React.useState(() => localStorage.getItem('slis_student_id') || null);
  const [profile, setProfile] = React.useState(null);
  const [page, setPage] = React.useState(() => localStorage.getItem('slis_student_page') || 'dashboard');

  React.useEffect(() => {
    if (studentId) {
      apiFetch(`/api/students/${studentId}`, {...MOCK_PROFILE, student_id: studentId}).then(setProfile);
    }
  }, [studentId]);

  React.useEffect(() => {
    if (page) localStorage.setItem('slis_student_page', page);
  }, [page]);

  const login = id => {
    localStorage.setItem('slis_student_id', id);
    setStudentId(id);
  };
  const logout = () => {
    localStorage.removeItem('slis_student_id');
    localStorage.removeItem('slis_student_page');
    setStudentId(null); setProfile(null);
  };

  if (!studentId) return <LoginPage onLogin={login} />;

  const PAGE_TITLES = { dashboard:'My Dashboard', recommendations:'My Recommendations', performance:'My Performance' };

  return (
    <div className="app-shell">
      <Sidebar page={page} setPage={setPage} studentId={studentId} studentName={profile?.name} onLogout={logout} />
      <div className="main-content">
        <div className="topbar">
          <span className="topbar-title">SLIS</span>
          <span className="topbar-sep">·</span>
          <span className="topbar-breadcrumb">{PAGE_TITLES[page]}</span>
          <span style={{marginLeft:'auto',fontFamily:'var(--font-mono)',fontSize:11,color:'var(--fg-3)'}}>{studentId}</span>
        </div>
        {page === 'dashboard'       && <DashboardPage profile={profile} />}
        {page === 'recommendations' && <RecommendationsPage studentId={studentId} />}
        {page === 'performance'     && <PerformancePage profile={profile} />}
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
