import React from 'react';
import { Mail, MapPin, Link } from 'lucide-react';

interface ResumePaperProps {
  name: string;
  role: string;
  summary: string;
  bullets: string[];
  skills: string[];
  email?: string;
  linkedin?: string;
  github?: string;
  projects?: any[];
}

const ResumePaper: React.FC<ResumePaperProps> = ({ name, role, summary, bullets, skills, email, linkedin, github, projects }) => {
  return (
    <div className="resume-paper" id="resume-document">
      {/* Header */}
      <header className="resume-header">
        <h1>{name || 'YOUR NAME'}</h1>
        <h2 className="role-tag">{role}</h2>
        
        <div className="contact-info">
          <span><Mail size={12} /> {email || 'email@example.com'}</span>
          <span><Link size={12} /> {linkedin || 'linkedin.com/in/username'}</span>
          <span><Link size={12} /> {github || 'github.com/username'}</span>
        </div>
      </header>

      {/* Summary */}
      <section className="resume-section">
        <h3 className="section-heading">Professional Summary</h3>
        <p>{summary}</p>
      </section>

      {/* Skills */}
      <section className="resume-section">
        <h3 className="section-heading">Skills</h3>
        <p className="skills-list">{skills.length > 0 ? skills.join(' • ') : 'Skills will appear here...'}</p>
      </section>

      {/* Experience */}
      <section className="resume-section">
        <h3 className="section-heading">Professional Experience</h3>
        <ul className="bullets-list">
          {bullets.map((bullet, idx) => (
            <li key={idx}>{bullet}</li>
          ))}
        </ul>
      </section>

      {/* Projects */}
      {projects && projects.length > 0 && (
        <section className="resume-section">
          <h3 className="section-heading">Selected Projects</h3>
          <div style={{ display: 'grid', gap: '10px' }}>
            {projects.map((proj, idx) => (
              <div key={idx}>
                <p style={{ fontWeight: 'bold' }}>{proj.title}</p>
                <p style={{ fontSize: '12px' }}>{proj.description}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      <style>{`
        .resume-paper {
          background: white;
          color: #000;
          padding: 40px 50px;
          border: 1px solid #e2e8f0;
          width: 100%;
          max-width: 800px;
          margin: 0 auto;
          font-family: 'Times New Roman', Times, serif; /* Improved ATS default */
          line-height: 1.4;
          text-align: left;
        }

        .resume-header {
          text-align: center;
          margin-bottom: 20px;
          border-bottom: 2px solid #000;
          padding-bottom: 10px;
        }

        .resume-header h1 {
          font-size: 24px;
          margin: 0;
          text-transform: uppercase;
        }

        .role-tag {
          font-size: 14px;
          margin: 5px 0;
          font-weight: bold;
        }

        .contact-info {
          display: flex;
          justify-content: center;
          gap: 15px;
          font-size: 11px;
          flex-wrap: wrap;
        }

        .contact-info span {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .resume-section {
          margin-top: 15px;
        }

        .section-heading {
          font-size: 12px;
          text-transform: uppercase;
          border-bottom: 1px solid #000;
          padding-bottom: 2px;
          margin-bottom: 8px;
          font-weight: bold;
        }

        .resume-section p {
          font-size: 12px;
          margin: 0;
        }

        .skills-list {
          font-weight: bold;
        }

        .bullets-list {
          padding-left: 20px;
          margin: 0;
        }

        .bullets-list li {
          font-size: 12px;
          margin-bottom: 4px;
        }
      `}</style>
    </div>
  );
};

export default ResumePaper;
