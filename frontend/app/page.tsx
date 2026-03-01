import { auth } from "@/lib/auth";
import { headers } from "next/headers";

export default async function Home() {
    const session = await auth.api.getSession({
        headers: await headers()
    });

    return (
        <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-slate-900 text-white">
            <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex">
                <h1 className="text-4xl font-bold mb-8">Invoice AI Processor</h1>
            </div>

            <div className="bg-slate-800 p-8 rounded-xl shadow-2xl border border-slate-700">
                {session ? (
                    <div>
                        <p className="text-xl mb-4">Welcome, {session.user.name}</p>
                        <div className="flex flex-col gap-4">
                            <button className="bg-blue-600 hover:bg-blue-500 px-6 py-2 rounded-lg font-semibold transition-colors">
                                Upload Invoice
                            </button>
                            <button className="text-slate-400 hover:text-white transition-colors">
                                Sign Out
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="text-center">
                        <p className="text-xl mb-6">Secure Invoice Processing</p>
                        <button className="bg-slate-100 text-slate-900 hover:bg-white px-8 py-3 rounded-lg font-bold text-lg transition-all transform hover:scale-105">
                            Get Started
                        </button>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mt-16 max-w-6xl">
                <div className="p-6 bg-slate-800/50 rounded-lg border border-slate-700 backdrop-blur-sm">
                    <h3 className="font-bold text-lg mb-2">Automated Extraction</h3>
                    <p className="text-slate-400 text-sm">Powered by Gemini 1.5 Flash for high accuracy OCR and data parsing.</p>
                </div>
                <div className="p-6 bg-slate-800/50 rounded-lg border border-slate-700 backdrop-blur-sm">
                    <h3 className="font-bold text-lg mb-2">Neon Database</h3>
                    <p className="text-slate-400 text-sm">Lightning fast data storage and retrieval using Neon Postgres.</p>
                </div>
                <div className="p-6 bg-slate-800/50 rounded-lg border border-slate-700 backdrop-blur-sm">
                    <h3 className="font-bold text-lg mb-2">Better Auth</h3>
                    <p className="text-slate-400 text-sm">Enterprise-grade authentication with social logins out of the box.</p>
                </div>
            </div>
        </main>
    );
}
