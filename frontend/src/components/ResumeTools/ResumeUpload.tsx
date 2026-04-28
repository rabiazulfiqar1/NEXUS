import React, { useState } from 'react';
import { Upload, FileText, CheckCircle2, Loader2 } from 'lucide-react';
import { resumeApi } from '../../services/api';

const ResumeUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setSuccess(false);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      await resumeApi.upload(file);
      setSuccess(true);
      setFile(null);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Authentication required. Please log in to upload your resume.');
      } else if (err.response?.status === 413) {
        setError('File too large. Please choose a smaller PDF file.');
      } else if (err.response?.status === 400) {
        setError('Invalid file format. Please upload a PDF file.');
      } else {
        setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      }
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '0.75rem', borderRadius: '1rem' }}>
          <FileText color="var(--primary)" />
        </div>
        <div>
          <h3 style={{ fontSize: '1.1rem' }}>Knowledge Base</h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Upload your latest PDF resume to seed the AI model.</p>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <label className="btn-primary" style={{ background: 'rgba(255, 255, 255, 0.05)', border: '1px dashed var(--border-glass)', cursor: 'pointer', flex: 1, justifyContent: 'center' }}>
          <input type="file" accept=".pdf" onChange={handleFileChange} style={{ display: 'none' }} />
          {file ? file.name : 'Select PDF Resume'}
        </label>
        
        {file && (
          <button onClick={handleUpload} className="btn-primary" disabled={uploading}>
            {uploading ? <Loader2 className="animate-spin" size={18} /> : <Upload size={18} />}
            Upload
          </button>
        )}
      </div>

      {success && (
        <div style={{ marginTop: '1rem', color: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.9rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckCircle2 size={16} /> Resume processed!
          </div>
          <button 
            onClick={async () => {
              try {
                await resumeApi.deleteResume();
                setSuccess(false);
                setFile(null);
              } catch (e) {}
            }}
            style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '0.8rem' }}
          >
            Remove
          </button>
        </div>
      )}
      {error && (
        <div style={{ marginTop: '1rem', color: '#ef4444', fontSize: '0.9rem' }}>
          {error}
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
