// PURPOSE: Animated risk score display component with severity-based colors and glow effects
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

const SEVERITY_CONFIG = {
  CRITICAL: {
    label: 'CRITICAL',
    color: 'text-severity-critical',
    glow: 'text-glow-critical',
    shadow: 'shadow-critical',
    bg: 'bg-severity-critical/10',
    border: 'border-severity-critical',
    gradient: 'from-severity-critical/20 to-transparent'
  },
  HIGH: {
    label: 'HIGH RISK',
    color: 'text-severity-high',
    glow: 'text-glow-high',
    shadow: 'shadow-high',
    bg: 'bg-severity-high/10',
    border: 'border-severity-high',
    gradient: 'from-severity-high/20 to-transparent'
  },
  MEDIUM: {
    label: 'MEDIUM RISK',
    color: 'text-severity-medium',
    glow: 'text-glow-medium',
    shadow: 'shadow-medium',
    bg: 'bg-severity-medium/10',
    border: 'border-severity-medium',
    gradient: 'from-severity-medium/20 to-transparent'
  },
  LOW: {
    label: 'LOW RISK',
    color: 'text-severity-low',
    glow: 'text-glow-low',
    shadow: 'shadow-low',
    bg: 'bg-severity-low/10',
    border: 'border-severity-low',
    gradient: 'from-severity-low/20 to-transparent'
  },
  INFO: {
    label: 'MINIMAL RISK',
    color: 'text-severity-info',
    glow: 'text-glow',
    shadow: 'shadow-glow',
    bg: 'bg-severity-info/10',
    border: 'border-severity-info',
    gradient: 'from-severity-info/20 to-transparent'
  }
};

function getSeverityConfig(severity) {
  const key = severity?.toUpperCase() || 'LOW';
  return SEVERITY_CONFIG[key] || SEVERITY_CONFIG.LOW;
}

export default function RiskScore({ score, severity, factors = [] }) {
  const [displayScore, setDisplayScore] = useState(0);
  const config = getSeverityConfig(severity);
  const circumference = 2 * Math.PI * 120;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  // Count findings by severity
  const severityCounts = factors.reduce((acc, f) => {
    const sev = f.severity?.toLowerCase() || 'info';
    acc[sev] = (acc[sev] || 0) + 1;
    return acc;
  }, {});

  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const increment = score / (duration / 16);

    const timer = setInterval(() => {
      start += increment;
      if (start >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [score]);

  return (
    <motion.div
      className="card flex flex-col items-center justify-center py-12 space-y-6"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      {/* Title */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-accent-primary tracking-wider uppercase">
          Threat Level
        </h2>
        <p className="text-text-dim text-sm mt-1">
          <span className="text-severity-low">0 = Safe</span>
          <span className="mx-2">→</span>
          <span className="text-severity-critical">100 = Dangerous</span>
        </p>
      </div>

      {/* Score Circle */}
      <div className="relative">
        {/* Background circle */}
        <svg className="transform -rotate-90" width="280" height="280">
          <circle
            cx="140"
            cy="140"
            r="120"
            stroke="rgba(0, 255, 242, 0.1)"
            strokeWidth="12"
            fill="none"
          />
          {/* Progress circle */}
          <motion.circle
            cx="140"
            cy="140"
            r="120"
            stroke="currentColor"
            strokeWidth="12"
            fill="none"
            strokeLinecap="round"
            className={config.color}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{
              strokeDasharray: circumference,
              filter: 'drop-shadow(0 0 8px currentColor)'
            }}
          />
        </svg>

        {/* Score display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            className={`text-7xl font-bold ${config.color} ${config.glow}`}
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            {displayScore}
          </motion.div>
          <motion.div
            className={`text-xs uppercase tracking-wider font-semibold mt-2 ${config.color}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
          >
            / 100
          </motion.div>
        </div>

        {/* Pulsing rings */}
        <motion.div
          className={`absolute inset-0 rounded-full border-2 ${config.border} opacity-30`}
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.3, 0, 0.3]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{ margin: '20px' }}
        />
      </div>

      {/* Severity badge */}
      <motion.div
        className={`px-6 py-3 rounded-lg ${config.bg} border-2 ${config.border} ${config.shadow}`}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2 }}
      >
        <div className={`text-lg font-bold uppercase tracking-widest ${config.color} ${config.glow}`}>
          {config.label}
        </div>
      </motion.div>

      {/* Verdict and recommendation */}
      <motion.div
        className="text-center max-w-md space-y-2"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4 }}
      >
        {severity?.toLowerCase() === 'critical' && (
          <>
            <p className="text-severity-critical font-bold text-lg">DO NOT USE</p>
            <p className="text-text-secondary text-sm">
              Critical vulnerabilities or supply chain threats detected. Find an alternative or upgrade immediately.
            </p>
          </>
        )}
        {severity?.toLowerCase() === 'high' && (
          <>
            <p className="text-severity-high font-bold text-lg">USE WITH EXTREME CAUTION</p>
            <p className="text-text-secondary text-sm">
              Significant security issues found. Review all findings before proceeding.
            </p>
          </>
        )}
        {severity?.toLowerCase() === 'medium' && (
          <>
            <p className="text-severity-medium font-bold text-lg">REVIEW BEFORE USING</p>
            <p className="text-text-secondary text-sm">
              Moderate concerns detected. Verify findings are acceptable for your use case.
            </p>
          </>
        )}
        {severity?.toLowerCase() === 'low' && (
          <>
            <p className="text-severity-low font-bold text-lg">GENERALLY SAFE</p>
            <p className="text-text-secondary text-sm">
              Minor or no concerns detected. Package appears safe for production use.
            </p>
          </>
        )}
      </motion.div>

      {/* Threat Summary - show what's driving the score */}
      {factors.length > 0 && (
        <motion.div
          className="w-full max-w-lg"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.6 }}
        >
          <div className="text-xs text-text-dim uppercase tracking-wider mb-2 text-center">
            Threat Summary
          </div>
          <div className="flex justify-center gap-3 flex-wrap mb-3">
            {severityCounts.critical > 0 && (
              <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-severity-critical/20 border border-severity-critical/50">
                <span className="text-severity-critical font-bold">{severityCounts.critical}</span>
                <span className="text-severity-critical text-xs">Critical</span>
              </div>
            )}
            {severityCounts.high > 0 && (
              <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-severity-high/20 border border-severity-high/50">
                <span className="text-severity-high font-bold">{severityCounts.high}</span>
                <span className="text-severity-high text-xs">High</span>
              </div>
            )}
            {severityCounts.medium > 0 && (
              <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-severity-medium/20 border border-severity-medium/50">
                <span className="text-severity-medium font-bold">{severityCounts.medium}</span>
                <span className="text-severity-medium text-xs">Medium</span>
              </div>
            )}
            {severityCounts.low > 0 && (
              <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-severity-low/20 border border-severity-low/50">
                <span className="text-severity-low font-bold">{severityCounts.low}</span>
                <span className="text-severity-low text-xs">Low</span>
              </div>
            )}
          </div>
          {/* Top issues preview */}
          <div className="text-center text-xs text-text-dim">
            {factors.filter(f => f.severity?.toLowerCase() === 'critical' || f.severity?.toLowerCase() === 'high')
              .slice(0, 3)
              .map((f, i) => (
                <div key={i} className="truncate">
                  • {f.name || f.description || 'Security issue detected'}
                </div>
              ))}
            {factors.length > 3 && (
              <div className="text-accent-primary mt-1">
                +{factors.length - 3} more findings below
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Progress bar */}
      <div className="w-full max-w-md">
        <div className="h-2 bg-secondary rounded-full overflow-hidden">
          <motion.div
            className={`h-full bg-gradient-to-r ${config.gradient} ${config.bg}`}
            initial={{ width: 0 }}
            animate={{ width: `${score}%` }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </div>
      </div>
    </motion.div>
  );
}
