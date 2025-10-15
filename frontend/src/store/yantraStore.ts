import { create } from 'zustand';

export interface Location {
  name: string;
  latitude: number;
  longitude: number;
  elevation: number;
  timezone: string;
}

export interface SolarPosition {
  timestamp: string;
  altitude: number;
  azimuth: number;
  declination: number;
  hour_angle: number;
  refraction_corrected: boolean;
}

export interface ValidationResult {
  timestamp: string;
  location: Location;
  predicted_position: SolarPosition;
  actual_position: SolarPosition;
  altitude_error: number;
  azimuth_error: number;
  rms_error: number;
  max_error: number;
  accuracy_level: 'excellent' | 'good' | 'acceptable' | 'poor';
}

export interface Dimension {
  value: number;
  tolerance: number;
  unit: string;
  description?: string;
}

export interface YantraDimensions {
  overall_length: Dimension;
  overall_width: Dimension;
  overall_height: Dimension;
  critical_dimensions: Record<string, any>;
  bom_items: Array<Record<string, any>>;
}

export interface ExportFile {
  format: string;
  url: string;
  size_bytes: number;
  checksum: string;
  expires_at: string;
  filename: string;
}

export interface YantraGeneration {
  id: string;
  yantra_type: 'samrat' | 'rama';
  location: Location;
  scale: number;
  dimensions: YantraDimensions;
  validation: ValidationResult;
  exports: ExportFile[];
  preview_url?: string;
  generated_at: string;
  processing_time_ms: number;
  metadata: Record<string, any>;
}

interface YantraStore {
  location: Location | null;
  currentGeneration: YantraGeneration | null;
  isGenerating: boolean;
  error: string | null;
  
  setLocation: (location: Location) => void;
  setGeneration: (generation: YantraGeneration) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setError: (error: string | null) => void;
  clearGeneration: () => void;
}

export const useYantraStore = create<YantraStore>((set) => ({
  location: null,
  currentGeneration: null,
  isGenerating: false,
  error: null,
  
  setLocation: (location) => set({ location }),
  
  setGeneration: (generation) => set({ 
    currentGeneration: generation,
    error: null 
  }),
  
  setIsGenerating: (isGenerating) => set({ isGenerating }),
  
  setError: (error) => set({ error }),
  
  clearGeneration: () => set({ 
    currentGeneration: null,
    error: null 
  }),
}));