import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, Search, LogOut, User, Plus, X, FileText, Briefcase, UserCircle } from 'lucide-react';
import { resumeApi, ResumeEnhanceResponse, CVGenerateResponse } from '../../services/api';
import ResultsView from './ResultsView';
import ResumeUpload from './ResumeUpload';
import JobsView from '../Jobs/Jobs';
import { supabase } from '../../services/supabase';
import { motion, AnimatePresence } from 'framer-motion';

const ResumeTools: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'resume' | 'cv' | 'jobs'>('resume');
  const [targetRole, setTargetRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResumeEnhanceResponse | CVGenerateResponse | null>(null);
  const [error, setError] = useState('');
  
  // Profile state for dynamic editing
  const [profile, setProfile] = useState<any>({
    full_name: '',
    email: '',
    linkedin_url: '',
    github_url: '',
    skills: []
  });
  const [newSkill, setNewSkill] = useState('');

  
  useEffect(() => {
    resumeApi.getProfile().then(data => {
      if (data) setProfile(data);
    }).catch(() => {});
  }, []);

  // Sync profile to backend on change
  useEffect(() => {
    if (profile.full_name || profile.skills.length > 0) {
      const timeoutId = setTimeout(async () => {
        try {
          await resumeApi.saveProfile(profile);
        } catch (e) {}
      }, 1000);
      return () => clearTimeout(timeoutId);
    }
  }, [profile]);

  const handleLogout = () => supabase.auth.signOut();

  const handleEnhance = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetRole) return;

    setLoading(true);
    setError('');
    try {
      const data = await resumeApi.enhance({ target_role: targetRole });
      setResult(data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Authentication required. Please log in to enhance your resume.');
      } else if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please try again later.');
      } else if (err.response?.status === 404) {
        setError('No profile found. Please upload your resume first.');
      } else {
        const msg = err.response?.data?.detail || err.message || 'Failed to enhance resume.';
        setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCV = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetRole) return;

    setLoading(true);
    setError('');
    try {
      const data = await resumeApi.generateCV({ target_role: targetRole });
      setResult(data);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Authentication required. Please log in to generate your CV.');
      } else if (err.response?.status === 429) {
        setError('Rate limit exceeded. Please try again later.');
      } else if (err.response?.status === 404) {
        setError('No profile found. Please upload your resume first.');
      } else {
        const msg = err.response?.data?.detail || err.message || 'Failed to generate CV.';
        setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
      }
    } finally {
      setLoading(false);
    }
  };

  const addSkill = () => {
    if (newSkill && !profile.skills.includes(newSkill)) {
      setProfile({ ...profile, skills: [...profile.skills, newSkill] });
      setNewSkill('');
    }
  };

  const removeSkill = (skill: string) => {
    setProfile({ ...profile, skills: profile.skills.filter((s: string) => s !== skill) });
  };

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
        <button onClick={handleLogout} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem' }}>
          <LogOut size={16} /> Sign Out
        </button>
      </div>

      <header style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h1 className="section-title">NEXUS AI Accelerator</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto', marginBottom: '2rem' }}>
          Real-time resume optimization for target roles.
        </p>
        
        {/* Tab Navigation */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginBottom: '2rem' }}>
          <button
            onClick={() => setActiveTab('resume')}
            className={`tab-button ${activeTab === 'resume' ? 'active' : ''}`}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem', borderRadius: '8px', border: '1px solid var(--border-glass)', background: activeTab === 'resume' ? 'var(--primary)' : 'transparent', color: activeTab === 'resume' ? 'white' : 'var(--text-secondary)', cursor: 'pointer', transition: 'all 0.3s ease' }}
          >
            <FileText size={18} /> Enhance Resume
          </button>
          <button
            onClick={() => setActiveTab('cv')}
            className={`tab-button ${activeTab === 'cv' ? 'active' : ''}`}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem', borderRadius: '8px', border: '1px solid var(--border-glass)', background: activeTab === 'cv' ? 'var(--primary)' : 'transparent', color: activeTab === 'cv' ? 'white' : 'var(--text-secondary)', cursor: 'pointer', transition: 'all 0.3s ease' }}
          >
            <UserCircle size={18} /> Generate CV
          </button>
          <button
            onClick={() => setActiveTab('jobs')}
            className={`tab-button ${activeTab === 'jobs' ? 'active' : ''}`}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem', borderRadius: '8px', border: '1px solid var(--border-glass)', background: activeTab === 'jobs' ? 'var(--primary)' : 'transparent', color: activeTab === 'jobs' ? 'white' : 'var(--text-secondary)', cursor: 'pointer', transition: 'all 0.3s ease' }}
          >
            <Briefcase size={18} /> Matching Jobs
          </button>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '2rem', marginBottom: '3rem' }}>
        <aside style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <ResumeUpload />
          
          {/* Profile Editor Card */}
          <div className="glass-card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <User size={18} color="var(--primary)" /> Profile Details
            </h3>
            
            <div style={{ display: 'grid', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Full Name</label>
                <input 
                  className="input-field" 
                  value={profile.full_name} 
                  onChange={e => setProfile({...profile, full_name: e.target.value})}
                  placeholder="Your Name"
                />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Email</label>
                <input 
                  className="input-field" 
                  value={profile.email} 
                  onChange={e => setProfile({...profile, email: e.target.value})}
                  placeholder="email@example.com"
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>LinkedIn</label>
                  <input className="input-field" value={profile.linkedin_url} onChange={e => setProfile({...profile, linkedin_url: e.target.value})} placeholder="URL" />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>GitHub</label>
                  <input className="input-field" value={profile.github_url} onChange={e => setProfile({...profile, github_url: e.target.value})} placeholder="URL" />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Skills (Unity, C#, etc.)</label>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <input 
                    className="input-field" 
                    value={newSkill} 
                    onChange={e => setNewSkill(e.target.value)} 
                    onKeyPress={e => e.key === 'Enter' && addSkill()}
                    placeholder="Add skill..." 
                  />
                  <button onClick={addSkill} className="btn-primary" style={{ padding: '0 0.75rem' }}><Plus size={18}/></button>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                  {profile.skills.map((skill: string) => (
                    <span key={skill} style={{ fontSize: '0.8rem', background: 'rgba(255,255,255,0.05)', padding: '0.2rem 0.6rem', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      {skill}
                      <X size={12} style={{ cursor: 'pointer', color: '#ef4444' }} onClick={() => removeSkill(skill)} />
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </aside>

        <section>
          {activeTab === 'resume' && (
            <>
              <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
                <form onSubmit={handleEnhance} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', marginBottom: '0.75rem', fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                      Target Career Goal
                    </label>
                    <div style={{ position: 'relative' }}>
                      <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                      <input
                        type="text"
                        className="input-field"
                        placeholder="e.g., Unity Game Developer..."
                        value={targetRole}
                        onChange={(e) => setTargetRole(e.target.value)}
                        style={{ paddingLeft: '3rem' }}
                      />
                    </div>
                  </div>
                  <button type="submit" className="btn-primary" disabled={loading || !targetRole} style={{ height: '48px' }}>
                    {loading ? <Loader2 className="animate-spin" size={20} /> : <Sparkles size={20} />}
                    {loading ? 'Analyzing...' : 'Enhance Resume'}
                  </button>
                </form>
              </div>
            </>
          )}

          {activeTab === 'cv' && (
            <>
              <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
                <form onSubmit={handleGenerateCV} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ display: 'block', marginBottom: '0.75rem', fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
                      Target Career Goal
                    </label>
                    <div style={{ position: 'relative' }}>
                      <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                      <input
                        type="text"
                        className="input-field"
                        placeholder="e.g., Senior Software Engineer..."
                        value={targetRole}
                        onChange={(e) => setTargetRole(e.target.value)}
                        style={{ paddingLeft: '3rem' }}
                      />
                    </div>
                  </div>
                  <button type="submit" className="btn-primary" disabled={loading || !targetRole} style={{ height: '48px' }}>
                    {loading ? <Loader2 className="animate-spin" size={20} /> : <UserCircle size={20} />}
                    {loading ? 'Generating...' : 'Generate CV'}
                  </button>
                </form>
              </div>
            </>
          )}

          {activeTab === 'jobs' && (
            <JobsView />
          )}

          <AnimatePresence>
            {result && activeTab !== 'jobs' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <ResultsView data={result} profileOverride={profile} isCV={activeTab === 'cv'} />
              </motion.div>
            )}
          </AnimatePresence>
          
          {error && activeTab !== 'jobs' && (
            <p style={{ color: '#ef4444', textAlign: 'center', marginTop: '1rem' }}>{error}</p>
          )}
        </section>
      </div>
    </div>
  );
};

export default ResumeTools;
