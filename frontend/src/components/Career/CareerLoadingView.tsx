import React, { useEffect, useState } from 'react';
import {
  User,
  BarChart3,
  PenTool,
  FileCheck,
  Check,
  Loader2,
  Clock,
} from 'lucide-react';
import { motion } from 'framer-motion';
import './CareerAnalysis.css';

const AGENTS = [
  {
    name: 'Profile Analyst',
    desc: 'Fetching profile & computing ATS scores…',
    icon: User,
    durationMs: 8000,
  },
  {
    name: 'Market Researcher',
    desc: 'Analysing trending skills for target role…',
    icon: BarChart3,
    durationMs: 10000,
  },
  {
    name: 'Resume Enhancer',
    desc: 'Rewriting bullets & surfacing gaps…',
    icon: PenTool,
    durationMs: 12000,
  },
  {
    name: 'CV Generator',
    desc: 'Assembling tailored CV document…',
    icon: FileCheck,
    durationMs: 8000,
  },
];

const TOTAL_DURATION = AGENTS.reduce((s, a) => s + a.durationMs, 0);

const CareerLoadingView: React.FC = () => {
  const [activeIdx, setActiveIdx] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsed((prev) => {
        const next = prev + 200;
        let cumulative = 0;
        for (let i = 0; i < AGENTS.length; i++) {
          cumulative += AGENTS[i].durationMs;
          if (next < cumulative) {
            setActiveIdx(i);
            break;
          }
          if (i === AGENTS.length - 1) setActiveIdx(AGENTS.length - 1);
        }
        return next;
      });
    }, 200);

    return () => clearInterval(interval);
  }, []);

  const progressPct = Math.min((elapsed / TOTAL_DURATION) * 100, 98);

  return (
    <motion.div
      className="career-loading"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.35 }}
    >
      <h3 className="career-loading-title">
        <Loader2 size={20} className="animate-spin" style={{ marginRight: 8, color: '#4a9eff' }} />
        Running Career Analysis
      </h3>
      <p className="career-loading-subtitle">
        CrewAI agents are analysing your profile. This may take 30–60 seconds.
      </p>

      <div className="career-agents">
        {AGENTS.map((agent, idx) => {
          const isDone = idx < activeIdx;
          const isActive = idx === activeIdx;
          const statusClass = isDone
            ? 'career-agent-step--done'
            : isActive
            ? 'career-agent-step--active'
            : '';
          const iconClass = isDone
            ? 'career-agent-icon--done'
            : isActive
            ? 'career-agent-icon--active'
            : 'career-agent-icon--pending';

          return (
            <motion.div
              key={agent.name}
              className={`career-agent-step ${statusClass}`}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.1, duration: 0.3 }}
            >
              <div className={`career-agent-icon ${iconClass}`}>
                {isDone ? <Check size={16} /> : isActive ? <Loader2 size={16} className="animate-spin" /> : <Clock size={14} />}
              </div>
              <div className="career-agent-info">
                <p className="career-agent-name">{agent.name}</p>
                <p className="career-agent-desc">
                  {isDone ? 'Completed' : isActive ? agent.desc : 'Waiting…'}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="career-progress-bar">
        <div
          className="career-progress-fill"
          style={{ width: `${progressPct}%` }}
        />
      </div>
    </motion.div>
  );
};

export default CareerLoadingView;
