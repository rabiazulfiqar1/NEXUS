import axios from 'axios';

import { supabase } from './supabase';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const getAuthToken = async () => {
  const { data } = await supabase.auth.getSession();
  return data.session?.access_token;
};

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds
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

export const authApi = {
  setToken: (token: string) => {
    localStorage.setItem('nexus_token', token);
  },
  getToken: () => localStorage.getItem('nexus_token'),
};

export const resumeApi = {
  enhance: async (payload: ResumeEnhanceRequest): Promise<ResumeEnhanceResponse> => {
    const response = await api.post('/resume/enhance', payload);
    return response.data;
  },
  generateCV: async (payload: CVGenerateRequest): Promise<CVGenerateResponse> => {
    const response = await api.post('/cv/generate', payload);
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
    const response = await api.post('/profile/manual', profile);
    return response.data;
  },
};

export default api;
