'use client';

import { useState } from 'react';
import { LandingPage } from '@/components/LandingPage';
import { Dashboard } from '@/components/Dashboard';

export default function Page() {
    const [showDashboard, setShowDashboard] = useState(false);

    if (!showDashboard) {
        return <LandingPage onStart={() => setShowDashboard(true)} />;
    }

    return <Dashboard />;
}
