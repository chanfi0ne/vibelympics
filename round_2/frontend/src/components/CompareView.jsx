// PURPOSE: Version comparison component showing CVE differences between two versions
import { useState } from 'react';
import { motion } from 'framer-motion';

const SEVERITY_COLORS = {
  critical: 'text-severity-critical border-severity-critical bg-severity-critical/10',
  high: 'text-severity-high border-severity-high bg-severity-high/10',
  moderate: 'text-severity-medium border-severity-medium bg-severity-medium/10',
  medium: 'text-severity-medium border-severity-medium bg-severity-medium/10',
  low: 'text-severity-low border-severity-low bg-severity-low/10',
};

function VulnBadge({ severity }) {
  const colors = SEVERITY_COLORS[severity?.toLowerCase()] || SEVERITY_COLORS.medium;
  return (
    <span className={`px-2 py-0.5 text-xs font-semibold uppercase rounded border ${colors}`}>
      {severity}
    </span>
  );
}

function VulnCard({ vuln, isFixed }) {
  return (
    <motion.div
      className={`p-3 rounded border ${isFixed ? 'border-severity-low/50 bg-severity-low/5' : 'border-accent-dim bg-secondary/30'}`}
      initial={{ opacity: 0, x: isFixed ? -20 : 20 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <VulnBadge severity={vuln.severity} />
            {isFixed && <span className="text-severity-low text-xs">FIXED</span>}
          </div>
          <p className="text-text-primary text-sm font-medium truncate">{vuln.summary}</p>
          <p className="text-text-dim text-xs mt-1">
            {vuln.cve_id || vuln.id}
            {vuln.fixed_in && <span className="ml-2">Fixed in: {vuln.fixed_in}</span>}
          </p>
        </div>
      </div>
    </motion.div>
  );
}

function VersionColumn({ analysis, label, isOld }) {
  const hasVulns = analysis.vuln_count > 0;
  
  return (
    <div className="flex-1 min-w-0">
      <div className={`text-center p-4 rounded-t border ${isOld ? 'border-severity-high/30 bg-severity-high/5' : 'border-severity-low/30 bg-severity-low/5'}`}>
        <div className="text-text-dim text-xs uppercase tracking-wider mb-1">{label}</div>
        <div className="text-accent-primary text-xl font-bold">{analysis.version}</div>
      </div>
      
      <div className="border border-t-0 border-accent-dim rounded-b p-4 space-y-3">
        <div className="grid grid-cols-2 gap-2 text-center">
          <div className="p-2 bg-secondary/30 rounded">
            <div className={`text-2xl font-bold ${hasVulns ? 'text-severity-critical' : 'text-severity-low'}`}>
              {analysis.vuln_count}
            </div>
            <div className="text-text-dim text-xs">Total CVEs</div>
          </div>
          <div className="p-2 bg-secondary/30 rounded">
            <div className="text-2xl font-bold text-severity-critical">{analysis.critical_count}</div>
            <div className="text-text-dim text-xs">Critical</div>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="p-2 bg-secondary/20 rounded">
            <div className="font-bold text-severity-high">{analysis.high_count}</div>
            <div className="text-text-dim">High</div>
          </div>
          <div className="p-2 bg-secondary/20 rounded">
            <div className="font-bold text-severity-medium">{analysis.medium_count}</div>
            <div className="text-text-dim">Medium</div>
          </div>
          <div className="p-2 bg-secondary/20 rounded">
            <div className="font-bold text-severity-low">{analysis.low_count}</div>
            <div className="text-text-dim">Low</div>
          </div>
        </div>

        {analysis.vulnerabilities?.length > 0 && (
          <div className="space-y-2 mt-4">
            <div className="text-text-dim text-xs uppercase tracking-wider">Vulnerabilities</div>
            {analysis.vulnerabilities.map((vuln) => (
              <VulnCard key={vuln.id} vuln={vuln} />
            ))}
          </div>
        )}
        
        {analysis.vuln_count === 0 && (
          <div className="text-center py-6">
            <div className="text-4xl mb-2">✅</div>
            <div className="text-severity-low font-semibold">No Known CVEs</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function CompareView({ result, onBack }) {
  if (!result) return null;

  const { old_version, new_version, vulnerabilities_fixed, risk_reduction, recommendation } = result;

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-accent-primary">Version Comparison</h2>
          <p className="text-text-dim text-sm">{result.package_name}</p>
        </div>
        <button onClick={onBack} className="btn-glow px-4 py-2 text-sm">
          Back
        </button>
      </div>

      {/* Risk Reduction Banner */}
      <motion.div
        className={`p-4 rounded-lg border-2 ${risk_reduction > 0 ? 'border-severity-low bg-severity-low/10' : 'border-accent-dim bg-secondary/30'}`}
        initial={{ scale: 0.95 }}
        animate={{ scale: 1 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <div className="text-text-dim text-xs uppercase tracking-wider mb-1">Risk Reduction</div>
            <div className={`text-3xl font-bold ${risk_reduction > 0 ? 'text-severity-low' : 'text-text-primary'}`}>
              {risk_reduction > 0 ? `−${risk_reduction}` : risk_reduction} points
            </div>
          </div>
          <div className="text-right">
            <div className="text-text-dim text-xs uppercase tracking-wider mb-1">CVEs Fixed</div>
            <div className="text-3xl font-bold text-severity-low">{vulnerabilities_fixed.length}</div>
          </div>
        </div>
        <p className="text-text-secondary text-sm mt-3 border-t border-accent-dim/30 pt-3">
          {recommendation}
        </p>
      </motion.div>

      {/* Side by Side Comparison */}
      <div className="flex gap-4">
        <VersionColumn analysis={old_version} label="Old Version" isOld={true} />
        <div className="flex items-center">
          <div className="text-accent-primary text-2xl">→</div>
        </div>
        <VersionColumn analysis={new_version} label="New Version" isOld={false} />
      </div>

      {/* Fixed Vulnerabilities List */}
      {vulnerabilities_fixed.length > 0 && (
        <motion.div
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="text-lg font-bold text-severity-low mb-4 flex items-center gap-2">
            <span>🛡️</span>
            Vulnerabilities Fixed by Upgrading
          </h3>
          <div className="space-y-2">
            {vulnerabilities_fixed.map((vuln) => (
              <VulnCard key={vuln.id} vuln={vuln} isFixed={true} />
            ))}
          </div>
        </motion.div>
      )}

      {/* Metadata */}
      <div className="text-center text-text-dim text-xs font-mono">
        Compared in {result.duration_ms}ms | {new Date(result.timestamp).toLocaleString()}
      </div>
    </motion.div>
  );
}
