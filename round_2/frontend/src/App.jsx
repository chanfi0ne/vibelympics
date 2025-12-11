// PURPOSE: Main application component orchestrating package audit workflow and UI layout
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import SearchBar from './components/SearchBar';
import CompareSearch from './components/CompareSearch';
import CompareView from './components/CompareView';
import Loading from './components/Loading';
import RiskScore from './components/RiskScore';
import RiskRadar from './components/RiskRadar';
import MetadataCard from './components/MetadataCard';
import FindingsList from './components/FindingsList';
import { useAudit } from './hooks/useAudit';

export default function App() {
  const { loading, result, error, auditPackage, reset } = useAudit();
  const [showResults, setShowResults] = useState(false);
  const [mode, setMode] = useState('audit'); // 'audit' or 'compare'
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareResult, setCompareResult] = useState(null);
  const [compareError, setCompareError] = useState(null);

  const handleSearch = async (packageName, version = null) => {
    // Don't hide results when switching versions - keeps UI stable
    const isVersionSwitch = result && result.package_name === packageName;
    if (!isVersionSwitch) {
      setShowResults(false);
    }
    await auditPackage(packageName, version);
    // Show results after audit completes
    if (!showResults) {
      setTimeout(() => setShowResults(true), 100);
    }
  };

  const handleCompare = async (data) => {
    setCompareLoading(true);
    setCompareError(null);
    setCompareResult(null);

    try {
      const response = await fetch('/api/audit/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail?.message || `HTTP error ${response.status}`);
      }

      const result = await response.json();
      setCompareResult(result);
    } catch (err) {
      setCompareError(err.message || 'Failed to compare versions');
    } finally {
      setCompareLoading(false);
    }
  };

  const handleReset = () => {
    reset();
    setShowResults(false);
    setCompareResult(null);
    setCompareError(null);
  };

  const switchMode = (newMode) => {
    handleReset();
    setMode(newMode);
  };

  const isIdle = !loading && !result && !compareLoading && !compareResult;

  return (
    <div className="min-h-screen bg-void relative">
      {/* Background grid pattern */}
      <div className="fixed inset-0 grid-pattern opacity-30 pointer-events-none" />

      {/* Main content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-accent-dim bg-primary/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="container mx-auto px-4 py-6">
            <div className="flex items-center justify-between">
              <motion.div
                className="flex-1"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
              >
                <h1 className="text-3xl md:text-4xl font-bold gradient-text tracking-wider">
                  CHAINSAW
                </h1>
                <p className="text-text-dim text-xs md:text-sm mt-1 font-mono">
                  Cutting through supply chain threats
                </p>
              </motion.div>

              {(result || compareResult) && (
                <motion.button
                  onClick={handleReset}
                  className="btn-glow px-4 py-2 text-sm ml-4"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  NEW SCAN
                </motion.button>
              )}
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="container mx-auto px-4 py-8">
          {/* Mode Toggle & Search - Visible when idle */}
          {isIdle && (
            <div className="max-w-4xl mx-auto mt-12">
              <motion.div
                className="text-center mb-8"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="text-6xl mb-6">🔒</div>
                <h2 className="text-3xl font-bold text-accent-primary mb-4">
                  NPM Supply Chain Security Auditor
                </h2>
                <p className="text-text-secondary max-w-2xl mx-auto leading-relaxed mb-8">
                  Analyze npm packages for supply chain security threats. Our multi-dimensional
                  risk assessment scans for authenticity, maintenance, security, and reputation indicators.
                </p>

                {/* Mode Toggle */}
                <div className="inline-flex rounded-lg border border-accent-dim p-1 mb-8">
                  <button
                    onClick={() => switchMode('audit')}
                    className={`px-6 py-2 rounded-md text-sm font-semibold transition-all ${
                      mode === 'audit'
                        ? 'bg-accent-primary text-void'
                        : 'text-text-secondary hover:text-accent-primary'
                    }`}
                  >
                    Deep Inspection
                  </button>
                  <button
                    onClick={() => switchMode('compare')}
                    className={`px-6 py-2 rounded-md text-sm font-semibold transition-all ${
                      mode === 'compare'
                        ? 'bg-accent-primary text-void'
                        : 'text-text-secondary hover:text-accent-primary'
                    }`}
                  >
                    Compare Versions
                  </button>
                </div>
              </motion.div>

              {/* Search Forms */}
              <AnimatePresence mode="wait">
                {mode === 'audit' ? (
                  <motion.div
                    key="audit-search"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                  >
                    <SearchBar onSearch={handleSearch} loading={loading} />
                  </motion.div>
                ) : (
                  <motion.div
                    key="compare-search"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                  >
                    <CompareSearch onCompare={handleCompare} loading={compareLoading} />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}

          {/* Loading State */}
          <AnimatePresence mode="wait">
            {(loading || compareLoading) && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <Loading />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error State */}
          <AnimatePresence mode="wait">
            {(error || compareError) && !loading && !compareLoading && (
              <motion.div
                key="error"
                className="max-w-2xl mx-auto mt-12"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
              >
                <div className="card border-2 border-severity-critical">
                  <div className="flex items-start space-x-4">
                    <div className="text-4xl">⚠️</div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-severity-critical mb-2">
                        {mode === 'compare' ? 'Comparison Failed' : 'Inspection Failed'}
                      </h3>
                      <p className="text-text-secondary mb-4">{error || compareError}</p>
                      <button
                        onClick={handleReset}
                        className="btn-glow px-6 py-2"
                      >
                        Try Again
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Compare Results */}
          <AnimatePresence mode="wait">
            {compareResult && (
              <motion.div
                key="compare-results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <CompareView result={compareResult} onBack={handleReset} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Audit Results */}
          <AnimatePresence mode="wait">
            {result && showResults && (
              <motion.div
                key="results"
                className="space-y-8 relative"
                initial={{ opacity: 0 }}
                animate={{ opacity: loading ? 0.6 : 1 }}
                transition={{ duration: 0.2 }}
                exit={{ opacity: 0 }}
              >
                {/* Loading overlay for version switches */}
                {loading && (
                  <div className="absolute inset-0 flex items-center justify-center z-50 bg-void/50 backdrop-blur-sm rounded-lg">
                    <div className="text-accent-primary text-lg font-mono animate-pulse">
                      Loading version...
                    </div>
                  </div>
                )}
                {/* Package Name Header with Version Picker */}
                <motion.div
                  className="text-center"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-3xl font-bold text-accent-primary mb-2">
                    Inspection Results
                  </h2>
                  <div className="flex items-center justify-center gap-2 flex-wrap">
                    <span className="text-text-primary font-semibold text-lg">{result.package_name}</span>
                    <span className="text-text-dim">@</span>
                    {/* Version Picker */}
                    <select
                      value={result.version}
                      onChange={(e) => handleSearch(result.package_name, e.target.value)}
                      className="bg-secondary border border-accent-dim rounded px-3 py-1 text-accent-primary font-mono text-sm focus:border-accent-primary focus:outline-none cursor-pointer"
                      disabled={loading}
                    >
                      {(result.available_versions || [result.version]).map((v) => (
                        <option key={v} value={v}>{v}</option>
                      ))}
                    </select>
                  </div>
                  
                  {/* Historical CVEs Badge */}
                  {result.historical_cves_fixed > 0 && (
                    <motion.div
                      className="mt-3 inline-flex items-center gap-2 px-4 py-2 rounded-full border border-severity-low/50 bg-severity-low/10"
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.2 }}
                    >
                      <span className="text-severity-low text-lg">✓</span>
                      <span className="text-severity-low text-sm font-medium">
                        {result.historical_cves_fixed} historical CVE{result.historical_cves_fixed !== 1 ? 's' : ''} fixed in this version
                      </span>
                    </motion.div>
                  )}
                </motion.div>

                {/* Risk Score - Full Width */}
                <RiskScore
                  score={result.risk_score}
                  severity={result.risk_level}
                  factors={result.factors || []}
                />

                {/* Two Column Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Left Column */}
                  <div className="space-y-8">
                    {result.radar_scores && (
                      <RiskRadar scores={result.radar_scores} />
                    )}
                  </div>

                  {/* Right Column */}
                  <div className="space-y-8">
                    <MetadataCard
                      metadata={{
                        ...result.metadata,
                        name: result.package_name,
                        version: result.version,
                      }}
                    />
                  </div>
                </div>

                {/* Findings - Full Width */}
                {result.factors && result.factors.length > 0 && (
                  <FindingsList findings={result.factors} />
                )}

                {/* No Findings Message */}
                {(!result.factors || result.factors.length === 0) && (
                  <motion.div
                    className="card text-center py-12"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.8 }}
                  >
                    <div className="text-6xl mb-4">✅</div>
                    <h3 className="text-2xl font-bold text-severity-low mb-2">
                      No Security Issues Found
                    </h3>
                    <p className="text-text-secondary max-w-md mx-auto">
                      This package passed all security checks with no significant concerns detected.
                    </p>
                  </motion.div>
                )}

                {/* Audit Metadata */}
                <motion.div
                  className="text-center text-text-dim text-xs font-mono mt-12"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1 }}
                >
                  {result.audit_duration_ms && (
                    <p>Scanned in {result.audit_duration_ms}ms</p>
                  )}
                  {result.timestamp && (
                    <p className="mt-1">
                      {new Date(result.timestamp).toLocaleString()}
                    </p>
                  )}
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* Footer */}
        <footer className="border-t border-accent-dim bg-primary/80 backdrop-blur-sm mt-20">
          <div className="container mx-auto px-4 py-6">
            <div className="flex flex-col md:flex-row items-center justify-between text-text-dim text-sm">
              <div className="flex items-center space-x-4 mb-4 md:mb-0">
                <span>© 2025 Chainsaw</span>
                <span className="hidden md:inline">|</span>
                <span className="text-accent-primary">Vibelympics Round 2</span>
              </div>
              <div className="flex items-center space-x-4">
                <a
                  href="https://github.com/vibelympics/round_2"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-accent-primary transition-colors"
                >
                  GitHub
                </a>
                <span>|</span>
                <span className="text-xs">Built with React + FastAPI</span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
