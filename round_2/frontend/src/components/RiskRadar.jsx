// PURPOSE: Radar chart visualization component for risk assessment dimensions
import { motion } from 'framer-motion';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip
} from 'recharts';

const DIMENSIONS = [
  { key: 'authenticity', label: 'Authenticity', description: 'Package identity verification' },
  { key: 'maintenance', label: 'Maintenance', description: 'Update frequency and activity' },
  { key: 'security', label: 'Security', description: 'Vulnerability and threat indicators' },
  { key: 'reputation', label: 'Reputation', description: 'Community trust and adoption' }
];

export default function RiskRadar({ scores = {} }) {
  const chartData = DIMENSIONS.map(dim => ({
    dimension: dim.label,
    value: scores?.[dim.key] ?? 0,
    fullMark: 100
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const dimension = DIMENSIONS.find(d => d.label === payload[0].payload.dimension);
      return (
        <div className="bg-card border border-accent-dim rounded-lg p-3 shadow-glow">
          <p className="text-accent-primary font-semibold text-sm">{dimension.label}</p>
          <p className="text-text-secondary text-xs mt-1">{dimension.description}</p>
          <p className="text-text-primary font-bold text-lg mt-2">
            {payload[0].value}<span className="text-text-dim text-sm">/100</span>
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.4 }}
    >
      {/* Title */}
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-accent-primary tracking-wider uppercase">
          Risk Assessment
        </h2>
        <p className="text-text-dim text-sm mt-1">Multi-dimensional threat analysis</p>
      </div>

      {/* Radar Chart */}
      <motion.div
        className="w-full h-[400px]"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.8 }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chartData}>
            <defs>
              <linearGradient id="radarGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#00fff2" stopOpacity={0.8} />
                <stop offset="100%" stopColor="#00fff2" stopOpacity={0.2} />
              </linearGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                  <feMergeNode in="coloredBlur"/>
                  <feMergeNode in="SourceGraphic"/>
                </feMerge>
              </filter>
            </defs>
            <PolarGrid
              stroke="#00fff2"
              strokeOpacity={0.2}
              strokeWidth={1}
            />
            <PolarAngleAxis
              dataKey="dimension"
              tick={{
                fill: '#00fff2',
                fontSize: 14,
                fontWeight: 600,
                fontFamily: 'JetBrains Mono, monospace'
              }}
              tickLine={false}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{
                fill: '#606070',
                fontSize: 11,
                fontFamily: 'JetBrains Mono, monospace'
              }}
              axisLine={false}
            />
            <Radar
              name="Risk Score"
              dataKey="value"
              stroke="#00fff2"
              strokeWidth={2}
              fill="url(#radarGradient)"
              fillOpacity={0.6}
              filter="url(#glow)"
              animationDuration={1500}
              animationBegin={600}
            />
            <Tooltip content={<CustomTooltip />} />
          </RadarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* Legend */}
      <motion.div
        className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-accent-dim"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        {DIMENSIONS.map((dim, index) => (
          <motion.div
            key={dim.key}
            className="flex items-start space-x-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 1.2 + index * 0.1 }}
          >
            <div className="w-3 h-3 rounded-full bg-accent-primary shadow-glow-sm mt-1 flex-shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="text-text-primary font-semibold text-sm">{dim.label}</div>
              <div className="text-text-dim text-xs mt-0.5">{dim.description}</div>
              <div className="flex items-center space-x-2 mt-1">
                <div className="flex-1 h-1 bg-secondary rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-accent-primary to-severity-info"
                    initial={{ width: 0 }}
                    animate={{ width: `${scores?.[dim.key] ?? 0}%` }}
                    transition={{ delay: 1.4 + index * 0.1, duration: 0.8 }}
                  />
                </div>
                <span className="text-accent-primary text-xs font-bold min-w-[3ch]">
                  {scores?.[dim.key] ?? 0}
                </span>
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
}
