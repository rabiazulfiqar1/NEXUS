import React, { useState } from 'react';
import { Key, Check, LogOut } from 'lucide-react';
import { authApi } from '../../services/api';

const TokenBar: React.FC = () => {
  const [token, setToken] = useState(authApi.getToken() || '');
  const [isSaved, setIsSaved] = useState(!!authApi.getToken());

  const handleSave = () => {
    if (token) {
      authApi.setToken(token);
      setIsSaved(true);
      window.location.reload(); // Refresh to apply token to interceptors
    }
  };

  const handleClear = () => {
    localStorage.removeItem('nexus_token');
    setToken('');
    setIsSaved(false);
    window.location.reload();
  };

  return (
    <div className="glass-card" style={{ padding: '0.75rem 1rem', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
      <Key size={18} color="var(--text-secondary)" />
      <input
        type="password"
        className="input-field"
        placeholder="Paste your Bearer Token here..."
        value={token}
        onChange={(e) => setToken(e.target.value)}
        disabled={isSaved}
        style={{ flex: 1, border: 'none', background: 'transparent' }}
      />
      {isSaved ? (
        <button onClick={handleClear} style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem' }}>
          <LogOut size={16} /> Logout
        </button>
      ) : (
        <button onClick={handleSave} className="btn-primary" style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>
          <Check size={16} /> Save Token
        </button>
      )}
    </div>
  );
};

export default TokenBar;
