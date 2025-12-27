import React from 'react';
import { FileText, Image, History, ClipboardList } from 'lucide-react';
import { clsx } from 'clsx';

interface TabItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

interface TopNavigationProps {
  tabs?: TabItem[];
  activeTab?: string;
  onTabChange?: (tabId: string) => void;
  className?: string;
}

const DEFAULT_TABS: TabItem[] = [
  { id: 'clinical', label: 'Clínico', icon: <ClipboardList className="w-4 h-4" /> },
  { id: 'history', label: 'Historial', icon: <History className="w-4 h-4" /> },
  { id: 'images', label: 'Imágenes', icon: <Image className="w-4 h-4" /> },
];

const TopNavigation: React.FC<TopNavigationProps> = ({
  tabs = DEFAULT_TABS,
  activeTab = 'clinical',
  onTabChange,
  className,
}) => {
  return (
    <div 
      className={clsx(
        'flex items-center gap-1 px-4 py-2 bg-gray-50 border-b border-gray-200',
        className
      )}
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange?.(tab.id)}
          className={clsx(
            'flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors',
            activeTab === tab.id
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
          )}
        >
          {tab.icon}
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export default TopNavigation;
