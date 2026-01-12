'use client'

import { SitaraHeroSection } from '@/components/ui/sitara-hero-section'
import Link from 'next/link'
import '../sitara-hero.css'

export default function HeroPage() {
  return (
    <>
      <SitaraHeroSection />
      
      {/* Call to action at the end of scroll */}
      <div className="fixed bottom-32 left-1/2 -translate-x-1/2 z-50 opacity-0 animate-fade-in" style={{ animationDelay: '2s', animationFillMode: 'forwards' }}>
        <Link 
          href="/"
          className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg hover:shadow-2xl hover:scale-105 duration-300"
        >
          Enter SITARA Platform
        </Link>
      </div>

      <style jsx>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in {
          animation: fade-in 1s ease-out;
        }
      `}</style>
    </>
  )
}
