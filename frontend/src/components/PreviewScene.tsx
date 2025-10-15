'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, ContactShadows } from '@react-three/drei';
import { Suspense } from 'react';

function Yantra() {
  return (
    <group rotation={[Math.PI * -0.1, Math.PI * 0.15, 0]}>
      {/* base */}
      <mesh position={[0, -0.52, 0]}>
        <cylinderGeometry args={[1.2, 1.2, 0.12, 64]} />
        <meshStandardMaterial color="#0d1226" metalness={0.2} roughness={0.6} />
      </mesh>

      {/* equatorial ring */}
      <mesh>
        <torusGeometry args={[1, 0.06, 24, 140]} />
        <meshStandardMaterial color="#f4c76b" metalness={0.85} roughness={0.35} />
      </mesh>

      {/* gnomon (inclined) */}
      <mesh rotation={[0.8, 0, 0]} position={[0, 0.4, 0]}>
        <cylinderGeometry args={[0.03, 0.03, 1.4, 24]} />
        <meshStandardMaterial color="#e9b055" metalness={0.8} roughness={0.3} />
      </mesh>

      {/* subtle hour rods */}
      {Array.from({ length: 12 }).map((_, i) => {
        const a = (i / 12) * Math.PI * 2;
        return (
          <mesh key={i} position={[Math.cos(a) * 0.86, 0, Math.sin(a) * 0.86]} rotation={[0, -a, 0]}>
            <boxGeometry args={[0.3, 0.01, 0.02]} />
            <meshStandardMaterial color="#f1d7a1" metalness={0.5} roughness={0.6} />
          </mesh>
        );
      })}
    </group>
  );
}

export default function PreviewScene() {
  return (
    <Canvas camera={{ position: [0, 0.6, 2.6], fov: 50 }}>
      <Suspense fallback={null}>
        <color attach="background" args={['transparent']} />
        <hemisphereLight intensity={0.6} color="#f4c76b" groundColor="#0a0f1f" />
        <directionalLight position={[3, 4, 2]} intensity={1.1} color="#f4c76b" />
        <Yantra />
        <ContactShadows opacity={0.35} scale={6} blur={2.5} far={2.5} />
        <OrbitControls enablePan={false} />
      </Suspense>
    </Canvas>
  );
}
