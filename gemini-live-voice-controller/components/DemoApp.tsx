import React from 'react';
import { AppSection, FormDataState } from '../types';

interface DemoAppProps {
  currentSection: AppSection;
  formData: FormDataState;
  onSectionChange: (section: AppSection) => void;
  onFormChange: (field: keyof FormDataState, value: string) => void;
}

export const DemoApp: React.FC<DemoAppProps> = ({
  currentSection,
  formData,
  onSectionChange,
  onFormChange
}) => {
  return (
    <div className="bg-white rounded-xl overflow-hidden shadow-xl h-full flex flex-col border border-slate-200">
      {/* App Header */}
      <div className="bg-indigo-600 p-4 flex justify-between items-center text-white">
        <div className="flex items-center gap-2">
           <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
             <span className="font-bold">A</span>
           </div>
           <span className="font-bold text-lg">Acme Corp App</span>
        </div>
        <div className="text-xs bg-indigo-700 px-2 py-1 rounded">Voice Enabled</div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-200 bg-slate-50">
        {(['dashboard', 'settings', 'profile'] as AppSection[]).map((section) => (
          <button
            key={section}
            onClick={() => onSectionChange(section)}
            className={`flex-1 py-3 text-sm font-medium capitalize transition-colors ${
              currentSection === section
                ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white'
                : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
            }`}
          >
            {section}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="p-6 flex-1 overflow-y-auto bg-slate-50">
        {currentSection === 'dashboard' && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-slate-800">Welcome Back!</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-100">
                <div className="text-sm text-slate-500">Total Users</div>
                <div className="text-2xl font-bold text-indigo-600">1,234</div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow-sm border border-slate-100">
                <div className="text-sm text-slate-500">Revenue</div>
                <div className="text-2xl font-bold text-emerald-600">$45.2k</div>
              </div>
            </div>
            <p className="text-slate-600 text-sm">
              Try saying: <em className="text-indigo-600">"Go to my profile and update my bio."</em>
            </p>
          </div>
        )}

        {currentSection === 'settings' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-slate-800">Settings</h2>
            <p className="text-slate-500 text-sm">Application configuration would go here.</p>
            <div className="p-4 bg-yellow-50 text-yellow-800 rounded-lg text-sm border border-yellow-100">
              Voice control can also toggle switches or sliders if tools are defined for them.
            </div>
          </div>
        )}

        {currentSection === 'profile' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-slate-800">Edit Profile</h2>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">First Name</label>
                  <input
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => onFormChange('firstName', e.target.value)}
                    className="w-full border-slate-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border text-slate-800"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Last Name</label>
                  <input
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => onFormChange('lastName', e.target.value)}
                    className="w-full border-slate-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border text-slate-800"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => onFormChange('email', e.target.value)}
                  className="w-full border-slate-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border text-slate-800"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Bio</label>
                <textarea
                  value={formData.bio}
                  onChange={(e) => onFormChange('bio', e.target.value)}
                  rows={3}
                  className="w-full border-slate-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring-indigo-500 p-2 border text-slate-800"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};