import React, { useState } from 'react';
import { Download, AlertCircle, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';
import { ResumeEnhanceResponse, CVGenerateResponse } from '../../services/api';
import ResumePaper from './ResumePaper';
import jsPDF from 'jspdf';
import { motion, AnimatePresence } from 'framer-motion';

interface ResultsViewProps {
  data: ResumeEnhanceResponse | CVGenerateResponse;
  profileOverride: any;
  isCV?: boolean;
}

const ResultsView: React.FC<ResultsViewProps> = ({ data, profileOverride, isCV = false }) => {
  const [showAnalysis, setShowAnalysis] = useState(false);

  const exportToPDF = () => {
    const doc = new jsPDF('p', 'mm', 'a4');
    const margin = 20;
    const pageWidth = doc.internal.pageSize.getWidth();
    let y = 20;

    // Strict Black & White for ATS
    doc.setTextColor(0, 0, 0);

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(20);
    const name = profileOverride?.full_name || 'NAME';
    doc.text(name.toUpperCase(), pageWidth / 2, y, { align: 'center' });
    y += 8;

    doc.setFontSize(11);
    doc.setFont('helvetica', 'bold');
    doc.text(data.target_role.toUpperCase(), pageWidth / 2, y, { align: 'center' });
    y += 8;

    doc.setFontSize(9);
    doc.setFont('helvetica', 'normal');
    const contactLine = `${profileOverride?.email || 'email@example.com'}  |  ${profileOverride?.linkedin_url || 'linkedin.com'}  |  ${profileOverride?.github_url || 'github.com'}`;
    doc.text(contactLine, pageWidth / 2, y, { align: 'center' });
    y += 4;
    
    doc.setDrawColor(0, 0, 0);
    doc.setLineWidth(0.3);
    doc.line(margin, y, pageWidth - margin, y);
    y += 10;

    const addSectionHeader = (title: string) => {
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(10);
      doc.text(title.toUpperCase(), margin, y);
      y += 1.5;
      doc.line(margin, y, pageWidth - margin, y);
      y += 6;
    };

    // Professional Summary / CV Professional Summary
    addSectionHeader('Professional Summary');
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    const summaryText = isCV ? (data as CVGenerateResponse).professional_summary : (data as ResumeEnhanceResponse).summary;
    const summaryLines = doc.splitTextToSize(summaryText, pageWidth - 2 * margin);
    doc.text(summaryLines, margin, y);
    y += summaryLines.length * 4.5 + 8;

    // Skills
    addSectionHeader('Skills');
    const skillsText = isCV ? (data as CVGenerateResponse).skills.join('  •  ') : (profileOverride?.skills || []).join('  •  ');
    doc.setFont('helvetica', 'bold');
    const skillLines = doc.splitTextToSize(skillsText, pageWidth - 2 * margin);
    doc.text(skillLines, margin, y);
    y += skillLines.length * 5 + 8;

    // Experience / Experience Bullets
    addSectionHeader('Professional Experience');
    doc.setFont('helvetica', 'normal');
    const bullets = isCV ? (data as CVGenerateResponse).experience_bullets : (data as ResumeEnhanceResponse).improved_bullets;
    bullets.forEach((bullet) => {
      const lines = doc.splitTextToSize(`•  ${bullet}`, pageWidth - 2 * margin - 5);
      if (y + lines.length * 5 > 280) { doc.addPage(); y = 20; }
      doc.text(lines, margin, y);
      y += lines.length * 4.5 + 2;
    });
    
    // Projects (CV only)
    if (isCV && (data as CVGenerateResponse).projects.length > 0) {
      y += 5;
      addSectionHeader('Selected Projects');
      (data as CVGenerateResponse).projects.forEach((proj: string) => {
        doc.setFont('helvetica', 'normal');
        const projLines = doc.splitTextToSize(`•  ${proj}`, pageWidth - 2 * margin - 5);
        if (y + projLines.length * 5 > 280) { doc.addPage(); y = 20; }
        doc.text(projLines, margin, y);
        y += projLines.length * 4.5 + 2;
      });
    }

    doc.save(`${name.replace(/\s+/g, '_')}_${isCV ? 'CV' : 'Resume'}.pdf`);
  };

  return (
    <div style={{ display: 'grid', gap: '2rem' }}>
      <section className="glass-card" style={{ padding: '3rem 1rem', textAlign: 'center', position: 'relative' }}>
        <div style={{ position: 'absolute', top: '1.5rem', left: '1.5rem' }}>
          <button onClick={exportToPDF} className="btn-primary" style={{ background: '#000', color: '#fff', border: 'none' }}>
            <Download size={18} /> Download ATS {isCV ? 'CV' : 'Resume'} PDF (B&W)
          </button>
        </div>
        
        <ResumePaper 
          name={profileOverride?.full_name}
          email={profileOverride?.email}
          linkedin={profileOverride?.linkedin_url}
          github={profileOverride?.github_url}
          role={data.target_role}
          summary={isCV ? (data as CVGenerateResponse).professional_summary : (data as ResumeEnhanceResponse).summary}
          bullets={isCV ? (data as CVGenerateResponse).experience_bullets : (data as ResumeEnhanceResponse).improved_bullets}
          skills={isCV ? (data as CVGenerateResponse).skills : (profileOverride?.skills || [])}
        />
      </section>

      <div style={{ textAlign: 'center' }}>
        <button 
          onClick={() => setShowAnalysis(!showAnalysis)}
          style={{ background: 'transparent', border: '1px solid var(--border-glass)', borderRadius: '2rem', padding: '0.5rem 1.5rem', color: 'var(--text-secondary)', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
        >
          {showAnalysis ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
          {showAnalysis ? 'Hide AI Analysis' : 'Show Strength Analysis'}
        </button>
      </div>

      <AnimatePresence>
        {showAnalysis && !isCV && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="grid" 
            style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}
          >
            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <h4 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <AlertCircle size={20} color="#f59e0b" /> Optimization Gaps
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {(data as ResumeEnhanceResponse).missing_keywords.map((kw, idx) => (
                  <span key={idx} style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#fbbf24', padding: '0.4rem 0.8rem', borderRadius: '2rem', fontSize: '0.85rem', border: '1px solid rgba(245, 158, 11, 0.2)' }}>
                    {kw}
                  </span>
                ))}
              </div>
            </div>

            <div className="glass-card" style={{ padding: '1.5rem' }}>
              <h4 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
                <TrendingUp size={20} color="#22d3ee" /> Next Steps
              </h4>
              <ul style={{ listStyle: 'none', display: 'grid', gap: '0.75rem' }}>
                {(data as ResumeEnhanceResponse).next_steps.map((step, idx) => (
                  <li key={idx} style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.5rem' }}>
                    <span style={{ color: '#22d3ee' }}>→</span> {step}
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ResultsView;
