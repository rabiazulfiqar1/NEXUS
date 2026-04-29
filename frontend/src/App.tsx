import { useState, useEffect } from 'react'
import ResumeTools from './components/ResumeTools/ResumeTools'
import Login from './components/Login'
import { supabase } from './services/supabase'
import { Session } from '@supabase/supabase-js'
import './App.css'

function App() {
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })

    return () => subscription.unsubscribe()
  }, [])

  if (loading) {
    return <div className="loading-screen">Loading NEXUS...</div>
  }

  return (
    <div className="App">
      <div className="bg-glow"></div>
      
      <main>
        {session ? <ResumeTools /> : <Login />}
      </main>

      <footer style={{ textAlign: 'center', padding: '4rem 2rem', color: 'var(--text-secondary)', fontSize: '0.9rem', borderTop: '1px solid var(--border-glass)', marginTop: '4rem' }}>
        <p>© 2026 NEXUS AI. Powered by Groq Inference Engine.</p>
      </footer>
    </div>
  )
}

export default App
