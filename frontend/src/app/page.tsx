'use client';

import { useState } from 'react';
import { YantraGenerator } from '@/components/YantraGenerator';
import { LocationPicker } from '@/components/LocationPicker';
import { useYantraStore } from '@/store/yantraStore';
import { Settings, Eye, Download } from 'lucide-react';

import CosmicBackground from '@/components/CosmicBackground';
import TopBar from '@/components/TopBar';
import Hero from '@/components/Hero';
import PreviewScene from '@/components/PreviewScene';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'generate' | 'preview' | 'export'>('generate');
  const { currentGeneration, isGenerating } = useYantraStore();

  return (
    <div className="relative min-h-screen">
      <CosmicBackground />
      <TopBar />
      <Hero />

      <main id="generator" className="container mx-auto px-4 pb-16">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Control Console */}
          <div className="space-y-4 lg:col-span-1">
            {/* Tab switch */}
            <div className="glass-xl rounded-2xl p-1.5 grid grid-cols-3 gap-1.5">
              <button
                onClick={() => setActiveTab('generate')}
                className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  activeTab === 'generate'
                    ? 'btn-aurum shadow-xl'
                    : 'text-slate-200 hover:bg-white/10'
                }`}
              >
                <Settings className="h-4 w-4 inline mr-2" />
                Generate
              </button>
              <button
                onClick={() => setActiveTab('preview')}
                disabled={!currentGeneration}
                className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  activeTab === 'preview'
                    ? 'bg-blue-600 text-white shadow-xl'
                    : 'text-slate-200 hover:bg-white/10'
                } ${!currentGeneration && 'opacity-50 cursor-not-allowed'}`}
              >
                <Eye className="h-4 w-4 inline mr-2" />
                Preview
              </button>
              <button
                onClick={() => setActiveTab('export')}
                disabled={!currentGeneration}
                className={`px-4 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  activeTab === 'export'
                    ? 'bg-purple-600 text-white shadow-xl'
                    : 'text-slate-200 hover:bg-white/10'
                } ${!currentGeneration && 'opacity-50 cursor-not-allowed'}`}
              >
                <Download className="h-4 w-4 inline mr-2" />
                Export
              </button>
            </div>

            {/* Panel */}
            <div className="glass-xl rounded-2xl p-6">
              {activeTab === 'generate' && (
                <div className="space-y-6">
                  <div>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="h-8 w-1 rounded bg-gradient-to-b from-amber-400 to-orange-600" />
                      <h2 className="title-aurum text-lg">Yantra Configuration</h2>
                    </div>
                    <YantraGenerator />
                  </div>
                  <hr className="hr-faint my-2" />
                  <div>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="h-8 w-1 rounded bg-gradient-to-b from-blue-400 to-blue-600" />
                      <h2 className="title-aurum text-lg">Location</h2>
                    </div>
                    <LocationPicker />
                  </div>
                </div>
              )}

              {activeTab === 'preview' && currentGeneration && (
                <div className="space-y-4">
                  <h2 className="title-aurum text-lg">Preview & Validation</h2>
                  <div className="space-y-2 text-sm text-slate-200">
                    <div className="flex justify-between border border-white/10 rounded-xl px-3 py-2">
                      <span className="text-slate-300/80">Type</span>
                      <span className="font-semibold capitalize">
                        {currentGeneration.yantra_type}
                      </span>
                    </div>
                    <div className="flex justify-between border border-white/10 rounded-xl px-3 py-2">
                      <span className="text-slate-300/80">Scale</span>
                      <span className="font-semibold">{currentGeneration.scale} m</span>
                    </div>
                    <div className="flex justify-between border border-white/10 rounded-xl px-3 py-2">
                      <span className="text-slate-300/80">Location</span>
                      <span className="font-semibold">{currentGeneration.location.name}</span>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'export' && currentGeneration && (
                <div className="space-y-2">
                  <h2 className="title-aurum text-lg">Downloads</h2>
                  <p className="text-sm text-slate-300/80">
                    DXF • STL • GLTF • PDF (links appear as exports finish)
                  </p>
                  <div className="text-slate-400 text-sm">Export panel coming soon.</div>
                </div>
              )}

              {isGenerating && (
                <div className="mt-6 rounded-xl border border-blue-400/30 bg-blue-500/10 p-4">
                  <div className="flex items-center gap-3">
                    <div className="h-6 w-6 border-2 border-blue-400/40 border-t-blue-400 rounded-full animate-spin" />
                    <div className="text-sm text-slate-200">
                      Calculating parametric geometry & validating ephemeris…
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right: Cinematic Preview */}
          <div className="lg:col-span-2">
            <div className="glass-xl rounded-3xl overflow-hidden h-[620px] breathe relative">
              <PreviewScene />
              {!currentGeneration && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="text-center">
                    <div className="title-aurum text-2xl text-aurum mb-2">Awaiting Generation</div>
                    <p className="text-slate-300/80">
                      Configure on the left and click <span className="text-aurum">Generate</span>.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Stats */}
            <div className="mt-6 grid grid-cols-2 gap-4">
              <div className="glass-xl rounded-2xl p-5">
                <div className="text-xs uppercase tracking-wide text-slate-300/70">Available Yantras</div>
                <div className="title-aurum text-3xl text-aurum mt-1">2</div>
                <div className="text-[12px] text-slate-400 mt-1">Samrat & Rama (v0.6)</div>
              </div>
              <div className="glass-xl rounded-2xl p-5">
                <div className="text-xs uppercase tracking-wide text-slate-300/70">Accuracy</div>
                <div className="title-aurum text-3xl mt-1 capitalize">
                  {currentGeneration?.validation.accuracy_level ?? 'N/A'}
                </div>
                <div className="text-[12px] text-slate-400 mt-1">Based on ephemeris</div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t border-white/10">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-slate-300/85">
          Built with <span className="text-red-400">❤</span> to preserve India&apos;s astronomical heritage •
          <span className="ml-1 text-slate-400">Open Source • FastAPI • Next.js • Three.js • Astropy</span>
        </div>
      </footer>
    </div>
  );
}
