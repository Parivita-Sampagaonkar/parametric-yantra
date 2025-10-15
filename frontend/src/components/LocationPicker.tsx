'use client';

import { useState } from 'react';
import { useYantraStore } from '@/store/yantraStore';
import { MapPin, Search, Navigation, Globe, Check } from 'lucide-react';

const FAMOUS_SITES = [
  {
    name: 'Jaipur Jantar Mantar',
    latitude: 26.9124,
    longitude: 75.7873,
    elevation: 431,
    timezone: 'Asia/Kolkata',
    emoji: '🏛️',
    description: 'Historic observatory, UNESCO World Heritage'
  },
  {
    name: 'Delhi Jantar Mantar',
    latitude: 28.6273,
    longitude: 77.2167,
    elevation: 216,
    timezone: 'Asia/Kolkata',
    emoji: '🕌',
    description: 'Built by Maharaja Jai Singh II in 1724'
  },
  {
    name: 'Ujjain Observatory',
    latitude: 23.1765,
    longitude: 75.7885,
    elevation: 493,
    timezone: 'Asia/Kolkata',
    emoji: '🌟',
    description: 'Ancient astronomical center'
  },
  {
    name: 'Varanasi Observatory',
    latitude: 25.2820,
    longitude: 82.9534,
    elevation: 80,
    timezone: 'Asia/Kolkata',
    emoji: '🛕',
    description: 'Spiritual and astronomical significance'
  },
];

export function LocationPicker() {
  const { location, setLocation } = useYantraStore();
  const [customMode, setCustomMode] = useState(false);
  const [lat, setLat] = useState('');
  const [lon, setLon] = useState('');

  const handlePresetSelect = (site: typeof FAMOUS_SITES[0]) => {
    setLocation(site);
    setCustomMode(false);
  };

  const handleCustomSubmit = () => {
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lon);

    if (isNaN(latitude) || isNaN(longitude)) {
      alert('Invalid coordinates');
      return;
    }

    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
      alert('Coordinates out of range');
      return;
    }

    setLocation({
      name: `Custom (${latitude.toFixed(4)}, ${longitude.toFixed(4)})`,
      latitude,
      longitude,
      elevation: 0,
      timezone: 'UTC',
    });
    setCustomMode(false);
  };

  return (
    <div className="space-y-4">
      {/* Current Location Display */}
      {location && (
        <div className="relative overflow-hidden p-4 rounded-xl bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-2 border-green-500/30 backdrop-blur-sm">
          <div className="absolute top-0 right-0 w-32 h-32 bg-green-500/5 rounded-full blur-2xl" />
          <div className="relative flex items-start gap-3">
            <div className="h-10 w-10 rounded-full bg-green-500/20 border border-green-500/30 flex items-center justify-center flex-shrink-0">
              <MapPin className="h-5 w-5 text-green-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-bold text-white truncate">{location.name}</span>
                <Check className="h-4 w-4 text-green-400" />
              </div>
              <div className="flex items-center gap-3 text-xs text-green-200/80 mb-2">
                <span className="px-2 py-0.5 rounded-md bg-green-500/10 border border-green-500/20">
                  {location.latitude.toFixed(4)}°N
                </span>
                <span className="px-2 py-0.5 rounded-md bg-green-500/10 border border-green-500/20">
                  {location.longitude.toFixed(4)}°E
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs text-green-300/60">
                <Navigation className="h-3 w-3" />
                <span>Elevation: {location.elevation}m</span>
                <span>•</span>
                <Globe className="h-3 w-3" />
                <span>{location.timezone}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Mode Toggle */}
      <div className="grid grid-cols-2 gap-2 p-1 rounded-xl bg-white/5 border border-white/10">
        <button
          onClick={() => setCustomMode(false)}
          className={`px-4 py-2.5 text-sm font-semibold rounded-lg transition-all ${
            !customMode
              ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
              : 'text-blue-200 hover:text-white hover:bg-white/5'
          }`}
        >
          <MapPin className="h-4 w-4 inline mr-2" />
          Famous Sites
        </button>
        <button
          onClick={() => setCustomMode(true)}
          className={`px-4 py-2.5 text-sm font-semibold rounded-lg transition-all ${
            customMode
              ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-lg'
              : 'text-blue-200 hover:text-white hover:bg-white/5'
          }`}
        >
          <Navigation className="h-4 w-4 inline mr-2" />
          Custom
        </button>
      </div>

      {/* Content */}
      {!customMode ? (
        <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
          {FAMOUS_SITES.map((site, index) => (
            <button
              key={site.name}
              onClick={() => handlePresetSelect(site)}
              className={`group w-full p-4 text-left rounded-xl border-2 transition-all ${
                location?.name === site.name
                  ? 'bg-gradient-to-r from-blue-500/20 to-purple-500/20 border-blue-400/50 shadow-lg'
                  : 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
              }`}
            >
              <div className="flex items-start gap-3">
                <div className="text-3xl">{site.emoji}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold text-white truncate">{site.name}</span>
                    {location?.name === site.name && (
                      <div className="h-2 w-2 bg-blue-400 rounded-full animate-pulse" />
                    )}
                  </div>
                  <p className="text-xs text-blue-300/70 mb-2">{site.description}</p>
                  <div className="flex items-center gap-2 text-xs text-blue-300/60">
                    <span className="px-2 py-0.5 rounded bg-white/5">
                      {site.latitude.toFixed(2)}°N
                    </span>
                    <span className="px-2 py-0.5 rounded bg-white/5">
                      {site.longitude.toFixed(2)}°E
                    </span>
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-blue-200 mb-2 flex items-center gap-2">
                <Navigation className="h-3 w-3" />
                Latitude (-90 to 90)
              </label>
              <input
                type="number"
                value={lat}
                onChange={(e) => setLat(e.target.value)}
                placeholder="26.9124"
                step="0.0001"
                className="w-full px-4 py-3 bg-white/5 border-2 border-white/10 rounded-xl text-white placeholder-blue-400/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-blue-200 mb-2 flex items-center gap-2">
                <Globe className="h-3 w-3" />
                Longitude (-180 to 180)
              </label>
              <input
                type="number"
                value={lon}
                onChange={(e) => setLon(e.target.value)}
                placeholder="75.7873"
                step="0.0001"
                className="w-full px-4 py-3 bg-white/5 border-2 border-white/10 rounded-xl text-white placeholder-blue-400/40 focus:outline-none focus:border-purple-500/50 focus:bg-white/10 transition-all"
              />
            </div>
          </div>
          <button
            onClick={handleCustomSubmit}
            className="w-full py-3 bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white text-sm font-bold rounded-xl transition-all shadow-lg hover:shadow-xl hover:shadow-purple-500/30"
          >
            <Navigation className="h-4 w-4 inline mr-2" />
            Set Custom Location
          </button>
        </div>
      )}

      {/* Quick Actions */}
      <div className="pt-3 border-t border-white/10">
        <button className="w-full px-4 py-3 text-sm font-medium text-blue-200 hover:text-white transition-colors flex items-center justify-center gap-2 rounded-xl hover:bg-white/5 group">
          <Search className="h-4 w-4 group-hover:scale-110 transition-transform" />
          <span>Search on Map</span>
          <span className="px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300 text-xs font-semibold">
            Coming Soon
          </span>
        </button>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(59, 130, 246, 0.3);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(59, 130, 246, 0.5);
        }
      `}</style>
    </div>
  );
}