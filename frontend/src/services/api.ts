import type { AuditResponse, SyntheticScenario, AdInput } from '../types/audit';

const API_BASE = '/api';

export async function fetchHealth(): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function fetchDemoScenarios(): Promise<SyntheticScenario[]> {
  const res = await fetch(`${API_BASE}/demo`);
  if (!res.ok) {
    throw new Error('Failed to load demo scenarios');
  }
  return res.json();
}

export async function fetchDemoScenarioById(id: string): Promise<SyntheticScenario> {
  const res = await fetch(`${API_BASE}/demo/${id}`);
  if (!res.ok) {
    throw new Error(`Failed to load demo scenario '${id}'`);
  }
  return res.json();
}

export async function auditByUrl(ad: AdInput, url: string, isSynthetic: boolean = false): Promise<AuditResponse> {
  const res = await fetch(`${API_BASE}/audit/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ad,
      url,
      is_synthetic_demo: isSynthetic,
    }),
  });
  return res.json();
}

export async function auditBySnapshot(ad: AdInput, file: File): Promise<AuditResponse> {
  const formData = new FormData();
  formData.append('headline', ad.headline);
  formData.append('description', ad.description);
  if (ad.cta) {
    formData.append('cta', ad.cta);
  }
  formData.append('html_file', file);

  const res = await fetch(`${API_BASE}/audit/snapshot`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function auditGeneral(params: {
  ad: AdInput;
  url?: string;
  html_content?: string;
  is_synthetic_demo?: boolean;
}): Promise<AuditResponse> {
  const res = await fetch(`${API_BASE}/audit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  return res.json();
}

export async function exportReport(audit: AuditResponse, format: 'csv' | 'json' | 'html' | 'markdown'): Promise<string> {
  const res = await fetch(`${API_BASE}/export/${format}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(audit),
  });
  return res.text();
}
