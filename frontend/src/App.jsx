import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Plus,
  Search,
  Upload,
  Users,
  FileText,
  ChevronRight,
  TrendingUp,
  AlertCircle,
  X,
  CheckCircle2,
  Settings,
  LayoutDashboard,
  BrainCircuit,
  Binary,
  Layers,
  Zap,
  Activity,
  Menu
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = import.meta.env.VITE_API_BASE || 'https://transportassignment.onrender.com';
console.log('API_BASE being used:', API_BASE);

function App() {
  const [jdText, setJdText] = useState('');
  const [jdReqs, setJdReqs] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [processingText, setProcessingText] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const parseJD = async () => {
    if (!jdText) return;
    setLoading(true);
    setError('');
    const formData = new FormData();
    formData.append('jd_text', jdText);
    try {
      const res = await axios.post(`${API_BASE}/parse-jd`, formData);
      setJdReqs(res.data);
      setSuccess('Job Profile synchronized.');
    } catch (err) {
      const msg = err.response?.data?.detail || err.message;
      setError(`System Error: JD Parsing failed. (${msg})`);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const files = e.target.files;
    if (!files.length) return;

    if (!jdReqs) {
      setError('Workflow Error: Set Job Profile first.');
      return;
    }

    setLoading(true);
    setProcessingText('Analyzing Ingested Files...');
    setError('');
    setSuccess('');
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const res = await axios.post(`${API_BASE}/evaluate-candidates`, formData);
      setCandidates(res.data);
      if (res.data.length > 0) {
        setSuccess(`Batch evaluation of ${res.data.length} profiles complete.`);
      } else {
        setError('Extraction Error: No data found in artifacts.');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || err.message;
      setError(`Connection Error: Evaluation pipeline severed. (${msg})`);
    } finally {
      setLoading(false);
      setProcessingText('');
    }
  };

  const applyOverride = async (candId, newScore, reason) => {
    try {
      await axios.post(`${API_BASE}/override-score`, null, {
        params: { candidate_id: candId, new_score: newScore, reason }
      });
      const res = await axios.get(`${API_BASE}/get-shortlist`);
      setCandidates(res.data);
      setSelectedCandidate(null);
    } catch (err) {
      setError('Administrative Error: Override failed.');
    }
  };

  return (
    <div className={`app-wrapper ${sidebarOpen ? 'sidebar-open' : ''}`}>
      {/* MOBILE HEADER */}
      <header className="mobile-header">
        <div className="tool-name">AI Talent Engine</div>
        <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
          {sidebarOpen ? <X /> : <Menu />}
        </button>
      </header>

      {/* SIDEBAR */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="tool-name">AI Talent Engine <span className="tool-tag">v2.1</span></div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '0.25rem' }}>Enterprise Recruitment Tool</p>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <div className="section-title"><LayoutDashboard size={14} /> Source Configuration</div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>Job Description (Raw Text)</p>
          <textarea
            className="enterprise-textarea"
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            placeholder="Paste raw JD text here..."
          />
          <button
            className="btn-primary"
            style={{ marginTop: '1rem' }}
            onClick={() => { parseJD(); setSidebarOpen(false); }}
            disabled={loading || !jdText}
          >
            {loading ? 'Processing...' : 'Run Extraction'}
          </button>
        </div>

        <div style={{ marginBottom: '2rem' }}>
          <div className="section-title"><Binary size={14} /> Artifact Ingestion</div>
          <div className="upload-zone" onClick={() => !loading && document.getElementById('fileInput').click()}>
            <Upload size={24} style={{ marginBottom: '1rem', opacity: 0.5 }} />
            <p style={{ fontSize: '0.85rem', fontWeight: 600 }}>Click to Upload Artifacts</p>
            <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>PDF, DOCX, JSON</p>
            <input
              id="fileInput"
              type="file"
              multiple
              hidden
              onChange={(e) => { handleFileUpload(e); setSidebarOpen(false); }}
              disabled={loading}
            />
          </div>
        </div>

        {jdReqs && (
          <div style={{ padding: '1rem', background: '#ffffff05', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div className="section-title" style={{ marginBottom: '0.75rem' }}>Current Profile</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {jdReqs.skills.slice(0, 8).map((s, i) => (
                <span key={i} className="skill-tag">{s}</span>
              ))}
            </div>
            <p style={{ fontSize: '0.75rem', marginTop: '0.75rem', color: 'var(--text-muted)' }}>Required: {jdReqs.experience_years}</p>
          </div>
        )}

        <div style={{ marginTop: 'auto', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
            <Settings size={14} /> System Settings
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '3rem' }}>
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.03em', marginBottom: '0.5rem' }}>Analysis Dashboard</h1>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Real-time semantic evaluation & ranking system.</p>
          </div>
          <div className="stats-container">
            <StatsCard label="Evaluated" value={candidates.length} icon={<Users size={14} />} />
            <StatsCard label="Avg. Match" value={candidates.length ? (candidates.reduce((acc, c) => acc + c.final_score, 0) / candidates.length).toFixed(1) : '0.0'} icon={<TrendingUp size={14} />} />
            <StatsCard label="System Load" value="Optimal" icon={<Zap size={14} />} />
          </div>
        </header>

        {error && (
          <div className="status-toast error">
            <AlertCircle size={18} /> {error}
          </div>
        )}

        {success && (
          <div className="status-toast success">
            <CheckCircle2 size={18} /> {success}
          </div>
        )}

        {loading && processingText && (
          <div className="glass-card" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', borderLeft: '4px solid var(--accent-primary)', background: 'linear-gradient(90deg, #3b82f610, transparent)' }}>
            <div className="spin-loader"></div>
            <div>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.25rem', fontWeight: 700 }}>{processingText}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>AI models are currently calculating multidimensional semantic scores...</p>
            </div>
          </div>
        )}

        {!loading && candidates.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ height: '60vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', background: 'radial-gradient(circle at center, #3b82f605, transparent)', borderRadius: '24px' }}
          >
            <div style={{ position: 'relative', marginBottom: '2.5rem' }}>
              <BrainCircuit size={80} style={{ color: 'var(--accent-primary)', opacity: 0.8 }} />
              <motion.div
                animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
                transition={{ repeat: Infinity, duration: 3 }}
                style={{ position: 'absolute', inset: -20, background: 'var(--accent-primary)', filter: 'blur(40px)', borderRadius: '50%', zIndex: -1 }}
              />
            </div>
            <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '1rem' }}>Awaiting System Input</h2>
            <p style={{ maxWidth: '500px', color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: '1.05rem', marginBottom: '2rem' }}>
              The evaluation engine is standing by. To begin the analysis, please configure the <b>Job Profile</b> in the sidebar and upload <b>Candidate Artifacts</b>.
            </p>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <div className="skill-tag" style={{ padding: '0.5rem 1rem' }}>1. Define Requirements</div>
              <div className="skill-tag" style={{ padding: '0.5rem 1rem' }}>2. Ingest Resumes</div>
              <div className="skill-tag" style={{ padding: '0.5rem 1rem' }}>3. Review Rankings</div>
            </div>
          </motion.div>
        )}

        <div className="ranking-container">
          {candidates.map((cand, idx) => (
            <div
              key={cand.id}
              className="candidate-card"
              onClick={() => setSelectedCandidate(cand)}
              style={{ cursor: 'pointer' }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>{cand.name.split('.')[0]}</h3>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span className="skill-tag" style={{ background: 'var(--accent-primary)', padding: '0.1rem 0.4rem' }}>MATCH</span>
                  </div>
                </div>
                <div className="score-circle">
                  {cand.final_score.toFixed(1)}
                </div>
              </div>

              <MetricRow label="Skills Alignment" score={cand.scores.skills_match.score} />
              <MetricRow label="Domain Expertise" score={cand.scores.experience_relevance.score} />

              <div style={{ marginTop: '1.5rem', display: 'flex', alignItems: 'center', justifySelf: 'flex-end', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                View Analysis Details <ChevronRight size={14} />
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* DETAIL MODAL */}
      <AnimatePresence>
        {selectedCandidate && (
          <div className="modal-backdrop" onClick={() => setSelectedCandidate(null)}>
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="modal-content"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="modal-header">
                <div>
                  <h2 style={{ fontSize: '1.5rem' }}>{selectedCandidate.name.split('.')[0]}</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Candidate Evaluation Profile</p>
                </div>
                <X onClick={() => setSelectedCandidate(null)} style={{ cursor: 'pointer', opacity: 0.5 }} />
              </div>

              <div className="modal-body">
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '3rem' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                    <div style={{ background: '#00000020', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
                      <div className="section-title"><BrainCircuit size={14} /> AI Recommendation</div>
                      <p style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-secondary)' }}>
                        {selectedCandidate.scores.hire_recommendation}
                      </p>
                    </div>

                    <DetailedMetric label="Technical Proficiency" score={selectedCandidate.scores.skills_match} />
                    <DetailedMetric label="Experience Relevance" score={selectedCandidate.scores.experience_relevance} />
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                    <DetailedMetric label="Academic Background" score={selectedCandidate.scores.education_certs} />

                    <div className="glass-card" style={{ padding: '1.5rem', border: '1px solid var(--accent-primary)' }}>
                      <div className="section-title" style={{ color: 'var(--accent-primary)' }}><Settings size={14} /> Admin Override</div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>Calibrate system-generated score manually.</p>

                      <input
                        type="range" min="0" max="10" step="0.1"
                        defaultValue={selectedCandidate.final_score}
                        style={{ width: '100%', marginBottom: '1.5rem' }}
                        id="scoreOverride"
                      />
                      <textarea
                        id="reasonOverride"
                        placeholder="Override justification..."
                        className="enterprise-textarea"
                        style={{ minHeight: '80px', marginBottom: '1rem' }}
                      />
                      <button
                        className="btn-primary"
                        onClick={() => {
                          const val = document.getElementById('scoreOverride').value;
                          const rsn = document.getElementById('reasonOverride').value;
                          applyOverride(selectedCandidate.id, val, rsn);
                        }}
                      >Commit Adjustment</button>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <style dangerouslySetInnerHTML={{
        __html: `
        .spin-loader {
          width: 24px;
          height: 24px;
          border: 3px solid #27272a;
          border-top-color: var(--accent-primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
      `}} />
    </div>
  );
}

function MetricRow({ label, score }) {
  return (
    <div className="metric-row">
      <div className="metric-label">
        <span>{label}</span>
        <span>{score}/10</span>
      </div>
      <div className="progress-bg">
        <div className="progress-fill" style={{ width: `${score * 10}%` }}></div>
      </div>
    </div>
  );
}

function DetailedMetric({ label, score }) {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
        <span style={{ fontWeight: 600 }}>{label}</span>
        <span style={{ color: 'var(--accent-primary)', fontWeight: 700 }}>{score.score}/10</span>
      </div>
      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5, marginBottom: '0.75rem' }}>
        {score.justification}
      </p>
      <div className="progress-bg">
        <div className="progress-fill" style={{ width: `${score.score * 10}%` }}></div>
      </div>
    </div>
  );
}

function StatsCard({ label, value, icon }) {
  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', padding: '0.75rem 1.25rem', borderRadius: '12px', display: 'flex', flexDirection: 'column', minWidth: '140px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
        {icon} {label}
      </div>
      <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent-primary)' }}>{value}</div>
    </div>
  );
}

export default App;
