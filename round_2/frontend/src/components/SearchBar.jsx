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

      {/* Helper text */}
      <motion.div
        className="mt-3 text-xs text-text-dim text-center sm:text-left"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <span className="inline-flex items-center space-x-2">
          <span>Press Enter or click AUDIT to scan package security</span>
        </span>
      </motion.div>
    </motion.form>
  );
}
