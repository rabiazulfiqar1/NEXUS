import React, { useEffect, useState } from 'react';
import {
  Target,
  TrendingUp,
  AlertTriangle,
  Download,
  Zap,
  Code2,
  Briefcase,
  FolderGit2,
  FileText,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { CareerAnalyzeResponse } from '../../services/api';
import './CareerAnalysis.css';

/* ── helpers ──────────────────────────────────────────────────────── */

function gaugeColor(pct: number): string {
  if (pct >= 80) return '#22c55e';
  if (pct >= 60) return '#22d3ee';
  if (pct >= 40) return '#f59e0b';
  return '#ef4444';
}

const CIRCUMFERENCE = 2 * Math.PI * 50; // r = 50

/* ── sub-components ──────────────────────────────────────────────── */

const AtsGauge: React.FC<{ score: number }> = ({ score }) => {
  const pct = Math.round(score * 100);
  const color = gaugeColor(pct);
  const [offset, setOffset] = useState(CIRCUMFERENCE);

  useEffect(() => {
    // trigger the animation after mount
    const raf = requestAnimationFrame(() =>
      setOffset(CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE),
    );
    return () => cancelAnimationFrame(raf);
  }, [pct]);

  return (
    <div className="ats-gauge-container">
      <div className="ats-gauge">
        <svg viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="50" className="ats-gauge-bg" />
          <circle
            cx="60"
            cy="60"
            r="50"
            className="ats-gauge-fill"
            style={{
              stroke: color,
              strokeDasharray: CIRCUMFERENCE,
              strokeDashoffset: offset,
              ['--gauge-color' as string]: color,
            }}
          />
        </svg>
        <div className="ats-gauge-label">
          <span className="ats-gauge-value" style={{ color }}>{pct}</span>
          <span className="ats-gauge-unit">ATS Score</span>
        </div>
      </div>
    </div>
  );
};

/* ── stagger variants ────────────────────────────────────────────── */

const containerVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

/* ── main component ──────────────────────────────────────────────── */

interface CareerAnalysisViewProps {
  data: CareerAnalyzeResponse;
  targetRole: string;
  onDownloadPdf: () => void;
}

const CareerAnalysisView: React.FC<CareerAnalysisViewProps> = ({
  data,
  targetRole,
  onDownloadPdf,
}) => {
  return (
    <motion.div
      className="career-analysis"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {/* ── Hero Banner ──────────────────────────────────────────── */}
      <motion.div className="career-hero" variants={itemVariants}>
        <div className="career-hero-top">
          <div className="career-hero-info">
            <h2 className="career-hero-title">
              <Target size={22} style={{ color: '#4a9eff' }} />
              Career Analysis Report
            </h2>
            <p className="career-hero-role">
              Target: <span style={{ color: '#e0e0e0' }}>{targetRole}</span>
            </p>
            <div className="career-hero-actions">
              <button className="career-btn-download" onClick={onDownloadPdf}>
                <Download size={16} /> Export CV as PDF
              </button>
            </div>
          </div>
          <AtsGauge score={data.ats_score ?? 0} />
        </div>
      </motion.div>

      {/* ── Professional Summary ──────────────────────────────────── */}
      <motion.div className="career-summary" variants={itemVariants}>
        <h4>
          <FileText size={16} style={{ color: '#4a9eff' }} /> Professional Summary
        </h4>
        <p>{data.professional_summary}</p>
      </motion.div>

      {/* ── Skills ────────────────────────────────────────────────── */}
      <motion.div className="career-section" variants={itemVariants}>
        <h4 className="career-section-header">
          <Code2 size={16} style={{ color: '#a78bfa' }} /> Skills
          <span className="section-count">{data.skills.length}</span>
        </h4>
        <div className="career-chips">
          {data.skills.map((skill, i) => (
            <motion.span
              key={skill}
              className="career-chip career-chip--skill"
              initial={{ opacity: 0, scale: 0.85 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3 + i * 0.04, duration: 0.25 }}
            >
              {skill}
            </motion.span>
          ))}
        </div>
      </motion.div>

      {/* ── Experience Bullets ────────────────────────────────────── */}
      <motion.div className="career-section" variants={itemVariants}>
        <h4 className="career-section-header">
          <Briefcase size={16} style={{ color: '#60a5fa' }} /> Experience
          <span className="section-count">{data.experience_bullets.length}</span>
        </h4>
        <ul className="career-bullets">
          {data.experience_bullets.map((bullet, idx) => (
            <motion.li
              key={idx}
              className="career-bullet"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 + idx * 0.06, duration: 0.3 }}
            >
              {bullet}
            </motion.li>
          ))}
        </ul>
      </motion.div>

      {/* ── Projects ─────────────────────────────────────────────── */}
      {data.projects.length > 0 && (
        <motion.div className="career-section" variants={itemVariants}>
          <h4 className="career-section-header">
            <FolderGit2 size={16} style={{ color: '#34d399' }} /> Projects
            <span className="section-count">{data.projects.length}</span>
          </h4>
          <ul className="career-bullets">
            {data.projects.map((project, idx) => (
              <motion.li
                key={idx}
                className="career-bullet"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 + idx * 0.06, duration: 0.3 }}
              >
                {project}
              </motion.li>
            ))}
          </ul>
        </motion.div>
      )}

      {/* ── Trending & Gaps side-by-side ──────────────────────────── */}
      <motion.div className="career-dual-grid" variants={itemVariants}>
        {/* Trending Skills Used */}
        <div className="career-section">
          <h4 className="career-section-header">
            <TrendingUp size={16} style={{ color: '#22d3ee' }} /> Trending Skills Used
            <span className="section-count">{data.trending_skills_used.length}</span>
          </h4>
          <div className="career-chips">
            {data.trending_skills_used.map((skill, i) => (
              <motion.span
                key={skill}
                className="career-chip career-chip--trending"
                initial={{ opacity: 0, scale: 0.85 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 + i * 0.05, duration: 0.25 }}
              >
                <Zap size={12} style={{ marginRight: 4 }} />
                {skill}
              </motion.span>
            ))}
          </div>
        </div>

        {/* Skill Gaps Remaining */}
        <div className="career-section">
          <h4 className="career-section-header">
            <AlertTriangle size={16} style={{ color: '#f59e0b' }} /> Skill Gaps
            <span className="section-count">{data.skill_gaps_remaining.length}</span>
          </h4>
          <div className="career-chips">
            {data.skill_gaps_remaining.map((skill, i) => (
              <motion.span
                key={skill}
                className="career-chip career-chip--gap"
                initial={{ opacity: 0, scale: 0.85 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 + i * 0.05, duration: 0.25 }}
              >
                {skill}
              </motion.span>
            ))}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default CareerAnalysisView;
