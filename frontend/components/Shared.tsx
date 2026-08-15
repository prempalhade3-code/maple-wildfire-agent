import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { AnimatePresence, motion } from 'framer-motion';

/* ============================================================
   GLOBAL_CSS — injected via dangerouslySetInnerHTML in _app.tsx.
   This is the actual source of truth for fonts + mesh backgrounds
   (it renders after globals.css, so it wins).
   ============================================================ */
export const GLOBAL_CSS = `
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Instrument+Serif:ital@1&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body {
  font-family: 'Inter', 'Outfit', sans-serif;
}

.font-sans { font-family: 'Inter', 'Outfit', sans-serif; }
.font-serif, .italic { font-family: 'Instrument Serif', Georgia, serif; }
.font-mono { font-family: 'JetBrains Mono', monospace; }

/* mesh backdrop base + two variants + drift animation */
.mesh-backdrop {
  position: absolute;
  inset: 0;
  background-size: 200% 200%;
  background-repeat: no-repeat;
  animation: meshDrift 22s ease-in-out infinite alternate;
  will-change: background-position;
  z-index: 0;
}

.mesh-backdrop.forest {
  background-color: #16130f;
  background-image:
    linear-gradient(180deg, rgba(11, 14, 13, 0.22), rgba(11, 14, 13, 0.48)),
    radial-gradient(circle at 50% 48%, rgba(13, 14, 13, 0.03), rgba(10, 12, 11, 0.36)),
    url('/images/maple-hero-wildfire.png');
  background-size: cover;
  background-position: center;
  animation: mapleHeroImageDrift 18s ease-in-out infinite alternate;
}

.mesh-backdrop.ember {
  background-color: #3d0f0f;
  background-image:
    radial-gradient(at 15% 25%, rgba(244, 63, 94, 0.85) 0px, transparent 55%),
    radial-gradient(at 85% 15%, rgba(249, 115, 22, 0.75) 0px, transparent 55%),
    radial-gradient(at 50% 85%, rgba(220, 38, 38, 0.7) 0px, transparent 55%),
    radial-gradient(at 90% 90%, rgba(180, 30, 30, 0.6) 0px, transparent 55%),
    radial-gradient(at 20% 80%, rgba(251, 146, 60, 0.6) 0px, transparent 55%);
}

@keyframes meshDrift {
  0% {
    background-position: 0% 10%, 100% 0%, 40% 100%, 100% 100%, 10% 90%;
  }
  50% {
    background-position: 15% 25%, 85% 20%, 55% 80%, 85% 85%, 20% 75%;
  }
  100% {
    background-position: 5% 15%, 95% 5%, 45% 95%, 95% 90%, 15% 85%;
  }
}

@keyframes mapleHeroImageDrift {
  from { background-position: center 48%; background-size: 104%; }
  to { background-position: center 54%; background-size: 110%; }
}

@media (prefers-reduced-motion: reduce) {
  .mesh-backdrop {
    animation: none;
  }
}

.page-fade {
  animation: pageFadeIn 0.4s ease-out;
}

@keyframes pageFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
`;

/* ============================================================
   NavBar — Home / Why Maple / Meet Maple / Platform, right
   aligned as one cluster, no separate Login button.
   ============================================================ */
const NAV_LINKS = [
  { label: 'Home', href: '/' },
  { label: 'Platform', href: '/platform' },
  { label: 'Why Maple', href: '/why-maple' },
  { label: 'Meet Maple', href: '/console' },
];

export function NavBar({ dark: _dark = false }: { dark?: boolean }) {
  const router = useRouter();

  return (
    <header className="sticky top-0 z-50 h-20 border-b border-black/[0.055] bg-white/95 backdrop-blur-xl transition-all duration-300">
      <div className="w-full h-full px-5 sm:px-8 lg:px-10 flex items-center justify-between">
        <Link href="/" className="maple-wordmark" aria-label="Maple home">
          Maple
        </Link>

        <nav className="hidden md:flex items-center gap-7 lg:gap-8 text-[14px] tracking-[-0.03em] font-normal text-zinc-700 font-sans">
          {NAV_LINKS.map((link) => {
            const isActive = router.pathname === link.href;
            return (
              <Link key={link.href} href={link.href}>
                <span
                  className={`cursor-pointer relative py-2 transition-colors duration-200 after:absolute after:bottom-0 after:left-0 after:h-px after:w-full after:origin-left after:bg-zinc-950 after:transition-transform after:duration-300 ${
                    isActive ? 'text-zinc-950 after:scale-x-100' : 'hover:text-zinc-950 after:scale-x-0 hover:after:scale-x-100'
                  }`}
                >
                  {link.label}
                </span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}

/* ============================================================
   Footer
   ============================================================ */
export function Footer({ dark: _dark = false }: { dark?: boolean }) {
  return (
    <footer className="border-t border-black/[0.06] bg-[#fdfdfc] py-8 px-6 text-center text-xs text-zinc-500 font-sans">
      <div className="max-w-[1140px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 tracking-[-0.01em]">
        <span>© 2026 Maple. All rights reserved.</span>
        <Link href="/console">
          <span className="text-xs font-medium text-zinc-950 hover:underline cursor-pointer">
            Launch Operations Console →
          </span>
        </Link>
      </div>
    </footer>
  );
}

/* ============================================================
   MeshBackdrop — variant="forest" | "ember"
   ============================================================ */
export function MeshBackdrop({ variant = 'forest' }: { variant?: 'forest' | 'ember' }) {
  return <div className={`mesh-backdrop ${variant}`} aria-hidden="true" />;
}

/* ============================================================
   FaqAccordion — items={[{q, a}]}
   ============================================================ */
export function FaqAccordion({ items }: { items: { q: string; a: string }[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <div className="space-y-0">
      {items.map((item, i) => {
        const isOpen = openIndex === i;
        return (
          <div key={i} className="border-b border-zinc-200">
            <button
              onClick={() => setOpenIndex(isOpen ? null : i)}
              className="flex items-center justify-between w-full text-left py-5 group"
            >
              <span className="text-base sm:text-lg text-zinc-800 font-medium group-hover:text-zinc-950 transition-colors font-sans">
                {item.q}
              </span>
              <span className="text-2xl font-light text-zinc-400 group-hover:text-zinc-950 shrink-0 ml-4 transition-transform" style={{ transform: isOpen ? 'rotate(45deg)' : 'none' }}>
                +
              </span>
            </button>
            <AnimatePresence initial={false}>
              {isOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
                  className="overflow-hidden"
                >
                  <p className="text-sm text-zinc-600 leading-relaxed pb-5 pr-8 font-sans">{item.a}</p>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}
