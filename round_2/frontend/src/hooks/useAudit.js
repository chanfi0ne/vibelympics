// PURPOSE: Custom React hook for managing package audit API calls and state
import { useState } from 'react';

export function useAudit() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const auditPackage = async (packageName) => {
    if (!packageName || !packageName.trim()) {
      setError('Package name is required');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('/api/audit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ package_name: packageName.trim() }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Audit error:', err);
      setError(err.message || 'Failed to audit package. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setLoading(false);
    setResult(null);
    setError(null);
  };

  return {
    loading,
    result,
    error,
    auditPackage,
    reset,
  };
}
