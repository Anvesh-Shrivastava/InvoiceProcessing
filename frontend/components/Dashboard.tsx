'use client';

import { useState, useEffect, useRef } from 'react';

interface Job {
    id: string;
    filename: string;
    status: string;
    storage_url: string;
    extraction_data: any;
    validation_results: any;
    thc_content: number;
    created_at: string;
}

export function Dashboard() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [uploading, setUploading] = useState(false);
    const [selectedJob, setSelectedJob] = useState<Job | null>(null);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Poll for jobs
    useEffect(() => {
        const fetchJobs = async () => {
            try {
                const res = await fetch('http://127.0.0.1:8000/jobs');
                if (!res.ok) throw new Error("Backend unreachable");
                const data = await res.json();
                setJobs(data);
                setError(null);
            } catch (error) {
                console.error("Error fetching jobs:", error);
            }
        };

        fetchJobs();
        const interval = setInterval(fetchJobs, 5000); // 5s interval
        return () => clearInterval(interval);
    }, []);

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        setUploading(true);
        setError(null);
        const formData = new FormData();
        Array.from(files).forEach(file => formData.append('files', file));

        try {
            const res = await fetch('http://127.0.0.1:8000/upload', {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Upload failed");
            }
        } catch (error: any) {
            console.error("Upload failed:", error);
            setError(error.message);
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleVerify = async (jobId: string, data: any) => {
        try {
            setError(null);
            const res = await fetch(`http://127.0.0.1:8000/jobs/${jobId}/verify`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (res.ok) {
                setSelectedJob(null);
            } else {
                const errData = await res.json();
                throw new Error(errData.detail || "Verification failed");
            }
        } catch (error: any) {
            console.error("Verification failed:", error);
            setError(`Verification failed: ${error.message}`);
        }
    };

    return (
        <main className="flex min-h-screen bg-slate-950 text-white font-sans">
            {/* Sidebar */}
            <div className="w-80 border-r border-slate-800 bg-slate-900/50 backdrop-blur-md flex flex-col h-screen overflow-hidden">
                <div className="p-6 border-b border-slate-800">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <span className="w-3 h-3 bg-blue-500 rounded-full animate-pulse"></span>
                        Active Jobs
                    </h2>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {jobs.map(job => (
                        <div
                            key={job.id}
                            onClick={() => setSelectedJob(job)}
                            className={`p-4 rounded-xl border transition-all cursor-pointer group ${selectedJob?.id === job.id
                                ? 'bg-blue-600/20 border-blue-500 shadow-lg shadow-blue-500/10'
                                : 'bg-slate-900 border-slate-800 hover:border-slate-600'
                                }`}
                        >
                            <div className="flex justify-between items-start mb-2">
                                <span className="text-xs font-mono text-slate-500 truncate w-32">{job.id}</span>
                                <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase ${job.status === 'COMPLETED' ? 'bg-green-500/20 text-green-400' :
                                    job.status.includes('FAILED') ? 'bg-red-500/20 text-red-400' :
                                        'bg-blue-500/20 text-blue-400'
                                    }`}>
                                    {job.status.split(':')[0]}
                                </span>
                            </div>
                            <p className="text-sm font-semibold truncate text-slate-200">{job.filename}</p>
                            <div className="mt-3 w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                                <div className={`h-full transition-all duration-1000 ${job.status === 'COMPLETED' ? 'w-full bg-green-500' :
                                    job.status === 'VERIFYING' ? 'w-3/4 bg-yellow-500' :
                                        job.status === 'VALIDATING' ? 'w-1/2 bg-blue-500' :
                                            'w-1/4 bg-slate-500'
                                    }`}></div>
                            </div>
                        </div>
                    ))}
                    {jobs.length === 0 && (
                        <div className="text-center py-12 text-slate-600 italic">No jobs yet</div>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col h-screen overflow-hidden">
                {!selectedJob ? (
                    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
                        <h1 className="text-5xl font-black mb-6 tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            Agentic Invoice Pipeline
                        </h1>
                        <p className="text-xl text-slate-400 mb-12 max-w-2xl leading-relaxed">
                            Upload multiple invoices to trigger our 3-stage agentic workflow:
                            <span className="text-blue-400"> Extraction</span>,
                            <span className="text-purple-400"> Validation</span>, and
                            <span className="text-green-400"> Human Review</span>.
                        </p>

                        <div className="relative group">
                            <input
                                type="file"
                                multiple
                                onChange={handleUpload}
                                className="hidden"
                                id="file-upload"
                                ref={fileInputRef}
                                disabled={uploading}
                            />
                            <label
                                htmlFor="file-upload"
                                className={`cursor-pointer bg-white text-slate-950 px-12 py-5 rounded-full font-black text-xl transition-all shadow-2xl hover:scale-105 active:scale-95 flex items-center gap-3 ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                            >
                                {uploading ? (
                                    <>
                                        <span className="w-5 h-5 border-2 border-slate-900 border-t-transparent rounded-full animate-spin"></span>
                                        Uploading...
                                    </>
                                ) : (
                                    <>
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 4v16m8-8H4" />
                                        </svg>
                                        Process Invoices
                                    </>
                                )}
                            </label>
                            {error && (
                                <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-400 font-bold max-w-md mx-auto">
                                    <p className="text-sm">Error: {error}</p>
                                </div>
                            )}
                            <div className="mt-4 text-slate-500 font-medium">Select one or more images</div>
                        </div>
                    </div>
                ) : (
                    /* Human Verification View */
                    <div className="flex-1 flex flex-col overflow-hidden bg-slate-900/30">
                        <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-950/80 backdrop-blur-md">
                            <div>
                                <h3 className="text-2xl font-black tracking-tight">{selectedJob.filename}</h3>
                                <p className="text-slate-500 font-mono text-sm">{selectedJob.id}</p>
                            </div>
                            <div className="flex gap-4">
                                <button
                                    onClick={() => setSelectedJob(null)}
                                    className="px-6 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg font-bold transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={() => handleVerify(selectedJob.id, selectedJob.extraction_data)}
                                    disabled={selectedJob.status === 'COMPLETED'}
                                    className={`px-8 py-2 rounded-lg font-bold transition-all ${selectedJob.status === 'COMPLETED'
                                        ? 'bg-green-600/50 cursor-not-allowed'
                                        : 'bg-green-600 hover:bg-green-500 shadow-lg shadow-green-500/20'
                                        }`}
                                >
                                    {selectedJob.status === 'COMPLETED' ? 'Verified' : 'Approve & Inventory'}
                                </button>
                            </div>
                        </div>

                        <div className="flex-1 flex overflow-hidden">
                            {/* Left: Image View */}
                            <div className="flex-1 p-8 bg-black/50 overflow-y-auto flex items-center justify-center border-r border-slate-800">
                                <img
                                    src={selectedJob.storage_url}
                                    alt="Invoice preview"
                                    className="max-w-full h-auto shadow-2xl rounded-sm border border-slate-800"
                                />
                            </div>

                            {/* Right: Data View */}
                            <div className="w-[450px] p-8 bg-slate-950 overflow-y-auto">
                                <div className="space-y-8">
                                    {/* Extraction Section */}
                                    <section>
                                        <h4 className="text-xs font-black text-blue-500 uppercase tracking-widest mb-4">Phase 1: Extraction Data</h4>
                                        <div className="grid gap-4">
                                            {selectedJob.extraction_data && Object.entries(selectedJob.extraction_data).map(([key, value]) => (
                                                <div key={key} className="bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                                                    <label className="text-[10px] text-slate-500 uppercase font-black block mb-1">{key.replace('_', ' ')}</label>
                                                    <input
                                                        type="text"
                                                        value={String(value)}
                                                        onChange={(e) => {
                                                            const newData = { ...selectedJob.extraction_data, [key]: e.target.value };
                                                            setSelectedJob({ ...selectedJob, extraction_data: newData });
                                                        }}
                                                        className="bg-transparent w-full text-slate-200 font-medium focus:outline-none"
                                                    />
                                                </div>
                                            ))}
                                        </div>
                                    </section>

                                    {/* Validation Section */}
                                    <section>
                                        <h4 className="text-xs font-black text-purple-500 uppercase tracking-widest mb-4">Phase 2: Agent Validation</h4>
                                        {selectedJob.validation_results ? (
                                            <div className={`p-6 rounded-2xl border ${selectedJob.validation_results.valid
                                                ? 'bg-green-500/10 border-green-500/30'
                                                : 'bg-red-500/10 border-red-500/30'
                                                }`}>
                                                <div className="flex items-center gap-3 mb-3">
                                                    <div className={`w-3 h-3 rounded-full ${selectedJob.validation_results.valid ? 'bg-green-500' : 'bg-red-500'}`}></div>
                                                    <span className={`font-black text-sm ${selectedJob.validation_results.valid ? 'text-green-400' : 'text-red-400'}`}>
                                                        {selectedJob.validation_results.valid ? 'PASSED' : 'FLAGGED'}
                                                    </span>
                                                </div>
                                                <p className="text-sm text-slate-300 leading-relaxed font-medium">
                                                    {selectedJob.validation_results.message}
                                                </p>
                                                {selectedJob.thc_content && (
                                                    <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center text-xs">
                                                        <span className="text-slate-500 font-bold uppercase">THC Concentration</span>
                                                        <span className={`font-black ${Number(selectedJob.thc_content) > 35 ? 'text-red-400' : 'text-green-400'}`}>
                                                            {selectedJob.thc_content}%
                                                        </span>
                                                    </div>
                                                )}
                                            </div>
                                        ) : (
                                            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-center">
                                                <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                                                <p className="text-xs text-slate-500 font-bold">Groq Agent is validating results...</p>
                                            </div>
                                        )}
                                    </section>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </main>
    );
}
