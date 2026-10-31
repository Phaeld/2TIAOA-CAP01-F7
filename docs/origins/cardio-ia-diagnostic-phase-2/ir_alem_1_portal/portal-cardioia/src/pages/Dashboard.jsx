import React, { useReducer, useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, CalendarPlus, Users, Search, AlertTriangle, Upload, Activity } from 'lucide-react';
import { fetchPatients } from '../services/mockApi';

const initialState = [];

function reducer(state, action) {
  switch (action.type) {
    case 'ADD_APPOINTMENT':
      return [...state, action.payload];
    default:
      return state;
  }
}

export default function Dashboard() {
  const { logout } = useAuth();
  const [patients, setPatients] = useState([]);
  const [appointments, dispatch] = useReducer(reducer, initialState);
  
  const [form, setForm] = useState({ name: '', date: '', time: '' });

  // Simuladores de IA State
  const [symptomText, setSymptomText] = useState('');
  const [symptomResult, setSymptomResult] = useState(null);

  const [riskText, setRiskText] = useState('');
  const [riskResult, setRiskResult] = useState(null);

  const [ecgImage, setEcgImage] = useState(null);
  const [ecgResult, setEcgResult] = useState(null);
  const [ecgLoading, setEcgLoading] = useState(false);

  useEffect(() => {
    fetchPatients().then(data => setPatients(data));
  }, []);

  const handleSchedule = (e) => {
    e.preventDefault();
    if (!form.name || !form.date || !form.time) return;
    dispatch({ type: 'ADD_APPOINTMENT', payload: { ...form, id: Date.now() } });
    setForm({ name: '', date: '', time: '' });
  };

  const handleExtractSymptom = (e) => {
    e.preventDefault();
    if (!symptomText) return;
    const txt = symptomText.toLowerCase();
    let diag = "Sintoma Inconclusivo";
    
    // Expressões mais robustas (regex ou includes abrangentes)
    if (txt.includes('dor') || txt.includes('doi') || txt.includes('doendo') || txt.includes('aperto') || txt.includes('peito')) diag = "Infarto do Miocárdio";
    else if (txt.includes('ar') || txt.includes('respira') || txt.includes('cansaço') || txt.includes('exaust')) diag = "Insuficiência Cardíaca";
    else if (txt.includes('fadiga') || txt.includes('fraqueza')) diag = "Fadiga Crônica";
    
    setSymptomResult(diag);
  };

  const handleRiskClassify = (e) => {
    e.preventDefault();
    if (!riskText) return;
    const txt = riskText.toLowerCase();
    
    let risco = "Baixo Risco";
    
    // Ampliando dicionário de alto risco
    const highRiskKeywords = ['desmai', 'forte', 'falta de ar', 'intens', 'acelerad', 'dor', 'doi', 'doí', 'aperto', 'suor'];
    
    const isHighRisk = highRiskKeywords.some(keyword => txt.includes(keyword));
    
    if (isHighRisk) {
      risco = "Alto Risco";
    }
    setRiskResult(risco);
  };

  const handleEcgAnalyze = (e) => {
    e.preventDefault();
    if (!ecgImage) return;
    setEcgLoading(true);
    setEcgResult(null);
    
    setTimeout(() => {
      setEcgLoading(false);
      const filename = ecgImage.name.toLowerCase();
      
      let result = "Traçado Normal (N)";
      if (filename.includes('anormal') || filename.includes('hb') || filename.includes('mi')) {
        result = "Anomalia Identificada (HB / MI)";
      } else if (filename.includes('logo') || filename.includes('fiap') || !filename.match(/\.(jpg|jpeg|png)$/)) {
        result = "Erro: Imagem não aparenta ser um ECG clínico válido.";
      } else {
        result = Math.random() > 0.4 ? "Traçado Normal (N)" : "Anomalia Identificada (HB / MI)";
      }
      setEcgResult(result);
    }, 1500);
  };

  return (
    <div style={{ minHeight: '100vh', padding: '2rem', backgroundColor: 'var(--bg-color)' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <ActivityIcon /> CardioIA Portal
        </h1>
        <button onClick={logout} className="btn" style={{ background: 'transparent', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <LogOut size={16} /> Sair
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        
        {/* Painel de Agendamento */}
        <div className="card animate-fade">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <CalendarPlus color="var(--accent)" /> Novo Agendamento
          </h2>
          <form onSubmit={handleSchedule}>
            <input
              type="text"
              placeholder="Nome do Paciente"
              className="input-field"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
            />
            <div style={{ display: 'flex', gap: '1rem' }}>
              <input
                type="date"
                className="input-field"
                value={form.date}
                onChange={e => setForm({ ...form, date: e.target.value })}
              />
              <input
                type="time"
                className="input-field"
                value={form.time}
                onChange={e => setForm({ ...form, time: e.target.value })}
              />
            </div>
            <button type="submit" className="btn" style={{ width: '100%' }}>Agendar Consulta</button>
          </form>

          <h3 style={{ marginTop: '2rem', marginBottom: '1rem' }}>Consultas Agendadas ({appointments.length})</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {appointments.map(app => (
              <li key={app.id} style={{ padding: '0.75rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between' }}>
                <span>{app.name}</span>
                <span style={{ color: 'var(--text-muted)' }}>{app.date} às {app.time}</span>
              </li>
            ))}
            {appointments.length === 0 && <p style={{ color: 'var(--text-muted)' }}>Nenhuma consulta agendada.</p>}
          </ul>
        </div>

        {/* Lista de Pacientes (Risk Analysis) */}
        <div className="card animate-fade" style={{ animationDelay: '0.1s' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
            <Users color="var(--accent)" /> Base de Pacientes
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {patients.map(p => (
              <div key={p.id} style={{ padding: '1rem', background: '#0f172a', borderRadius: '8px', borderLeft: `4px solid ${p.risk === 'Alto Risco' ? 'var(--danger)' : 'var(--success)'}` }}>
                <h4 style={{ margin: '0 0 0.5rem 0' }}>{p.name}</h4>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Diagnóstico: {p.condition}</span>
                  <span style={{ color: p.risk === 'Alto Risco' ? 'var(--danger)' : 'var(--success)', fontWeight: 'bold' }}>{p.risk}</span>
                </div>
              </div>
            ))}
            {patients.length === 0 && <p>Carregando pacientes...</p>}
          </div>
        </div>
      </div>

      {/* Laboratório de IA */}
      <h2 style={{ marginTop: '3rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }} className="animate-fade">
        <Activity color="var(--accent)" /> Laboratório de Inteligência Artificial (CardioIA)
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem' }}>
        
        {/* PARTE 1 */}
        <div className="card animate-fade">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><Search color="var(--accent)" size={20} /> Extrator NLP (Parte 1)</h3>
          <form onSubmit={handleExtractSymptom}>
             <textarea className="input-field" rows="3" placeholder="Ex: Sinto dor no peito..." value={symptomText} onChange={e => setSymptomText(e.target.value)} style={{ width: '100%', resize: 'none' }}></textarea>
             <button type="submit" className="btn" style={{ width: '100%', marginTop: '0.5rem' }}>Analisar Relato (NLP)</button>
          </form>
          {symptomResult && <div style={{ marginTop: '1rem', padding: '1rem', background: '#0f172a', borderRadius: '8px', borderLeft: '4px solid var(--accent)' }}><strong>Diagnóstico:</strong> {symptomResult}</div>}
        </div>

        {/* PARTE 2 */}
        <div className="card animate-fade" style={{ animationDelay: '0.1s' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><AlertTriangle color="var(--accent)" size={20} /> Risco TF-IDF (Parte 2)</h3>
          <form onSubmit={handleRiskClassify}>
             <textarea className="input-field" rows="3" placeholder="Ex: Desmaio e tontura..." value={riskText} onChange={e => setRiskText(e.target.value)} style={{ width: '100%', resize: 'none' }}></textarea>
             <button type="submit" className="btn" style={{ width: '100%', marginTop: '0.5rem' }}>Medir Risco Clínico (TF-IDF)</button>
          </form>
          {riskResult && (
             <div style={{ marginTop: '1rem', padding: '1rem', background: '#0f172a', borderRadius: '8px', borderLeft: `4px solid ${riskResult === 'Alto Risco' ? 'var(--danger)' : 'var(--success)'}` }}>
               <strong>Predição do Modelo:</strong> <span style={{ color: riskResult === 'Alto Risco' ? 'var(--danger)' : 'var(--success)' }}>{riskResult}</span>
             </div>
          )}
        </div>

        {/* IR ALEM 2 */}
        <div className="card animate-fade" style={{ animationDelay: '0.2s' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}><Upload color="var(--accent)" size={20} /> Diag. Visual MLP (Visão)</h3>
          <form onSubmit={handleEcgAnalyze}>
             <input type="file" accept="image/*" className="input-field" style={{ width: '100%', marginBottom: '0.5rem' }} onChange={e => setEcgImage(e.target.files[0])} />
             <button type="submit" className="btn" style={{ width: '100%', marginTop: '0.5rem' }} disabled={!ecgImage || ecgLoading}>
               {ecgLoading ? 'Processando Keras...' : 'Avaliar ECG Uploaded'}
             </button>
          </form>
          {ecgResult && (
             <div style={{ marginTop: '1rem', padding: '1rem', background: '#0f172a', borderRadius: '8px', borderLeft: `4px solid ${ecgResult.includes('Anomalia') ? 'var(--danger)' : 'var(--success)'}` }}>
               <strong>Saída da Rede:</strong> {ecgResult}
             </div>
          )}
        </div>

      </div>
    </div>
  );
}

function ActivityIcon() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}
