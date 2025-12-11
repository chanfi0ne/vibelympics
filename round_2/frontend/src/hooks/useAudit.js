// PURPOSE: Custom React hook for managing package audit API calls and state
import { useState } from 'react';

export function useAudit() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const auditPackage = async (packageName, version = null) => {
    if (!packageName || !packageName.trim()) {
      setError('Package name is required');
      return;
    }

    setLoading(true);
    setError(null);
    // Don't clear result - keep showing old data while loading new version
    // This prevents the results section from unmounting/remounting

    try {
      const requestBody = { package_name: packageName.trim().toLowerCase() };
      if (version) {
        requestBody.version = version;
      }
      
      const response = await fetch('/api/audit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        // Handle error detail which may be a string or object
        let errorMessage = `HTTP error! status: ${response.status}`;
        if (errorData.detail) {
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          } else if (errorData.detail.message) {
            errorMessage = errorData.detail.message;
          } else {
            errorMessage = JSON.stringify(errorData.detail);
          }
        }
        throw new Error(errorMessage);
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
