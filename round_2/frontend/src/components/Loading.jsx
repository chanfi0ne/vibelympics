// PURPOSE: Terminal-style loading animation component with scanning effect
import { motion } from 'framer-motion';

export default function Loading() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex flex-col items-center justify-center py-20 space-y-8"
    >
      {/* Scanning animation */}
      <div className="relative w-64 h-64 flex items-center justify-center">
        {/* Outer ring */}
        <motion.div
          className="absolute w-64 h-64 border-2 border-accent-dim rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        />

        {/* Middle ring */}
        <motion.div
          className="absolute w-48 h-48 border-2 border-accent-primary/40 rounded-full"
          animate={{ rotate: -360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        />

        {/* Inner ring */}
        <motion.div
          className="absolute w-32 h-32 border-2 border-accent-primary rounded-full shadow-glow"
          animate={{ rotate: 360 }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
        />

        {/* Center pulse */}
        <motion.div
          className="w-4 h-4 bg-accent-primary rounded-full shadow-glow"
          animate={{
            scale: [1, 1.5, 1],
            opacity: [1, 0.5, 1],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />

        {/* Scanning line */}
        <motion.div
          className="absolute w-full h-[2px] bg-gradient-to-r from-transparent via-accent-primary to-transparent"
          style={{ transformOrigin: 'center' }}
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        />
      </div>

      {/* Terminal text */}
      <div className="space-y-2 text-center font-mono">
        <motion.div
          className="text-accent-primary text-xl font-semibold tracking-wider"
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          SCANNING PACKAGE
        </motion.div>

        <div className="flex items-center justify-center space-x-1 text-text-secondary text-sm">
          <span>Analyzing dependencies</span>
          <motion.span
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 1, repeat: Infinity, times: [0, 0.5, 1] }}
          >
            .
          </motion.span>
          <motion.span
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 1, repeat: Infinity, times: [0, 0.5, 1], delay: 0.2 }}
          >
            .
          </motion.span>
          <motion.span
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 1, repeat: Infinity, times: [0, 0.5, 1], delay: 0.4 }}
          >
            .
          </motion.span>
        </div>
      </div>

      {/* Terminal-style progress indicators */}
      <div className="w-full max-w-md space-y-2 text-xs text-text-dim font-mono">
        <ProgressLine text="Fetching from npm Registry" delay={0} />
        <ProgressLine text="Verifying GitHub repository" delay={0.3} />
        <ProgressLine text="Checking Sigstore provenance" delay={0.6} />
        <ProgressLine text="Scanning for vulnerabilities" delay={0.9} />
      </div>

      {/* Vulnerability sources indicator */}
      <motion.div
        className="w-full max-w-md mt-4 p-4 border border-accent-dim/30 rounded-lg bg-secondary/20"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        <div className="text-xs text-text-dim uppercase tracking-wider mb-3">
          Vulnerability Databases
        </div>
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <SourceIndicator name="GitHub Advisory (GHSA)" delay={1.4} />
          <SourceIndicator name="National Vuln DB (NVD)" delay={1.6} />
          <SourceIndicator name="npm Security Advisories" delay={1.8} />
          <SourceIndicator name="OSV Aggregated Feed" delay={2.0} />
        </div>
        <div className="text-[10px] text-text-dim mt-3 text-center">
          Powered by OSV.dev - Open Source Vulnerability Database
        </div>
      </motion.div>
    </motion.div>
  );
}

function SourceIndicator({ name, delay }) {
  return (
    <motion.div
      className="flex items-center space-x-2"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay }}
    >
      <motion.span
        className="text-severity-low"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: delay + 0.2, type: "spring" }}
      >
        ✓
      </motion.span>
      <span className="text-text-secondary">{name}</span>
    </motion.div>
  );
}

function ProgressLine({ text, delay }) {
  return (
    <motion.div
      className="flex items-center space-x-2"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: [0, 1, 0.7], x: 0 }}
      transition={{ duration: 1, delay, repeat: Infinity, repeatDelay: 1.2 }}
    >
      <span className="text-accent-primary">{'>'}</span>
      <span>{text}</span>
      <motion.div
        className="flex-1 h-[1px] bg-gradient-to-r from-accent-primary/50 to-transparent"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.8, delay: delay + 0.2, repeat: Infinity, repeatDelay: 1.2 }}
        style={{ transformOrigin: 'left' }}
      />
    </motion.div>
  );
}
