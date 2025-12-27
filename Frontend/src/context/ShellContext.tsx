import React, { createContext, useContext, useState, type ReactNode } from 'react';

interface ShellContextType {
    sidebarContent: ReactNode;
    setSidebarContent: (content: ReactNode) => void;
}

const ShellContext = createContext<ShellContextType | undefined>(undefined);

export const ShellProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [sidebarContent, setSidebarContent] = useState<ReactNode>(null);

    return (
        <ShellContext.Provider value={{ sidebarContent, setSidebarContent }}>
            {children}
        </ShellContext.Provider>
    );
};

export const useShell = () => {
    const context = useContext(ShellContext);
    if (!context) {
        throw new Error('useShell must be used within a ShellProvider');
    }
    return context;
};
