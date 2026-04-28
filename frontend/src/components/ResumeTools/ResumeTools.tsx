import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, Search, LogOut, User, Plus, X } from 'lucide-react';
import { resumeApi, ResumeEnhanceResponse } from '../../services/api';
import ResultsView from './ResultsView';
import ResumeUpload from './ResumeUpload';
import { supabase } from '../../services/supabase';
import { motion, AnimatePresence } from 'framer-motion';

const ResumeTools: React.FC = () => {
  const [targetRole, setTargetRole] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResumeEnhanceResponse | null>(null);
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

  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    resumeApi.getProfile().then(data => {
      if (data) setProfile(data);
    }).catch(() => {});
  }, []);

  // Sync profile to backend on change
  useEffect(() => {
    if (profile.full_name || profile.skills.length > 0) {
      const timeoutId = setTimeout(async () => {
        setSyncing(true);
        try {
          await resumeApi.saveProfile(profile);
        } catch (e) {}
        setSyncing(false);
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
      const msg = err.response?.data?.detail || err.message || 'Failed to enhance resume.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
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

      <header style={{ marginBottom: '3rem', textAlign: 'center' }}>
        <h1 className="section-title">NEXUS AI Accelerator</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto' }}>
          Real-time resume optimization for target roles.
        </p>
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
                {loading ? 'Analyzing...' : 'Generate Resume'}
              </button>
            </form>
          </div>

          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <ResultsView data={result} profileOverride={profile} />
              </motion.div>
            )}
          </AnimatePresence>
          
          {error && (
            <p style={{ color: '#ef4444', textAlign: 'center', marginTop: '1rem' }}>{error}</p>
          )}
        </section>
      </div>
    </div>
  );
};

export default ResumeTools;
