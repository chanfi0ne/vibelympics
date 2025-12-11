// PURPOSE: Main application component orchestrating package audit workflow and UI layout
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import SearchBar from './components/SearchBar';
import Loading from './components/Loading';
import RiskScore from './components/RiskScore';
import RiskRadar from './components/RiskRadar';
import MetadataCard from './components/MetadataCard';
import FindingsList from './components/FindingsList';
import { useAudit } from './hooks/useAudit';

export default function App() {
  const { loading, result, error, auditPackage, reset } = useAudit();
  const [showResults, setShowResults] = useState(false);

  const handleSearch = async (packageName) => {
    setShowResults(false);
    await auditPackage(packageName);
    if (!error) {
      setTimeout(() => setShowResults(true), 100);
    }
  };

  const handleReset = () => {
    reset();
    setShowResults(false);
  };

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
                  REPOJACKER
                </h1>
                <p className="text-text-dim text-xs md:text-sm mt-1 font-mono">
                  Detect supply chain threats before they detect you
                </p>
              </motion.div>

              {result && (
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
          {/* Search Bar - Always Visible */}
          {!loading && !result && (
            <div className="max-w-4xl mx-auto mt-20">
              <motion.div
                className="text-center mb-12"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
              >
                <div className="text-6xl mb-6">🔒</div>
                <h2 className="text-3xl font-bold text-accent-primary mb-4">
                  NPM Supply Chain Security Auditor
                </h2>
                <p className="text-text-secondary max-w-2xl mx-auto leading-relaxed">
                  Analyze npm packages for supply chain security threats. Our multi-dimensional
                  risk assessment scans for authenticity, maintenance, security, and reputation indicators.
                </p>
              </motion.div>
              <SearchBar onSearch={handleSearch} loading={loading} />
            </div>
          )}

          {/* Loading State */}
          <AnimatePresence mode="wait">
            {loading && (
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
            {error && !loading && (
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
                        Audit Failed
                      </h3>
                      <p className="text-text-secondary mb-4">{error}</p>
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

          {/* Results */}
          <AnimatePresence mode="wait">
            {result && showResults && (
              <motion.div
                key="results"
                className="space-y-8"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                {/* Package Name Header */}
                <motion.div
                  className="text-center"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                >
                  <h2 className="text-3xl font-bold text-accent-primary mb-2">
                    Audit Results
                  </h2>
                  <p className="text-text-dim">
                    Package: <span className="text-text-primary font-semibold">{result.package_name}</span>
                  </p>
                </motion.div>

                {/* Risk Score - Full Width */}
                <RiskScore
                  score={result.risk_score}
                  severity={result.risk_level}
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
                {result.audit_id && (
                  <motion.div
                    className="text-center text-text-dim text-xs font-mono mt-12"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 1 }}
                  >
                    <p>Audit ID: {result.audit_id}</p>
                    {result.timestamp && (
                      <p className="mt-1">
                        Completed: {new Date(result.timestamp).toLocaleString()}
                      </p>
                    )}
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </main>

        {/* Footer */}
        <footer className="border-t border-accent-dim bg-primary/80 backdrop-blur-sm mt-20">
          <div className="container mx-auto px-4 py-6">
            <div className="flex flex-col md:flex-row items-center justify-between text-text-dim text-sm">
              <div className="flex items-center space-x-4 mb-4 md:mb-0">
                <span>© 2025 Repojacker</span>
                <span className="hidden md:inline">|</span>
                <span className="text-accent-primary">0 CVEs</span>
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
