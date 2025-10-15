'use client';

import { Info } from 'lucide-react';

export default function TopBar() {
  return (
    <header className="sticky top-0 z-40">
      <div className="container mx-auto px-4 py-4">
        <div className="glass-xl rounded-2xl px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-xl btn-aurum flex items-center justify-center shadow-xl sun-glow">
              <span className="title-aurum text-xl font-bold">य</span>
            </div>
            <div>
              <div className="title-aurum text-lg tracking-wide">Parametric Yantra Generator</div>
              <p className="text-[12px] text-slate-300/80">Ancient Astronomy • Modern Ephemeris</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded-full border border-blue-400/40 text-[11px] text-blue-200/90">
              v0.6.0 Beta
            </span>
            <button className="h-9 w-9 rounded-xl border border-white/10 hover:bg-white/10 text-slate-200">
              <Info className="h-5 w-5 mx-auto" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
