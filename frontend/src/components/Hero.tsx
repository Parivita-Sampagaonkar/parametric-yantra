'use client';

import { motion } from 'framer-motion';

export default function Hero() {
  return (
    <section className="relative container mx-auto px-4 pt-10 pb-8">
      <div className="glass-xl rounded-3xl p-8 overflow-hidden">
        <div className="absolute -right-24 -top-24 h-80 w-80 rounded-full bg-amber-400/10 blur-3xl sun-glow" />
        <div className="absolute -left-24 -bottom-24 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />

        <motion.h1
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: 'easeOut' }}
          className="title-aurum text-3xl md:text-4xl font-extrabold"
        >
          Where <span className="text-aurum">Yantra</span> meets the Sky
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.65 }}
          className="mt-2 text-slate-300/85 max-w-2xl"
        >
          Generate scientifically faithful instruments inspired by Jantar Mantar — aligned to your
          latitude, validated by ephemeris.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="mt-5"
        >
          <a href="#generator" className="inline-flex items-center gap-2 btn-aurum px-5 py-3 rounded-xl font-semibold shadow-lg hover:brightness-110">
            Generate Now
            <span className="text-sm">→</span>
          </a>
        </motion.div>
      </div>
    </section>
  );
}
