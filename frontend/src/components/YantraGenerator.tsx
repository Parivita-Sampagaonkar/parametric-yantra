'use client';

import { useState } from 'react';
import { useYantraStore } from '@/store/yantraStore';
import { generateYantra } from '@/lib/api';
import { Sparkles, Layers, Ruler, Scissors, ToggleLeft, ToggleRight, AlertCircle } from 'lucide-react';

type YantraType = 'samrat' | 'rama';

export function YantraGenerator() {
  const { setGeneration, setIsGenerating, location, setError } = useYantraStore();
  const [yantraType, setYantraType] = useState<YantraType>('samrat');
  const [scale, setScale] = useState(2.0);
  const [materialThickness, setMaterialThickness] = useState(0.012);
  const [kerfCompensation, setKerfCompensation] = useState(0.002);
  const [includeBase, setIncludeBase] = useState(true);
  const [localErr, setLocalErr] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!location) {
      setLocalErr('Please select a location first');
      return;
    }
    setLocalErr(null);
    setError(null);
    setIsGenerating(true);
    try {
      const result = await generateYantra({
        yantra_type: yantraType,
        location,
        scale,
        material_thickness: materialThickness,
        kerf_compensation: kerfCompensation,
        include_base: includeBase,
      });
      setGeneration(result);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || 'Generation failed';
      setLocalErr(msg);
      setError(msg);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Yantra Type Selection */}
      <div>
        <label className="block text-sm font-semibold text-blue-200 mb-3 flex items-center gap-2">
          <Layers className="h-4 w-4" />
          Yantra Type
        </label>
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => setYantraType('samrat')}
            className={`group relative p-4 rounded-xl border-2 transition-all ${
              yantraType === 'samrat'
                ? 'bg-gradient-to-br from-amber-500/20 to-orange-600/20 border-amber-500/50 shadow-lg shadow-amber-500/20'
                : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
            }`}
          >
            <div className="text-3xl mb-2">🌅</div>
            <div className="text-base font-bold text-white mb-1">Samrat</div>
            <div className="text-xs text-blue-300/70">Equatorial Sundial</div>
            {yantraType === 'samrat' && (
              <div className="absolute top-2 right-2">
                <div className="h-2 w-2 bg-amber-400 rounded-full animate-pulse" />
              </div>
            )}
          </button>
          <button
            onClick={() => setYantraType('rama')}
            className={`group relative p-4 rounded-xl border-2 transition-all ${
              yantraType === 'rama'
                ? 'bg-gradient-to-br from-blue-500/20 to-indigo-600/20 border-blue-500/50 shadow-lg shadow-blue-500/20'
                : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
            }`}
          >
            <div className="text-3xl mb-2">🎯</div>
            <div className="text-base font-bold text-white mb-1">Rama</div>
            <div className="text-xs text-blue-300/70">Alt-Azimuth Pillars</div>
            {yantraType === 'rama' && (
              <div className="absolute top-2 right-2">
                <div className="h-2 w-2 bg-blue-400 rounded-full animate-pulse" />
              </div>
            )}
          </button>
        </div>
      </div>

      {/* Scale Slider */}
      <div>
        <label className="block text-sm font-semibold text-blue-200 mb-3 flex items-center gap-2">
          <Ruler className="h-4 w-4" />
          Scale: <span className="text-amber-400 font-bold">{scale.toFixed(1)}m</span>
        </label>
        <div className="space-y-2">
          <input
            type="range"
            min="0.5"
            max="10"
            step="0.5"
            value={scale}
            onChange={(e) => setScale(parseFloat(e.target.value))}
            className="w-full h-3 rounded-lg appearance-none cursor-pointer"
            style={{
              background: `linear-gradient(to right, rgb(251 191 36) 0%, rgb(251 191 36) ${((scale - 0.5) / 9.5) * 100}%, rgba(255,255,255,0.1) ${((scale - 0.5) / 9.5) * 100}%, rgba(255,255,255,0.1) 100%)`
            }}
          />
          <div className="flex justify-between text-xs">
            <span className="px-2 py-1 rounded-md bg-white/5 text-blue-300/80">
              Desktop (0.5m)
            </span>
            <span className="px-2 py-1 rounded-md bg-white/5 text-blue-300/80">
              Monument (10m)
            </span>
          </div>
        </div>
      </div>

      {/* Material Thickness */}
      <div>
        <label className="block text-sm font-semibold text-blue-200 mb-3 flex items-center gap-2">
          <Layers className="h-4 w-4" />
          Material Thickness: <span className="text-green-400 font-bold">{(materialThickness * 1000).toFixed(1)}mm</span>
        </label>
        <input
          type="range"
          min="0.003"
          max="0.050"
          step="0.001"
          value={materialThickness}
          onChange={(e) => setMaterialThickness(parseFloat(e.target.value))}
          className="w-full h-3 rounded-lg appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right, rgb(34 197 94) 0%, rgb(34 197 94) ${((materialThickness - 0.003) / 0.047) * 100}%, rgba(255,255,255,0.1) ${((materialThickness - 0.003) / 0.047) * 100}%, rgba(255,255,255,0.1) 100%)`
          }}
        />
      </div>

      {/* Kerf Compensation */}
      <div>
        <label className="block text-sm font-semibold text-blue-200 mb-3 flex items-center gap-2">
          <Scissors className="h-4 w-4" />
          Kerf Compensation: <span className="text-purple-400 font-bold">{(kerfCompensation * 1000).toFixed(1)}mm</span>
        </label>
        <input
          type="range"
          min="0"
          max="0.010"
          step="0.001"
          value={kerfCompensation}
          onChange={(e) => setKerfCompensation(parseFloat(e.target.value))}
          className="w-full h-3 rounded-lg appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(to right, rgb(168 85 247) 0%, rgb(168 85 247) ${(kerfCompensation / 0.010) * 100}%, rgba(255,255,255,0.1) ${(kerfCompensation / 0.010) * 100}%, rgba(255,255,255,0.1) 100%)`
          }}
        />
      </div>

      {/* Include Base Toggle */}
      <div className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-all">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {includeBase ? (
              <ToggleRight className="h-5 w-5 text-blue-400" />
            ) : (
              <ToggleLeft className="h-5 w-5 text-blue-300/50" />
            )}
            <span className="text-sm font-medium text-white">Include Base Platform</span>
          </div>
          <button
            onClick={() => setIncludeBase(!includeBase)}
            className={`relative inline-flex h-7 w-14 items-center rounded-full transition-colors ${
              includeBase ? 'bg-gradient-to-r from-blue-500 to-blue-600' : 'bg-white/20'
            }`}
          >
            <span
              className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-lg transition-transform ${
                includeBase ? 'translate-x-8' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Error Message */}
      {localErr && (
        <div className="p-4 rounded-xl bg-red-500/10 border-2 border-red-500/30 backdrop-blur-sm">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="text-sm font-semibold text-red-300 mb-1">Generation Error</div>
              <div className="text-xs text-red-200/80">{localErr}</div>
            </div>
          </div>
        </div>
      )}

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={!location}
        className="group relative w-full py-4 bg-gradient-to-r from-amber-500 via-orange-500 to-orange-600 hover:from-amber-600 hover:via-orange-600 hover:to-orange-700 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold rounded-xl transition-all shadow-xl hover:shadow-2xl hover:shadow-amber-500/30 disabled:cursor-not-allowed disabled:opacity-50 overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000" />
        <div className="relative flex items-center justify-center gap-3">
          <Sparkles className="h-6 w-6 group-hover:rotate-12 transition-transform" />
          <span className="text-lg">Generate Yantra</span>
          <Sparkles className="h-6 w-6 group-hover:-rotate-12 transition-transform" />
        </div>
      </button>

      {/* Info Notes */}
      <div className="space-y-2 pt-2 border-t border-white/10">
        <div className="flex items-start gap-2 text-xs text-blue-300/80">
          <span className="text-sm">ℹ️</span>
          <span>Parametric geometry uses your location's latitude for accurate alignment.</span>
        </div>
        <div className="flex items-start gap-2 text-xs text-blue-300/80">
          <span className="text-sm">🎯</span>
          <span>Validation checks against Skyfield ephemeris for scientific accuracy.</span>
        </div>
      </div>
    </div>
  );
}