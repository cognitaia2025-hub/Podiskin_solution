import React, { useState, useEffect } from 'react';
import logoPodoskin from '../assets/logo_podoskin.png';
import logoCognita from '../assets/cognita_ia.png';

const DynamicLogo: React.FC = () => {
    const [isFlipped, setIsFlipped] = useState(false);

    useEffect(() => {
        const cycleTimer = setInterval(() => {
            // Flip to Cognita
            setIsFlipped(true);

            // Wait 10 seconds and flip back
            setTimeout(() => {
                setIsFlipped(false);
            }, 10000);
        }, 300000); // 5 minutes

        return () => clearInterval(cycleTimer);
    }, []);

    return (
        <div className="relative w-12 h-12 perspective-1000">
            <div
                className={`relative w-full h-full transition-transform duration-1000 preserve-3d ${isFlipped ? 'rotate-y-180' : ''
                    }`}
            >
                {/* Front: Podoskin */}
                <div className="absolute inset-0 w-full h-full backface-hidden rounded-lg bg-white p-1 flex items-center justify-center shadow-sm border border-gray-100">
                    <img src={logoPodoskin} alt="Podoskin" className="max-w-full max-h-full object-contain" />
                </div>

                {/* Back: Cognita */}
                <div className="absolute inset-0 w-full h-full backface-hidden rotate-y-180 rounded-lg bg-white p-1 flex items-center justify-center shadow-sm border border-gray-100">
                    <img src={logoCognita} alt="Cognita IA" className="max-w-full max-h-full object-contain" />
                </div>
            </div>
        </div>
    );
};

export default DynamicLogo;
