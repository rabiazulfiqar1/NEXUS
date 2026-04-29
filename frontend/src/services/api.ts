import axios from 'axios';

import { supabase } from './supabase';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const getAuthToken = async () => {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token;
};

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 180 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(async (config) => {
  const token = await getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface ResumeEnhanceRequest {
  resume_text?: string;
  target_role: string;
}

export interface ResumeEnhanceResponse {
  mode: string;
  target_role: string;
  summary: string;
  improved_bullets: string[];
  missing_keywords: string[];
  next_steps: string[];
}

export interface CVGenerateRequest {
  target_role: string;
}

export interface CVGenerateResponse {
  mode: string;
  target_role: string;
  professional_summary: string;
  skills: string[];
  experience_bullets: string[];
  projects: string[];
}

export interface CareerAnalyzeResponse {
  professional_summary: string;
  skills: string[];
  experience_bullets: string[];
  projects: string[];
  ats_score: number;
  trending_skills_used: string[];
  skill_gaps_remaining: string[];
}

export interface CareerAnalyzeStartResponse {
  job_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
}

export interface CareerAnalyzeStatusResponse {
  job_id?: string;
  status: 'queued' | 'running' | 'completed' | 'failed';
  target_role?: string;
  result?: CareerAnalyzeResponse;
  error?: string;
}

export const authApi = {
  setToken: (token: string) => {
    localStorage.setItem('nexus_token', token);
  },
  getToken: () => localStorage.getItem('nexus_token'),
};

export interface AtsScoreResponse {
  job_id: string;
  ats_score: number;
}

export const resumeApi = {
  enhance: async (payload: ResumeEnhanceRequest): Promise<ResumeEnhanceResponse> => {
    const response = await api.post('/resume/enhance', payload);
    return response.data;
  },
  generateCV: async (payload: CVGenerateRequest): Promise<CVGenerateResponse> => {
    const response = await api.post('/cv/generate', payload);
    return response.data;
  },
  careerAnalyze: async (targetRole: string): Promise<CareerAnalyzeStartResponse> => {
    const response = await api.post('/career/analyze', null, {
      params: { target_role: targetRole },
    });
    return response.data;
  },
  careerAnalyzeStatus: async (jobId: string): Promise<CareerAnalyzeStatusResponse> => {
    const response = await api.get(`/career/analyze/${jobId}`);
    return response.data;
  },
  getLatestCareerCV: async (): Promise<CareerAnalyzeResponse> => {
    const response = await api.get('/career/cv/latest');
    return response.data;
  },
  exportCareerCV: async (): Promise<Blob> => {
    const response = await api.get('/career/cv/export', {
      responseType: 'blob',
    });
    return response.data;
  },
  getJobs: async (): Promise<any[]> => {
    const response = await api.get('/jobs');
    return response.data;
  },
  getTargetedJobs: async (targetRole: string): Promise<any[]> => {
    const response = await api.get(`/jobs?target_role=${encodeURIComponent(targetRole)}`);
    return response.data;
  },
  getJobAtsScore: async (jobId: string): Promise<AtsScoreResponse> => {
    const response = await api.get(`/jobs/${jobId}/ats-score`);
    return response.data;
  },
  upload: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/profile/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  getProfile: async (): Promise<any> => {
    const response = await api.get('/profile');
    return response.data;
  },
  deleteResume: async (): Promise<any> => {
    const response = await api.delete('/profile/resume');
    return response.data;
  },
  saveProfile: async (profile: any): Promise<any> => {
    const { email, ...payload } = profile || {};
    const response = await api.post('/profile/manual', payload);
    return response.data;
  },
};

export default api;
