'use client';

import { Canvas } from '@react-three/fiber';
import { Stars, OrbitControls, Effects } from '@react-three/drei';
import { Suspense, useRef } from 'react';
import * as THREE from 'three';

function SunHalo() {
  const mesh = useRef<THREE.Mesh>(null!);
  return (
    <mesh ref={mesh} position={[0, 0, -8]}>
      <sphereGeometry args={[1.2, 32, 32]} />
      <meshBasicMaterial color="#f4c76b" transparent opacity={0.18} />
    </mesh>
  );
}

export default function CosmicBackground() {
  return (
    <div className="absolute inset-0 -z-10">
      <Canvas camera={{ position: [0, 0, 6], fov: 55 }}>
        <Suspense fallback={null}>
          <Stars radius={120} depth={60} count={1500} factor={3} saturation={0} fade />
          <ambientLight intensity={0.25} />
          <pointLight position={[3, 2, 4]} intensity={1.2} color="#f4c76b" />
          <SunHalo />
          {/* soft glow */}
          <Effects disableGamma>
            {/* post-processing bloom-like */}
            {/* drei's Effects wraps three-stdlib EffectComposer; defaults are fine */}
          </Effects>
          <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.25} />
        </Suspense>
      </Canvas>
    </div>
  );
}
