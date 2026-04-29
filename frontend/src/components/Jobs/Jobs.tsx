import React, { useState, useEffect } from 'react';
import { Briefcase, MapPin, Calendar, ExternalLink, RefreshCw } from 'lucide-react';
import { resumeApi } from '../../services/api';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  description: string;
  employment_type: string;
  source: string;
  url: string;
  posted_at: string;
  similarity: number;
}

const JobsView: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      const jobsData = await resumeApi.getJobs();
      setJobs(jobsData || []);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch jobs';
      if (err.response?.status === 401) {
        setError('Authentication required. Please log in to view job recommendations.');
      } else if (err.response?.status === 404) {
        setError('No profile found. Please upload your resume first.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.5) return '#22c55e';
    if (similarity >= 0.4) return '#f59e0b';
    return '#ef4444';
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <RefreshCw size={24} style={{ animation: 'spin 1s linear infinite' }} />
        <p>Loading job recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: '#ef4444', marginBottom: '1rem' }}>{error}</p>
        <button onClick={fetchJobs} className="btn-primary" style={{ background: '#000', color: '#fff' }}>
          <RefreshCw size={16} /> Retry
        </button>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '2rem', textAlign: 'center' }}>
        <Briefcase size={48} style={{ marginBottom: '1rem', opacity: 0.5 }} />
        <h3>No Jobs Found</h3>
        <p style={{ color: 'var(--text-secondary)' }}>
          No job recommendations available. Make sure your resume is uploaded and processed.
        </p>
        <button onClick={fetchJobs} className="btn-primary" style={{ background: '#000', color: '#fff', marginTop: '1rem' }}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gap: '1.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h2 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Briefcase size={24} />
          Job Recommendations
        </h2>
        <button onClick={fetchJobs} className="btn-secondary" style={{ border: '0px solid var(--border-glass)', background: 'transparent' , color: 'white'}}>
          <RefreshCw size={16} /> Refresh
        </button>
      </div>

      <div style={{ display: 'grid', gap: '1rem' }}>
        {jobs.map((job) => (
          <div key={job.id} className="glass-card" style={{ padding: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>
                  {job.title}
                </h3>
                <p style={{ margin: '0 0 0.5rem 0', fontWeight: 'bold', color: 'var(--text-secondary)' }}>
                  {job.company}
                </p>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <MapPin size={14} /> {job.location}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Calendar size={14} /> {formatDate(job.posted_at)}
                  </span>
                  <span style={{ 
                    background: 'rgba(34, 197, 94, 0.1)', 
                    color: '#22c55e', 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: '1rem', 
                    fontSize: '0.8rem' 
                  }}>
                    {job.employment_type}
                  </span>
                </div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                <div style={{ 
                  background: `${getSimilarityColor(job.similarity)}20`, 
                  color: getSimilarityColor(job.similarity), 
                  padding: '0.5rem', 
                  borderRadius: '0.5rem', 
                  fontSize: '0.9rem', 
                  fontWeight: 'bold',
                  textAlign: 'center',
                  minWidth: '80px'
                }}>
                  {(job.similarity * 100).toFixed(1)}% Match
                </div>
                <a 
                  href={job.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '0.25rem', 
                    color: 'var(--accent)', 
                    textDecoration: 'none',
                    fontSize: '0.9rem'
                  }}
                >
                  <ExternalLink size={14} /> Apply
                </a>
              </div>
            </div>
            
            <div style={{ 
              marginTop: '1rem', 
              paddingTop: '1rem', 
              borderTop: '1px solid var(--border-glass)' 
            }}>
              <p style={{ 
                margin: 0, 
                color: 'var(--text-secondary)', 
                fontSize: '0.9rem',
                lineHeight: 1.5,
                maxHeight: '100px',
                overflow: 'hidden',
                position: 'relative'
              }}>
                {job.description.substring(0, 300)}...
                {job.description.length > 300 && (
                  <span style={{ 
                    position: 'absolute', 
                    bottom: 0, 
                    right: 0, 
                    background: 'linear-gradient(transparent, var(--bg-glass))', 
                    padding: '0 1rem' 
                  }}>
                    <a href={job.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)' }}>
                      Read more
                    </a>
                  </span>
                )}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default JobsView;
