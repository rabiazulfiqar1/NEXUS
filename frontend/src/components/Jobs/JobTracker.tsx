import React, { useState, useEffect } from 'react';
import {
  Bookmark,
  Send,
  MessageSquare,
  Trophy,
  XCircle,
  ChevronRight,
  Trash2,
  ShieldCheck,
  Loader2,
  ExternalLink,
  Download,
  FileText,
  ClipboardList,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { resumeApi } from '../../services/api';
import './JobTracker.css';

/* ── Types ────────────────────────────────────────────────────────── */

export type TrackerStatus = 'saved' | 'applied' | 'interview' | 'offer' | 'rejected';

export interface TrackedJob {
  id: string;
  title: string;
  company: string;
  location: string;
  url: string;
  similarity: number;
  ats_score?: number;
  status: TrackerStatus;
  added_at: string;
  notes?: string;
}

/* ── Column config ────────────────────────────────────────────────── */

const COLUMNS: { key: TrackerStatus; label: string; icon: React.ReactNode; dotClass: string }[] = [
  { key: 'saved',     label: 'Saved',      icon: <Bookmark size={14} />,        dotClass: 'status-dot--saved' },
  { key: 'applied',   label: 'Applied',    icon: <Send size={14} />,            dotClass: 'status-dot--applied' },
  { key: 'interview', label: 'Interview',  icon: <MessageSquare size={14} />,   dotClass: 'status-dot--interview' },
  { key: 'offer',     label: 'Offer',      icon: <Trophy size={14} />,          dotClass: 'status-dot--offer' },
  { key: 'rejected',  label: 'Rejected',   icon: <XCircle size={14} />,         dotClass: 'status-dot--rejected' },
];

const STATUS_ORDER: TrackerStatus[] = ['saved', 'applied', 'interview', 'offer', 'rejected'];

function nextStatus(current: TrackerStatus): TrackerStatus | null {
  const idx = STATUS_ORDER.indexOf(current);
  if (idx < 0 || idx >= STATUS_ORDER.length - 1) return null;
  return STATUS_ORDER[idx + 1];
}

/* ── localStorage helpers ─────────────────────────────────────────── */

const STORAGE_KEY = 'nexus_tracked_jobs';

function loadTracked(): TrackedJob[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveTracked(jobs: TrackedJob[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(jobs));
}

/* ── Component ────────────────────────────────────────────────────── */

interface JobTrackerProps {
  /** Jobs available from the recommendations list to add to the tracker */
  availableJobs?: any[];
}

const JobTracker: React.FC<JobTrackerProps> = ({ availableJobs = [] }) => {
  const [tracked, setTracked] = useState<TrackedJob[]>(loadTracked);
  const [atsLoading, setAtsLoading] = useState<Record<string, boolean>>({});
  const [cvExporting, setCvExporting] = useState(false);
  const [exportError, setExportError] = useState('');

  // Persist every change
  useEffect(() => {
    saveTracked(tracked);
  }, [tracked]);

  /* ── Actions ────────────────────────────────────────────────────── */

  const addJob = (job: any) => {
    if (tracked.find((t) => t.id === job.id)) return;
    const newJob: TrackedJob = {
      id: job.id,
      title: job.title,
      company: job.company,
      location: job.location || '',
      url: job.url || '',
      similarity: job.similarity || 0,
      status: 'saved',
      added_at: new Date().toISOString(),
    };
    setTracked((prev) => [...prev, newJob]);
  };

  const removeJob = (id: string) => {
    setTracked((prev) => prev.filter((j) => j.id !== id));
  };



  const advanceJob = (id: string) => {
    setTracked((prev) =>
      prev.map((j) => {
        if (j.id !== id) return j;
        const next = nextStatus(j.status);
        return next ? { ...j, status: next } : j;
      }),
    );
  };

  const fetchAtsScore = async (id: string) => {
    setAtsLoading((prev) => ({ ...prev, [id]: true }));
    try {
      const result = await resumeApi.getJobAtsScore(id);
      setTracked((prev) =>
        prev.map((j) =>
          j.id === id ? { ...j, ats_score: result.ats_score } : j,
        ),
      );
    } catch {
      // silently fail — score stays undefined
    } finally {
      setAtsLoading((prev) => ({ ...prev, [id]: false }));
    }
  };

  const handleExportCV = async () => {
    setCvExporting(true);
    setExportError('');
    try {
      const pdfBlob = await resumeApi.exportCareerCV();
      const url = window.URL.createObjectURL(pdfBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'nexus_career_cv.pdf';
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setExportError('No CV found. Run a Career Analysis first.');
      } else {
        setExportError('Failed to export CV.');
      }
    } finally {
      setCvExporting(false);
    }
  };

  /* ── Computed ───────────────────────────────────────────────────── */

  const trackedIds = new Set(tracked.map((j) => j.id));
  const untracked = availableJobs.filter((j) => !trackedIds.has(j.id));

  const getSimilarityColor = (s: number) => {
    if (s >= 0.5) return '#22c55e';
    if (s >= 0.4) return '#f59e0b';
    return '#ef4444';
  };

  const getAtsColor = (s: number) => {
    if (s >= 0.7) return '#22c55e';
    if (s >= 0.5) return '#22d3ee';
    if (s >= 0.3) return '#f59e0b';
    return '#ef4444';
  };

  /* ── Render ─────────────────────────────────────────────────────── */

  return (
    <div className="job-tracker">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="tracker-header">
        <h2>
          <ClipboardList size={22} style={{ color: '#4a9eff' }} />
          Job Tracker
        </h2>
        <div className="tracker-stats">
          {COLUMNS.map((col) => {
            const count = tracked.filter((j) => j.status === col.key).length;
            return (
              <div key={col.key} className="tracker-stat">
                <span className={`status-dot ${col.dotClass}`} />
                {col.label}: <span className="tracker-stat-value">{count}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Export Bar ──────────────────────────────────────────────── */}
      <div className="tracker-export-bar">
        <div className="tracker-export-info">
          <span className="tracker-export-title">
            <FileText size={16} style={{ color: '#4a9eff' }} />
            Career CV Export
          </span>
          <span className="tracker-export-desc">
            Download your latest AI-generated CV as a PDF
          </span>
        </div>
        <div className="tracker-export-actions">
          <button
            className="tracker-export-btn tracker-export-btn--primary"
            onClick={handleExportCV}
            disabled={cvExporting}
          >
            {cvExporting ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Download size={14} />
            )}
            {cvExporting ? 'Exporting…' : 'Export CV PDF'}
          </button>
        </div>
        {exportError && (
          <span style={{ color: '#ef4444', fontSize: '0.75rem', width: '100%' }}>
            {exportError}
          </span>
        )}
      </div>

      {/* ── Kanban Columns ─────────────────────────────────────────── */}
      <div className="tracker-columns">
        {COLUMNS.map((col) => {
          const colJobs = tracked.filter((j) => j.status === col.key);
          return (
            <div key={col.key} className="tracker-column">
              <div className="tracker-column-header">
                <span className="tracker-column-title">
                  <span className={`status-dot ${col.dotClass}`} />
                  {col.label}
                </span>
                <span className="tracker-column-badge">{colJobs.length}</span>
              </div>
              <div className="tracker-column-body">
                <AnimatePresence>
                  {colJobs.length === 0 && (
                    <div className="tracker-column-empty">No jobs</div>
                  )}
                  {colJobs.map((job) => {
                    const next = nextStatus(job.status);
                    return (
                      <motion.div
                        key={job.id}
                        className="tracker-card"
                        layout
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        transition={{ duration: 0.2 }}
                      >
                        <p className="tracker-card-title">{job.title}</p>
                        <p className="tracker-card-company">{job.company}</p>
                        <div className="tracker-card-meta">
                          <span
                            className="tracker-card-match"
                            style={{
                              background: `${getSimilarityColor(job.similarity)}18`,
                              color: getSimilarityColor(job.similarity),
                            }}
                          >
                            {(job.similarity * 100).toFixed(0)}% match
                          </span>

                          {/* ATS Score */}
                          {job.ats_score != null ? (
                            <span
                              className="ats-badge"
                              style={{
                                background: `${getAtsColor(job.ats_score)}18`,
                                color: getAtsColor(job.ats_score),
                              }}
                            >
                              <ShieldCheck size={10} style={{ marginRight: 3 }} />
                              ATS {(job.ats_score * 100).toFixed(0)}%
                            </span>
                          ) : (
                            <button
                              className="ats-score-btn"
                              onClick={() => fetchAtsScore(job.id)}
                              disabled={atsLoading[job.id]}
                              title="Compute ATS score"
                            >
                              {atsLoading[job.id] ? (
                                <Loader2 size={10} className="animate-spin" />
                              ) : (
                                <ShieldCheck size={10} />
                              )}
                              {atsLoading[job.id] ? '…' : 'ATS'}
                            </button>
                          )}
                        </div>

                        <div
                          className="tracker-card-actions"
                          style={{ marginTop: '0.5rem' }}
                        >
                          {next && (
                            <button
                              className="tracker-card-action"
                              onClick={() => advanceJob(job.id)}
                              title={`Move to ${next}`}
                            >
                              <ChevronRight size={10} /> {next}
                            </button>
                          )}
                          {job.url && (
                            <a
                              href={job.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="tracker-card-action"
                              style={{ textDecoration: 'none' }}
                              title="Open job listing"
                            >
                              <ExternalLink size={10} />
                            </a>
                          )}
                          <button
                            className="tracker-card-action tracker-card-action--remove"
                            onClick={() => removeJob(job.id)}
                            title="Remove from tracker"
                          >
                            <Trash2 size={10} />
                          </button>
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Add from recommendations ───────────────────────────────── */}
      {untracked.length > 0 && (
        <div style={{ marginTop: '0.5rem' }}>
          <h4
            style={{
              fontFamily: "'VT323', monospace",
              fontSize: '1.1rem',
              color: '#e0e0e0',
              margin: '0 0 0.75rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
          >
            <Bookmark size={16} style={{ color: '#60a5fa' }} />
            Add from Recommendations
            <span
              style={{
                fontFamily: "'Share Tech Mono', monospace",
                fontSize: '0.75rem',
                color: 'var(--text-secondary)',
                background: 'rgba(255,255,255,0.05)',
                padding: '0.1rem 0.5rem',
                borderRadius: '2px',
                marginLeft: 'auto',
              }}
            >
              {untracked.length} available
            </span>
          </h4>
          <div style={{ display: 'grid', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
            {untracked.map((job) => (
              <div
                key={job.id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.6rem 0.75rem',
                  background: 'var(--surface-glass)',
                  border: '1px solid var(--border-glass)',
                  gap: '0.75rem',
                }}
              >
                <div style={{ flex: 1, minWidth: 0 }}>
                  <p
                    style={{
                      fontFamily: "'VT323', monospace",
                      fontSize: '0.95rem',
                      color: '#e0e0e0',
                      margin: 0,
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {job.title}
                  </p>
                  <p style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', margin: '0.1rem 0 0' }}>
                    {job.company}
                  </p>
                </div>
                <span
                  style={{
                    fontSize: '0.7rem',
                    color: getSimilarityColor(job.similarity),
                    flexShrink: 0,
                  }}
                >
                  {(job.similarity * 100).toFixed(0)}%
                </span>
                <button
                  className="tracker-card-action"
                  onClick={() => addJob(job)}
                  style={{ flexShrink: 0 }}
                >
                  <Bookmark size={10} /> Save
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobTracker;
