import React, { useEffect, useRef } from 'react';

const NeuralBackground = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) {
      console.error('NeuralBackground: Canvas ref is null');
      return;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      console.error('NeuralBackground: Could not get 2d context');
      return;
    }
    
    console.log('NeuralBackground: Initializing animation');
    let animationFrameId;
    let particles = [];
    let time = 0;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Particle class - with subtle floating movement
    class Particle {
      constructor() {
        this.baseX = Math.random() * canvas.width;
        this.baseY = Math.random() * canvas.height;
        this.x = this.baseX;
        this.y = this.baseY;
        this.baseRadius = Math.random() * 2 + 1.5; // Larger base to prevent negative radius
        this.pulseSpeed = Math.random() * 0.02 + 0.01;
        this.pulseOffset = Math.random() * Math.PI * 2;
        
        // Subtle floating movement properties
        this.floatSpeedX = Math.random() * 0.001 + 0.0005; // Slow but visible
        this.floatSpeedY = Math.random() * 0.001 + 0.0005;
        this.floatOffsetX = Math.random() * Math.PI * 2;
        this.floatOffsetY = Math.random() * Math.PI * 2;
        this.floatRange = 30; // Movement range in pixels
      }

      update(time) {
        // Subtle floating animation - moves in a slow sine wave pattern
        this.x = this.baseX + Math.sin(time * this.floatSpeedX + this.floatOffsetX) * this.floatRange;
        this.y = this.baseY + Math.cos(time * this.floatSpeedY + this.floatOffsetY) * this.floatRange;
      }

      draw(time) {
        // Pulsating radius - ensure it's always positive
        const pulse = Math.sin(time * this.pulseSpeed + this.pulseOffset);
        const radius = this.baseRadius * (1 + pulse * 0.3); // Multiply instead of add
        
        // Pulsating opacity - VERY VISIBLE for debugging
        const opacity = 0.4 + (pulse * 0.2);

        ctx.beginPath();
        ctx.arc(this.x, this.y, radius, 0, Math.PI * 2);
        
        // Gradient for softer glow
        const gradient = ctx.createRadialGradient(
          this.x, this.y, 0,
          this.x, this.y, radius * 4
        );
        gradient.addColorStop(0, `rgba(255, 54, 33, ${opacity})`);
        gradient.addColorStop(0.5, `rgba(255, 54, 33, ${opacity * 0.5})`);
        gradient.addColorStop(1, 'rgba(255, 54, 33, 0)');
        
        ctx.fillStyle = gradient;
        ctx.fill();
        ctx.closePath();
      }
    }

    // Create particles - MORE for debugging visibility
    const particleCount = Math.floor((canvas.width * canvas.height) / 15000);
    console.log(`NeuralBackground: Creating ${particleCount} particles`);
    for (let i = 0; i < particleCount; i++) {
      particles.push(new Particle());
    }

    // Draw connections between nearby particles
    const drawConnections = (time) => {
      const maxDistance = 200;
      const basePulse = Math.sin(time * 0.005) * 0.5 + 0.5;
      
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < maxDistance) {
            const distanceFactor = 1 - distance / maxDistance;
            const opacity = distanceFactor * 0.3 * basePulse; // VERY VISIBLE for debugging
            
            ctx.beginPath();
            ctx.strokeStyle = `rgba(255, 54, 33, ${opacity})`;
            ctx.lineWidth = 1.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
            ctx.closePath();
          }
        }
      }
    };

    // Animation loop
    const animate = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update particle positions
      particles.forEach(particle => {
        particle.update(time);
      });

      // Draw connections first (behind particles)
      drawConnections(time);

      // Draw particles with pulsating effect
      particles.forEach(particle => {
        particle.draw(time);
      });

      time += 1;
      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100vh',
        zIndex: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
        backgroundColor: 'rgba(255, 0, 0, 0.05)', // DEBUG: Red tint to verify it's rendering
      }}
    >
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
        }}
      />
      {/* Gradient fade from top to bottom - REDUCED for debugging */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'linear-gradient(to bottom, rgba(15, 31, 36, 0) 0%, rgba(15, 31, 36, 0) 60%, rgba(15, 31, 36, 0.8) 100%)',
          pointerEvents: 'none',
        }}
      />
    </div>
  );
};

export default NeuralBackground;
