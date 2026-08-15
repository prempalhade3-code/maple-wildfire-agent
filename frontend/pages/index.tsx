import React from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import Typewriter from 'typewriter-effect';
import { NavBar, Footer, MeshBackdrop, FaqAccordion } from '../components/Shared';

const PARTNERS = ['PacificGrid', 'Sonoma Power', 'Redwood Utility', 'Coastal Energy', 'Sequoia Grid', 'Bluepeak'];

const FAQS = [
  { q: 'Is Maple right for my utility?', a: 'Yes, if you operate high-voltage transmission or sub-transmission lines through wildland-urban interface terrain.' },
  { q: 'Does Maple replace our SCADA system?', a: "No. Maple sits alongside your existing SCADA historian and issues de-energization directives through it — it doesn't replace your relays or breakers." },
  { q: 'How is risk actually scored?', a: 'We combine live wind, humidity, and temperature telemetry with soil moisture, canopy density, and slope data at each 100-foot span.' },
  { q: 'What happens when a span is isolated?', a: 'The affected span de-energizes, compute or critical loads on that segment reroute automatically, and operators get a full SCADA log of the sequence.' },
  { q: 'Can we run this without automatic actuation?', a: 'Yes. Maple can run in advisory-only mode, surfacing risk without ever triggering a breaker trip on its own.' },
];

function RevealHeading({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.h2
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-12%' }}
      variants={{ visible: { transition: { staggerChildren: 0.16 } } }}
      className={`maple-display maple-line-reveal ${className}`}
    >
      {children}
    </motion.h2>
  );
}

function RevealLine({ children }: { children: React.ReactNode }) {
  return <span className="maple-reveal-line"><motion.span variants={{ hidden: { y: '115%', opacity: 0 }, visible: { y: '0%', opacity: 1, transition: { duration: 0.82, ease: [0.22, 1, 0.36, 1] } } }}>{children}</motion.span></span>;
}

export default function Home() {
  return (
    <div className="bg-[#fbfbfd] text-zinc-950 min-h-screen font-sans antialiased selection:bg-zinc-900 selection:text-white page-fade">
      <Head>
        <title>Maple | Surgical Wildfire Grid Safety</title>
        <meta name="description" content="Maple turns physical earth data and live grid telemetry into surgical, span-by-span de-energization directives." />
      </Head>

      <NavBar />

      <main className="w-full pb-20">
        {/* HERO — full-bleed, no rounded card, matches reference exactly */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.7 }}
          className="relative text-center text-white overflow-hidden flex flex-col items-center justify-between h-[calc(100svh-6rem)] min-h-0 my-2 mx-4 sm:mx-8 rounded-[2rem] px-6 pt-10 sm:pt-12 pb-8 sm:pb-10"
        >
          <MeshBackdrop variant="forest" />

          <div className="relative z-10 flex-1 flex flex-col items-center justify-center max-w-4xl mx-auto">
            <h1 className="text-5xl sm:text-6xl md:text-[68px] font-normal tracking-[-0.055em] leading-[1.04] mb-8">
              See the spark <br className="hidden sm:inline" />
              <span className="italic font-normal tracking-[-0.045em]">
                <Typewriter
                  options={{
                    strings: [
                      'before it starts.',
                      'before it spreads.',
                      'before the shutoff.',
                    ],
                    autoStart: true,
                    loop: true,
                    deleteSpeed: 34,
                    delay: 58,
                  }}
                />
              </span>
            </h1>

            <p className="text-[17px] sm:text-[19px] tracking-[-0.025em] text-white/90 max-w-xl font-normal leading-[1.45] mb-10">
              Maple turns live weather and physical-earth intelligence into decisive, span-level protection for the grid.
            </p>

            <Link
              href="/console"
              className="group inline-flex items-center gap-4 rounded-full border border-white/40 bg-white/[0.96] py-2 pl-6 pr-2 text-[15px] font-medium tracking-[-0.025em] text-zinc-950 shadow-[0_10px_30px_rgba(0,0,0,0.13)] transition-all duration-300 hover:-translate-y-1 hover:bg-white hover:shadow-[0_16px_38px_rgba(0,0,0,0.2)] active:scale-[0.98]"
            >
              Explore live risk <span className="flex h-9 w-9 items-center justify-center rounded-full bg-zinc-950 text-lg text-white transition-transform duration-300 group-hover:translate-x-0.5 group-hover:rotate-[-12deg]">↗</span>
            </Link>
          </div>

          <div className="relative z-10 w-full max-w-5xl mx-auto">
            <motion.span
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.7 }}
              transition={{ duration: 0.58, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
              className="text-[10px] font-mono text-white/70 tracking-[0.18em] uppercase mb-5 block"
            >Securing grid segments for</motion.span>
            <div className="maple-marquee" aria-label="Utilities secured by Maple">
              <div className="maple-marquee-track">
                {[...PARTNERS, ...PARTNERS].map((p, i) => <span key={`${p}-${i}`} className="text-[17px] font-medium tracking-[-0.035em] text-white">{p}</span>)}
              </div>
            </div>
          </div>
        </motion.section>

        <div className="maple-reference">
          {/* WHY TEAMS SWITCH */}
          <section className="max-w-[1140px] min-h-[calc(100svh-5rem)] mx-auto px-6 sm:px-10 py-12 sm:py-14 flex flex-col justify-center">
            <div className="mb-16 sm:mb-20">
              <span className="maple-overline mb-7 block">Why grid teams switch</span>
              <RevealHeading className="max-w-[760px]"><RevealLine>Isolate risk how you&apos;ve</RevealLine><RevealLine>always wanted to.</RevealLine></RevealHeading>
            </div>

            <motion.section initial={{ opacity: 0, scale: 0.97 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true, margin: '-12%' }} transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }} className="maple-wildfire-experience" aria-label="Maple wildfire intelligence in action">
              <div className="maple-sky-orb" aria-hidden="true" />
              <div className="maple-scene-grain" aria-hidden="true" />
              <div className="maple-wind maple-wind-one" aria-hidden="true" /><div className="maple-wind maple-wind-two" aria-hidden="true" /><div className="maple-wind maple-wind-three" aria-hidden="true" />
              <div className="maple-embers" aria-hidden="true">{Array.from({ length: 18 }, (_, i) => <i key={i} />)}</div>
              <div className="maple-birds" aria-hidden="true"><i /><i /><i /><i /></div>
              <div className="maple-deer" aria-hidden="true"><i className="maple-deer-body" /><i className="maple-deer-neck" /><i className="maple-deer-head" /><i className="maple-deer-leg maple-deer-leg-a" /><i className="maple-deer-leg maple-deer-leg-b" /><i className="maple-deer-tail" /></div>
              <div className="maple-fox" aria-hidden="true"><i /><i /><i /></div>
              <div className="maple-scene-copy">
                <span className="maple-overline">THE MAPLE WATCHTOWER</span>
                <p>Wind changes. Vegetation dries. One span becomes dangerous.</p>
              </div>
              <div className="maple-risk-story maple-story-weather"><span>34 mph</span><small>wind crossing the ridge</small></div>
              <div className="maple-risk-story maple-story-fuel"><span>9.2%</span><small>live fuel moisture</small></div>
              <div className="maple-signal-beacon"><div className="maple-beacon-rings" /><div className="maple-beacon-core"><span>SPAN 04</span><b>78</b><em>risk</em></div></div>
              <div className="maple-decision"><i>↗</i><div><span>MAPLE DECIDES</span><b>Isolate the line,<br />not the county.</b></div></div>
              <div className="maple-tower maple-tower-left" aria-hidden="true"><i /><i /><i /></div><div className="maple-tower maple-tower-right" aria-hidden="true"><i /><i /><i /></div>
              <svg className="maple-transmission" viewBox="0 0 1200 330" preserveAspectRatio="none" aria-hidden="true"><path className="maple-wire" d="M-20 132 C160 254 276 210 427 140 S713 52 920 150 S1110 193 1230 83" /><path className="maple-wire maple-wire-active" d="M427 140 S713 52 920 150" /><circle cx="427" cy="140" r="7" /><circle className="maple-hot-node" cx="670" cy="75" r="10" /><circle cx="920" cy="150" r="7" /></svg>
              <div className="maple-mountains maple-mountains-back" aria-hidden="true" /><div className="maple-mountains maple-mountains-front" aria-hidden="true" />
              <div className="maple-smoke" aria-hidden="true"><i /><i /><i /><i /></div>
              <div className="maple-fireline" aria-hidden="true">{Array.from({ length: 15 }, (_, i) => <i key={i} />)}</div>
              <div className="maple-forest maple-forest-back" aria-hidden="true">{Array.from({ length: 22 }, (_, i) => <i key={i} />)}</div>
              <div className="maple-forest maple-forest-front" aria-hidden="true">{Array.from({ length: 28 }, (_, i) => <i key={i} />)}</div>
              <div className="maple-experience-footer"><span>Weather, fuel, and terrain flow into every line decision.</span><span><b>14 seconds</b> from signal to action</span></div>
            </motion.section>
          </section>

          {/* OPERATOR EXPERIENCE */}
          <section className="max-w-[1140px] mx-auto px-6 sm:px-10 pt-[150px] pb-[164px]">
            <div className="grid grid-cols-1 lg:grid-cols-[1.05fr_0.82fr] gap-14 lg:gap-16 items-center">
              <motion.div
                initial={{ opacity: 0, x: -28 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-8%' }}
                transition={{ duration: 0.72, ease: [0.22, 1, 0.36, 1] }}
                className="relative maple-texture maple-noise-night rounded-[23px] overflow-hidden p-7 sm:p-9 shadow-[0_18px_45px_rgba(11,21,44,0.2)]"
              >
                <div className="relative z-10 overflow-hidden rounded-[15px] bg-[#fbfbfa] shadow-[0_12px_30px_rgba(0,0,0,0.22)]">
                  <div className="bg-[#f0efed] px-5 py-3 flex items-center gap-2 border-b border-black/[0.06]">
                    <div className="flex gap-1.5"><span className="w-3 h-3 rounded-full bg-[#ff6259]" /><span className="w-3 h-3 rounded-full bg-[#ffbe2e]" /><span className="w-3 h-3 rounded-full bg-[#29c840]" /></div>
                    <span className="mx-auto pr-10 text-[11px] tracking-[-0.02em] text-zinc-400">operator@grid-node — console</span>
                  </div>
                  <div className="min-h-[310px] p-5 sm:p-7 font-mono text-[12px] leading-[1.75] text-zinc-700 whitespace-pre-wrap bg-white">
                    <Typewriter options={{ strings: ['$ maple init grid-node-04\n> Connected. Telemetry span registered.\n\n$ maple check --span 04\n> Running risk evaluation on Span 04...\n> wind 34mph · soil 9% · canopy dense\n> risk: 78% — recommend isolate'], autoStart: true, loop: true, delay: 30, deleteSpeed: 20 }} />
                  </div>
                </div>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 26 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-8%' }} transition={{ duration: 0.7, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}>
                <span className="maple-overline mb-7 block">The operator experience</span>
                <RevealHeading className="mb-9"><RevealLine>Prepare for the storm,</RevealLine><RevealLine><span className="italic font-normal">not just the shutoff.</span></RevealLine></RevealHeading>
                <p className="maple-body max-w-[390px]">Operators get a live CLI and dashboard view into every span&apos;s risk factors, with full SCADA logs from first wind gust to breaker trip.</p>
              </motion.div>
            </div>
          </section>

          {/* CTA */}
          <section className="max-w-[1140px] mx-auto px-6 sm:px-10 pt-[150px] pb-[164px]">
            <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-10%' }} transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }} className="maple-texture maple-noise-ember relative overflow-hidden rounded-[24px] px-8 py-[122px] text-center shadow-[0_18px_45px_rgba(105,12,20,0.16)]">
              <div className="relative z-10">
                <h2 className="mx-auto max-w-[650px] text-[clamp(2.3rem,4vw,3.9rem)] leading-[1.02] tracking-[-0.06em] font-normal text-white">Stop losing whole counties to one hot span.</h2>
                <Link href="/console" className="mt-11 inline-flex items-center gap-3 rounded-full bg-white px-7 py-3.5 text-[15px] font-medium tracking-[-0.025em] text-zinc-950 transition-transform duration-300 hover:-translate-y-1 hover:scale-[1.02] active:scale-[0.98]">Launch Operations Console <span className="text-xl leading-none">→</span></Link>
              </div>
            </motion.div>
          </section>

          {/* FAQ */}
          <section className="max-w-[860px] mx-auto px-6 sm:px-10 pt-[150px] pb-[132px]">
            <motion.div initial={{ opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: '-10%' }} transition={{ duration: 0.65, ease: [0.22, 1, 0.36, 1] }}>
              <h2 className="maple-display mb-11">FAQs</h2>
              <FaqAccordion items={FAQS} />
            </motion.div>
          </section>
        </div>
      </main>

      <Footer />
    </div>
  );
}
