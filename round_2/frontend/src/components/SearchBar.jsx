// PURPOSE: Package search input component with terminal-style styling and glow effects
import { useState } from 'react';
import { motion } from 'framer-motion';

export default function SearchBar({ onSearch, loading, disabled }) {
  const [packageName, setPackageName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (packageName.trim() && !loading && !disabled) {
      onSearch(packageName.trim());
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="w-full max-w-3xl mx-auto"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1 relative">
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
            <span className="text-accent-primary font-bold text-lg">{'>'}</span>
          </div>
          <input
            type="text"
            value={packageName}
            onChange={(e) => setPackageName(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter npm package name (e.g., lodash, express)"
            className="input-terminal pl-10"
            disabled={loading || disabled}
            autoFocus
          />
        </div>

        <motion.button
          type="submit"
          className="btn-glow whitespace-nowrap px-8"
          disabled={loading || disabled || !packageName.trim()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {loading ? (
            <span className="flex items-center space-x-2">
              <motion.span
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="inline-block"
              >
                ⟳
              </motion.span>
              <span>SCANNING</span>
            </span>
          ) : (
            'AUDIT'
          )}
        </motion.button>
      </div>

      {/* Example packages */}
      <motion.div
        className="mt-4 text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <span className="text-xs text-text-dim mr-2">Try examples:</span>
        <div className="inline-flex flex-wrap gap-2 mt-2 sm:mt-0">
          {[
            { name: 'lodash', label: 'lodash', risk: 'low' },
            { name: 'express', label: 'express', risk: 'low' },
            { name: 'lodahs', label: 'lodahs (typosquat)', risk: 'high' },
            { name: 'event-stream', label: 'event-stream', risk: 'medium' },
          ].map((example) => (
            <motion.button
              key={example.name}
              type="button"
              onClick={() => {
                setPackageName(example.name);
                onSearch(example.name);
              }}
              disabled={loading || disabled}
              className={`text-xs px-3 py-1 rounded border transition-all ${
                example.risk === 'high'
                  ? 'border-severity-critical/50 text-severity-critical hover:bg-severity-critical/10'
                  : example.risk === 'medium'
                  ? 'border-severity-medium/50 text-severity-medium hover:bg-severity-medium/10'
                  : 'border-accent-dim text-text-secondary hover:border-accent-primary hover:text-accent-primary'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {example.label}
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Helper text */}
      <motion.div
        className="mt-3 text-xs text-text-dim text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        <span>Press Enter or click AUDIT to scan package security</span>
      </motion.div>
    </motion.form>
  );
}
