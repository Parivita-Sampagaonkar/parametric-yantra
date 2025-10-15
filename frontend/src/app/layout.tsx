import type { Metadata } from 'next';
import './globals.css';
import { Rajdhani, Cinzel } from 'next/font/google';

const rajdhani = Rajdhani({ subsets: ['latin'], weight: ['400','500','600','700'] });
const cinzel = Cinzel({ subsets: ['latin'], weight: ['600','700','800'] });

export const metadata: Metadata = {
  title: 'Parametric Yantra Generator | Ancient Astronomy Meets Modern Tech',
  description:
    "Generate scientifically accurate astronomical instruments from India's Jantar Mantar observatories, adapted to any location on Earth.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body
        className={`${rajdhani.className} antialiased min-h-screen bg-[radial-gradient(1200px_800px_at_70%_-10%,rgba(251,191,36,0.08),rgba(0,0,0,0)),radial-gradient(800px_600px_at_10%_10%,rgba(3,105,161,0.25),rgba(0,0,0,0)),linear-gradient(180deg,#050718,#0c1430)] text-slate-100`}
      >
        {/* gold title font utility */}
        <div className={`${cinzel.className} sr-only`} />
        {children}
      </body>
    </html>
  );
}
