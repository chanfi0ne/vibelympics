// PURPOSE: Package metadata display component with verification status indicators
import { motion } from 'framer-motion';

export default function MetadataCard({ metadata }) {
  const InfoRow = ({ label, value, icon, verified }) => (
    <motion.div
      className="flex items-start justify-between py-3 border-b border-accent-dim/30 last:border-0"
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center space-x-2 text-text-dim text-sm">
        {icon && <span className="text-accent-primary">{icon}</span>}
        <span>{label}</span>
      </div>
      <div className="flex items-center space-x-2 text-text-primary text-sm font-semibold ml-4 text-right">
        <span className="break-all">{value || 'N/A'}</span>
        {verified && (
          <motion.span
            className="text-severity-low text-base"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.5, type: "spring" }}
          >
            ✓
          </motion.span>
        )}
      </div>
    </motion.div>
  );

  const formatNumber = (num) => {
    if (!num) return 'N/A';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      {/* Header */}
      <div className="mb-6 pb-4 border-b border-accent-dim">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold text-accent-primary tracking-wider uppercase break-all">
              {metadata.name || 'Unknown Package'}
            </h2>
            <div className="flex items-center space-x-3 mt-2">
              <span className="text-text-secondary text-sm">
                Version: <span className="text-accent-primary font-semibold">{metadata.version || 'N/A'}</span>
              </span>
              {metadata.latest_version && metadata.version !== metadata.latest_version && (
                <span className="text-severity-medium text-xs">
                  (Latest: {metadata.latest_version})
                </span>
              )}
            </div>
          </div>
        </div>
        {metadata.description && (
          <p className="text-text-secondary text-sm mt-3 leading-relaxed">
            {metadata.description}
          </p>
        )}
      </div>

      {/* Metadata Grid */}
      <div className="space-y-1">
        <InfoRow
          label="Author"
          value={metadata.author || metadata.publisher}
          icon="👤"
        />

        <InfoRow
          label="License"
          value={metadata.license}
          icon="📜"
        />

        <InfoRow
          label="Weekly Downloads"
          value={formatNumber(metadata.downloads_last_week)}
          icon="⬇️"
        />

        <InfoRow
          label="Published"
          value={formatDate(metadata.created_at)}
          icon="📅"
        />

        <InfoRow
          label="Last Updated"
          value={formatDate(metadata.modified_at)}
          icon="🔄"
        />

        {metadata.repository && (
          <InfoRow
            label="Repository"
            value={
              <a
                href={metadata.repository.startsWith('http') ? metadata.repository : `https://${metadata.repository}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-primary hover:text-accent-glow underline"
              >
                {metadata.repository.replace(/^https?:\/\//, '')}
              </a>
            }
            icon="🔗"
            verified={metadata.repository_verified}
          />
        )}

        {metadata.homepage && metadata.homepage !== metadata.repository && (
          <InfoRow
            label="Homepage"
            value={
              <a
                href={metadata.homepage.startsWith('http') ? metadata.homepage : `https://${metadata.homepage}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-primary hover:text-accent-glow underline"
              >
                {metadata.homepage.replace(/^https?:\/\//, '')}
              </a>
            }
            icon="🏠"
          />
        )}

        {metadata.maintainers && metadata.maintainers.length > 0 && (
          <InfoRow
            label="Maintainers"
            value={`${metadata.maintainers.length} contributor${metadata.maintainers.length !== 1 ? 's' : ''}`}
            icon="👥"
          />
        )}
      </div>

      {/* Keywords */}
      {metadata.keywords && metadata.keywords.length > 0 && (
        <motion.div
          className="mt-6 pt-6 border-t border-accent-dim"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <div className="text-text-dim text-xs uppercase tracking-wider mb-3">Keywords</div>
          <div className="flex flex-wrap gap-2">
            {metadata.keywords.slice(0, 10).map((keyword, index) => (
              <motion.span
                key={keyword}
                className="px-3 py-1 bg-secondary border border-accent-dim rounded text-text-secondary text-xs"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 + index * 0.05 }}
              >
                {keyword}
              </motion.span>
            ))}
            {metadata.keywords.length > 10 && (
              <span className="px-3 py-1 text-text-dim text-xs">
                +{metadata.keywords.length - 10} more
              </span>
            )}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
