import React from 'react';
import { Keyboard, X } from 'lucide-react';
import { KeyboardShortcut, formatShortcut } from '../utils/useKeyboardShortcuts';

interface ShortcutsHelpProps {
  isOpen: boolean;
  onClose: () => void;
  shortcuts: KeyboardShortcut[];
}

export const ShortcutsHelp: React.FC<ShortcutsHelpProps> = ({
  isOpen,
  onClose,
  shortcuts,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border-2 border-slate-700 rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-600 rounded-lg">
              <Keyboard size={20} className="text-white" />
            </div>
            <h2 className="text-xl font-bold text-slate-100">Keyboard Shortcuts</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-slate-200"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="space-y-3">
            {shortcuts.map((shortcut, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-slate-600 transition-colors"
              >
                <div className="flex-1">
                  <p className="text-sm font-medium text-slate-200">
                    {shortcut.description}
                  </p>
                </div>
                <div className="flex gap-1">
                  {formatShortcut(shortcut)
                    .split(' + ')
                    .map((key, i, arr) => (
                      <React.Fragment key={i}>
                        <kbd className="px-3 py-1.5 bg-slate-900 border border-slate-600 rounded text-xs font-mono text-slate-300 shadow-sm min-w-[2.5rem] text-center">
                          {key}
                        </kbd>
                        {i < arr.length - 1 && (
                          <span className="text-slate-600 self-center px-1">+</span>
                        )}
                      </React.Fragment>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-700 bg-slate-900/50">
          <p className="text-sm text-slate-500 text-center">
            Press <kbd className="px-2 py-0.5 bg-slate-800 border border-slate-600 rounded text-xs font-mono text-slate-400">?</kbd> anytime to view shortcuts
          </p>
        </div>
      </div>
    </div>
  );
};
