// PURPOSE: Search form for version comparison feature
import { useState } from 'react';
import { motion } from 'framer-motion';

export default function CompareSearch({ onCompare, loading, disabled }) {
  const [packageName, setPackageName] = useState('');
  const [versionOld, setVersionOld] = useState('');
  const [versionNew, setVersionNew] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (packageName.trim() && versionOld.trim() && versionNew.trim() && !loading && !disabled) {
      onCompare({
        package_name: packageName.trim(),
        version_old: versionOld.trim(),
        version_new: versionNew.trim(),
      });
    }
  };

  const handleExample = () => {
    setPackageName('lodash');
    setVersionOld('4.17.11');
    setVersionNew('4.17.21');
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="w-full max-w-3xl mx-auto space-y-4"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Package Name */}
      <div>
        <label className="text-text-dim text-xs uppercase tracking-wider mb-2 block">Package Name</label>
        <div className="relative">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <span className="text-accent-primary font-bold text-lg">{'>'}</span>
          </div>
          <input
            type="text"
            value={packageName}
            onChange={(e) => setPackageName(e.target.value)}
            placeholder="e.g., lodash"
            className="input-terminal pl-10 w-full"
            disabled={loading || disabled}
          />
        </div>
      </div>

      {/* Version Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="text-text-dim text-xs uppercase tracking-wider mb-2 block">Old Version</label>
          <input
            type="text"
            value={versionOld}
            onChange={(e) => setVersionOld(e.target.value)}
            placeholder="e.g., 4.17.11"
            className="input-terminal w-full"
            disabled={loading || disabled}
          />
        </div>
        <div>
          <label className="text-text-dim text-xs uppercase tracking-wider mb-2 block">New Version</label>
          <input
            type="text"
            value={versionNew}
            onChange={(e) => setVersionNew(e.target.value)}
            placeholder="e.g., 4.17.21"
            className="input-terminal w-full"
            disabled={loading || disabled}
          />
        </div>
      </div>

      {/* Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <motion.button
          type="submit"
          className="btn-glow flex-1 px-8 py-3"
          disabled={loading || disabled || !packageName.trim() || !versionOld.trim() || !versionNew.trim()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {loading ? (
            <span className="flex items-center justify-center space-x-2">
              <motion.span
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="inline-block"
              >
                ⟳
              </motion.span>
              <span>COMPARING</span>
            </span>
          ) : (
            'COMPARE VERSIONS'
          )}
        </motion.button>
      </div>

      {/* Example */}
      <motion.div
        className="text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <span className="text-xs text-text-dim mr-2">Try example:</span>
        <motion.button
          type="button"
          onClick={handleExample}
          disabled={loading || disabled}
          className="text-xs px-3 py-1 rounded border border-accent-dim text-text-secondary hover:border-accent-primary hover:text-accent-primary transition-all"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          lodash 4.17.11 → 4.17.21
        </motion.button>
      </motion.div>
    </motion.form>
  );
}
