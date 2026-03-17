"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, Text, OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import type { Opportunity } from "../data/opportunities";
import { calculateWeightedScore } from "../data/opportunities";

function OpportunitySphere({
  opportunity,
  position,
  isSelected,
  onClick,
}: {
  opportunity: Opportunity;
  position: [number, number, number];
  isSelected: boolean;
  onClick: () => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const score = calculateWeightedScore(opportunity.scores);
  const size = 0.3 + (score / 10) * 0.5;

  const color = new THREE.Color(opportunity.color);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.scale.setScalar(
        isSelected ? 1.3 + Math.sin(state.clock.elapsedTime * 3) * 0.1 : 1
      );
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
      <group position={position}>
        <mesh ref={meshRef} onClick={onClick}>
          <sphereGeometry args={[size, 32, 32]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={isSelected ? 0.8 : 0.3}
            roughness={0.2}
            metalness={0.8}
            transparent
            opacity={isSelected ? 1 : 0.85}
          />
        </mesh>
        {/* Glow ring */}
        {isSelected && (
          <mesh rotation={[Math.PI / 2, 0, 0]}>
            <torusGeometry args={[size + 0.15, 0.02, 16, 32]} />
            <meshBasicMaterial color={opportunity.color} transparent opacity={0.6} />
          </mesh>
        )}
        <Text
          position={[0, size + 0.3, 0]}
          fontSize={0.18}
          color="white"
          anchorX="center"
          anchorY="bottom"
          outlineWidth={0.02}
          outlineColor="black"
        >
          {opportunity.icon} {opportunity.shortName}
        </Text>
        <Text
          position={[0, -size - 0.2, 0]}
          fontSize={0.14}
          color={opportunity.color}
          anchorX="center"
          anchorY="top"
          font={undefined}
        >
          {score.toFixed(1)}/10
        </Text>
      </group>
    </Float>
  );
}

function ParticleField() {
  const points = useRef<THREE.Points>(null);
  const count = 500;

  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      arr[i * 3] = (Math.random() - 0.5) * 30;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 30;
      arr[i * 3 + 2] = (Math.random() - 0.5) * 30;
    }
    return arr;
  }, []);

  useFrame((state) => {
    if (points.current) {
      points.current.rotation.y = state.clock.elapsedTime * 0.02;
      points.current.rotation.x = state.clock.elapsedTime * 0.01;
    }
  });

  return (
    <points ref={points}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial size={0.03} color="#7c3aed" transparent opacity={0.6} sizeAttenuation />
    </points>
  );
}

export default function Scene3D({
  opportunities,
  selectedId,
  onSelect,
}: {
  opportunities: Opportunity[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}) {
  const positions: [number, number, number][] = useMemo(() => {
    const sorted = [...opportunities].sort(
      (a, b) => calculateWeightedScore(b.scores) - calculateWeightedScore(a.scores)
    );
    return sorted.map((_, i) => {
      const angle = (i / sorted.length) * Math.PI * 2;
      const radius = 3 + (i / sorted.length) * 2;
      const y = (sorted.length / 2 - i) * 0.3;
      return [Math.cos(angle) * radius, y, Math.sin(angle) * radius];
    });
  }, [opportunities]);

  const sorted = useMemo(
    () =>
      [...opportunities].sort(
        (a, b) => calculateWeightedScore(b.scores) - calculateWeightedScore(a.scores)
      ),
    [opportunities]
  );

  return (
    <div className="w-full h-[500px] relative rounded-2xl overflow-hidden border border-purple-900/30">
      <div className="absolute top-4 left-4 z-10 text-sm text-purple-300/70">
        Drag to rotate / Scroll to zoom / Click a sphere
      </div>
      <Canvas camera={{ position: [0, 3, 10], fov: 55 }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1} color="#7c3aed" />
        <pointLight position={[-10, -10, -10]} intensity={0.5} color="#3b82f6" />
        <spotLight position={[0, 15, 0]} intensity={0.8} color="#fbbf24" angle={0.3} />
        <ParticleField />
        {sorted.map((opp, i) => (
          <OpportunitySphere
            key={opp.id}
            opportunity={opp}
            position={positions[i]}
            isSelected={selectedId === opp.id}
            onClick={() => onSelect(opp.id)}
          />
        ))}
        <OrbitControls
          enableDamping
          dampingFactor={0.05}
          rotateSpeed={0.5}
          minDistance={5}
          maxDistance={20}
        />
      </Canvas>
    </div>
  );
}
