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
        <ProgressLine text="Fetching package metadata" delay={0} />
        <ProgressLine text="Analyzing repository" delay={0.3} />
        <ProgressLine text="Checking authenticity signals" delay={0.6} />
        <ProgressLine text="Scanning for threats" delay={0.9} />
      </div>
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
