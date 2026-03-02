'use client';

import Link from 'next/link';

export function LandingPage({ onStart }: { onStart: () => void }) {
    return (
        <div className="flex min-h-screen flex-col bg-slate-950 text-white font-sans overflow-hidden">
            {/* Navigation */}
            <nav className="flex items-center justify-between p-8 border-b border-slate-800 bg-slate-950/50 backdrop-blur-md sticky top-0 z-50">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center font-black text-slate-950">A</div>
                    <span className="text-xl font-black tracking-tight">AXON INVOICE</span>
                </div>
                <div className="flex items-center gap-6">
                    <button className="text-slate-400 hover:text-white font-bold transition-colors cursor-default">Log in</button>
                </div>
            </nav>

            {/* Hero Section */}
            <main className="flex-1 flex flex-col items-center justify-center p-8 text-center relative">
                {/* Background Decorations */}
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[128px] -z-10 animate-pulse"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[128px] -z-10 animate-pulse" style={{ animationDelay: '2s' }}></div>

                <div className="max-w-4xl space-y-8">
                    <h1 className="text-7xl font-black tracking-tight leading-none bg-gradient-to-b from-white to-slate-500 bg-clip-text text-transparent">
                        Revolutionize Your <br /> Invoice Processing
                    </h1>
                    <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed font-medium">
                        Harness the power of agentic AI to extract, validate, and verify invoices with 99.8% accuracy. Automate your accounts payable workflow in minutes.
                    </p>
                    <div className="flex items-center justify-center gap-6 pt-8">
                        <button
                            onClick={onStart}
                            className="bg-blue-600 text-white px-10 py-5 rounded-full font-black text-xl hover:bg-blue-500 hover:scale-105 active:scale-95 transition-all shadow-2xl shadow-blue-500/20"
                        >
                            Start
                        </button>
                    </div>
                </div>

                {/* Capabilities Grid */}
                <div className="grid md:grid-cols-3 gap-8 mt-32 max-w-6xl w-full">
                    <div className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 backdrop-blur-sm hover:border-blue-500/50 transition-all group">
                        <div className="w-12 h-12 bg-blue-500/20 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-bold mb-3">AI Extraction</h3>
                        <p className="text-slate-500 font-medium">Precision OCR & NLP engines extract line items, taxes, and vendor details automatically.</p>
                    </div>

                    <div className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 backdrop-blur-sm hover:border-purple-500/50 transition-all group">
                        <div className="w-12 h-12 bg-purple-500/20 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-bold mb-3">Agentic Validation</h3>
                        <p className="text-slate-500 font-medium">Autonomous agents cross-check data against your business rules and historical records.</p>
                    </div>

                    <div className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 backdrop-blur-sm hover:border-green-500/50 transition-all group">
                        <div className="w-12 h-12 bg-green-500/20 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                        </div>
                        <h3 className="text-xl font-bold mb-3">Human-in-the-Loop</h3>
                        <p className="text-slate-500 font-medium">Intuitive review interface for complex cases, ensuring 100% confidence in every payment.</p>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="p-12 border-t border-slate-900 mt-32 text-center text-slate-600 font-medium">
                <p>&copy; 2026 AXON INVOICE AI. All rights reserved.</p>
            </footer>
        </div>
    );
}
