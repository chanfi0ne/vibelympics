// PURPOSE: Expandable findings list component with severity-based styling and animations
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const SEVERITY_CONFIG = {
  CRITICAL: {
    badge: 'badge-critical',
    icon: '🔴',
    label: 'CRITICAL'
  },
  HIGH: {
    badge: 'badge-high',
    icon: '🟠',
    label: 'HIGH'
  },
  MEDIUM: {
    badge: 'badge-medium',
    icon: '🟡',
    label: 'MEDIUM'
  },
  LOW: {
    badge: 'badge-low',
    icon: '🟢',
    label: 'LOW'
  },
  INFO: {
    badge: 'badge-info',
    icon: '🔵',
    label: 'INFO'
  }
};

function FindingItem({ finding, index }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const config = SEVERITY_CONFIG[finding.severity] || SEVERITY_CONFIG.INFO;

  return (
    <motion.div
      className="border border-accent-dim rounded-lg overflow-hidden bg-secondary/30"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 flex items-center justify-between hover:bg-secondary/50 transition-colors duration-200"
      >
        <div className="flex items-center space-x-4 flex-1 min-w-0">
          {/* Severity Badge */}
          <span className={`badge ${config.badge} flex-shrink-0`}>
            <span className="mr-1">{config.icon}</span>
            {config.label}
          </span>

          {/* Finding Name */}
          <div className="text-left flex-1 min-w-0">
            <h3 className="text-text-primary font-semibold text-sm break-words">
              {finding.name || 'Unnamed Finding'}
            </h3>
          </div>
        </div>

        {/* Expand Icon */}
        <motion.div
          className="text-accent-primary text-xl ml-4 flex-shrink-0"
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          ▼
        </motion.div>
      </button>

      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-6 pt-2 space-y-4 border-t border-accent-dim/30">
              {/* Description */}
              {finding.description && (
                <div>
                  <div className="text-text-dim text-xs uppercase tracking-wider mb-2">
                    Description
                  </div>
                  <p className="text-text-secondary text-sm leading-relaxed">
                    {finding.description}
                  </p>
                </div>
              )}

              {/* Details */}
              {finding.details && (
                <div>
                  <div className="text-text-dim text-xs uppercase tracking-wider mb-2">
                    Technical Details
                  </div>
                  <div className="bg-void rounded p-4 border border-accent-dim/30">
                    <pre className="text-text-secondary text-xs font-mono whitespace-pre-wrap break-words">
                      {typeof finding.details === 'string'
                        ? finding.details
                        : JSON.stringify(finding.details, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Metadata Grid */}
              <div className="grid grid-cols-2 gap-4 pt-2">
                {finding.confidence && (
                  <div>
                    <div className="text-text-dim text-xs uppercase tracking-wider mb-1">
                      Confidence
                    </div>
                    <div className="text-text-primary text-sm font-semibold">
                      {finding.confidence}%
                    </div>
                  </div>
                )}

                {finding.category && (
                  <div>
                    <div className="text-text-dim text-xs uppercase tracking-wider mb-1">
                      Category
                    </div>
                    <div className="text-text-primary text-sm font-semibold capitalize">
                      {finding.category.replace(/_/g, ' ')}
                    </div>
                  </div>
                )}
              </div>

              {/* Recommendation */}
              {finding.recommendation && (
                <div className="mt-4 p-4 bg-accent-primary/5 border-l-2 border-accent-primary rounded">
                  <div className="text-accent-primary text-xs uppercase tracking-wider mb-2 flex items-center space-x-2">
                    <span>💡</span>
                    <span>Recommendation</span>
                  </div>
                  <p className="text-text-secondary text-sm leading-relaxed">
                    {finding.recommendation}
                  </p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function FindingsList({ findings }) {
  const [filterSeverity, setFilterSeverity] = useState('ALL');

  const filteredFindings = filterSeverity === 'ALL'
    ? findings
    : findings.filter(f => f.severity === filterSeverity);

  const severityCounts = findings.reduce((acc, finding) => {
    acc[finding.severity] = (acc[finding.severity] || 0) + 1;
    return acc;
  }, {});

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.5 }}
    >
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-accent-primary tracking-wider uppercase">
              Security Findings
            </h2>
            <p className="text-text-dim text-sm mt-1">
              {findings.length} issue{findings.length !== 1 ? 's' : ''} detected
            </p>
          </div>
        </div>

        {/* Severity Filter */}
        <div className="flex flex-wrap gap-2">
          <FilterButton
            active={filterSeverity === 'ALL'}
            onClick={() => setFilterSeverity('ALL')}
            label={`All (${findings.length})`}
          />
          {Object.entries(SEVERITY_CONFIG).map(([severity, config]) => {
            const count = severityCounts[severity] || 0;
            if (count === 0) return null;
            return (
              <FilterButton
                key={severity}
                active={filterSeverity === severity}
                onClick={() => setFilterSeverity(severity)}
                label={`${config.icon} ${config.label} (${count})`}
                className={filterSeverity === severity ? config.badge : ''}
              />
            );
          })}
        </div>
      </div>

      {/* Findings List */}
      <div className="space-y-3">
        {filteredFindings.length > 0 ? (
          filteredFindings.map((finding, index) => (
            <FindingItem key={index} finding={finding} index={index} />
          ))
        ) : (
          <motion.div
            className="text-center py-12 text-text-dim"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="text-4xl mb-4">🔍</div>
            <p>No findings match the selected filter</p>
          </motion.div>
        )}
      </div>

      {/* Summary Stats */}
      {findings.length > 0 && (
        <motion.div
          className="mt-6 pt-6 border-t border-accent-dim grid grid-cols-2 md:grid-cols-5 gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          {Object.entries(SEVERITY_CONFIG).map(([severity, config]) => {
            const count = severityCounts[severity] || 0;
            return (
              <div key={severity} className="text-center">
                <div className={`text-2xl font-bold ${config.badge.replace('badge-', 'text-severity-')}`}>
                  {count}
                </div>
                <div className="text-text-dim text-xs uppercase tracking-wider mt-1">
                  {config.label}
                </div>
              </div>
            );
          })}
        </motion.div>
      )}
    </motion.div>
  );
}

function FilterButton({ active, onClick, label, className = '' }) {
  return (
    <motion.button
      onClick={onClick}
      className={`px-4 py-2 rounded text-xs font-semibold uppercase tracking-wider transition-all duration-200 ${
        active
          ? className || 'bg-accent-primary text-void border-2 border-accent-primary shadow-glow'
          : 'bg-secondary text-text-secondary border-2 border-accent-dim hover:border-accent-primary'
      }`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {label}
    </motion.button>
  );
}
