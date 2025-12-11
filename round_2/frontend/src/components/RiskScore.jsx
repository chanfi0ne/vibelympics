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

export default function RiskScore({ score, severity }) {
  const [displayScore, setDisplayScore] = useState(0);
  const config = getSeverityConfig(severity);
  const circumference = 2 * Math.PI * 120;
  const strokeDashoffset = circumference - (score / 100) * circumference;

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
          Risk Score
        </h2>
        <p className="text-text-dim text-sm mt-1">Supply Chain Security Assessment</p>
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

      {/* Score interpretation */}
      <motion.div
        className="text-center text-text-secondary text-sm max-w-md"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.4 }}
      >
        {score >= 76 && 'Severe supply chain threats detected. Exercise extreme caution.'}
        {score >= 51 && score < 76 && 'Significant security concerns identified. Review carefully.'}
        {score >= 26 && score < 51 && 'Moderate risk factors present. Additional verification recommended.'}
        {score < 26 && 'Low risk profile with minor concerns. Generally safe to use.'}
      </motion.div>

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
